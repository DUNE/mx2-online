import SC_Util
import CAENVMEwrapper
import wx
import time
import threading
import SC_MainMethods

def FindVMEdev(vmeDevList, devAddr):
    for dev in vmeDevList:
        if (dev.BaseAddress()==devAddr): return dev

class VMEDevice():
    def __init__(self, controller, baseAddr, moduleType):
        self.controller=controller
        self.baseAddr=baseAddr
        self.type=moduleType     
    def BaseAddress(self): return self.baseAddr
    def Type(self): return self.type
    def Description(self):
        if (self.type==SC_Util.VMEdevTypes.CROC or self.type==SC_Util.VMEdevTypes.CRIM or self.type==SC_Util.VMEdevTypes.DIG):
            return self.type+':'+str((self.baseAddr & 0xFF0000)>>16)
        if (self.type==SC_Util.VMEdevTypes.CH):
            return self.type+':'+str(((self.baseAddr & 0x00F000)>>12)/4)
        if (self.type==SC_Util.VMEdevTypes.DIGCH):
            return self.type+':'+str((self.baseAddr & 0x000F00)>>8)
        if (self.type==SC_Util.VMEdevTypes.CROCE): #32bits
            return self.type+':'+str((self.baseAddr & 0xFF000000)>>24)
        if (self.type==SC_Util.VMEdevTypes.CHE):   #32bits
            return self.type+':'+str(((self.baseAddr & 0x000F0000)>>16)/4)

class DIGChannel(VMEDevice):
    def __init__(self, chNumber, baseAddr, controller):
        self.chBaseAddr=baseAddr+(chNumber<<8)
        self.chNumber=chNumber;
        VMEDevice.__init__(self, controller, self.chBaseAddr, SC_Util.VMEdevTypes.DIGCH)
        addrWRZSThres           = 0x1024 + self.chBaseAddr
        addrWRZSNSamp           = 0x1028 + self.chBaseAddr
        addrWRThresholdValue    = 0x1080 + self.chBaseAddr
        addrWRThresholdOverUnder= 0x1084 + self.chBaseAddr
        addrROStatus            = 0x1088 + self.chBaseAddr
        addrROAMCFPGAFirmware   = 0x108C + self.chBaseAddr
        addrROBufferOccupancy   = 0x1094 + self.chBaseAddr
        addrWRDACOffset         = 0x1098 + self.chBaseAddr
        addrWRADCConfiguration  = 0x109C + self.chBaseAddr
        self.RegsWR={
            addrWRZSThres:{'name':'WRZSThres', 'value':0x0,
                'sects':{0x00000FFF:{'name':'Threshold', 'offset':0},
                         0x7FFFF000:{'name':'reserved', 'offset':12},
                         0x80000000:{'name':'NegativeLogic', 'offset':31}}},
            addrWRZSNSamp:{'name':'WRZSNSamp', 'value':0x0,
                'sects':{0x001FFFFF:{'name':'ZSAMP-NsubsOvUnThrs', 'offset':0},
                         0x0000FFFF:{'name':'ZLE-NafterThrs', 'offset':0},
                         0xFFFF0000:{'name':'ZLE-NbeforeThrs', 'offset':16}}},
            addrWRThresholdValue:{'name':'WRThresholdValue', 'value':0x0,
                'sects':{0x00000FFF:{'name':'Thrs', 'offset':0},
                         0xFFFFF000:{'name':'reserved', 'offset':12}}},
            addrWRThresholdOverUnder:{'name':'WRThresholdOverUnder', 'value':0x0,
                'sects':{0x00000FFF:{'name':'ThrsOvUn', 'offset':0},
                         0xFFFFF000:{'name':'reserved', 'offset':12}}},
            addrWRDACOffset:{'name':'WRDACOffset', 'value':0x0,
                'sects':{0x0000FFFF:{'name':'Offset', 'offset':0},
                         0xFFFF0000:{'name':'reserved', 'offset':16}}},
            addrWRADCConfiguration:{'name':'WRADCConfiguration', 'value':0x0,
                'sects':{0x0000FFFF:{'name':'ADCConfig', 'offset':0},
                         0xFFFF0000:{'name':'reserved', 'offset':16}}}
            }
        self.RegsWO={}
        self.RegsRO={
            addrROBufferOccupancy:{'name':'ROBufferOccupancy', 'value':0x0,
                'sects':{0x000003FF:{'name':'Occupied', 'offset':0}}},
            addrROStatus:{'name':'ROStatus', 'value':0x0,
                'sects':{0x00000001:{'name':'MemFull', 'offset':0},
                         0x00000002:{'name':'MemEmpty', 'offset':1},
                         0x00000004:{'name':'Busy', 'offset':2},
                         0x00000018:{'name':'reserved', 'offset':3},
                         0x00000020:{'name':'Error', 'offset':5}}},
            addrROAMCFPGAFirmware:{'name':'ROFPGAFirmware', 'value':0x0,
                'sects':{0x000000FF:{'name':'Minor', 'offset':0},
                         0x0000FF00:{'name':'Major', 'offset':8},
                         0x00FF0000:{'name':'Day', 'offset':16},
                         0x0F000000:{'name':'Month', 'offset':24},
                         0xF0000000:{'name':'Year', 'offset':28}}}
            }
    def Number(self): return self.chNumber
    def NodeList(self): return [self.Description(), []]
    def ReadAll(self):
        dReadAll={}; dReadAll.update(self.RegsWR); dReadAll.update(self.RegsRO)
        prevDataWidth=self.controller.dataWidth
        self.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD32
        for addr in list(dReadAll.keys()): dReadAll[addr]['value']=self.controller.ReadCycle(addr)
        self.controller.dataWidth=prevDataWidth
        return dReadAll

class DIG(VMEDevice):
    NChannels=8
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.DIG)
        #ROEventReadoutBuffer          = 0x0000-0x0FFC    //R
        self.addrWRChannelConfiguration          = 0x8000 + baseAddr
        self.addrWOChannelConfigurationBitSet    = 0x8004 + baseAddr
        self.addrWOChannelConfigurationBitClear  = 0x8008 + baseAddr
        self.addrWRBufferOrganization            = 0x800C + baseAddr
        self.addrWRBufferFree                    = 0x8010 + baseAddr     #Cristian's Note: CAEN say it's WR but I found it's WOnly
        self.addrWRCustomSize                    = 0x8020 + baseAddr
        self.addrWRAcquisitionControl            = 0x8100 + baseAddr
        self.addrROAcquisitionStatus             = 0x8104 + baseAddr
        self.addrWOSWTrigger                     = 0x8108 + baseAddr
        self.addrWRTriggerSourceEnableMask       = 0x810C + baseAddr
        self.addrWRFrontPanelTriggerOutEnableMask= 0x8110 + baseAddr
        self.addrWRPostTriggerSetting            = 0x8114 + baseAddr
        self.addrWRFrontPanelIOData              = 0x8118 + baseAddr     #Cristian's Note: CAEN say it's WR but I found it's ROnly
        self.addrWRFrontPanelIOControl           = 0x811C + baseAddr
        self.addrWRChannelEnableMask             = 0x8120 + baseAddr
        self.addrROFPGAFirmwareRevision          = 0x8124 + baseAddr
        self.addrROEventStored                   = 0x812C + baseAddr
        self.addrWRSetMonitorDAC                 = 0x8138 + baseAddr
        self.addrROBoardInfo                     = 0x8140 + baseAddr
        #WRMonitorMode = 0x8144,//RW  CAEN Note : To be implemented
        self.addrROEventSize                     = 0x814C + baseAddr
        self.addrWRVMEControl                    = 0xEF00 + baseAddr
        self.addrROVMEStatus                     = 0xEF04 + baseAddr
        self.addrWRBoardId                       = 0xEF08 + baseAddr
        self.addrWRMulticastBaseAddrAndCtrl      = 0xEF0C + baseAddr
        self.addrWRRelocationAddress             = 0xEF10 + baseAddr
        self.addrWRInterruptStatusId             = 0xEF14 + baseAddr
        self.addrWRInterruptEventNumber          = 0xEF18 + baseAddr
        self.addrWRBLTEventNumber                = 0xEF1C + baseAddr
        self.addrWRVMEScratch                    = 0xEF20 + baseAddr
        self.addrWOSWReset                       = 0xEF24 + baseAddr
        self.addrWOSWClear                       = 0xEF28 + baseAddr
        self.addrWRFlashEnable                   = 0xEF2C + baseAddr
        self.addrWRFlashData                     = 0xEF30 + baseAddr
        self.addrWOConfigurationReload           = 0xEF34 + baseAddr
        #ROConfigurationROM = 0xF000-0xF3FC //R
        self.RegsWR={
            self.addrWRChannelConfiguration:{'name':'WRChConfig', 'value':0x0,
                'sects':{0x00000001:{'name':'reserved', 'offset':0},
                         0x00000002:{'name':'TrgOverlapEn', 'offset':1},
                         0x00000004:{'name':'reserved', 'offset':2},
                         0x00000008:{'name':'TestPattGenEn', 'offset':3},
                         0x00000010:{'name':'MemAccesRnd0Seq1', 'offset':4},
                         0x00000020:{'name':'reserved', 'offset':5},
                         0x00000040:{'name':'TrgOutOnInpOver0Under1Thr', 'offset':6},
                         0x00000780:{'name':'reserved', 'offset':7},
                         0x00000800:{'name':'Pack25En', 'offset':11},
                         0x0000F000:{'name':'reserved', 'offset':12},
                         0x000F0000:{'name':'ZSAlgorithm', 'offset':16},
                         0xFFF00000:{'name':'reserved', 'offset':20}}},
            self.addrWRBufferOrganization:{'name':'WRBufferOrganiz', 'value':0x0,
                'sects':{0x0000000F:{'name':'BufferCode', 'offset':0},
                         0xFFFFFFF0:{'name':'reserved', 'offset':4}}},
            #Cristian's Note: CAEN say it's WR but I found it's WOnly
            #addrWRBufferFree:{'name':'WRBufferFree', 'value':0x0,
            #    'sects':{0x00000FFF:{'name':'FreesFistNBuffers', 'offset':0},
            #             0xFFFFF000:{'name':'reserved', 'offset':12}}},
            self.addrWRCustomSize:{'name':'WRCustomSize', 'value':0x0, 'sects':{}},
            self.addrWRAcquisitionControl:{'name':'WRAcqControl', 'value':0x0,
                'sects':{0x00000003:{'name':'Mode', 'offset':0},
                         0x00000004:{'name':'Stop0Run1', 'offset':2},
                         0x00000008:{'name':'CountTrgAcc0All1', 'offset':3},
                         0xFFFFFFF0:{'name':'reserved', 'offset':4}}},
            self.addrWRTriggerSourceEnableMask:{'name':'WRTrgSourceEnMask', 'value':0x0,
                'sects':{0x000000FF:{'name':'ChNTrgEn', 'offset':0},
                         0x00FFFF00:{'name':'reserved', 'offset':8},
                         0x07000000:{'name':'LocalTrgCoincLevel', 'offset':24},
                         0x38000000:{'name':'reserved', 'offset':27},
                         0x40000000:{'name':'ExtTrgEn', 'offset':30},
                         0x80000000:{'name':'SWTrgEn', 'offset':31}}},
            self.addrWRFrontPanelTriggerOutEnableMask:{'name':'WRPanelTrgOutEnMask', 'value':0x0,
                'sects':{0x000000FF:{'name':'ChNTrgEn', 'offset':0},
                         0x3FFFFF00:{'name':'reserved', 'offset':8},
                         0x40000000:{'name':'ExtTrgEn', 'offset':30},
                         0x80000000:{'name':'SWTrgEn', 'offset':31}}},
            self.addrWRPostTriggerSetting:{'name':'WRPostTrgSetting', 'value':0x0, 'sects':{}},
            #Cristian's Note: CAEN say it's WR but I found it's ROnly
            #addrWRFrontPanelIOData:{'name':'WRPanelIOData', 'value':0x0,
            #    'sects':{0x0000FFFF:{'name':'PanelIOdata', 'offset':0},
            #             0xFFFF0000:{'name':'reserved', 'offset':16}}},
            self.addrWRFrontPanelIOControl:{'name':'WRPanelIOControl', 'value':0x0,
                'sects':{0x00000001:{'name':'TrgClkNIM0TTL1', 'offset':0},
                         0x00000002:{'name':'PanelOutEn0HiZ1', 'offset':1},
                         0x00000004:{'name':'LVDS3-0In0Out1', 'offset':2},
                         0x00000008:{'name':'LVDS7-4In0Out1', 'offset':3},
                         0x00000010:{'name':'LVDS11-8In0Out1', 'offset':4},
                         0x00000020:{'name':'LVDS15-12In0Out1', 'offset':5},
                         0x000000C0:{'name':'Mode', 'offset':6},
                         0x00003F00:{'name':'reserved', 'offset':8},
                         0x00004000:{'name':'TrgOutTestMode', 'offset':14},
                         0x00008000:{'name':'TrgOutMode', 'offset':15},
                         0xFFFF0000:{'name':'reserved', 'offset':16}}},
            self.addrWRChannelEnableMask:{'name':'WRChEnMask', 'value':0x0,
                'sects':{0x000000FF:{'name':'ChNEn', 'offset':0},
                         0xFFFFFF00:{'name':'reserved', 'offset':8}}},
            self.addrWRSetMonitorDAC:{'name':'WRSetMonitorDAC', 'value':0x0,
                'sects':{0x00000FFF:{'name':'DACValue', 'offset':0},
                         0xFFFFF000:{'name':'reserved', 'offset':12}}},
            self.addrWRVMEControl:{'name':'WRVMEControl', 'value':0x0,
                'sects':{0x00000007:{'name':'InterruptLevel', 'offset':0},
                         0x00000008:{'name':'OpticalIntEn', 'offset':3},
                         0x00000010:{'name':'BERREn', 'offset':4},
                         0x00000020:{'name':'ALIGN64En', 'offset':5},
                         0x00000040:{'name':'RELOCEn', 'offset':6},
                         0x00000080:{'name':'RlsIntMode', 'offset':7},
                         0xFFFFFF00:{'name':'reserved', 'offset':8}}},
            self.addrWRBoardId:{'name':'WRBoardId', 'value':0x0,
                'sects':{0x0000001F:{'name':'GEO', 'offset':0},
                         0xFFFFFFE0:{'name':'reserved', 'offset':5}}},
            self.addrWRMulticastBaseAddrAndCtrl:{'name':'WRMCSTAddrAndCtrl', 'value':0x0,
                'sects':{0x000000FF:{'name':'MCST/CBLT', 'offset':0},
                         0x00000300:{'name':'DaisyChain', 'offset':8},
                         0xFFFFFC00:{'name':'reserved', 'offset':10}}},
            self.addrWRRelocationAddress:{'name':'WRRelocationAddr', 'value':0x0,
                'sects':{0x0000FFFF:{'name':'A31-A16AddrBits', 'offset':0},
                         0xFFFF0000:{'name':'reserved', 'offset':0}}},
            self.addrWRInterruptStatusId:{'name':'WRInterrStatusId', 'value':0x0, 'sects':{}},
            self.addrWRInterruptEventNumber:{'name':'WRInterrEventNumber', 'value':0x0,
                'sects':{0x000003FF:{'name':'EventNumber', 'offset':0},
                         0xFFFFFC00:{'name':'reserved', 'offset':10}}},
            self.addrWRBLTEventNumber:{'name':'WRBLTEventNumber', 'value':0x0,
                'sects':{0x000000FF:{'name':'CompleteEvents', 'offset':0},
                         0xFFFFFF00:{'name':'reserved', 'offset':8}}},
            self.addrWRVMEScratch:{'name':'WRVMEScratch', 'value':0x0, 'sects':{}}
            #Cristian's Note: I commented out the addrWRFlash ON PURPOSE (SAFETY) 
            #addrWRFlashEnable:{'name':'WRFlashEnable', 'value':0x0, 'sects':{}},
            #addrWRFlashData:{'name':'addrWRFlashData', 'value':0x0, 
            #    'sects':{0x000000FF:{'name':'SPIdata', 'offset':0},
            #             0xFFFFFF00:{'name':'reserved', 'offset':8}}}
            }
        self.RegsWO={
            self.addrWOChannelConfigurationBitSet:{'name':'WOChannelConfigurationBitSet', 'value':0x0,
                'sects':{0x000000FF:{'name':'SetBits', 'offset':0},
                         0xFFFFFF00:{'name':'reserved', 'offset':8}}},
            self.addrWOChannelConfigurationBitClear:{'name':'WOChannelConfigurationBitClear', 'value':0x0,
                'sects':{0x000000FF:{'name':'ClearBits', 'offset':0},
                         0xFFFFFF00:{'name':'reserved', 'offset':8}}},
            #Cristian's Note: CAEN say it's WR but I found it's WOnly
            self.addrWRBufferFree:{'name':'WOBufferFree', 'value':0x0,
                'sects':{0x00000FFF:{'name':'FreesFistNBuffers', 'offset':0},
                         0xFFFFF000:{'name':'reserved', 'offset':12}}},
            self.addrWOSWTrigger:{'name':'WOSWTrigger', 'value':0x0, 'sects':{}},
            self.addrWOSWReset:{'name':'WOSWReset', 'value':0x0, 'sects':{}},
            self.addrWOSWClear:{'name':'WOSWClear', 'value':0x0, 'sects':{}},
            self.addrWOConfigurationReload:{'name':'WOConfigurationReload', 'value':0x0, 'sects':{}}
            }
        self.RegsRO={
            self.addrROAcquisitionStatus:{'name':'ROAcqStatus', 'value':0x0,
                'sects':{0x00000003:{'name':'reserved', 'offset':0},
                         0x00000004:{'name':'RunOff0On1', 'offset':2},
                         0x00000008:{'name':'EventReady', 'offset':3},
                         0x00000010:{'name':'EventFull', 'offset':4},
                         0x00000020:{'name':'ClkExternal', 'offset':5},
                         0x00000040:{'name':'PLLBypass', 'offset':6},
                         0x00000080:{'name':'PLLLocked', 'offset':7},
                         0x00000100:{'name':'BoardReady', 'offset':8},
                         0xFFFFFE00:{'name':'reserved', 'offset':9}}},
            #Cristian's Note: CAEN say it's WR but I found it's ROnly
            self.addrWRFrontPanelIOData:{'name':'ROPanelIOData', 'value':0x0,
                'sects':{0x0000FFFF:{'name':'PanelIOdata', 'offset':0},
                         0xFFFF0000:{'name':'reserved', 'offset':16}}},
            self.addrROFPGAFirmwareRevision:{'name':'ROFPGAFirmwareRev', 'value':0x0,
                'sects':{0x000000FF:{'name':'Minor', 'offset':0},
                         0x0000FF00:{'name':'Major', 'offset':8},
                         0x00FF0000:{'name':'Day', 'offset':16},
                         0x0F000000:{'name':'Month', 'offset':24},
                         0xF0000000:{'name':'Year', 'offset':28}}},
            self.addrROEventStored:{'name':'ROEventStored', 'value':0x0, 'sects':{}},
            self.addrROBoardInfo:{'name':'ROBoardInfo', 'value':0x0,
                'sects':{0x000000FF:{'name':'BoardType', 'offset':0},
                         0x0000FF00:{'name':'MemorySize', 'offset':8},
                         0xFFFF0000:{'name':'reserved', 'offset':16}}},
            self.addrROEventSize:{'name':'ROEventSize', 'value':0x0, 'sects':{}},
            self.addrROVMEStatus:{'name':'ROVMEStatus', 'value':0x0,
                'sects':{0x00000001:{'name':'EventReady', 'offset':0},
                         0x00000002:{'name':'OutBufferFull', 'offset':1},
                         0x00000004:{'name':'BussError', 'offset':2},
                         0xFFFFFFF8:{'name':'reserved', 'offset':0}}}
            }
        self.channels=[]
        for chNumber in range(self.__class__.NChannels):
            self.channels.append(DIGChannel(chNumber, baseAddr, controller))
    def Channels(self): return self.channels
    def NodeList(self):
        return [self.Description(), [theCh.NodeList() for theCh in self.channels]]
    def ReadAll(self):
        dReadAll={}; dReadAll.update(self.RegsRO); dReadAll.update(self.RegsWR);
        prevDataWidth=self.controller.dataWidth
        self.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD32
        for addr in list(dReadAll.keys()): dReadAll[addr]['value']=self.controller.ReadCycle(addr)
        self.controller.dataWidth=prevDataWidth
        return dReadAll
    def ReadRegister(self, regAddr):
        prevDataWidth=self.controller.dataWidth
        self.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD32
        regData=self.controller.ReadCycle(regAddr)
        self.controller.dataWidth=prevDataWidth
        return regData
    def WriteRegister(self, regAddr, regData):
        prevDataWidth=self.controller.dataWidth
        self.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD32
        self.controller.WriteCycle(regAddr, regData)
        self.controller.dataWidth=prevDataWidth
    def AcquisitionControlRUN(self):
        data=self.ReadRegister(self.addrWRAcquisitionControl)
        data=data or 0x4
        self.WriteRegister(self.addrWRAcquisitionControl, data)
    def AcquisitionControlSTOP(self):
        data=self.ReadRegister(self.addrWRAcquisitionControl)
        #data=data and 0xB 
        '''I found out that after a SoftwareTrigger the [1:0] bits got set to 0xB
            for reasons I don't understand, and this prevents the sending of other
            software triggeres, so the work around is to set them back to 0'''
        data=0
        self.WriteRegister(self.addrWRAcquisitionControl, data)   
    def ReadNEventsStored(self): return self.ReadRegister(self.addrROEventStored)
    def ReadNextEventSize(self): return self.ReadRegister(self.addrROEventSize)
    def ReadAcqStatus(self): return self.ReadRegister(self.addrROAcquisitionStatus)
    def SendSoftwareTrigger(self): self.WriteRegister(self.addrWOSWTrigger, 0)   
    def SendSoftwareReset(self): self.WriteRegister(self.addrWOSWReset, 0) 
    def SendSoftwareClear(self): self.WriteRegister(self.addrWOSWClear, 0)
    def ReadOneEvent(self):
        msg=[]; iTry=1
        while (True):
            word0=self.ReadRegister(self.BaseAddress())
            if word0!=0xFFFFFFFF:
                eventSize=word0&0xFFFF
                msg.append(word0)
                msg.append(self.ReadRegister(self.BaseAddress()))
                msg.append(self.ReadRegister(self.BaseAddress()))
                msg.append(self.ReadRegister(self.BaseAddress()))
                for i in range(eventSize-4):
                    msg.append(self.ReadRegister(self.BaseAddress()))
                return DIGEvent(msg, 0)
            else:
                iTry+=1
                if iTry==3: raise Exception('\nUnable to find the "start" of the next Event')

def DIGDictOfRegsToString(dRegs):
    lines=[]
    lineHeader = str('%s%s%s%s'%(
        'RegAddr'.ljust(10,' '),'RegName'.ljust(20,' '),
        'RegValue'.ljust(10,' '), 'RegSections -->'.ljust(20,' ')))
    lines.append(lineHeader)
    dRegsKeys=list(dRegs.keys()); dRegsKeys.sort()
    for key in dRegsKeys:
        lineBody = str('%s%s%s'%(
            hex(key)[2:].rjust(6,'0').ljust(10,' ').upper(),
            dRegs[key]['name'].ljust(20, ' '),
            hex(dRegs[key]['value'])[2:-1].rjust(8,'0').ljust(10,' ').upper()))
        lineSections=''
        if dRegs[key]['sects']!={}:
            sectsKeys=list(dRegs[key]['sects'].keys())
            sectsKeys.sort()           
##            # USE THIS SECTION FOR MULTIPLE LINE FORMAT
##            iSection=0
##            for skey in sectsKeys:
##                theSection=str('%s(%s)=%s'%(dRegs[key]['sects'][skey]['name'],hex(skey),
##                    (dRegs[key]['value'] & skey)>>dRegs[key]['sects'][skey]['offset'])).ljust(35,' ')
##                if iSection==0: lineSections += theSection
##                else: lineSections += str('\n'+' '*40) + theSection
##                iSection+=1
            # USE THIS SECTION FOR ONLY ONE LINE FORMAT
            for skey in sectsKeys:
                theSection=str('%s(%s)=%s'%(dRegs[key]['sects'][skey]['name'],hex(skey),
                    (dRegs[key]['value'] & skey)>>dRegs[key]['sects'][skey]['offset'])).ljust(35,' ')
                lineSections += theSection
        lines.append(lineBody+lineSections)
    return lines

class CROCChannel(VMEDevice):
    def __init__(self, chNumber, baseAddr, controller):
        self.chBaseAddr=baseAddr+0x4000*chNumber
        self.chNumber=chNumber;
        VMEDevice.__init__(self, controller, self.chBaseAddr, SC_Util.VMEdevTypes.CH)
        self.RegRMemory      = self.chBaseAddr + SC_Util.CROCCHRegs.RegRMemory
        self.RegWInput       = self.chBaseAddr + SC_Util.CROCCHRegs.RegWInput
        self.RegWSendMessage = self.chBaseAddr + SC_Util.CROCCHRegs.RegWSendMessage
        self.RegRStatus      = self.chBaseAddr + SC_Util.CROCCHRegs.RegRStatus
        self.RegWClearStatus = self.chBaseAddr + SC_Util.CROCCHRegs.RegWClearStatus
        self.RegRLoopDelay   = self.chBaseAddr + SC_Util.CROCCHRegs.RegRLoopDelay
        self.RegRDPMPointer  = self.chBaseAddr + SC_Util.CROCCHRegs.RegRDPMPointer
        self.FEBs=[]
    def Number(self): return self.chNumber
    def NodeList(self):
        FEBsAddresses=[]
        #for feb in self.FEBs: FEBsAddresses.append("FE:"+str(feb.Address))
        for feb in self.FEBs: FEBsAddresses.append("FE:"+str(feb))
        return [self.Description(), FEBsAddresses]
    def ReadDPM(self, offset):
        if (offset>0x1FFF): raise Exception("address " + hex(offset) + " is out of range")
        return int(self.controller.ReadCycle(self.RegRMemory+offset))
    def ReadFullDPMBLT(self):
        dpmPointer=self.DPMPointerRead()
        rcvmsgLength=dpmPointer-2
        #make D32 BLT reading size compatible with rcvmsgLength
        if rcvmsgLength%4==0: size=rcvmsgLength
        else: size=rcvmsgLength+(4-(rcvmsgLength%4))
        return self.controller.ReadCycleBLT(self.RegRMemory, size)
    def WriteFIFO(self, data): self.controller.WriteCycle(self.RegWInput, data)
    def SendMessage(self): self.controller.WriteCycle(self.RegWSendMessage, 0x0101)
    def ReadStatus(self): return int(self.controller.ReadCycle(self.RegRStatus))
    def ClearStatus(self): self.controller.WriteCycle(self.RegWClearStatus, 0x0202)
    def ReadLoopDelay(self): return int(self.controller.ReadCycle(self.RegRLoopDelay)) 
    def DPMPointerReset(self): self.controller.WriteCycle(self.RegWClearStatus, 0x0808)
    def DPMPointerRead(self):
        data=int(self.controller.ReadCycle(self.RegRDPMPointer))
        datasw=int(((data&0xFF)<<8) | ((data&0xFF00)>>8))
        return datasw

class CROCEChannelE(VMEDevice):
    def __init__(self, cheNumber, baseAddr, controller):
        self.cheBaseAddr=baseAddr+0x00040000*cheNumber
        self.cheNumber=cheNumber;
        VMEDevice.__init__(self, controller, self.cheBaseAddr, SC_Util.VMEdevTypes.CHE)
        self.RRcvMemory                = self.cheBaseAddr + SC_Util.CROCECHERegs.RRcvMemory
        self.WSendMemory               = self.cheBaseAddr + SC_Util.CROCECHERegs.WSendMemory
        self.RFramePointersMemory      = self.cheBaseAddr + SC_Util.CROCECHERegs.RFramePointersMemory
        self.RegWRConfig               = self.cheBaseAddr + SC_Util.CROCECHERegs.RegWRConfig
        self.RegWCommands              = self.cheBaseAddr + SC_Util.CROCECHERegs.RegWCommand
        self.RegRRDFECounter           = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRRDFECounter
        self.RegRTXRstTpInDelayCounter = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRTXRstTpInDelayCounter
        self.RegRRcvMemFramesCounter   = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRRcvMemFramesCounter
        self.RegRStatusFrame           = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRStatusFrame
        self.RegRStatusTXRX            = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRStatusTXRX
        self.RegRRcvMemWPointer        = self.cheBaseAddr + SC_Util.CROCECHERegs.RegRRcvMemWPointer
        self.RegWRHeaderData           = self.cheBaseAddr + SC_Util.CROCECHERegs.RegWRHeaderData
        self.WRFlashMemory             = self.cheBaseAddr + SC_Util.CROCECHERegs.WRFlashMemory
        self.FEBs=[]
    def Number(self): return self.cheNumber
    def NodeList(self):
        FEBsAddresses=[]
        #for feb in self.FEBs: FEBsAddresses.append("FE:"+str(feb.Address))
        for feb in self.FEBs: FEBsAddresses.append("FE:"+str(feb))
        return [self.Description(), FEBsAddresses]
    def ReadConfiguration(self): return int(self.controller.ReadCycle(self.RegWRConfig, am='A32_U_DATA', dw='D16'))
    def WriteConfiguration(self, data): self.controller.WriteCycle(self.RegWRConfig, data, am='A32_U_DATA', dw='D16')
    def WriteCommands(self, data): self.controller.WriteCycle(self.RegWCommands, data, am='A32_U_DATA', dw='D16')
    def ReadRDFECounter(self): return (0x3FFF & int(self.controller.ReadCycle(self.RegRRDFECounter, am='A32_U_DATA', dw='D16')))
    def ReadTXRstTpInDelayCounter(self):
        bit6to0=(0xFE00 & int(self.controller.ReadCycle(self.RegRTXRstTpInDelayCounter, am='A32_U_DATA', dw='D16')))>>9
        bit7   =(0x4000 & int(self.controller.ReadCycle(self.RegRRDFECounter, am='A32_U_DATA', dw='D16')))>> 14
        return int((bit7<<7)+bit6to0)
    def ReadRcvMemFramesCounter(self):return 0x01FF & int(self.controller.ReadCycle(self.RegRRcvMemFramesCounter, am='A32_U_DATA', dw='D16'))
    def ReadStatusFrame(self): return int(self.controller.ReadCycle(self.RegRStatusFrame, am='A32_U_DATA', dw='D16'))
    def ReadStatusTXRX(self): return int(self.controller.ReadCycle(self.RegRStatusTXRX, am='A32_U_DATA', dw='D16'))
    def ReadRcvMemWPointer(self):
        bit15to0=(0xFFFF & int(self.controller.ReadCycle(self.RegRRcvMemWPointer, am='A32_U_DATA', dw='D16')))
        bit16   =(0x8000 & int(self.controller.ReadCycle(self.RegRRDFECounter, am='A32_U_DATA', dw='D16')))>>15
        return int((bit16<<16)+bit15to0)
    def ReadHeaderData(self): return int(self.controller.ReadCycle(self.RegWRHeaderData, am='A32_U_DATA', dw='D16'))
    def WriteHeaderData(self, data): self.controller.WriteCycle(self.RegWRHeaderData, data, am='A32_U_DATA', dw='D16')
    def ReadAllRegisters(self): return [
        int(self.controller.ReadCycle(self.RegWRConfig, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegRRDFECounter, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegRRcvMemFramesCounter, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegRStatusFrame, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegRStatusTXRX, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegRRcvMemWPointer, am='A32_U_DATA', dw='D16')),
        int(self.controller.ReadCycle(self.RegWRHeaderData, am='A32_U_DATA', dw='D16'))]
    def WriteSendMemory(self, data, addr=0):
        waddr = self.WSendMemory | addr
        self.controller.WriteCycle(waddr, data, am='A32_U_DATA', dw='D16')
    def WriteFlashMemory(self, data, addr=0):
        waddr = self.WRFlashMemory | addr
        self.controller.WriteCycle(waddr, data, am='A32_U_DATA', dw='D16')
    def ReadReceiveMemory(self, addr, dw='D16'):
        return int(self.controller.ReadCycle(self.RRcvMemory | addr, 'A32_U_DATA', dw))
    def ReadFramePointersMemory(self, addr, dw='D16'):
        return int(self.controller.ReadCycle(self.RFramePointersMemory | addr, 'A32_U_DATA', dw))
    def ReadFlashMemoryTop(self, addr, dw='D16'):
        return int(self.controller.ReadCycle(self.WRFlashMemory | addr, 'A32_U_DATA', dw))
    def ReadFlashMemoryBottom(self, addr, dw='D16'):
        return int(self.controller.ReadCycle((self.WRFlashMemory+0x400) | addr, 'A32_U_DATA', dw))
    def ReadFullDPMBLT(self):
        dpmPointer=self.ReadRcvMemWPointer()+((0x8000&self.ReadRDFECounter())<<1)
        rcvmsgLength=dpmPointer
        #make D32 BLT reading size compatible with rcvmsgLength
        if rcvmsgLength%4==0: size=rcvmsgLength
        else: size=rcvmsgLength+(4-(rcvmsgLength%4))
        return self.controller.ReadCycleBLT(self.RRcvMemory, size, am='A32_U_BLT')
##    def ReadFullDPMD16(self):
##        rcvmsgLength=self.ReadRcvMemWPointer()+((0x8000&self.ReadRDFECounter())<<1)
##        rcvmembytes=[]
##        for iaddr in range(0,rcvmsgLength,2):
##            data=self.ReadReceiveMemory(self.RRcvMemory | iaddr, dw='D16')
##            rcvmembytes.append((0xFF00&data)>>8)
##            rcvmembytes.append((0x00FF&data))
##        return rcvmembytes
    def GetWRRegValues(self):
        return [(hex(self.RegWRConfig)[2:].rjust(8, '0'),  hex(self.ReadConfiguration())[2:].rjust(4, '0')),
                (hex(self.RegWRHeaderData)[2:].rjust(8, '0'), hex(self.ReadHeaderData())[2:].rjust(4, '0'))]
    def FlashWREN(self):
        self.FlashWriteGenericSequence([0x0006])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashWRDI(self):
        self.FlashWriteGenericSequence([0x0004])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashRDSR(self,ntimesOdd=1):
        if ntimesOdd%2==0:
            raise Exception('FlashRDSR Error1: parameter ntimesOdd must be odd integer')
        theWordsSequence=[0x0005]
        if ntimesOdd>=3:
            for i in range(1,ntimesOdd,2):
                theWordsSequence.append(0x0)
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashWRSR(self, dataByte):
        self.FlashWriteGenericSequence([((dataByte&0xFF)<<8)+0x01])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashREAD(self, addr24bits, nBytesEven, dw='D16'):
        if addr24bits%4!=0:
            raise Exception('FlashREAD Error1: parameter addr24bits must be multiple of four, found %s'%addr24bits)
        if nBytesEven%2==1:
            raise Exception('FlashREAD Error2: parameter nBytesEven must be even integer, found %s'%nBytesEven)
        theWordsSequence=[(((addr24bits&0xFF0000)>>8)+0x03), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)]+(nBytesEven/2)*[0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
        time.sleep(0.002) # *** CG 11.14.2014 Missing hanshake to check that 'SendFlashMessage' is done ***
        msgrcvstr=''
        if dw=='D16':
            for i in range(len(theWordsSequence)):
                msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i,dw='D16')).upper()[2:].rjust(4, '0')
        if dw=='D32':
            if len(theWordsSequence)%2==0:
                theLength32=len(theWordsSequence)/2
            else:
                theLength32=(len(theWordsSequence)+1)/2
            for i in range(theLength32):
                msgrcvstr += hex(self.ReadFlashMemoryBottom(4*i,dw='D32')).upper()[2:].rjust(8, '0')
            if len(theWordsSequence)%2==1:
                msgrcvstr=msgrcvstr[:-4]
        if len(msgrcvstr)!=2*(4+nBytesEven):
            raise Exception('FlashREAD Error3: Hex string length of READOUT page is %s, should be %s'%(len(msgrcvstr),2*(4+nBytesEven)))
        return msgrcvstr
    def FlashSE(self, addr24bits):
        self.FlashWriteGenericSequence([(((addr24bits&0xFF0000)>>8)+0x20), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashBE(self, addr24bits):
        self.FlashWriteGenericSequence([(((addr24bits&0xFF0000)>>8)+0x52), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashCE(self):
        self.FlashWriteGenericSequence([0x60])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashWRITE(self, addr24bits, wordsData):
        theWordsSequence=[(((addr24bits&0xFF0000)>>8)+0x02), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)]+wordsData
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashDP(self):
        self.FlashWriteGenericSequence([0xB9])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashRDP(self):
        self.FlashWriteGenericSequence([0xAB])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashRDID(self):
        theWordsSequence=[0x9F,0x0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashREMS(self):
        theWordsSequence=[0x90,0x0,0x0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashRDSCUR(self,ntimesOdd=1):
        if ntimesOdd%2==0:
            raise Exception('FlashRDSR Error1: parameter ntimesOdd must be odd integer')
        theWordsSequence=[0x002B]
        if ntimesOdd>=3:
            for i in range(1,ntimesOdd,2):
                theWordsSequence.append(0x0)
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashWRSCUR(self, dataByte):
        self.FlashWriteGenericSequence([((data&0xFF)<<8)+0x2F])
        self.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
    def FlashWriteGenericSequence(self, theWordsSequence):
        self.WriteCommands(SC_Util.CHECmds['ClearStatus'])
        if self.ReadStatusFrame()!=0x4040:
            raise Exception('FlashWriteGenericSequence Error1: StatusFrame=%s after ClearStatus'%hex(self.ReadStatusFrame()))
        for word in theWordsSequence:
            self.WriteFlashMemory(word)
        if self.ReadStatusFrame()!=0x4040:
            raise Exception('FlashWriteGenericSequence Error2: StatusFrame=%s after WriteFlashMemory'%hex(self.ReadStatusFrame()))

class CROC(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CROC)
        self.RegWRTimingSetup      = baseAddr + SC_Util.CROCRegs.RegWRTimingSetup
        self.RegWRResetAndTestMask = baseAddr + SC_Util.CROCRegs.RegWRResetAndTestMask
        self.RegWChannelReset      = baseAddr + SC_Util.CROCRegs.RegWChannelReset
        self.RegWFastCommand       = baseAddr + SC_Util.CROCRegs.RegWFastCommand
        self.RegWTestPulse         = baseAddr + SC_Util.CROCRegs.RegWTestPulse 
        self.channels=[]
        for chNumber in range(4):
            self.channels.append(CROCChannel(chNumber, baseAddr, controller))
        #self.channels[0].FEBs=[FEB(1), FEB(2), FEB(3), FEB(4)]
        #self.channels[1].FEBs=[FEB(5), FEB(6), FEB(7), FEB(8)]
        #self.channels[2].FEBs=[FEB(9), FEB(10), FEB(11), FEB(12)]
        #self.channels[3].FEBs=[FEB(13), FEB(14), FEB(15), FEB(16), FEB(17)]
    def Channels(self): return self.channels
    def NodeList(self): return [self.Description(), 
        [self.channels[0].NodeList(), self.channels[1].NodeList(),
        self.channels[2].NodeList(), self.channels[3].NodeList()]]
    def WriteTimingSetup(self, data): self.controller.WriteCycle(self.RegWRTimingSetup, data)
    def ReadTimingSetup(self): return int(self.controller.ReadCycle(self.RegWRTimingSetup))
    def SendFastCommand(self, data): self.controller.WriteCycle(self.RegWFastCommand, data)
    def WriteRSTTP(self, data): self.controller.WriteCycle(self.RegWRResetAndTestMask, data)
    def ReadRSTTP(self): return int(self.controller.ReadCycle(self.RegWRResetAndTestMask))
    def SendRSTOnly(self): self.controller.WriteCycle(self.RegWChannelReset, 0x0202)
    def SendTPOnly(self): self.controller.WriteCycle(self.RegWTestPulse, 0x0404)
    def GetWRRegValues(self):
        return [(hex(self.RegWRTimingSetup)[2:].rjust(6, '0'),  hex(self.ReadTimingSetup())[2:].rjust(4, '0')),
                (hex(self.RegWRResetAndTestMask)[2:].rjust(6, '0'), hex(self.ReadRSTTP())[2:].rjust(4, '0'))]

class CROCE(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CROCE)
        self.RegWRTimingSetup      = baseAddr + SC_Util.CROCERegs.RegWRTimingSetup
        self.RegWRResetAndTestMask = baseAddr + SC_Util.CROCERegs.RegWRResetAndTestMask
        self.RegWChannelReset      = baseAddr + SC_Util.CROCERegs.RegWChannelReset
        self.RegWFastCommand       = baseAddr + SC_Util.CROCERegs.RegWFastCommand
        self.RegWTestPulse         = baseAddr + SC_Util.CROCERegs.RegWTestPulse
        self.RegWRRDFEPulseDelay   = baseAddr + SC_Util.CROCERegs.RegWRRDFEPulseDelay
        self.RegWSoftwareRDFE      = baseAddr + SC_Util.CROCERegs.RegWSoftwareRDFE
        self.RegWRStatusAndVersion = baseAddr + SC_Util.CROCERegs.RegRStatusAndVersion
        self.WRFlashMemory         = baseAddr + SC_Util.CROCERegs.WRFlashMemory
        self.channels=[]
        for cheNumber in range(4):
            self.channels.append(CROCEChannelE(cheNumber, baseAddr, controller))
        self.includeCRC='Unknown'
    def Channels(self): return self.channels
    def NodeList(self): return [self.Description(), 
        [self.channels[0].NodeList(), self.channels[1].NodeList(),
        self.channels[2].NodeList(), self.channels[3].NodeList()]]
    def WriteTimingSetup(self, data): self.controller.WriteCycle(self.RegWRTimingSetup, data, am='A32_U_DATA', dw='D16')
    def ReadTimingSetup(self): return int(self.controller.ReadCycle(self.RegWRTimingSetup, am='A32_U_DATA', dw='D16'))
    def SendFastCommand(self, data): self.controller.WriteCycle(self.RegWFastCommand, data, am='A32_U_DATA', dw='D16')
    def WriteRSTTP(self, data): self.controller.WriteCycle(self.RegWRResetAndTestMask, data, am='A32_U_DATA', dw='D16'),
    def ReadRSTTP(self): return int(self.controller.ReadCycle(self.RegWRResetAndTestMask, am='A32_U_DATA', dw='D16'))
    def SendRSTOnly(self): self.controller.WriteCycle(self.RegWChannelReset, 0x0202, am='A32_U_DATA', dw='D16')
    def SendTPOnly(self): self.controller.WriteCycle(self.RegWTestPulse, 0x0404, am='A32_U_DATA', dw='D16')
    def SendFLASHReload(self): self.controller.WriteCycle(self.RegWChannelReset, 0x0808, am='A32_U_DATA', dw='D16')
    def WriteRDFEPulseDelay(self, data): self.controller.WriteCycle(self.RegWRRDFEPulseDelay, data, am='A32_U_DATA', dw='D16')
    def ReadRDFEPulseDelay(self): return int(self.controller.ReadCycle(self.RegWRRDFEPulseDelay, am='A32_U_DATA', dw='D16'))
    def SendSoftwareRDFE(self): self.controller.WriteCycle(self.RegWSoftwareRDFE, 0x001F, am='A32_U_DATA', dw='D16')
    def ReadStatusAndVersion(self): return int(self.controller.ReadCycle(self.RegWRStatusAndVersion, am='A32_U_DATA', dw='D16'))
    def WriteStatusAndVersion(self, data): self.controller.WriteCycle(self.RegWRStatusAndVersion, data, am='A32_U_DATA', dw='D16')
    def ReadFlashMemoryTop(self, addr, dw='D16'):
        return int(self.controller.ReadCycle(self.WRFlashMemory | addr, 'A32_U_DATA', dw))
    def ReadFlashMemoryBottom(self, addr, dw='D16'):
        return int(self.controller.ReadCycle((self.WRFlashMemory+0x400) | addr, 'A32_U_DATA', dw))
    def FlashWREN(self):
        self.FlashWriteGenericSequence([0x0006])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashWRDI(self):
        self.FlashWriteGenericSequence([0x0004])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashRDSR(self,ntimesOdd=1):
        if ntimesOdd%2==0:
            raise Exception('FlashRDSR Error1: parameter ntimesOdd must be odd integer')
        theWordsSequence=[0x0005]
        if ntimesOdd>=3:
            for i in range(1,ntimesOdd,2):
                theWordsSequence.append(0x0)
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashWRSR(self, dataByte):
        self.FlashWriteGenericSequence([((dataByte&0xFF)<<8)+0x01])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashSE(self, addr24bits):
        self.FlashWriteGenericSequence([(((addr24bits&0xFF0000)>>8)+0x20), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashBE(self, addr24bits):
        self.FlashWriteGenericSequence([(((addr24bits&0xFF0000)>>8)+0x52), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashCE(self):
        self.FlashWriteGenericSequence([0x60])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)                               
    def FlashWRITE(self, addr24bits, wordsData):
        theWordsSequence=[(((addr24bits&0xFF0000)>>8)+0x02), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)]+wordsData
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashDP(self):
        self.FlashWriteGenericSequence([0xB9])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashRDP(self):
        self.FlashWriteGenericSequence([0xAB])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashRDID(self):
        theWordsSequence=[0x9F,0x0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashREMS(self):
        theWordsSequence=[0x90,0x0,0x0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashRDSCUR(self,ntimesOdd=1):
        if ntimesOdd%2==0:
            raise Exception('FlashRDSR Error1: parameter ntimesOdd must be odd integer')
        theWordsSequence=[0x002B]
        if ntimesOdd>=3:
            for i in range(1,ntimesOdd,2):
                theWordsSequence.append(0x0)
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
        msgrcvstr=''
        for i in range(len(theWordsSequence)):
            msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i)).upper()[2:].rjust(4, '0')           
        return msgrcvstr
    def FlashWRSCUR(self, dataByte):
        self.FlashWriteGenericSequence([((data&0xFF)<<8)+0x2F])
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
    def FlashREAD(self, addr24bits, nBytesEven, dw='D16'):
        if addr24bits%4!=0:
            raise Exception('FlashREAD Error1: parameter addr24bits must be multiple of four, found %s'%addr24bits)
        if nBytesEven%2==1:
            raise Exception('FlashREAD Error2: parameter nBytesEven must be even integer, found %s'%nBytesEven)
        theWordsSequence=[(((addr24bits&0xFF0000)>>8)+0x03), ((addr24bits&0xFF)<<8)+((addr24bits&0xFF00)>>8)]+(nBytesEven/2)*[0]
        self.FlashWriteGenericSequence(theWordsSequence)
        self.WriteStatusAndVersion(0x5000) # Keep FlashMem_Enable(bit#12) set and Send CmdSendFlashMessage(bit#14)
        time.sleep(0.002) # *** CG 11.14.2014 Missing hanshake to check that 'SendFlashMessage' is done ***
        msgrcvstr=''
        if dw=='D16':
            for i in range(len(theWordsSequence)):
                msgrcvstr += hex(self.ReadFlashMemoryBottom(2*i,dw='D16')).upper()[2:].rjust(4, '0')
        if dw=='D32':
            if len(theWordsSequence)%2==0:
                theLength32=len(theWordsSequence)/2
            else:
                theLength32=(len(theWordsSequence)+1)/2
            for i in range(theLength32):
                msgrcvstr += hex(self.ReadFlashMemoryBottom(4*i,dw='D32')).upper()[2:].rjust(8, '0')
            if len(theWordsSequence)%2==1:
                msgrcvstr=msgrcvstr[:-4]
        if len(msgrcvstr)!=2*(4+nBytesEven):
            raise Exception('FlashREAD Error3: Hex string length of READOUT page is %s, should be %s'%(len(msgrcvstr),2*(4+nBytesEven)))
        return msgrcvstr
    def FlashWriteGenericSequence(self, theWordsSequence):
        self.WriteStatusAndVersion(0x9000) # Keep FlashMem_Enable(bit#12) set and Send CmdClearStatus(bit#15)
        theConfig=(0xFFF0 & self.ReadStatusAndVersion()) #discard firmware version bits#3-0
        if (0x1000!=theConfig):
            raise Exception('FlashWriteGenericSequence Error1: StatusFrame=%4X after ClearStatus'%theConfig)
        for word in theWordsSequence:
            self.WriteFlashMemory(word)
        theConfig=(0xFFF0 & self.ReadStatusAndVersion()) #discard firmware version bits#3-0
        if (0x1000!=theConfig):
            raise Exception('FlashWriteGenericSequence Error2: StatusFrame=%4X after WriteFlashMemory'%theConfig)
    def WriteFlashMemory(self, data, addr=0):
        waddr = self.WRFlashMemory | addr
        self.controller.WriteCycle(waddr, data, am='A32_U_DATA', dw='D16')
    def GetWRRegValues(self):
        return [(hex(self.RegWRTimingSetup)[2:].rjust(8, '0'),  hex(self.ReadTimingSetup())[2:].rjust(4, '0')),
                (hex(self.RegWRResetAndTestMask)[2:].rjust(8, '0'), hex(self.ReadRSTTP())[2:].rjust(4, '0')),
                (hex(self.RegWRRDFEPulseDelay)[2:].rjust(8, '0'), hex(self.ReadRDFEPulseDelay())[2:].rjust(4, '0'))]  

class CRIM(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CRIM)
        self.TimingModule = CRIMTimingModule(controller, baseAddr)
        self.ChannelModule = CRIMChannelModule(controller, baseAddr)
        self.InterrupterModule = CRIMInterrupterModule(controller, baseAddr)
    def NodeList(self): return [self.Description(), []]
    def GetWRRegValues(self):
        regval = [(hex(self.ChannelModule.RegWRMode)[2:].rjust(6, '0'), hex(self.ChannelModule.ReadMode())[2:].rjust(4, '0')),
            (hex(self.TimingModule.RegWRTimingSetup)[2:].rjust(6, '0'),  hex(self.TimingModule.ReadTimingSetup())[2:].rjust(4, '0')),
            (hex(self.TimingModule.RegWRGateWidth)[2:].rjust(6, '0'), hex(self.TimingModule.ReadGateWidth())[2:].rjust(4, '0')),
            (hex(self.TimingModule.RegWRTCALBDelay)[2:].rjust(6, '0'), hex(self.TimingModule.ReadTCALBDelay())[2:].rjust(4, '0')),
            (hex(self.TimingModule.RegWRScrapRegister)[2:].rjust(6, '0'), hex(self.TimingModule.ReadScrap())[2:].rjust(4, '0')),
            (hex(self.InterrupterModule.RegWRMask)[2:].rjust(6, '0'), hex(self.InterrupterModule.ReadMask())[2:].rjust(4, '0')),
            (hex(self.InterrupterModule.RegWRStatus)[2:].rjust(6, '0'), hex(self.InterrupterModule.ReadStatus())[2:].rjust(4, '0')),
            (hex(self.InterrupterModule.RegWRIntConfig)[2:].rjust(6, '0'), hex(self.InterrupterModule.ReadIntConfig())[2:].rjust(4, '0'))]
        for RegAddr in self.InterrupterModule.RegWRVectorTable:
            regval.append((hex(RegAddr)[2:].rjust(6, '0'), hex(int(self.controller.ReadCycle(RegAddr)))[2:].rjust(4, '0')))
        return regval
class CRIMTimingModule(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CRIM)
        self.RegWRTimingSetup = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWRTimingSetup
        self.RegWRGateWidth   = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWRGateWidth
        self.RegWRTCALBDelay  = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWRTCALBDelay
        self.RegWTRIGGERSend  = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWTRIGGERSend
        self.RegWTCALBSend    = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWTCALBSend
        self.RegWGATE         = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWGATE
        self.RegWCNTRST       = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWCNTRST
        self.RegWSequencerReset     = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWSequencerReset
        self.RegRMTMTimingViolations= baseAddr + SC_Util.CRIMTimingModuleRegs.RegRMTMTimingViolations
        self.RegWRScrapRegister     = baseAddr + SC_Util.CRIMTimingModuleRegs.RegWRScrapRegister
        self.RegRGateTimestampLower = baseAddr + SC_Util.CRIMTimingModuleRegs.RegRGateTimestampLower
        self.RegRGateTimestampUpper = baseAddr + SC_Util.CRIMTimingModuleRegs.RegRGateTimestampUpper
    def WriteTimingSetup(self, data): self.controller.WriteCycle(self.RegWRTimingSetup, data)
    def ReadTimingSetup(self): return int(self.controller.ReadCycle(self.RegWRTimingSetup))
    def WriteGateWidth(self, data): self.controller.WriteCycle(self.RegWRGateWidth, data)
    def ReadGateWidth(self): return int(self.controller.ReadCycle(self.RegWRGateWidth))
    def WriteTCALBDelay(self, data): self.controller.WriteCycle(self.RegWRTCALBDelay, data)
    def ReadTCALBDelay(self): return int(self.controller.ReadCycle(self.RegWRTCALBDelay))
    def SendTRIGGER(self): self.controller.WriteCycle(self.RegWTRIGGERSend, 0x0404)
    def SendTCALB(self): self.controller.WriteCycle(self.RegWTCALBSend, 0x0404)
    def SendGateStart(self): self.controller.WriteCycle(self.RegWGATE, 0x0401)
    def SendGateStop(self): self.controller.WriteCycle(self.RegWGATE, 0x0402)
    def SendSequenceCNTRST(self): self.controller.WriteCycle(self.RegWCNTRST, 0x0202)
    def SendSequenceCNTRSTSGATETCALB(self): self.controller.WriteCycle(self.RegWCNTRST, 0x0808)
    def WriteSequencerReset(self): self.controller.WriteCycle(self.RegWSequencerReset, 0x0202)
    def ReadMTMTimingViolations(self): return int(self.controller.ReadCycle(self.RegRMTMTimingViolations))
    def WriteMTMTimingViolationsClear(self): self.controller.WriteCycle(self.RegWCNTRST, 0x1001)
    def WriteScrap(self, data): self.controller.WriteCycle(self.RegWRScrapRegister, data)
    def ReadScrap(self): return int(self.controller.ReadCycle(self.RegWRScrapRegister))
    def ReadGateTimestamp(self):
        dataLower = int(self.controller.ReadCycle(self.RegRGateTimestampLower))
        dataUpper = (int(self.controller.ReadCycle(self.RegRGateTimestampUpper)) & 0xFFF) << 16
        return dataUpper | dataLower
class CRIMChannelModule(CROCChannel, VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CRIM)
        self.RegRMemory     = baseAddr + SC_Util.CRIMCHModuleRegs.RegRMemory
        self.RegWInput      = baseAddr + SC_Util.CRIMCHModuleRegs.RegWInput
        self.RegWResetFIFO  = baseAddr + SC_Util.CRIMCHModuleRegs.RegWResetFIFO
        self.RegWSendMessage= baseAddr + SC_Util.CRIMCHModuleRegs.RegWSendMessage
        self.RegRStatus     = baseAddr + SC_Util.CRIMCHModuleRegs.RegRStatus
        self.RegWClearStatus= baseAddr + SC_Util.CRIMCHModuleRegs.RegWClearStatus
        self.RegWSendSYNC   = baseAddr + SC_Util.CRIMCHModuleRegs.RegRLoopDelay
        self.RegRDPMPointer = baseAddr + SC_Util.CRIMCHModuleRegs.RegRDPMPointer
        self.RegRDecodTmgCmd= baseAddr + SC_Util.CRIMCHModuleRegs.RegRDecodTmgCmd
        self.RegWRMode      = baseAddr + SC_Util.CRIMCHModuleRegs.RegWRMode
    def ResetFIFO(self): self.controller.WriteCycle(self.RegWResetFIFO, 0x0808)
    def SendSYNC(self): self.controller.WriteCycle(self.RegWSendSYNC, 0x0101)
    def ReadDecodTmgCmd(self): return int(self.controller.ReadCycle(self.RegRDecodTmgCmd))
    def WriteMode(self, data): self.controller.WriteCycle(self.RegWRMode, data)
    def ReadMode(self): return int(self.controller.ReadCycle(self.RegWRMode))
class CRIMInterrupterModule(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CRIM)
        self.RegWRMask = baseAddr + SC_Util.CRIMInterrupterModuleRegs.RegWRMask
        self.RegWRStatus = baseAddr + SC_Util.CRIMInterrupterModuleRegs.RegWRStatus
        self.RegWClearInterrupt = baseAddr + SC_Util.CRIMInterrupterModuleRegs.RegWClearInterrupt
        self.RegWRIntConfig = baseAddr + SC_Util.CRIMInterrupterModuleRegs.RegWRIntConfig
        self.RegWRVectorTable = []
        for RegAddr in SC_Util.CRIMInterrupterModuleRegs.RegWRVectorTable:
            self.RegWRVectorTable.append(baseAddr + RegAddr)
    def WriteMask(self, data): self.controller.WriteCycle(self.RegWRMask, data)
    def ReadMask(self): return int(self.controller.ReadCycle(self.RegWRMask))
    def WriteStatus(self, data): self.controller.WriteCycle(self.RegWRStatus, data)
    def ReadStatus(self): return int(self.controller.ReadCycle(self.RegWRStatus))
    def SendClearInterrupt(self): self.controller.WriteCycle(self.RegWClearInterrupt, 0x81)
    def WriteIntConfig(self, data): self.controller.WriteCycle(self.RegWRIntConfig, data)
    def ReadIntConfig(self): return int(self.controller.ReadCycle(self.RegWRIntConfig))
    def WriteVectorTable(self, data):
        for i in range(len(self.RegWRVectorTable)):
            self.controller.WriteCycle(self.RegWRVectorTable[i], data[i])
    def ReadVectorTable(self):
        data = []
        for RegAddr in self.RegWRVectorTable: data.append(int(self.controller.ReadCycle(RegAddr)))
        return data

class FEB():
    def __init__(self, febAddress):
        self.Address=febAddress
    def FPGADescription(self, theCROCXChannelX, theCROCX, theType='CROC'):
        if theType=='CROC': return '%s:%d,%d,%d,%d'%(SC_Util.VMEdevTypes.FPGA, self.Address,
            theCROCXChannelX.chNumber, theCROCX.baseAddr>>16, theCROCX.controller.boardNum)
        if theType=='CROCE': return '%s:%d,%d,%d,%d'%(SC_Util.VMEdevTypes.FPGA, self.Address,
            theCROCXChannelX.cheNumber, theCROCX.baseAddr>>24, theCROCX.controller.boardNum)
    def TRIPDescription(self, theTripIndex, theCROCXChannelX, theCROCX, theType='CROC'):
        if theType=='CROC': return '%s:%s,%d,%d,%d,%d'%(SC_Util.VMEdevTypes.TRIP,
            theTripIndex, self.Address, theCROCXChannelX.chNumber, theCROCX.baseAddr>>16, theCROCX.controller.boardNum)
        if theType=='CROCE': return '%s:%s,%d,%d,%d,%d'%(SC_Util.VMEdevTypes.TRIP,
            theTripIndex, self.Address, theCROCXChannelX.cheNumber, theCROCX.baseAddr>>24, theCROCX.controller.boardNum)
    def FLASHDescription(self, thePageIndex, theCROCXChannelX, theCROCX, theType='CROC'):
        if theType=='CROC': return '%s:%s,%d,%d,%d,%d'%(SC_Util.VMEdevTypes.FLASH,
            thePageIndex, self.Address, theCROCXChannelX.chNumber, theCROCX.baseAddr>>16, theCROCX.controller.boardNum)
        if theType=='CROCE': return '%s:%s,%d,%d,%d,%d'%(SC_Util.VMEdevTypes.FLASH,
            thePageIndex, self.Address, theCROCXChannelX.cheNumber, theCROCX.baseAddr>>24, theCROCX.controller.boardNum)
    def FPGARead(self, theCROCXChannelX, theType='CROC', theIncludeCRC='Unknown', theDescription=''):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGARead) + Frame.NRegsFPGA*[0]
        if theType=='CROC':
            return WriteSendReceive(sentMessage, Frame.MessageDataLengthFPGA, self.Address,
                Frame.DeviceFPGA, theCROCXChannelX, dw='D16', useBLT=True, theDescription=theDescription)
        if theType=='CROCE':
            #in v95 the fpga has 55 registers instead of 54
            #in v96 the fpga has 59 registers
            if theIncludeCRC==False:
                theLength=Frame.MessageDataLengthFPGA
            else:
                theLength=Frame.MessageDataLengthFPGA
            return WriteSendReceiveCROCE(sentMessage, theLength, self.Address,
               Frame.DeviceFPGA, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC, theDescription=theDescription)
    def FPGADumpRead(self, theCROCXChannelX, theType='CROC', theIncludeCRC='Unknown', theDescription=''):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGADumpRead)
        if theType=='CROC':
            return WriteSendReceive(sentMessage, Frame.MessageDataLengthFPGA, self.Address,
                Frame.DeviceFPGA, theCROCXChannelX, dw='D16', useBLT=True)
        if theType=='CROCE':
            #in v95 the fpga has 55 registers instead of 54
            #in v96 the fpga has 59 registers
            if theIncludeCRC==False:
                theLength=Frame.MessageDataLengthFPGA
            else:
                theLength=Frame.MessageDataLengthFPGA
            return WriteSendReceiveCROCE(sentMessage, theLength, self.Address,
                Frame.DeviceFPGA, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC, theDescription=theDescription)
    def FPGAWrite(self, theCROCXChannelX, sentMessageData, theType='CROC', theIncludeCRC='Unknown', theDescription=''):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGAWrite) + sentMessageData
        if theType=='CROC':
            return WriteSendReceive(sentMessage, Frame.MessageDataLengthFPGA, self.Address,
                Frame.DeviceFPGA, theCROCXChannelX, dw='D16', useBLT=True)
        if theType=='CROCE':
            #in v95 the fpga has 55 registers instead of 54
            if theIncludeCRC==False:
                theLength=Frame.MessageDataLengthFPGA
            else:
                theLength=Frame.MessageDataLengthFPGA
            return WriteSendReceiveCROCE(sentMessage, theLength, self.Address,
                Frame.DeviceFPGA, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC, theDescription=theDescription)
    def TRIPRead(self, theCROCXChannelX, theTRIPIndex=None, theType='CROC', theIncludeCRC='Unknown'):
        if theTRIPIndex!=None:
            sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRi[theTRIPIndex])
        else:sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRAll) 
        sentMessageData = self.ParseTRIPAllRegsPhysicalToMessage(Frame.NRegsTRIPPhysical*[0], Frame.InstrTRIPRead)
        sentMessage = sentMessageHeader + sentMessageData
        if theType=='CROC': return WriteSendReceive(sentMessage, Frame.MessageDataLengthTRIPRead, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D16', useBLT=True)
        if theType=='CROCE': return WriteSendReceiveCROCE(sentMessage, Frame.MessageDataLengthTRIPRead, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC)
    def TRIPWrite(self, theCROCXChannelX, theRegs, theTRIPIndex=None, theType='CROC', theIncludeCRC='Unknown'):
        if theTRIPIndex!=None:
            sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRi[theTRIPIndex])
        else:sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRAll) 
        pRegs = self.ParseTRIPRegsLogicalToPhysical(theRegs)
        sentMessageData = self.ParseTRIPAllRegsPhysicalToMessage(pRegs, Frame.InstrTRIPWrite)
        sentMessage = sentMessageHeader + sentMessageData
        if theType=='CROC': WriteSendReceive(sentMessage, Frame.MessageDataLengthTRIPWrite, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D16', useBLT=True)
        if theType=='CROCE': WriteSendReceiveCROCE(sentMessage, Frame.MessageDataLengthTRIPWrite, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC)
    def TRIPProgramRST(self, theCROCXChannelX, theType='CROC', theIncludeCRC='Unknown'):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceTRIP, Frame.FuncTRIPWRAll) + [0,8,8,8,8,8,0,0]
        if theType=='CROC': return WriteSendReceive(sentMessage, 9, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D16', useBLT=False)
        if theType=='CROCE': return WriteSendReceiveCROCE(sentMessage, 9, self.Address,
            Frame.DeviceTRIP, theCROCXChannelX, dw='D16', useBLT=False, includeCRC=theIncludeCRC)
    def BRAMReadDiscrim(self, theCROCXChannelX, theType, theIncludeCRC, theDataType23Hits):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone,
            self.Address, Frame.DeviceBRAM, Frame.FuncBRAMReadDiscrim)
        if theType=='CROC':
            return WriteSendReceive(sentMessage, 0, self.Address,
                Frame.DeviceBRAM, theCROCXChannelX, dw='D16', useBLT=True)    
        if theType=='CROCE':
##            if theDataType23Hits==False:
##                if theIncludeCRC==False:
##                    theLength=Frame.MessageDataLengthBRAMTripRead+1
##                else:
##                    theLength=Frame.MessageDataLengthBRAMTripRead
##            else:
##                if theIncludeCRC==False:
##                    theLength=Frame.MessageDataLengthBRAMTripRead24Hith+1 #(zero+data+zero+dummy)
##                else:
##                    theLength=Frame.MessageDataLengthBRAMTripRead24Hith   #(zero+data+zero)
            return WriteSendReceiveCROCE(sentMessage, 0, self.Address,
                Frame.DeviceBRAM, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC)
    def BRAMReadTrip(self, theCROCXChannelX, index, theType, theIncludeCRC, theDataType23Hits):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone,
            self.Address, Frame.DeviceBRAM, Frame.FuncBRAMReadTripx[index])
        #Comment 10.22.2012 for CROCE vx(no   CRC) compatibility with CROC: LengthCROCE=LengthCROC+1
        #Comment 11.01.2013 for CROCE v3(with CRC) compatibility with CROC: LengthCROCE=LengthCROC
        #Frame.MessageDataLengthBRAMTripRead=578        #FRED=1zero+2bytes*36channels*8hits+1dummy=578
        #Frame.MessageDataLengthBRAMTripRead24Hith=1730 #FRED=1zero+2bytes*36channels*24hits+1zero=1730
        if theType=='CROC':
            return WriteSendReceive(sentMessage, Frame.MessageDataLengthBRAMTripRead, self.Address,
                Frame.DeviceBRAM, theCROCXChannelX, dw='D16', useBLT=True)    
        if theType=='CROCE':
            if theDataType23Hits==False:
                if theIncludeCRC==False:
                    theLength=Frame.MessageDataLengthBRAMTripRead+1
                else:
                    theLength=Frame.MessageDataLengthBRAMTripRead
            else:
                if theIncludeCRC==False:
                    theLength=Frame.MessageDataLengthBRAMTripRead24Hith+1 #(zero+data+zero+dummy)
                else:
                    theLength=Frame.MessageDataLengthBRAMTripRead24Hith   #(zero+data+zero)
            return WriteSendReceiveCROCE(sentMessage, theLength, self.Address,
                Frame.DeviceBRAM, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC)
    def BRAMReadHit(self, theCROCXChannelX, index, theType, theIncludeCRC, theDataType23Hits):
        if index<=7:
            sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone,
                self.Address, Frame.DeviceBRAM, Frame.FuncBRAMReadHitx[index])
        else:
            if index<=22 and theDataType23Hits==True :
                sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone,
                    self.Address, Frame.DeviceBRAM2, Frame.FuncBRAM2ReadHitx[index])
            else:
                raise Exception('BRAMReadHit: Error Hit index=%d while theDataType23Hits==%s.'%(index,theDataType23Hits))
        #Comment 10.22.2012 for CROCE compatibility with CROC: LengthCROCE=LengthCROC+1
        #Comment 11.01.2013 for CROCE v3(with CRC) compatibility with CROC: LengthCROCE=LengthCROC
        #Frame.MessageDataLengthBRAMHitRead=432 #FRED=2bytes*36channels*6trips=432
        if theType=='CROC':
            return WriteSendReceive(sentMessage, Frame.MessageDataLengthBRAMHitRead, self.Address,
                Frame.DeviceBRAM, theCROCXChannelX, dw='D16', useBLT=True)    
        if theType=='CROCE':
            if theDataType23Hits==False:
                if theIncludeCRC==False:
                    theLength=Frame.MessageDataLengthBRAMHitRead+1 #1dummy at end
                else:
                    theLength=Frame.MessageDataLengthBRAMHitRead
                theDeviceBRAM=Frame.DeviceBRAM
            else:
                if theIncludeCRC==False:
                    theLength=Frame.MessageDataLengthBRAMHitRead+3
                else:
                    theLength=Frame.MessageDataLengthBRAMHitRead+2
                if index<=7:
                    theDeviceBRAM=Frame.DeviceBRAM
                else:
                    theDeviceBRAM=Frame.DeviceBRAM2
            return WriteSendReceiveCROCE(sentMessage, theLength, self.Address,
                theDeviceBRAM, theCROCXChannelX, dw='D32', useBLT=True, includeCRC=theIncludeCRC)
    def FLASHMainMemPageRead(self, theCROCXChannelX, pageAddr, theType='CROC',  includeCRC='Unknown', dw='D16', useBLT=False):
        sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFLASH, Frame.FuncFLASHCommand)
        sentMessageDataOpCode = Flash().MakeOpCodeMessageMainMemPageRead(pageAddr)
        sentMessage = sentMessageHeader + sentMessageDataOpCode + Flash.NBytesPerPage*[0]
        if theType=='CROC':
            rcvMessageData,rcvMFH_10bytes=WriteSendReceive(
                sentMessage, Frame.MessageDataLengthFLASHMMPRead, self.Address, Frame.DeviceFLASH, theCROCXChannelX, 0, dw, useBLT)
        if theType=='CROCE':
            rcvMessageData,rcvMFH_10bytes=WriteSendReceiveCROCE(
                sentMessage, Frame.MessageDataLengthFLASHMMPRead, self.Address, Frame.DeviceFLASH, theCROCXChannelX, 0, dw, useBLT, includeCRC)
        return rcvMessageData[len(sentMessageDataOpCode):len(sentMessageDataOpCode)+Flash.NBytesPerPage]
    def FLASHMainMemPageProgThroughBuffer(self, theCROCXChannelX, pageAddr, pageBytes, bufferIndex=1,
        theType='CROC', theIncludeCRC='Unknown', dw='D16', useBLT=False):
        sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFLASH, Frame.FuncFLASHCommand)
        sentMessageDataOpCode = Flash().MakeOpCodeMessageMainMemPageProgThroughBuffer(bufferIndex, pageAddr)
        sentMessage = sentMessageHeader + sentMessageDataOpCode + pageBytes
        if theType=='CROC':
            WriteSendReceive(sentMessage, Frame.MessageDataLengthFLASHMMPPTB, self.Address,
                Frame.DeviceFLASH, theCROCXChannelX, appendData=pageBytes[0], dw=dw, useBLT=useBLT)
        if theType=='CROCE':   
            WriteSendReceiveCROCE(sentMessage, Frame.MessageDataLengthFLASHMMPPTB, self.Address,
                Frame.DeviceFLASH, theCROCXChannelX, appendData=pageBytes[0], dw=dw, useBLT=useBLT, includeCRC=theIncludeCRC)
        sentMessage = sentMessageHeader + [Flash.OpStatRegRead] + 8*[0]
        if theType=='CROC':
            for i in range(100):
                rcvMessageData, rcvMFH_10bytes = WriteSendReceive(sentMessage, 9, self.Address,
                    Frame.DeviceFLASH, theCROCXChannelX, appendData=0, dw=dw, useBLT=useBLT)
                #print 'i=%d, rcvMFH_10bytes=%s, rcvMessageData=%s'%(i, rcvMFH_10bytes, rcvMessageData) 
                if rcvMessageData[8]&0x80==0x80: break
        if theType=='CROCE':
            for i in range(100):
                rcvMessageData, rcvMFH_10bytes = WriteSendReceiveCROCE(sentMessage, 9, self.Address,
                    Frame.DeviceFLASH, theCROCXChannelX, appendData=0, dw=dw, useBLT=useBLT, includeCRC=theIncludeCRC)
                #print 'i=%d, rcvMFH_10bytes=%s, rcvMessageData=%s'%(i, rcvMFH_10bytes, rcvMessageData)
                if rcvMessageData[8]&0x80==0x80: break       
        if i==100: raise Exception('MainMemPageProgThroughBuffer StatusBit NOT Ready')
    def WriteFileToFlash(self, theCROCXChannelX=None, theCROCX=None, theVMECROCXs=None, toThisFEB=False,
            toThisCHX=False, toThisCROCX=False, toAllCROCXs=False, theFrame=None,
            theType=None, dw='D16', useBLT=False):
        dlg = wx.FileDialog(theFrame, message='READ Flash Configuration', defaultDir='', defaultFile='',
            wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
        if dlg.ShowModal()==wx.ID_OK:
            filename=dlg.GetFilename()
            dirname=dlg.GetDirectory()
            theFrame.SetStatusText('WriteFLASH FromFILE %s'%filename, 1)
            f=open(filename,'r')
            pagesAddrFile, pagesBytesFile = Flash().ParseFileLinesToMessages(f)
            f.close()
            if toThisFEB:
                self.WritePagesToFlash(self, theCROCXChannelX, theCROCX, pagesAddrFile, pagesBytesFile,
                    theFrame, theType, dw=dw, useBLT=useBLT)     
            if toThisCHX:
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    self.WritePagesToFlash(theFEB, theCROCXChannelX, theCROCX, pagesAddrFile, pagesBytesFile,
                        theFrame, theType, dw=dw, useBLT=useBLT)
            if toThisCROCX:
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        self.WritePagesToFlash(theFEB, theCROCXChannelX, theCROCX, pagesAddrFile, pagesBytesFile,
                            theFrame, theType, dw=dw, useBLT=useBLT)
            if toAllCROCXs:
                for theCROCX in theVMECROCXs:
                    for theCROCXChannelX in theCROCX.Channels():
                        for febAddress in theCROCXChannelX.FEBs:
                            theFEB=FEB(febAddress)
                            self.WritePagesToFlash(theFEB, theCROCXChannelX, theCROCX, pagesAddrFile, pagesBytesFile,
                                theFrame, theType, dw=dw, useBLT=useBLT)
        dlg.Destroy()
    def WritePagesToFlash(self, theFEB, theCROCXChannelX, theCROCX, pagesAddrFile, pagesBytesFile,
        theFrame, theType, dw='D16', useBLT=False):
        errPages=''
        msg="%s Writing BEGIN %s ..."%(time.ctime(), theFEB.FLASHDescription('', theCROCXChannelX, theCROCX, theType))
        print(msg); theFrame.SetStatusText(msg, 2)
        theIncludeCRC=theCROCX.includeCRC
        for iPage in range(Flash.NPages):
            theFEB.FLASHMainMemPageProgThroughBuffer(theCROCXChannelX, pagesAddrFile[iPage], pagesBytesFile[iPage],
                bufferIndex=1, theType=theType, theIncludeCRC=theIncludeCRC, dw=dw, useBLT=useBLT)
            pageBytesRead=theFEB.FLASHMainMemPageRead(theCROCXChannelX, pagesAddrFile[iPage],
                theType=theType, includeCRC=theIncludeCRC, dw=dw, useBLT=useBLT)
            if pageBytesRead!=pagesBytesFile[iPage]: errPages += '%s '%iPage
            if iPage%100==0:
                theFrame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                theFrame.Refresh(); theFrame.Update()
        theFrame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
        if errPages:
            print("Write ERROR %s, page %s"%(theFEB.FLASHDescription('', theCROCXChannelX, theCROCX, theType), errPages))
            theFrame.SetStatusText("Write ERROR on %s"%theFEB.FLASHDescription('', theCROCXChannelX, theCROCX, theType), 2)
        else:
            msg="%s Write    DONE %s"%(time.ctime(), theFEB.FLASHDescription('', theCROCXChannelX, theCROCX, theType))
            print(msg); theFrame.SetStatusText(msg, 2)
    def AlignGateDelays(self, theCROCX, theCROCXChannelX, theNumberOfMeas, theLoadTimerValue, theGateStartValue, theType='CROC'):
        if theCROCXChannelX.FEBs==[]: return
        if theType=='CROE':
            theIncludeCRC=theCROCX.includeCRC
        else:
            theIncludeCRC='Unknown'
        print('Reporting FEBs TPDelay measurements on %s %s CRATE:%s'%(
            theCROCXChannelX.Description(),theCROCX.Description(),theCROCX.controller.boardNum))
        #Set LoadTimerValue and GateStartValue equal for ALL boards in this Channel
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=FEB(febAddress)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theIncludeCRC)
            #message word 0-3: WR Timer, 32 bits
            rcvMessageData[0] = (theLoadTimerValue)     & 0xFF
            rcvMessageData[1] = (theLoadTimerValue>>8)  & 0xFF
            rcvMessageData[2] = (theLoadTimerValue>>16) & 0xFF
            rcvMessageData[3] = (theLoadTimerValue>>24) & 0xFF
            #message word 4-5: WR Gate Start, 16 bits
            rcvMessageData[4] = (theGateStartValue)     & 0xFF
            rcvMessageData[5] = (theGateStartValue>>8)  & 0xFF
            theFEB.FPGAWrite(theCROCXChannelX, rcvMessageData, theType, theIncludeCRC)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theIncludeCRC)
        #Enable TP
        if theType=='CROC':
            theCROCX.WriteRSTTP(1<<theCROCXChannelX.Number())
        if theType=='CROCE':
            theCROCX.WriteRSTTP(0x0001)
            theCROCXChannelX.WriteConfiguration(theCROCXChannelX.ReadConfiguration()|0x0020)
        #Acquire TPDelay information
        TPDelay=[]
        for iMeas in range(theNumberOfMeas):
            theCROCX.SendFastCommand(SC_Util.FastCmds['LoadTimer'])
            theCROCX.SendTPOnly()
            #Get TP delay for ALL FEBs in this Channel
            FEBsTPDelay=[]
            for febAddress in theCROCXChannelX.FEBs:
                theFEB=FEB(febAddress)
                rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theIncludeCRC)
                #message word 9, bit 6 - 7: R  TP Count2b, 2 bits
                tpCount2b=(rcvMessageData[9]>>6)&0x03
                #message word 12-15: R  TP Count, 32 bits
                tpCount32b=rcvMessageData[12]+(rcvMessageData[13]<<8)+(rcvMessageData[14]<<16)+(rcvMessageData[15]<<24)
                if tpCount2b==0: tpCount=tpCount32b+1
                else: tpCount=tpCount32b+0.25*tpCount2b
                FEBsTPDelay.append([febAddress, tpCount])
                #first position == febAddress, second position == tpCount
            thisMeasMinValue=FEBsTPDelay[0][1]
            for feb in FEBsTPDelay:
                if feb[1]<thisMeasMinValue: thisMeasMinValue=feb[1]
            for feb in FEBsTPDelay: feb[1]-=thisMeasMinValue
            TPDelay.append(FEBsTPDelay)
        #Disable RST and TP
        if theType=='CROC':
            theCROCX.WriteRSTTP(0)
        if theType=='CROCE':
            theCROCX.WriteRSTTP(0)
            theCROCXChannelX.WriteConfiguration(theCROCXChannelX.ReadConfiguration()&0xFFCF)
        #Calculate average value of ALL measurements
        TPDelayAvg=[]
        for i in range(len(theCROCXChannelX.FEBs)): TPDelayAvg.append([0,0])
        for iFEB in range(len(theCROCXChannelX.FEBs)):
            TPDelayAvg[iFEB][0]=TPDelay[0][iFEB][0]
            for iMeas in range(theNumberOfMeas):
                TPDelayAvg[iFEB][1]+=TPDelay[iMeas][iFEB][1]
            TPDelayAvg[iFEB][1]/=theNumberOfMeas         
        for feb in TPDelayAvg:
            print('FEB:%s, AvgDelay=%s'%(feb[0],feb[1]))
        #Update new values to FPGA's Timer and GateStart
        for iFEB in TPDelayAvg:
            theFEB=FEB(iFEB[0])
            theDelay = int(round(float(iFEB[1])/2))
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theIncludeCRC)
            #message word 0-3: WR Timer, 32 bits
            rcvMessageData[0] -= (theDelay)     & 0xFF
            rcvMessageData[1] -= (theDelay>>8)  & 0xFF
            rcvMessageData[2] -= (theDelay>>16) & 0xFF
            rcvMessageData[3] -= (theDelay>>24) & 0xFF
            #message word 4-5: WR Gate Start, 16 bits
            rcvMessageData[4] -= (theDelay)     & 0xFF
            rcvMessageData[5] -= (theDelay>>8)  & 0xFF
            theFEB.FPGAWrite(theCROCXChannelX, rcvMessageData, theType, theIncludeCRC)      
    def GetAllHVParams(self, vmeCROCXs, theType='CROC', devVal=0):
        hvVals=[]
        rcvMessage=[]
        rcvMFH_10bytes=[]
        for theCROCX in vmeCROCXs:
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    rcvMessage,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theCROCX.includeCRC, 
                        theDescription=theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType))
                    #message word 23-24: WR HV Target, 16 bits
                    hvTarget=rcvMessage[23]+(rcvMessage[24]<<8)
                    #message word 25-26: R  HV Actual, 16 bits
                    hvActual=rcvMessage[25]+(rcvMessage[26]<<8)
                    #message word 22, bit 6: WR HV Auto(0)Man(1), 1 bit
                    hvAuto0Manual1=(rcvMessage[22]>>6)&0x01
                    if hvAuto0Manual1==0: hvMode='Auto'
                    if hvAuto0Manual1==1: hvMode='Manual'
                    #message word 22, bit 7: WR HV Enable(1), 1 bit
                    hvEnable1=(rcvMessage[22]>>7)&0x01
                    if hvEnable1==0: hvEnabled='False'
                    if hvEnable1==1: hvEnabled='True'
                    #message word 31: WR HV NumAvg (bits 4-7)
                    hvNumAvg=(rcvMessage[31]>>4)&0x0F
                    #message word 33-34: WR HV PeriodMan, 16 bits
                    hvPeriodMan=rcvMessage[33]+(rcvMessage[34]<<8)
                    #message word 35-36: R  HV PeriodAuto, 16 bits
                    hvPeriodAuto=rcvMessage[35]+(rcvMessage[36]<<8)                    
                    #message word 37: WR HV PulseWidth, 8 bits
                    hvPulseWidth=rcvMessage[37]
                    if abs(hvActual-hvTarget)>=devVal:
                        if theType=='CROC':
                            descr={'FEB':febAddress, 'Channel':theCROCXChannelX.chNumber,
                                   'CROC':theCROCX.baseAddr>>16, 'CRATE':theCROCX.controller.boardNum}
                        if theType=='CROCE':
                            descr={'FEB':febAddress, 'Channel':theCROCXChannelX.cheNumber,
                                   'CROCE':theCROCX.baseAddr>>24, 'CRATE':theCROCX.controller.boardNum}
                        hvVals.append({'FPGA':descr, 'Actual':hvActual, 'Target':hvTarget, 'A-T':hvActual-hvTarget,
                            'Mode':hvMode, 'Enabled':hvEnabled, 'NumAvg':hvNumAvg, 'PeriodMan':hvPeriodMan,
                            'PeriodAuto':hvPeriodAuto, 'PulseWidth':hvPulseWidth})
        return hvVals
    def SetAllHVTarget(self, vmeCROCXs, theType='CROC', hvVal=0):
        rcvMessage=[]
        rcvMFH_10bytes=[]
        for theCROCX in vmeCROCXs:
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    rcvMessage,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theCROCX.includeCRC)
                    #message word 23-24: WR HV Target, 16 bits
                    rcvMessage[23] = (hvVal) & 0xFF
                    rcvMessage[24] = (hvVal>>8) & 0xFF
                    theFEB.FPGAWrite(theCROCXChannelX, rcvMessage, theType, theCROCX.includeCRC)
    def ParseMessageToFPGAtxtRegs(self, msg, txtRegs):
        #message word 0-3: WR Timer, 32 bits
        txtRegs[14].SetValue(hex(msg[0]+(msg[1]<<8)+(msg[2]<<16)+(msg[3]<<24))[2:].upper().rjust(8,'0'))
        #message word 4-5: WR Gate Start, 16 bits
        txtRegs[1].SetValue(str(msg[4]+(msg[5]<<8)))
        #message word 6-7: WR Gate Length, 16 bits
        txtRegs[2].SetValue(str(msg[6]+(msg[7]<<8)))
        #message word 8 and 9-bit 0: R  DCM2 PhaseTotal, 9 bits
        txtRegs[35].SetValue(str(msg[8]+((msg[9]&0x01)<<8)))
        #message word 9, bit 1: R  DCM2 PhaseDone, 1 bit
        txtRegs[34].SetValue(str((msg[9]>>1)&0x01))
        #message word 9, bit 2: R  DCM1 NoCLK(0), 1 bit
        txtRegs[32].SetValue(str((msg[9]>>2)&0x01))
        #message word 9, bit 3: R  DCM2 NoCLK(0), 1 bit
        txtRegs[33].SetValue(str((msg[9]>>3)&0x01))
        #message word 9, bit 4: R  DCM1 Lock(0), 1 bit
        txtRegs[30].SetValue(str((msg[9]>>4)&0x01))
        #message word 9, bit 5: R  DCM2 Lock(0), 1 bit
        txtRegs[31].SetValue(str((msg[9]>>5)&0x01))
        #message word 9, bits 6-7: R  TP Count2b, 2 bits
        txtRegs[36].SetValue(str((msg[9]>>6)&0x03))
        #message word 10: WR Phase Ticks, 8 bits
        txtRegs[29].SetValue(str(msg[10]))
        #message word 11, bit 0: R  ExtTriggFound, 1 bit
        txtRegs[40].SetValue(str((msg[11])&0x01))
        #message word 11, bit 1: WR ExtTriggRearm, 1 bit
        txtRegs[41].SetValue(str((msg[11]>>1)&0x01))
        #message word 11, bit 2: R  SCmdErr(1), 1 bit
        txtRegs[47].SetValue(str((msg[11]>>2)&0x01))
        #message word 11, bit 3: R  FCmdErr(1), 1 bit
        txtRegs[48].SetValue(str((msg[11]>>3)&0x01))
        #message word 11, bit 4: WR Phase -(0)+(1), 1 bit
        txtRegs[28].SetValue(str((msg[11]>>4)&0x01))
        #message word 11, bit 5: WR Phase R(0)S(1), 1 bit
        txtRegs[27].SetValue(str((msg[11]>>5)&0x01))
        #message word 11, bit 6: R  RXLockErr(1), 1 bit
        txtRegs[49].SetValue(str((msg[11]>>6)&0x01))
        #message word 11, bit 7: R  TXSyncErr(1), 1 bit
        txtRegs[50].SetValue(str((msg[11]>>7)&0x01))
        #message word 12-15: R  TP Count, 32 bits
        txtRegs[37].SetValue(hex(msg[12]+(msg[13]<<8)+(msg[14]<<16)+(msg[15]<<24))[2:].upper().rjust(8,'0'))
        #message word 16: WR Trip0 En+Inj, 8 bits
        txtRegs[15].SetValue(str(msg[16]))
        #message word 17: WR Trip1 En+Inj, 8 bits
        txtRegs[16].SetValue(str(msg[17]))
        #message word 18: WR Trip2 En+Inj, 8 bits
        txtRegs[17].SetValue(str(msg[18]))
        #message word 19: WR Trip3 En+Inj, 8 bits
        txtRegs[18].SetValue(str(msg[19]))
        #message word 20: WR Trip4 En+Inj, 8 bits
        txtRegs[19].SetValue(str(msg[20]))
        #message word 21: WR Trip5 En+Inj, 8 bits
        txtRegs[20].SetValue(str(msg[21]))
        #message word 22, bits 5-0: WR Trip PowOFF, 1 bit for each trip
        txtRegs[0].SetValue(str(msg[22]&0x3F))
        #message word 22, bit 6: WR HV Auto(0)Man(1), 1 bit
        txtRegs[6].SetValue(str((msg[22]>>6)&0x01))
        #message word 22, bit 7: WR HV Enable(1), 1 bit
        txtRegs[3].SetValue(str((msg[22]>>7)&0x01))
        #message word 23-24: WR HV Target, 16 bits
        txtRegs[4].SetValue(str(msg[23]+(msg[24]<<8)))
        #message word 25-26: R  HV Actual, 16 bits
        txtRegs[5].SetValue(str(msg[25]+(msg[26]<<8)))        
        #message word 27-bits 3-0: WR After Pulse Ticks, 4 bits 
        txtRegs[52].SetValue(str((msg[27])&0x0F))
        #message word 27-bits 6-4: WR Spare, 3 bits
        txtRegs[55].SetValue(str((msg[27]>>4)&0x07))
        #message word 27-bit 7: R  Digitization Done, 1 bit
        txtRegs[54].SetValue(str((msg[27]>>7)&0x01))
        #message word 28 and 29-bits 3-0: WR InjDAC Value, 12 bits
        txtRegs[23].SetValue(str(msg[28]+((msg[29]&0x0F)<<8)))
        #message word 29, bits 5-4: WR InjDAC Mode(0), 2 bits
        txtRegs[24].SetValue(str((msg[29]>>4)&0x03))
        #message word 29, bit 6: R  InjDAC Done(1), 1 bit
        txtRegs[26].SetValue(str((msg[29]>>6)&0x01))
        #message word 29, bit 7: WR InjDAC R(0)S(1), 1 bit
        txtRegs[25].SetValue(str((msg[29]>>7)&0x01))
        #message word 30-bits 3-0: WR TripX InjRange, 4 bits
        txtRegs[21].SetValue(str((msg[30])&0x0F))
        #message word 30-bits 7-4: WR TripX InjPhase, 4 bits
        txtRegs[22].SetValue(str((msg[30]>>4)&0x0F))
        #message word 31-bits 3-0: R  FE Board ID, 4 bits
        txtRegs[13].SetValue(str((msg[31])&0x0F))
        #message word 31-bits 6-4: WR HV NumAvg, 3 bits
        txtRegs[7].SetValue(str((msg[31]>>4)&0x07))
        #message word 31-bit 7: WR Enable Hit Preview, 1 bit
        txtRegs[51].SetValue(str((msg[31]>>7)&0x01))
        #message word 32: R  Firmware Version, 8 bits
        txtRegs[12].SetValue(str(msg[32]))
        #message word 33-34: WR HV PeriodMan, 16 bits
        txtRegs[8].SetValue(str(msg[33]+(msg[34]<<8)))
        #message word 35-36: R  HV PeriodAuto, 16 bits
        txtRegs[9].SetValue(str(msg[35]+(msg[36]<<8)))
        #message word 37: WR HV PulseWidth, 8 bits
        txtRegs[10].SetValue(str(msg[37]))
        #message word 38-39: R  Temperature, 16 bits
        txtRegs[11].SetValue(str(msg[38]+(msg[39]<<8)))
        #message word 40: WR TripX Threshold, 8 bits
        txtRegs[38].SetValue(str(msg[40]))
        #message word 41-bits 5-0: R  TripX Comparators, 6 bits
        txtRegs[39].SetValue(str(msg[41]&0x3F))
        #message word 41-bits 7-6: WR TripX ACQ Mode, 2 bits
        txtRegs[53].SetValue(str((msg[41]>>6)&0x03))        
        #message word 42-43: WR DiscMaskT0 (0x), 16 bits
        txtRegs[42].SetValue(hex(msg[42]+(msg[43]<<8))[2:].upper().rjust(4,'0'))
        #message word 44-45: WR DiscMaskT1 (0x), 16 bits
        txtRegs[43].SetValue(hex(msg[44]+(msg[45]<<8))[2:].upper().rjust(4,'0'))
        #message word 46-47: WR DiscMaskT2 (0x), 16 bits
        txtRegs[44].SetValue(hex(msg[46]+(msg[47]<<8))[2:].upper().rjust(4,'0'))
        #message word 48-49: WR DiscMaskT3 (0x), 16 bits
        txtRegs[45].SetValue(hex(msg[48]+(msg[49]<<8))[2:].upper().rjust(4,'0'))
        #message word 50-53: R  GateTimeStamp, 32 bits
        txtRegs[46].SetValue(hex(msg[50]+(msg[51]<<8)+(msg[52]<<16)+(msg[53]<<24))[2:].upper().rjust(8,'0'))
        #
        #print 'ParseMessageToFPGAtxtRegs, len(msg)=%s'%len(msg)
        if msg[32]==95 and len(msg)>=55: #message word 32: R  Firmware Version, 8 bits
            txtRegs[56].SetValue('0000') #not defined in v95
            txtRegs[57].SetValue('0000') #not defined in v95
            txtRegs[58].SetValue(hex(msg[54])[2:].upper().rjust(2,'0'))
        elif msg[32]==96 and len(msg)>=59: #message word 32: R  Firmware Version, 8 bits
            #message word 54-55: R  Trip20HitCnt (0x), 16 bits
            #message word 56-57: R  Trip31HitCnt (0x), 16 bits
            #message word 58: WR Spare 8b v95
            txtRegs[56].SetValue(hex(msg[54]+(msg[55]<<8))[2:].upper().rjust(4,'0'))
            txtRegs[57].SetValue(hex(msg[56]+(msg[57]<<8))[2:].upper().rjust(4,'0'))
            txtRegs[58].SetValue(hex(msg[58])[2:].upper().rjust(2,'0'))
        else:
            txtRegs[56].SetValue('0000')
            txtRegs[57].SetValue('0000')
            txtRegs[58].SetValue('00')
    def ParseFPGARegsToMessage(self, txtRegs):
        msg=Frame.NRegsFPGA*[0]
        #message word 0-3: WR Timer, 32 bits
        msg[0] = (int(txtRegs[14].GetValue(),16)) & 0xFF
        msg[1] = (int(txtRegs[14].GetValue(),16)>>8) & 0xFF
        msg[2] = (int(txtRegs[14].GetValue(),16)>>16) & 0xFF
        msg[3] = (int(txtRegs[14].GetValue(),16)>>24) & 0xFF
        #message word 4-5: WR Gate Start, 16 bits
        msg[4] = (int(txtRegs[1].GetValue())) & 0xFF
        msg[5] = (int(txtRegs[1].GetValue())>>8) & 0xFF
        #message word 6-7: WR Gate Length, 16 bits
        msg[6] = (int(txtRegs[2].GetValue())) & 0xFF
        msg[7] = (int(txtRegs[2].GetValue())>>8) & 0xFF
        #message word 8-9: Read Only
        #message word 10: WR Phase Ticks, 8 bits
        msg[10] = (int(txtRegs[30].GetValue())) & 0xFF
        #message word 11, bit 1: WR ExtTriggRearm, 1 bit
        #message word 11, bit 4: WR Phase -(0)+(1), 1 bit
        #message word 11, bit 5: WR Phase R(0)S(1), 1 bit
        msg[11] = ((int(txtRegs[41].GetValue()) & 0x01) << 1) + \
                  ((int(txtRegs[28].GetValue()) & 0x01) << 4) + \
                  ((int(txtRegs[27].GetValue()) & 0x01) << 5)
        #message word 12-15: Read Only
        #message word 16: WR Trip0 En+Inj, 8 bits
        msg[16] = (int(txtRegs[15].GetValue())) & 0xFF
        #message word 17: WR Trip1 En+Inj, 8 bits
        msg[17] = (int(txtRegs[16].GetValue())) & 0xFF
        #message word 18: WR Trip2 En+Inj, 8 bits
        msg[18] = (int(txtRegs[17].GetValue())) & 0xFF
        #message word 19: WR Trip3 En+Inj, 8 bits
        msg[19] = (int(txtRegs[18].GetValue())) & 0xFF
        #message word 20: WR Trip4 En+Inj, 8 bits
        msg[20] = (int(txtRegs[19].GetValue())) & 0xFF
        #message word 21: WR Trip5 En+Inj, 8 bits
        msg[21] = (int(txtRegs[20].GetValue())) & 0xFF
        #message word 22, bit 5-0: WR Trip PowOFF, 1 bit for each trip
        #message word 22, bit 6: WR HV Auto(0)Man(1), 1 bit
        #message word 22, bit 7: WR HV Enable(1), 1 bit
        msg[22] = ((int(txtRegs[0].GetValue()) & 0x3F)) + \
                  ((int(txtRegs[6].GetValue()) & 0x01) << 6) + \
                  ((int(txtRegs[3].GetValue()) & 0x01) << 7)
        #message word 23-24: WR HV Target, 16 bits
        msg[23] = (int(txtRegs[4].GetValue())) & 0xFF
        msg[24] = (int(txtRegs[4].GetValue())>>8) & 0xFF
        #message word 25-26: Read Only
        #message word 27-bits 3-0: WR After Pulse Ticks, 4 bits 
        #message word 27-bits 6-4: WR Spare, 3 bits
        #message word 27-bit 7: R  Digitization Done, 1 bit
        msg[27] = ((int(txtRegs[52].GetValue()) & 0x0F) << 0) + \
                  ((int(txtRegs[55].GetValue()) & 0x07) << 4)
        #message word 28 and 29-bits 3-0: WR InjDAC Value, 12 bits
        msg[28] = (int(txtRegs[23].GetValue())) & 0xFF
        #message word 28 and 29-bits 3-0: WR InjDAC Value, 12 bits
        #message word 29, bits 5-4: WR InjDAC Mode(0), 2 bits
        #message word 29, bit 6: R  InjDAC Done(1), 1 bit
        #message word 29, bit 7: WR InjDAC R(0)S(1), 1 bit
        msg[29] = ((int(txtRegs[23].GetValue()) & 0xF00) >> 8) + \
                  ((int(txtRegs[24].GetValue()) & 0x03) << 4) + \
                  ((int(txtRegs[25].GetValue()) & 0x01) << 7)
        #message word 30-bits 3-0: WR TripX InjRange, 4 bits
        #message word 30-bits 7-4: WR TripX InjPhase, 4 bits
        #a special case for InjectPhase register
        injPhase=int(txtRegs[22].GetValue())
        if injPhase==1 or injPhase==2 or injPhase==4 or injPhase==8:
            msg[30] = ((int(txtRegs[21].GetValue()) & 0x0F)) + \
                      ((int(txtRegs[22].GetValue()) & 0x0F) << 4)
        else: raise Exception(txtRegs[22].GetName() + ' must be 1, 2, 4 or 8')
        #message word 31-bits 3-0: R  FE Board ID, 4 bits
        #message word 31-bits 6-4: WR HV NumAvg, 3 bits
        #message word 31-bit 7: WR Enable Hit Preview, 1 bit
        msg[31] = ((int(txtRegs[7].GetValue()) & 0x07) << 4) + \
                  ((int(txtRegs[51].GetValue()) & 0x01) << 7)        
        #message word 32: Read Only
        #message word 33-34: WR HV PeriodMan, 16 bits
        msg[33] = (int(txtRegs[8].GetValue())) & 0xFF
        msg[34] = (int(txtRegs[8].GetValue())>>8) & 0xFF
        #message word 35-36: Read Only
        #message word 37: WR HV PulseWidth, 8 bits
        pw=(int(txtRegs[10].GetValue())) & 0xFF
        if pw<=30: msg[37]=pw
        else: msg[37]=30        
        #message word 38-39: Read Only
        #message word 40: WR TripX Threshold, 8 bits
        msg[40] = (int(txtRegs[38].GetValue())) & 0xFF
        #message word 41-bits 5-0: R  TripX Comparators, 6 bits
        #message word 41-bits 7-6: WR TripX ACQ Mode, 2 bits
        msg[41] = ((int(txtRegs[53].GetValue()) & 0x03) << 6)
        #message word 42-43: WR DiscMaskT0 (0x), 16 bits
        msg[42] = (int(txtRegs[42].GetValue(),16)) & 0xFF
        msg[43] = (int(txtRegs[42].GetValue(),16)>>8) & 0xFF
        #message word 44-45: WR DiscMaskT1 (0x), 16 bits
        msg[44] = (int(txtRegs[43].GetValue(),16)) & 0xFF
        msg[45] = (int(txtRegs[43].GetValue(),16)>>8) & 0xFF
        #message word 46-47: WR DiscMaskT2 (0x), 16 bits
        msg[46] = (int(txtRegs[44].GetValue(),16)) & 0xFF
        msg[47] = (int(txtRegs[44].GetValue(),16)>>8) & 0xFF
        #message word 48-49: WR DiscMaskT3 (0x), 16 bits
        msg[48] = (int(txtRegs[45].GetValue(),16)) & 0xFF
        msg[49] = (int(txtRegs[45].GetValue(),16)>>8) & 0xFF
        #message word 50-53: Read Only
        #print 'ParseFPGARegsToMessage, NRegsFPGA=%s'%len(msg)
        if (int(txtRegs[12].GetValue())==91 or int(txtRegs[12].GetValue())==95) and len(msg)>=55 : #message word 32: R  Firmware Version, 8 bits
            #message word 54: WR Spare 8b FOR v95
            msg[54] = (int(txtRegs[58].GetValue(),16)) & 0xFF
        elif int(txtRegs[12].GetValue())==96 and len(msg)>=59 : #message word 32: R  Firmware Version, 8 bits
            #message word 54-57: Read Only
            #message word 58: WR Spare 8b FOR v96
            msg[58] = (int(txtRegs[58].GetValue(),16)) & 0xFF
        return msg
    def ParseTRIPRegsLogicalToPhysical(self, txtRegs):
        pRegs=Frame.NRegsTRIPPhysical*[0]
        for i in range(10): pRegs[i]=(int(txtRegs[i].GetValue()) & 0xFF)
        pRegs[10]=((int(txtRegs[10].GetValue()) & 0x0F)<<6) + (int(txtRegs[11].GetValue()) & 0x3F)
        pRegs[11]=((int(txtRegs[12].GetValue()) & 0x03)<<2) + (int(txtRegs[13].GetValue()) & 0x03)
        pRegs[12]=0
        pRegs[13]=((int(txtRegs[14].GetValue()) & 0x01)) + \
                   ((int(txtRegs[15].GetValue(),16) & 0xFF)<<1) + ((int(txtRegs[16].GetValue(),16) & 0xFF)<<9) + \
                   ((int(txtRegs[17].GetValue(),16) & 0xFF)<<17) + ((int(txtRegs[18].GetValue(),16) & 0xFF)<<25) + \
                   ((int(txtRegs[19].GetValue()) & 0x01)<<33)
        return pRegs
    def ParseTRIPRegsPhysicalToLogical(self, pRegs, txtRegs, append=False):
        if append==False:
            for i in range(10): txtRegs[i].SetValue(str(pRegs[i]).ljust(4))
            txtRegs[10].SetValue(str(pRegs[10] >> 6).ljust(4))       # gain
            txtRegs[11].SetValue(str(pRegs[10] & 0x3F).ljust(4))     # pipedel
            txtRegs[12].SetValue(str(pRegs[11] >> 2).ljust(4))       # irsel
            txtRegs[13].SetValue(str(pRegs[11] & 0x03).ljust(4))     # iwsel
            for i in range(14,20,1):
                txtRegs[i].SetValue('0'.ljust(4))
        else:
            for i in range(10): txtRegs[i].SetValue(txtRegs[i].GetValue() + str(pRegs[i]).ljust(4))
            txtRegs[10].SetValue(txtRegs[10].GetValue() + str(pRegs[10] >> 6).ljust(4))       # gain
            txtRegs[11].SetValue(txtRegs[11].GetValue() + str(pRegs[10] & 0x3F).ljust(4))     # pipedel
            txtRegs[12].SetValue(txtRegs[12].GetValue() + str(pRegs[11] >> 2).ljust(4))       # irsel
            txtRegs[13].SetValue(txtRegs[13].GetValue() + str(pRegs[11] & 0x03).ljust(4))     # iwsel
            for i in range(14,20,1):
                txtRegs[i].SetValue(txtRegs[i].GetValue() + '0'.ljust(4))        
    def TripPrgEnc(self, prgRST, prgDIN, prgCLK, prgCTRL):
        return ((prgRST<<3)+(prgDIN<<2)+(prgCLK<<1)+prgCTRL) & 0x0F         
    def ParseTRIPOneRegPhysicalToMessage(self, regAddr=0, instrID=0, regValue=0, regNBits=0, chipID=10):
        msg=[]
        msg.append(self.TripPrgEnc(0,0,0,0))
        msg.append(self.TripPrgEnc(0,0,0,1))        # assert CTRL line
        for i in range(4,-1,-1): 
            data=(chipID>>i)&0x01                   # parse chipID, 5bits, MSB first
            msg.append(self.TripPrgEnc(0,data,1,1)) # CLK up
            msg.append(self.TripPrgEnc(0,data,0,1)) # CLK down
        for i in range(4,-1,-1):                     
            data=(regAddr>>i)&0x01                  # parse regAddr, 5bits, MSB first
            msg.append(self.TripPrgEnc(0,data,1,1)) # CLK up
            msg.append(self.TripPrgEnc(0,data,0,1)) # CLK down
        for i in range(2,-1,-1):                     
            data=(instrID>>i)&0x01                  # parse instrID, 3bits, MSB first
            msg.append(self.TripPrgEnc(0,data,1,1)) # CLK up
            msg.append(self.TripPrgEnc(0,data,0,1)) # CLK down
        msg.append((self.TripPrgEnc(0,0,1,1)))      # CLK up    dummy bit
        msg.append((self.TripPrgEnc(0,0,0,1)))      # CLK down  dummy bit
        for i in range(0,regNBits,1):                     
            data=(regValue>>i)&0x01                 # parse regValue, regNBits, LSB first
            msg.append(self.TripPrgEnc(0,data,1,1)) # CLK up
            msg.append(self.TripPrgEnc(0,data,0,1)) # CLK down
        # !!!! CAUTION !!!!
        # For unknown reasons the following BIT, when CTRL goes low, is now different
        # from my ORIGINAL implementation (the one back to SBC controller)
        # It used to be (0,0,0,1)+(0,0,0,0) for both TripInstruction Read and Write.
        # NOW I have to make them different or else the Trip will provide wrong data output...    
        if instrID==Frame.InstrTRIPRead:
            msg.append(self.TripPrgEnc(0,0,1,1))        # CTRL keep high
            msg.append(self.TripPrgEnc(0,0,0,0))        # CTRL go low
        if instrID==Frame.InstrTRIPWrite:
            msg.append(self.TripPrgEnc(0,0,0,1))        # CTRL keep high
            msg.append(self.TripPrgEnc(0,0,0,0))        # CTRL go low
        msg.append(self.TripPrgEnc(0,0,1,0))        # CLK up    one more 
        msg.append(self.TripPrgEnc(0,0,0,0))        # CLK down  one more
        msg.append(self.TripPrgEnc(0,0,1,0))        # CLK up    one more 
        msg.append(self.TripPrgEnc(0,0,0,0))        # CLK down  one more
        #print 'regAddr=%s, instrID=%s, regValue=%s, regNBits=%s, chipID=%s'%(regAddr, instrID, regValue, regNBits, chipID)
        #print msg, len(msg)
        #print 'begining=%s'%msg[0:2]
        #print 'chipID=%s'%msg[2:12]
        #print 'regAddr=%s'%msg[12:22]
        #print 'instrID=%s'%msg[22:28]
        #print 'dummy=%s'%msg[28:30]
        #print 'regValue=%s'%msg[30:-6]
        #print 'ending=%s'%msg[-6:]
        return msg
    def ParseTRIPAllRegsPhysicalToMessage(self, pRegs, instrID):
        msg=[]
        for i in range(10):
            msg.extend(self.ParseTRIPOneRegPhysicalToMessage(i+1, instrID, pRegs[i], 8))
        msg.extend(self.ParseTRIPOneRegPhysicalToMessage(11, instrID, pRegs[10], 10))
        msg.extend(self.ParseTRIPOneRegPhysicalToMessage(12, instrID, pRegs[11], 4))
        if instrID==Frame.InstrTRIPWrite:
            msg.extend(self.ParseTRIPOneRegPhysicalToMessage(14, instrID, pRegs[13], 34))
        #print 'ParseTRIPAllRegsPhysicalToMessage'
        #print msg, len(msg)
        return msg
    def ParseMessageToTRIPtxtRegs(self, msg, theTRIPIndex, txtRegs):
        pRegs = self.ParseMessageToTRIPRegsPhysical(msg, theTRIPIndex)
        self.ParseTRIPRegsPhysicalToLogical(pRegs, txtRegs, append=False)
    def ParseMessageToTRIPtxtRegs6(self, msg, txtRegs):    
        for txt in txtRegs:  txt.SetValue('')
        for iTrip in range(Frame.NTRIPs):
            pRegs = self.ParseMessageToTRIPRegsPhysical(msg, iTrip)
            self.ParseTRIPRegsPhysicalToLogical(pRegs, txtRegs, append=True)
    def ParseMessageToTRIPRegsPhysical(self, msg, theTRIPIndex):
        pRegs=Frame.NRegsTRIPPhysical*[0]
        msgRegBorders=[0, 52*1, 52*2, 52*3, 52*4, 52*5, 52*6, 52*7, 52*8, 52*9, 52*10, 520+56, 520+56+44]
        pRegsNBits=[8,8,8,8,8,8,8,8,8,8,10,4]        
        for iReg in range(12):
            regMsg = msg[msgRegBorders[iReg]:msgRegBorders[iReg+1]]
            #print regMsg, len(regMsg)
            err='Error parsing TRIP received data: register ' + str(iReg)
            if regMsg[0]!=0  or regMsg[1]!=1:
                raise Exception(err + ' header')
            if regMsg[-5]!=0 or regMsg[-4]!=2 or regMsg[-3]!=0 or regMsg[-2]!=2 or regMsg[-1]!=0:
                raise Exception(err + ' trailer')
            # check: (clk,ctrl) is 3,1,3,1,3,1... for 5ChipID+5RegAddr+3Instr+1dummy=14x2=28
            for index in range(2,2+28,2): 
                if regMsg[index]!=3 or regMsg[index+1]!=1:
                    raise Exception(err + ' clk up/down')
            # check: ONLY ONE position for dummy bit
            if regMsg[30]!=3: 
                raise Exception(err + ' clk phase after dummy bit')
            # check: (clk,ctrl) is now 1,3,1,3.... and get register value one bit at a time
            for index in range(31, 31+2*pRegsNBits[iReg], 2):
                if regMsg[index]&0x3!=1 or regMsg[index+1]&0x3!=3:
                    raise Exception(err + ' clk up/down indx=' + str(index))
                if regMsg[index]&0xFC != regMsg[index+1]&0xFC:
                    raise Exception(err + ' data up/down indx=' + str(index))
                pRegs[iReg] += (((regMsg[index])>>(2+theTRIPIndex)) & 0x01) << (pRegsNBits[iReg]-1-(index-31)/2)
            #print 'pReg[%d]=%d'%(iReg, pRegs[iReg])
        return pRegs
    def DecodeBRAMDiscrims(self, rcvDataBytes, source, theDataType23Hits):
        #print 'inside SC_MainObjects: DecodeBRAMDiscrims: source=%s, rcvDataBytes=%s'%(source,rcvDataBytes)
        if rcvDataBytes[0]!=0: raise Exception('DecodeBRAMDiscrims: Error rcvDataBytes[0]=%d instead of 0.'%rcvDataBytes[0])
        discrims=[[],[],[],[]]
        indx=3
        #only four TRIPS have discriminator data
        if theDataType23Hits==False:
            nHitsPerTRIP=[(rcvDataBytes[1]>>0)&0xF, (rcvDataBytes[1]>>4)&0xF, (rcvDataBytes[2]>>0)&0xF, (rcvDataBytes[2]>>4)&0xF]
        else:
            ###nHitsPerTRIP=[rcvDataBytes[1], rcvDataBytes[1], rcvDataBytes[2], rcvDataBytes[2]]
            #updated code to work with FEB v96 push in pair/independent
            if rcvDataBytes[2]&0x80==0:
                #push in pairs
                nHitsPerTRIP=[rcvDataBytes[1]&0x1F, rcvDataBytes[1]&0x1F, rcvDataBytes[2]&0x1F, rcvDataBytes[2]&0x1F]
            elif rcvDataBytes[2]&0x80==0x80 and rcvDataBytes[4]&0x80==0x80:
                #push independent, new mode introduced in FEB v96
                nHitsPerTRIP=[rcvDataBytes[1]&0x1F, rcvDataBytes[3]&0x1F, rcvDataBytes[2]&0x1F, rcvDataBytes[4]&0x1F]
                indx=5 #new pointer for independent push case (two extra bytes in rcvDataBytes)
            else: raise Exception('DecodeBRAMDiscrims: Error unable to decode nHitsPerTRIP\nrcvDataBytes=%s'%\
                ''.join([hex(x)[2:].rjust(2,'0') for x in rcvDataBytes]))
        for iTrip in range(4):
            nhits=nHitsPerTRIP[iTrip]
            for iHit in range(nhits):
                #caution: range(0)=[], range(1)=[0], range(2)=[0,1]...
                discrim=['%s:TRIP:%d:HIT:%d'%(source,iTrip,iHit)]
                discrim.extend(self.DecodeDiscrimHit(rcvDataBytes[indx:indx+40]))
                discrims[iTrip].append(discrim)
                indx+=40
        return discrims
    def DecodeDiscrimHit(self, data):
        delays=16*[0]
        found=16*[0]
        for idel in range(0, 32, 2):
            word=data[idel]+(data[idel+1]<<8)
            for ich in range(16):
                bit=(word & (1<<ich))>>ich
                if found[ich]==1 and bit==0:
                    raise Exception('DecodeDiscrimHit: Error discrim delay ticks decoding data error')
                elif found[ich]==0:
                    if bit==0: delays[ich]+=1
                    else: found[ich]=1
        quaters=16*[0]
        lsw=data[32]+(data[33]<<8) #LeastSignificantWord(16bits)
        msw=data[34]+(data[35]<<8) #MostSignificantWord(16bits)
        for ich in range(16):
            qtr=((lsw & (1<<ich))>>ich) + (((msw & (1<<ich))>>ich)<<1)
            if qtr==0: quaters[ich]=1
            else: quaters[ich]=0.25*qtr
        timestamp=data[36]+(data[37]<<8)+(data[38]<<16)+(data[39]<<24)
        #print 'DecodeDiscrimHit: delays=%s'%(delays)
        #print 'DecodeDiscrimHit: quaters=%s'%(quaters) 
        #print 'DecodeDiscrimHit: timestamp=%08X'%(timestamp)
        return [timestamp, [delays[ich]+quaters[ich] for ich in range(16)]]
    def DecodeBRAMTrips(self, rcvDataBytes, source, itrip, theDataType23Hits):
        if rcvDataBytes[0]!=0: raise Exception('DecodeBRAMTrips: Error rcvDataBytes[0]=%d instead of 0.'%rcvDataBytes[0])
        #Commented out 10.22.2012 for CROCE compatibility with CROC: LengthCROCE=LengthCROC+1 
        #if len(rcvDataBytes)!=Frame.MessageDataLengthBRAMTripRead:
        #    #2bytes*36channels*8hits=576+2dummy=578==Frame.MessageDataLengthBRAMTripRead
        #    raise Exception('DecodeBRAMTrips: Error expecting %d data words, received %d'%(Frame.MessageDataLengthBRAMTripRead, len(rcvDataBytes)))
        if theDataType23Hits==False:
            triphits=[[],[],[],[],[],[],[],[]]
        else:
            triphits=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]       
        indx=1
        for ihit in range(len(triphits)):
            hitdata=[]
            for ich in range(36):
                hitdata.append(((rcvDataBytes[indx]+(rcvDataBytes[indx+1]<<8))&0x3FFC)>>2)
                indx+=2
            triphits[ihit]=['%s:TRIP:%s:HIT:%s'%(source,itrip,ihit), hitdata[3:-1]]
        return triphits
    def DecodeBRAMHits(self, rcvDataBytes, source, ihit, theDataType23Hits):
        ########################################################################
        #This is a temp fix (11.04.2013) to accomodate feb.v91 on croce2.v3
        #(with two crcs); there is a flaw in feb.v91, instead of 2*36*6=432bytes
        #the feb sends zero+431bytes, so a dummy zero is added at the end.
        if len(rcvDataBytes)==Frame.MessageDataLengthBRAMHitRead:
            rcvDataBytes.append(0)
        ########################################################################
        if rcvDataBytes[0]!=0: raise Exception('DecodeBRAMHits: Error rcvDataBytes[0]=%d instead of 0.'%rcvDataBytes[0])
        hittrips=[[],[],[],[],[],[]]
        indx=1
        for itrip in range(6):
            tripdata=[]
            for ich in range(36):
                tripdata.append(((rcvDataBytes[indx]+(rcvDataBytes[indx+1]<<8))&0x3FFC)>>2)
                indx+=2
            hittrips[itrip]=['%s:TRIP:%s:HIT:%s'%(source,itrip,ihit), tripdata[3:-1]]
        return hittrips
    
class CROCEFlash():
    #FLASH==67.108.864bits(0x4000000)==8.388.608Bytes(0x800000)==32768Pages*256Bytes==2048Sectors*4KBytes==128Blocks*64KBytes
    #The firmware.mcs file has 5.145.184Bytes. The *.spidata files contains 40200Pages*128Bytes/Page=5.145.600Bytes
    #The user area starts at address 5.177.344Bytes==40448Pages_of_128Bytes==1264Sectors_of_4KBytes==79Blocks_of_64KBytes
    NBytesPerPage=128 #my choice.
    NPages=40200      #this is the firmware region (and *.spidata file region).
    def ParseFileLinesToMessages(self, f):
        iPage=0
        pagesAddrFile=CROCEFlash.NPages*[0]
        pagesBytesFile=CROCEFlash.NPages*[0] 
        for line in f:
            if iPage>=CROCEFlash.NPages:
                raise Exception("The file has more lines than expected %s"%iPage)
            pagesAddrFile[iPage], pagesBytesFile[iPage] = int(line[0:5]), line[6:]
            if pagesAddrFile[iPage]!=iPage:
                raise Exception("Error in file's page address field at line %s"%iPage)
            if len(pagesBytesFile[iPage])-1!=2*CROCEFlash.NBytesPerPage: #CAUTION, there is an \n charcter at the end of lines
                raise Exception("Error in file's page data field at line %s, expected %s hex characters, found %s"\
                    %(iPage,2*CROCEFlash.NBytesPerPage,len(pagesBytesFile[iPage])-1))
            iPage+=1  
        if iPage<CROCEFlash.NPages:
            raise Exception("The file has less lines than expected %s"%iPage)
        return pagesAddrFile, pagesBytesFile

class Flash():
    NPages=1075
    NBytesPerPage=264
    #Read operation commands
    OpBuffer1Read=0xD4
    OpBuffer2Read=0xD6
    OpStatRegRead=0xD7
    OpMainMemPageRead=0xD2
    OpContinuousArrayRead=0xE8
    #Write operation commands
    OpBuffer1Write=0x84
    OpBuffer2Write=0x87
    OpMainMemPageProgThroughBuffer1=0x82
    OpMainMemPageProgThroughBuffer2=0x85
    #Additional operation commands
    OpMainMemToBuffer1Transfer=0x53
    OpMainMemToBuffer2Transfer=0x55
    OpMainMemToBuffer1Compare=0x60
    OpMainMemToBuffer2Compare=0x61
    def ParseFileLineToMessage(self, line):
        try:
            pageAddr=int(line[0:4])
            pageBytes=[int(line[5+2*i:5+2*(i+1)],16) for i in range(Flash.NBytesPerPage)]
        except: raise Exception('Parsing error in line %s...'%line[0:20])
        return pageAddr, pageBytes
    def ParseFileLinesToMessages(self, f):
        iPage=0
        pagesAddrFile=Flash.NPages*[0]
        pagesBytesFile=Flash.NPages*[0]
        for line in f:
            if iPage>=Flash.NPages: raise Exception("The file has more lines than expected %s"%iPage)
            pagesAddrFile[iPage], pagesBytesFile[iPage] = Flash().ParseFileLineToMessage(line)
            if pagesAddrFile[iPage]!=iPage: raise Exception("Error in file's page address field at line %s"%iPage)
            iPage+=1
        if iPage<Flash.NPages: raise Exception("The file has less lines than expected %s"%iPage)
        return pagesAddrFile, pagesBytesFile        
    def MakeOpCodeMessageMainMemPageRead(self, pageAddress, byteAddress=0):
        byte0=Flash.OpMainMemPageRead
        byte1=(pageAddress&0x780)>>7
        byte2=((pageAddress&0x7F)<<1) + ((byteAddress&0x100)>>8)
        byte3=byteAddress&0xFF
        return [byte0, byte1, byte2, byte3, 0, 0, 0, 0]
    def MakeOpCodeMessageMainMemPageProgThroughBuffer(self, bufferIndex, pageAddress, byteAddress=0):
        if bufferIndex!=1 and bufferIndex!=2: raise Exception('Flash Buffer Index out of range')
        if bufferIndex==1: byte0=Flash.OpMainMemPageProgThroughBuffer1
        if bufferIndex==2: byte0=Flash.OpMainMemPageProgThroughBuffer2
        byte1=(pageAddress&0x780)>>7
        byte2=((pageAddress&0x7F)<<1) + ((byteAddress&0x100)>>8)
        byte3=byteAddress&0xFF
        return [byte0, byte1, byte2, byte3]
        
class Frame():
    DirectionMask=0x80
    DirectionM2S=0x00
    DirectionS2M=0x80
    BroadcastMask=0x70
    BroadcastNone=0x00
    BroadcastLoadTimer=0x10
    BroadcastResetTimer=0x20
    BroadcastOpenGate=0x30
    BroadcastSoftReset=0x40
    FEBAddressMask=0x0F
    DeviceMask=0xF0
    DeviceNone=0x00
    DeviceTRIP=0x10
    DeviceFPGA=0x20
    DeviceBRAM=0x30
    DeviceFLASH=0x40
    DeviceBRAM2=0x50
    FuncMask=0x0F
    FuncNone=0x00
    FuncFPGAWrite=0x01
    FuncFPGARead=0x02
    FuncFPGADumpRead=0x03
    FuncTRIPWRAll=0x01
    FuncTRIPWRi=[2,3,4,5,6,7]
    FuncFLASHCommand=0x01
    FuncFLASHSetReset=0x02
    FuncBRAMReadHitx=[1,2,3,4,5,6,14,15]
    FuncBRAMReadDiscrim=7
    FuncBRAMReadTripx=[8,9,10,11,12,13]
    FuncBRAM2ReadHitx=[0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    StatusDeviceOK=0x01
    StatusFuncOK=0x02
    StatusCRCOK=0x01
    StatusEndHeaderOK=0x02
    StatusMaxLengthERR=0x04
    StatusSecondStartErr=0x08
    StatusNAHeaderErr=0x10
    NRegsFPGA=59                            #was 54 in v91, now is 55 in v95, now is 59 in v96
    NRegsTRIPLogical=20
    NRegsTRIPPhysical=14
    NTRIPs=6
    MessageHeaderLength=9                   #FRED=1start+8=9
    MessageDataLengthFPGA=59                #FRED=54+dummy=55, now is 59 in v96
    MessageDataLengthTRIPRead=621           #FRED=644+dummy=645; 644=54*10+58+46
    MessageDataLengthTRIPWrite=725          #FRED=750+dummy=751; 750=54*10+58+46+106
    MessageDataLengthFLASHMMPRead=273
    MessageDataLengthFLASHMMPPTB=269
    MessageDataLengthBRAMTripRead=578       #FRED=2bytes*36channels*8hits=576+1byte00Begin+1byteXXend=578
    MessageDataLengthBRAMHitRead=432        #FRED=2bytes*36channels*6trips=432+dummy=433
##    MessageDataLengthBRAMDiscrimRead=1281   #FRED=2bytes*20records*8hits*4trips=1280+dummy=1281
    MessageDataLengthBRAMTripRead24Hith=1730#FRED=1zero+2bytes*36channels*24hits+1dummy=1730 
    InstrTRIPWrite=1
    InstrTRIPRead=4
    def MakeHeader(self, direction, broadcast, febAddress, device, function, frameID0=0, frameID1=0):
        return [direction+broadcast+febAddress, device+function, 0, frameID0, frameID1, 0, 0, 0, 0]
    def GetReceivedHeaderErrors(self, header, direction, broadcast, febAddress, device, frameID0=0, frameID1=0):
        err=[]
        if len(header)!=Frame.MessageHeaderLength: err.append('HeaderLenth!=%s'%Frame.MessageHeaderLength)
        if header[0]&Frame.DirectionMask!=direction: err.append('Direction!=%s'%direction)
        if header[0]&Frame.BroadcastMask!=broadcast: err.append('Broadcast!=%s'%broadcast)
        if header[0]&Frame.FEBAddressMask!=febAddress: err.append('FEBAddress!=%s'%febAddress)
        if header[1]&Frame.DeviceMask!=device: err.append('Device!=0x%s'%hex(device))
        if header[1]&Frame.StatusDeviceOK!=Frame.StatusDeviceOK: err.append('StatusDeviceOK=False')
        if header[1]&Frame.StatusFuncOK!=Frame.StatusFuncOK: err.append('StatusFuncOK=False')
        if header[2]&Frame.StatusCRCOK!=Frame.StatusCRCOK: err.append('StatusCRCOK=False')
        if header[2]&Frame.StatusEndHeaderOK!=Frame.StatusEndHeaderOK: err.append('StatusEndHeaderOK=False')
        if header[2]&Frame.StatusMaxLengthERR==Frame.StatusMaxLengthERR: err.append('StatusMaxLengthERR=True')
        if header[2]&Frame.StatusSecondStartErr==Frame.StatusSecondStartErr: err.append('StatusSecondStartErr=True')
        if header[2]&Frame.StatusNAHeaderErr==Frame.StatusNAHeaderErr: err.append('StatusNAHeaderErr=True')
        if header[3]&frameID0!=frameID0: err.append('frameID0!=%s'%frameID0)
        if header[4]&frameID1!=frameID1: err.append('frameID1!=%s'%frameID1)
        return err
def WriteSendReceive(sentMessage, rcvMessageLength, theFEBAddress, theFEBDevice, theCROCChannel,
        appendData=0, dw='D16', useBLT=False, theDescription=''):
    ClearAndCheckStatusRegister(theCROCChannel, theDescription=theDescription)
    ResetAndCheckDPMPointer(theCROCChannel, theDescription=theDescription)
    WriteFIFOAndCheckStatus(sentMessage, theCROCChannel, appendData, theDescription=theDescription) 
    SendFIFOAndCheckStatus(theCROCChannel)
    if useBLT: rcvMessageHeader, rcvMessageData = GetRcvMessageHeaderAndDataBLT(theCROCChannel)
    else: rcvMessageHeader, rcvMessageData = GetRcvMessageHeaderAndData(theCROCChannel)
    ###print [hex(x) for x in sentMessage], len(sentMessage)
    ###print [hex(x) for x in rcvMessageHeader], len(rcvMessageHeader)
    ###print [hex(x) for x in rcvMessageData], len(rcvMessageData)
    rcvHeaderErr=Frame().GetReceivedHeaderErrors(rcvMessageHeader,
        Frame.DirectionS2M, Frame.BroadcastNone, theFEBAddress, theFEBDevice)
    if len(rcvHeaderErr)!=0: raise Exception(rcvHeaderErr)
    if rcvMessageLength!=0 and len(rcvMessageData)!=rcvMessageLength: raise Exception(
        'Error rcvDataLength expected=%s, rcv=%s'%(rcvMessageLength, len(rcvMessageData)))
    return rcvMessageData,[]
def WriteSendReceiveCROCE(sentMessage, rcvMessageLength, theFEBAddress, theFEBDevice, theCROCEChannelE,
        appendData=0, dw='D16', useBLT=False, includeCRC=False, theDescription=''):
    ClearAndCheckStatusRegisterCROCE(theCROCEChannelE, theDescription=theDescription)
    WriteFIFOAndCheckStatusCROCE(sentMessage, theCROCEChannelE, appendData, theDescription=theDescription)
    SendFIFOAndCheckStatusCROCE(theCROCEChannelE, theDescription=theDescription)
    rcvMFH_10bytes,rcvMessageHeader,rcvMessageData,rcvMessageCRCs=\
        GetRcvMessageHeaderAndDataCROCE(theCROCEChannelE,dw,useBLT,includeCRC)
##    print '--------------------------------------------------------------------------------'
##    print 'WriteSendReceiveCROCE: length=%s, sentMessage     =%s'%\
##        (str(len(sentMessage)).rjust(3,'0'),''.join([hex(x)[2:].rjust(2,'0') for x in sentMessage]))
##    print 'WriteSendReceiveCROCE: length=%s, rcvMFH_10bytes  =%s'%\
##        (str(len(rcvMFH_10bytes)).rjust(3,'0'),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMFH_10bytes]))
##    print 'WriteSendReceiveCROCE: length=%s, rcvMessageHeader=%s'%\
##        (str(len(rcvMessageHeader)).rjust(3,'0'),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageHeader]))
##    print 'WriteSendReceiveCROCE: length=%s, rcvMessageData  =%s'%\
##        (str(len(rcvMessageData)).rjust(3,'0'),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageData]))
##    print 'WriteSendReceiveCROCE: length=%s, rcvMessageCRCs  =%s'%\
##        (str(len(rcvMessageCRCs)).rjust(3,'0'),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageCRCs]))
    rcvHeaderErr=Frame().GetReceivedHeaderErrors(rcvMessageHeader,
        Frame.DirectionS2M, Frame.BroadcastNone, theFEBAddress, theFEBDevice) 
    if len(rcvHeaderErr)!=0:
        print('FrameHeaderError from %s: %s'%(theDescription, rcvHeaderErr))  #CG 2015.07.27
        raise Exception(rcvHeaderErr)
    if sentMessage[1]==0x21 or sentMessage[1]==0x22 or sentMessage[1]==0x23:
        #special case for FPGA Register frame:
        if not( (len(rcvMessageData)==55 or len(rcvMessageData)==59) and
                (rcvMessageData[32]==91 or rcvMessageData[32]==95 or rcvMessageData[32]==96 or rcvMessageData[32]==97) ) : \
            raise Exception('WriteSendReceiveCROCE Error rcvDataLength expected=55/59, rcv=%s, feb_version=%d'% \
            (len(rcvMessageData), rcvMessageData[32]))
    else:
        #for all other frame types:
        if rcvMessageLength!=0 and len(rcvMessageData)!=rcvMessageLength: raise Exception(
            'WriteSendReceiveCROCE Error rcvDataLength expected=%s, rcv=%s'%(rcvMessageLength, len(rcvMessageData)))
    return rcvMessageData,rcvMFH_10bytes
def ClearAndCheckStatusRegister(theCROCChannel, chk=True, theDescription=''):
    theCROCChannel.ClearStatus()
    if chk:
        status=theCROCChannel.ReadStatus()
        if (status!=0x3700): raise Exception(
            "Error after clear STATUS register for channel " + hex(theCROCChannel.chBaseAddr) + theDescription + " status=" + hex(status))
def ClearAndCheckStatusRegisterCROCE(theCROCEChannelE, chk=True, theDescription=''):
    config=theCROCEChannelE.ReadConfiguration()
    if (config&0xF400!=0x0000): theCROCEChannelE.WriteConfiguration(config&0x083F)
    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
    if chk:
        #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
        data=theCROCEChannelE.ReadAllRegisters() # check FramesCounter,StatusFrame,StatusTXRX,RcvMemWPointer
        if data[2:6]!=[0x0000,0x4040,0x2410,0x0000]: raise Exception(
            '%s %s ClearAndCheckStatusRegisterCROCE Error ReadAllRegisters=%s, should be [0xXXXX,0xXXXX,0x0000,0x4040,0x2410,0x0000,0xXXXX]'\
            %(theCROCEChannelE.Description(),theDescription,['0x'+hex(d)[2:].rjust(4,'0') for d in data]))
def ResetAndCheckDPMPointer(theCROCChannel, chk=True, theDescription=''):
    theCROCChannel.DPMPointerReset()
    if chk:
        dpmPointer=theCROCChannel.DPMPointerRead()
        if (dpmPointer!=0x02): raise Exception(
            "Error after DPMPointerReset() for channel " + hex(theCROCChannel.chBaseAddr) + theDescription + " DPMPointer=" + hex(dpmPointer))
def WriteFIFOAndCheckStatus(theMessage, theCROCChannel, appendData=0, chk=True, theDescription=''):
    if len(theMessage)%2==1: theMessage.append(appendData)
    for i in range(0,len(theMessage),2):
        data = (theMessage[i]<<8) + theMessage[i+1]
        theCROCChannel.WriteFIFO(data)
    if chk:
        status=theCROCChannel.ReadStatus()
        if (status!=0x3710): raise Exception(
            "Error after fill FIFO for channel " + hex(theCROCChannel.chBaseAddr) + theDescription + " status=" + hex(status))
def WriteFIFOAndCheckStatusCROCE(theMessage, theCROCEChannelE, appendData=0, chk=True, theDescription=''):
    if len(theMessage)%2==1: theMessage.append(appendData)
    for i in range(0,len(theMessage),2):
        data = (theMessage[i]<<8) + theMessage[i+1]
        theCROCEChannelE.WriteSendMemory(data)
    if chk:
        #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
        data=theCROCEChannelE.ReadAllRegisters() # check FramesCounter,StatusFrame,StatusTXRX,RcvMemWPointer
        if data[2:6]!=[0x0000,0x0040,0x2410,0x0000]: raise Exception(
            '%s %s WriteFIFOAndCheckStatusCROCE Error ReadAllRegisters=%s, should be [0xXXXX,0xXXXX,0x0000,0x0040,0x2410,0x0000,0xXXXX]'\
            %(theCROCEChannelE.Description(),theDescription,['0x'+hex(d)[2:].rjust(4,'0') for d in data]))
def SendFIFOAndCheckStatus(theCROCChannel, chk=True, theDescription=''):
    theCROCChannel.SendMessage()
    for i in range(100):
        status=theCROCChannel.ReadStatus()
        if (status==0x3703): break
    if (status!=0x3703): raise Exception(
        "Error after send message for channel " + hex(theCROCChannel.chBaseAddr) + theDescription + " status=" + hex(status))
def SendFIFOAndCheckStatusCROCE(theCROCEChannelE, chk=True, theDescription=''):
    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendMessage'])
    for i in range(100):
        #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
        data=theCROCEChannelE.ReadAllRegisters()
        if data[2:5]==[0x0001,0x1010,0x2410]: break # check FramesCounter,StatusFrame,StatusTXRX
    if (data[2:5]!=[0x0001,0x1010,0x2410]): raise Exception(
        '%s %s SendFIFOAndCheckStatusCROCE Error ReadAllRegisters=%s, should be [0x00XX,0xXXXX,0x0001,0x1010,0x2410,0xXXXX,0xXXXX]'\
        %(theCROCEChannelE.Description(),theDescription,['0x'+hex(d)[2:].rjust(4,'0') for d in data]))
def GetRcvMessageHeaderAndData(theCROCChannel):
    dpmPointer=theCROCChannel.DPMPointerRead()
    rcvMessage=[]
    rcvMessageHeader=[]
    rcvMessageData=[]
    for i in range(0, dpmPointer, 2):
        data=theCROCChannel.ReadDPM(i)
        rcvMessage.append((data&0xFF00)>>8)
        rcvMessage.append(data&0x00FF)
    rcvLength=rcvMessage[0]+(rcvMessage[1]<<8)
    #print 'inside SC_MainObjects: GetRcvMessageHeaderAndData     : dpmPointer=%s, rcvLength=%s'%(dpmPointer,rcvLength)
    #print 'CROC     : rcvMessage      =%s, %s'%(''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessage]),len(rcvMessage))
    if rcvLength!=(dpmPointer-2): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' DPMPointer=' + dpmPointer +' <> RcvMessageLength+2=' + rcvLength)
    if rcvLength<(2+Frame.MessageHeaderLength): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' RcvMessageHeaderLength=' + str(rcvLength) +' (too short)')
    rcvMessageHeader=rcvMessage[2:11]
    if rcvLength>11: rcvMessageData=rcvMessage[11:rcvLength]
    #print 'CROC     : rcvMessageHeader=%s, %s'%(''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageHeader]),len(rcvMessageHeader))
    #print 'CROC     : rcvMessageData  =%s, %s'%(''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageData]),len(rcvMessageData))
    return (rcvMessageHeader, rcvMessageData)
def GetRcvMessageHeaderAndDataCROCE(theCROCEChannelE,dw='D16',useBLT=False,includeCRC=False):
    #print 'inside SC_MainObjects: GetRcvMessageHeaderAndDataCROCE'
    rcvMessage=[]
    rcvMessageMFH=[]
    rcvMessageHeader=[]
    rcvMessageData=[]
    rcvMessageCRCs=[]
    RcvMemWPointerRegister=theCROCEChannelE.ReadRcvMemWPointer()+((0x8000&theCROCEChannelE.ReadRDFECounter())<<1)
    StatusFrameRegister=theCROCEChannelE.ReadStatusFrame()
    readNbytes=0
    if dw=='D16':
        if useBLT==True: raise Exception(
            '%s: Error BLT D16 mode not supported by CROCE'%theCROCEChannelE.Description())
        #adjust the number of bytes to read
        if RcvMemWPointerRegister%2==0:
            readNbytes=RcvMemWPointerRegister
        else:
            readNbytes=RcvMemWPointerRegister + 1
        #read
        for i in range(0, readNbytes, 2):
            data=theCROCEChannelE.ReadReceiveMemory(i,dw)
            rcvMessage.append((data&0xFF00)>>8)
            rcvMessage.append(data&0x00FF)
    if dw=='D32':
        #adjust the number of bytes to read
        if RcvMemWPointerRegister%4==0:
            readNbytes=RcvMemWPointerRegister
        else:
            readNbytes=RcvMemWPointerRegister + (4-RcvMemWPointerRegister%4)
        #read
        if useBLT==False:
            for i in range(0, readNbytes, 4):
                data=theCROCEChannelE.ReadReceiveMemory(i,dw)
                rcvMessage.append((data&0xFF000000)>>24)
                rcvMessage.append((data&0x00FF0000)>>16)
                rcvMessage.append((data&0x0000FF00)>>8)
                rcvMessage.append((data&0x000000FF))
        if useBLT==True:
            addr=theCROCEChannelE.RRcvMemory
            rcvMessage=theCROCEChannelE.controller.ReadCycleBLT(addr,readNbytes,am='A32_U_BLT')
##    print 'GetRcvMessageHeaderAndDataCROCE:%s RcvMemWPointerRegister=%s, StatusFrameRegister=%s'%\
##          (theCROCEChannelE.Description(),RcvMemWPointerRegister,hex(StatusFrameRegister))
##    print 'GetRcvMessageHeaderAndDataCROCE:%s dw=%s, useBLT=%s, includeCRC=%s, NumberOfReadBytes=%s'%\
##          (theCROCEChannelE.Description(),dw,useBLT,includeCRC,readNbytes)
    #get the MinervaFrameHeader (10bytes) and check some of these bytes 
    rcvMessageMFH=rcvMessage[0:10]
    rcvMessageMFHLength1=(rcvMessageMFH[0]<<8)+rcvMessageMFH[1]
    rcvMessageMFHStatus =(rcvMessageMFH[2]<<8)+rcvMessageMFH[3]
    rcvMessageMFHLength2=(rcvMessageMFH[8]<<8)+rcvMessageMFH[9]
    if rcvMessageMFHLength1!=rcvMessageMFHLength2: raise Exception(
        '%s: GetRcvMessageHeaderAndDataCROCE Error rcvMessageMFHLength1=%s <> rcvMessageMFHLength2=%s'\
        %(theCROCEChannelE.Description(),'0x'+hex(rcvMessageMFHLength1)[2:].rjust(4,'0'),\
          '0x'+hex(rcvMessageMFHLength2)[2:].rjust(4,'0')))
    if rcvMessageMFHLength1!=RcvMemWPointerRegister: raise Exception(
        '%s: GetRcvMessageHeaderAndDataCROCE Error RcvMemWPointerRegister=%s <> rcvMessageMFHLength1=%s'\
        %(theCROCEChannelE.Description(),'0x'+hex(RcvMemWPointerRegister)[2:].rjust(4,'0'),\
          '0x'+hex(rcvMessageMFHLength1)[2:].rjust(4,'0')))
    if rcvMessageMFHStatus!=StatusFrameRegister: raise Exception(
        '%s: GetRcvMessageHeaderAndDataCROCE Error StatusFrameRegister=%s <> rcvMessageMFHStatus=%s'\
        %(theCROCEChannelE.Description(),'0x'+hex(StatusFrameRegister)[2:].rjust(4,'0'),\
          '0x'+hex(rcvMessageMFHStatus)[2:].rjust(4,'0')))
    #get the frame message header 
    if RcvMemWPointerRegister<(10+Frame.MessageHeaderLength): raise Exception(
        '%s: GetRcvMessageHeaderAndDataCROCE Error RcvMemWPointerRegister=%s < 10 + %s (message too short)'\
        %(theCROCEChannelE.Description(),RcvMemWPointerRegister,Frame.MessageHeaderLength))
    rcvMessageHeader=rcvMessage[10:10+Frame.MessageHeaderLength]
    #get the frame message data
    if includeCRC==False:
        rcvMessageData=rcvMessage[10+Frame.MessageHeaderLength:RcvMemWPointerRegister]
        rcvMessageCRCs=[]
    else:
        if RcvMemWPointerRegister<(10+Frame.MessageHeaderLength+2): raise Exception(
            '%s: GetRcvMessageHeaderAndDataCROCE Error RcvMemWPointerRegister=%s < 10 + %s + 2 (message too short)'\
            %(theCROCEChannelE.Description(),RcvMemWPointerRegister,Frame.MessageHeaderLength))
        rcvMessageData=rcvMessage[10+Frame.MessageHeaderLength:RcvMemWPointerRegister-2]
        rcvMessageCRCs=rcvMessage[RcvMemWPointerRegister-2:RcvMemWPointerRegister]
##    print 'GetRcvMessageHeaderAndDataCROCE:%s rcvMessage      =%s, %s'%(theCROCEChannelE.Description(),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessage]),len(rcvMessage))
##    print 'GetRcvMessageHeaderAndDataCROCE:%s rcvMessageMFH   =%s, %s'%(theCROCEChannelE.Description(),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageMFH]),len(rcvMessageMFH))
##    print 'GetRcvMessageHeaderAndDataCROCE:%s rcvMessageHeader=%s, %s'%(theCROCEChannelE.Description(),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageHeader]),len(rcvMessageHeader))
##    print 'GetRcvMessageHeaderAndDataCROCE:%s rcvMessageData  =%s, %s'%(theCROCEChannelE.Description(),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageData]),len(rcvMessageData))
##    print 'GetRcvMessageHeaderAndDataCROCE:%s rcvMessageCRCs  =%s, %s'%(theCROCEChannelE.Description(),''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageCRCs]),len(rcvMessageCRCs))
    return (rcvMessageMFH,rcvMessageHeader, rcvMessageData, rcvMessageCRCs)
def GetRcvMessageHeaderAndDataBLT(theCROCChannel):
    #print 'inside SC_MainObjects: GetRcvMessageHeaderAndDataBLT'
    dpmPointer=theCROCChannel.DPMPointerRead()
    rcvLength=theCROCChannel.ReadDPM(0)
    rcvLength=((rcvLength&0xFF00)>>8) + ((rcvLength&0x00FF)<<8)
    #print 'inside SC_MainObjects: GetRcvMessageHeaderAndDataBLT: dpmPointer=%s, rcvLength=%s'%(dpmPointer,rcvLength)
    if rcvLength!=(dpmPointer-2): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' DPMPointer=' + str(dpmPointer) +' <> RcvMessageLength+2=' + str(rcvLength))
    if rcvLength<(2+Frame.MessageHeaderLength): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' RcvMessageLength=' + str(rcvLength) +' (too short)')
    rcvMessageHeader=[]
    rcvMessageData=[]
    addr=theCROCChannel.RegRMemory
    if rcvLength%4==0: size=rcvLength #make size compatible with D32 BLT reading
    if rcvLength%4==1: size=rcvLength+3
    if rcvLength%4==2: size=rcvLength+2
    if rcvLength%4==3: size=rcvLength+1
    rcvMessage = theCROCChannel.controller.ReadCycleBLT(addr, size)
    rcvMessageHeader=rcvMessage[2:11]
    if rcvLength>11: rcvMessageData=rcvMessage[11:rcvLength]
    #print 'CROC BLT : rcvMessageHeader=%s, %s'%(''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageHeader]),len(rcvMessageHeader))
    #print 'CROC BLT : rcvMessageData  =%s, %s'%(''.join([hex(x)[2:].rjust(2,'0') for x in rcvMessageData]),len(rcvMessageData))
    return (rcvMessageHeader, rcvMessageData)


class DIGEvent:
    __HeaderSize=4                      # (bytes) see V1720 data sheet pages 24-28
    __MaxNSamplesPerChannel=0xFFFFF     # (samples, 12bits) 1M=1,048,575 samples
    __MaxNControlWordsPerChannel=14     # see V1720 data sheet pages 29-30
    __DataFormatNormal=0                # see V1720 data sheet pages 24-28
    __DataFormatZLE=1                   # see V1720 data sheet pages 24-28
    __Pack25Disabled=0                  # see V1720 data sheet page 52, 4.12, ChannelCongiguration (0x8000)
    __Pack25Enabled=1                   # see V1720 data sheet page 52, 4.12, ChannelCongiguration (0x8000)
    def __init__(self, message, pack25):
        self.msg=message
        self.pack25=pack25
        self.GetHeader()
        self.GetData()
    def GetHeader(self):
        ''' Returns EventHeader information (four 32bit words) as a dicionary
            {'EventSize':self.EventSize,
             'BoardID':self.BoardID,'DataFormat':self.DataFormat,'Pattern':self.Pattern,'ChannelMask':self.ChannelMask, 
             'EventCounter':self.EventCounter,
             'TriggerTimeTag':self.TriggerTimeTag} '''
        if len(self.msg)<DIGEvent.__HeaderSize or self.msg==[]:
            raise Exception('EventHeader Error: EventMessage length must be at least %s 32bit words'%self.__class__.__HeaderSize)
        if self.msg[0]&0xF0000000!=0xA0000000:
            raise Exception('EventHeader Error: First 32bit word must be 0xAXXXXXXX')
        self.EventSize      = int(self.msg[0] & 0x0FFFFFFF)
        self.ChannelMask    = int(self.msg[1] & 0x000000FF)
        self.Pattern        = int(self.msg[1] & 0x00FFFF00) >> 8
        self.DataFormat     = int(self.msg[1] & 0x01000000) >> 24
        self.BoardID        = int(self.msg[1] & 0xF8000000) >> 27
        self.EventCounter   = int(self.msg[2] & 0x00FFFFFF)
        self.TriggerTimeTag = int(self.msg[3] & 0xFFFFFFFF)
        return {'EventSize':self.EventSize,
                'BoardID':self.BoardID,'DataFormat':self.DataFormat,'Pattern':self.Pattern,'ChannelMask':self.ChannelMask, 
                'EventCounter':self.EventCounter,
                'TriggerTimeTag':self.TriggerTimeTag}
    def GetData(self):
        ''' Returns EventData information as a list of 8 lists, one for each DIG's channel
            Each inner list contains NSamplesPerChannel numbers (12bit)
            or it is an empty list if the channel is not enabled.'''
        self.CheckDataLengthConsistency()
        self.UncompressData()
        return self.Data
    def CheckDataLengthConsistency(self): 
        DataSize=self.EventSize-DIGEvent.__HeaderSize
        NChannelsEnabled=0
        #counting the number of channels enabled (using self.ChannelMask) 
        for index in range(DIG.NChannels):
            if (self.ChannelMask & (1<<index)) !=0: NChannelsEnabled += 1
        if NChannelsEnabled==0:
            if DataSize<=0: return
            else: raise Exception('EventData Error: EventHeader shows %s channels are enabled while EventData shows %s 32bit words'%(NChannelsEnabled, hex(DataSize)))
        #we have channels enabled, thus:
        if self.DataFormat==DIGEvent.__DataFormatNormal:
            if DataSize % NChannelsEnabled != 0:
                raise Exception('CheckDataLengthConsistency Error: DataSize=%s, NChannelsEnabled=%s'%(DataSize,NChannelsEnabled))
            WordsPerChannel=int(DataSize/NChannelsEnabled)
            self.N32bitWordsPerChannel=[]
            self.NSamplesPerChannel=[]
            for index in range(DIG.NChannels):
                self.N32bitWordsPerChannel.append( WordsPerChannel * ((self.ChannelMask>>index)&0x1) )
                #print 'index=%s, N32bitWordsPerChannel=%s'%(index,self.N32bitWordsPerChannel[index])
                if self.pack25==DIGEvent.__Pack25Disabled:
                    self.NSamplesPerChannel.append( 2 *  self.N32bitWordsPerChannel[index] )
                else:
                    if self.pack25==DIGEvent.__Pack25Enabled:
                        self.NSamplesPerChannel.append( int(2.5 *  self.N32bitWordsPerChannel[index]) )
                    else: raise Exception('Error: Pack value must be %s or %s'%(DIGEvent.__Pack25Disabled,DIGEvent.__Pack25Enabled))
        if self.DataFormat==DIGEvent.__DataFormatZLE:
            #DataLengthConsistency cannot be checked at this point
            #It will be done by self.UncompressData()
            raise Exception('ZeroLengthEncoding=%s NOT implemented yet...'%(self.DataFormat))
        #print '\nCheckDataLengthConsistency():'
        #print 'DataSize=%s, NChannelsEnabled=%s'%(DataSize,NChannelsEnabled)
        #print 'N32bitWordsPerChannel=%s'%(self.N32bitWordsPerChannel)
        #print 'NSamplesPerChannel=%s'%(self.NSamplesPerChannel)     
    def UncompressData(self):
        self.Data=[]
        ChDataBegin = DIGEvent.__HeaderSize
        for iCH in range(DIG.NChannels):
            self.Data.append([])
            if (self.ChannelMask & (1<<iCH)) !=0:
                # see V1720 data sheet pages 26-28 Fig.3.8 Event Organization
                if self.DataFormat==DIGEvent.__DataFormatNormal and self.pack25==DIGEvent.__Pack25Disabled:
                    for iWord in range(self.N32bitWordsPerChannel[iCH]):
                        self.Data[iCH].append( (self.msg[ChDataBegin + iWord] &0x00000FFF) >> 0 )
                        self.Data[iCH].append( (self.msg[ChDataBegin + iWord] &0x0FFF0000) >> 16)                        
                    ChDataBegin += self.N32bitWordsPerChannel[iCH]
                    continue                   
                # see V1720 data sheet pages 26-28 Fig.3.8 Event Organization
                if self.DataFormat==DIGEvent.__DataFormatNormal and self.pack25==DIGEvent.__Pack25Enabled:
                    for iWord in range(self.N32bitWordsPerChannel[iCH]):
                        if iWord%2==0:
                            self.Data[iCH].append( (self.msg[ChDataBegin + iWord] & 0x00000FFF) >> 0 )
                            self.Data[iCH].append( (self.msg[ChDataBegin + iWord] & 0x00FFF000) >> 12)
                        else:
                            self.Data[iCH].append( ((self.msg[ChDataBegin + iWord - 1] & 0x3F000000) >> 24) + \
                                                   ((self.msg[ChDataBegin + iWord - 0] & 0x0000003F) << 6) )
                            self.Data[iCH].append( (self.msg[ChDataBegin + iWord] & 0x0003FFC0) >> 6)
                            self.Data[iCH].append( (self.msg[ChDataBegin + iWord] & 0x3FFC0000) >> 18 )
                    ChDataBegin += self.N32bitWordsPerChannel[iCH]
                    continue 
                # see V1720 data sheet pages 26-28 Fig.3.8 Event Organization
                if self.DataFormat==DIGEvent.__DataFormatZLE and self.pack25==DIGEvent.__Pack25Disabled:
                    raise Exception('ZeroLengthEncoding=%s NOT implemented yet...'%(self.DataFormat))
                # see V1720 data sheet pages 26-28 Fig.3.8 Event Organization
                if self.DataFormat==DIGEvent.__DataFormatZLE and self.pack25==DIGEvent.__Pack25Enabled:
                    raise Exception('ZeroLengthEncoding=%s NOT implemented yet...'%(self.DataFormat))
        ###print '\nUncompressData():'
        ###print self.Data
        
    def ToStringHeader(self, mode=0):
        ''' Returns the EventHeader as a string for display purpose
            mode=0 (default) -> one line string
            mode=1 multiple line string'''
        if mode==0: width1=1; width2=1; frmt=7*'%s:%s  '
        if mode==1: width1=15; width2=8; frmt=7*'%s:%s\n'
        return str(frmt%(
            'ChannelMask'.ljust(width1, ' '),   hex(self.ChannelMask)[2:].rjust(width2, '0').upper(), \
            'EventSize'.ljust(width1, ' '),     hex(self.EventSize)[2:].rjust(width2, '0').upper(), \
            'EventCounter'.ljust(width1, ' '),  hex(self.EventCounter)[2:].rjust(width2, '0').upper(), \
            'TriggerTimeTag'.ljust(width1, ' '),hex(self.TriggerTimeTag)[2:].rjust(width2, '0').upper(), \
            'DataFormat'.ljust(width1, ' '),    hex(self.DataFormat)[2:].rjust(width2, '0').upper(), \
            'Pattern'.ljust(width1, ' '),       hex(self.Pattern)[2:].rjust(width2, '0').upper(), \
            'BoardID'.ljust(width1, ' '),       hex(self.BoardID)[2:].rjust(width2, '0').upper()))

    def ToStringEvent(self, nValuesPerLine=1, includeHeader=False, nPad=8, cPad='0', typeHex=True):
        ''' Returns the Event as a list of strings for display purpose'''
        if includeHeader: msg=self.msg
        else: msg=self.msg[4:]
        return self.ToStringList(msg, nValuesPerLine, nPad, cPad, typeHex)

    def ToStringData(self, nValuesPerLine=1, nPad=4, cPad='0', typeHex=False):
        ''' Returns the EventData as a list of string for display purpose'''
        lines=[]
        for ilst in range(len(self.Data)):
            lines.append('Channel %s'%ilst)
            lines+=self.ToStringList(self.Data[ilst], nValuesPerLine, nPad, cPad, typeHex)
        return lines
            
    def ToStringList(self, msg, nValuesPerLine, nPad=8, cPad='0', typeHex=True):
        ###hex(dRegs[key]['value'])[2:-1].rjust(8,'0').ljust(10,' ').upper()))
        nlines=int(len(msg)/nValuesPerLine)
        if len(msg) % nValuesPerLine !=0: nlines+=1
        lines=[]
        if typeHex:
            for i in range(nlines):
                istart=i*nValuesPerLine
                istop=(i+1)*nValuesPerLine
                line=''
                if istop<len(msg):
                    for x in msg[istart:istop]: line+=(hex(x)[2:-1]).rjust(nPad, cPad).upper() + ' '
                else:
                    for x in msg[istart:]: line+=hex(x)[2:-1].rjust(nPad, cPad).upper() + ' '
                lines.append(line)
        else:
            for i in range(nlines):
                istart=i*nValuesPerLine
                istop=(i+1)*nValuesPerLine
                line=''
                if istop<len(msg):
                    for x in msg[istart:istop]: line+=str(x).rjust(nPad, cPad).upper() + ' '
                else:
                    for x in msg[istart:]: line+=str(x).rjust(nPad, cPad).upper() + ' '
                lines.append(line)
        return lines    


class WorkerThreadCROCE(threading.Thread):
    def __init__(self,threadNumber,window,nEvents,CROCE,CROCEChannelE,CROCEs,CROCEsAllCRATEs,ReadType,DataType23Hits):
        threading.Thread.__init__(self)
        self.threadNumber=threadNumber
        self.window=window
        self.nEvents=nEvents
        self.CROCE=CROCE
        self.CROCEChannelE=CROCEChannelE
        if ReadType==4: self.CROCEs=CROCEsAllCRATEs
        else: self.CROCEs=CROCEs
        self.ReadType=ReadType
        self.DataType23Hits=DataType23Hits
        self.timeToQuit=threading.Event()
        self.timeToQuit.clear()
    def stop(self):
        self.timeToQuit.set()
    def run(self):
        #wx.CallAfter(self.window.LogMessage, 'Thread %d start running'%(self.threadNumber))
        tt1=time.time()
        for iEvent in range(self.nEvents):
            if self.timeToQuit.isSet():
                wx.CallAfter(self.window.LogMessage, 'Thread %d quitting iEvent=%d %s'%(self.threadNumber,iEvent,time.ctime()))
                break
            # 1. Send OpenGate to simulate a new event
            if self.ReadType==0 or self.ReadType==1 or self.ReadType==2:    # RO one FEB or one CH or one CROCE
                self.CROCE.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif self.ReadType==3 or self.ReadType==4:                      # RO all CROCEs this CRATE or all CRATEs
                for croce in self.CROCEs:
                    croce.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            # ... gives FEBs time to digitize hits: minim 300microsecs for 8 hits digitized, ~1.2milisec for 23 hits digitized
            time.sleep(0.002)
            # 2. Send SoftwareRDFE signal
            if self.ReadType==0 or self.ReadType==1 or self.ReadType==2:    # RO one FEB or one CH or one CROCE
                self.CROCE.SendSoftwareRDFE()
            elif self.ReadType==3 or self.ReadType==4:                      # RO all CROCEs this CRATE or all CRATEs
                for croce in self.CROCEs:
                    croce.SendSoftwareRDFE()
            # 3. Pooling RDFE done <=> RDFECounter incremented
            if self.ReadType==0 or self.ReadType==1:                        # RO one FEB or one CH
                for timeout in range(100):  # for one FEB with 4 frames = 1discr+2Hits+1DevReg => timeout~7 Thus 10 FEBs will be ~70
                    if self.CROCEChannelE.ReadRDFECounter()==iEvent+1:
                        #wx.CallAfter(self.window.LogMessage, 'pooling RDFE ReadType=0,1 timeout=%s'%timeout)
                        break
            elif self.ReadType==2:                                          # RO one CROCE
                for ich in range(4):
                    for timeout in range(100):
                        if self.CROCE.Channels()[ich].ReadRDFECounter()==iEvent+1:
                            break
            elif self.ReadType==3 or self.ReadType==4:                      # RO all CROCEs this CRATE or all CRATEs
                for croce in self.CROCEs:
                    for ich in range(4):
                        for timeout in range(100):
                            if croce.Channels()[ich].ReadRDFECounter()==iEvent+1:
                                break
            #readout data...
            rcvmem=[]
            if self.ReadType==0 or self.ReadType==1:                        # RO one FEB or RO one CH
                rcvmem.append(['CRATE:%s:%s:%s'%(self.CROCE.controller.boardNum, self.CROCE.Description(), self.CROCEChannelE.Description()), self.CROCEChannelE.ReadFullDPMBLT()])
                #wx.CallAfter(self.window.LogMessage, ['%s:%s'%(self.CROCE.Description(), self.CROCEChannelE.Description()), self.CROCEChannelE.ReadFullDPMBLT()])
            elif self.ReadType==2:                                          # RO one CROCE
                for ich in range(4):
                    rcvmem.append(['CRATE:%s:%s:%s'%(self.CROCE.controller.boardNum, self.CROCE.Description(), self.CROCE.Channels()[ich].Description()), self.CROCE.Channels()[ich].ReadFullDPMBLT()])
                    #wx.CallAfter(self.window.LogMessage, ['%s:%s'%(self.CROCE.Description(), self.CROCE.Channels()[ich].Description()), self.CROCE.Channels()[ich].ReadFullDPMBLT()])
            elif self.ReadType==3 or self.ReadType==4:                      # RO all CROCEs this CRATE or all CRATEs
                for croce in self.CROCEs:
                    for ich in range(4):
                        rcvmem.append(['CRATE:%s:%s:%s'%(croce.controller.boardNum, croce.Description(), croce.Channels()[ich].Description()), croce.Channels()[ich].ReadFullDPMBLT()])
                        #wx.CallAfter(self.window.LogMessage, ['%s:%s'%(croce.Description(), croce.Channels()[ich].Description()), croce.Channels()[ich].ReadFullDPMBLT()])
            #wx.CallAfter(self.window.LogMessage, rcvmem)
            frms=SC_MainMethods.DAQSplitRcvmemInFrames(rcvmem, 'CROCE')
            ###SC_MainMethods.DAQReadRcvMemReportFrames(iEvent, frms, self.WriteType, self.WFile, None, 'CROCE', DataType23Hits)
            msg=[('%05d '%iEvent)+str(frm) for frm in frms]
            wx.CallAfter(self.window.LogMessage, '\n'.join(msg))
        tt2=time.time()
        wx.CallAfter(self.window.LogMessage, 'Thread run time = %s)'%(tt2-tt1))
        wx.CallAfter(self.window.ThreadFinished, self)
            







        
