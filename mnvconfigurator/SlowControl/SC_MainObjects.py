import SC_Util
import wx
import time

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

class CROC(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMEdevTypes.CROC)
        self.RegWRTimingSetup       = baseAddr + SC_Util.CROCRegs.RegWRTimingSetup
        self.RegWRResetAndTestMask  = baseAddr + SC_Util.CROCRegs.RegWRResetAndTestMask
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
    def ReadTimingSetup(self): return int(self.controller.ReadCycle(self.RegWRTimingSetup))
    def WriteTimingSetup(self, data): self.controller.WriteCycle(self.RegWRTimingSetup, data)
    def SendFastCommand(self, data): self.controller.WriteCycle(self.RegWFastCommand, data)
    def WriteRSTTP(self, data): self.controller.WriteCycle(self.RegWRResetAndTestMask, data)
    def ReadRSTTP(self): return int(self.controller.ReadCycle(self.RegWRResetAndTestMask))
    def SendRSTOnly(self): self.controller.WriteCycle(self.RegWChannelReset, 0x0202)
    def SendTPOnly(self): self.controller.WriteCycle(self.RegWTestPulse, 0x0404)
    def GetWRRegValues(self):
        return [(hex(self.RegWRTimingSetup)[2:].rjust(6, '0'),  hex(self.ReadTimingSetup())[2:].rjust(4, '0')),
                (hex(self.RegWRResetAndTestMask)[2:].rjust(6, '0'), hex(self.ReadRSTTP())[2:].rjust(4, '0'))]

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
    def FPGADescription(self, theCROCChannel, theCROC):
        return '%s:%d,%d,%d'%(SC_Util.VMEdevTypes.FPGA, self.Address, theCROCChannel.chNumber, theCROC.baseAddr>>16)
    def TRIPDescription(self, theTripIndex, theCROCChannel, theCROC):
        return '%s:%s,%d,%d,%d'%(SC_Util.VMEdevTypes.TRIP, theTripIndex, self.Address, theCROCChannel.chNumber, theCROC.baseAddr>>16)
    def FLASHDescription(self, thePageIndex, theCROCChannel, theCROC):
        return '%s:%s,%d,%d,%d'%(SC_Util.VMEdevTypes.FLASH, thePageIndex, self.Address, theCROCChannel.chNumber, theCROC.baseAddr>>16)
    def FPGARead(self, theCROCChannel):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGARead) + Frame.NRegsFPGA*[0]
        return WriteSendReceive(sentMessage, Frame.MessageDataLengthFPGA, self.Address, Frame.DeviceFPGA, theCROCChannel, useBLT=True)
    def FPGAWrite(self, theCROCChannel, sentMessageData):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGAWrite) + sentMessageData
        return WriteSendReceive(sentMessage, Frame.MessageDataLengthFPGA, self.Address, Frame.DeviceFPGA, theCROCChannel, useBLT=True)
    def TRIPProgramRST(self, theCROCChannel):
        sentMessage = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceTRIP, Frame.FuncTRIPWRAll) + [0,8,8,8,8,8,0,0]
        return WriteSendReceive(sentMessage, 9, self.Address, Frame.DeviceTRIP, theCROCChannel) 
    def TRIPRead(self, theCROCChannel, theTRIPIndex=None):
        if theTRIPIndex!=None:
            sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRi[theTRIPIndex])
        else:sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRAll) 
        sentMessageData = self.ParseTRIPAllRegsPhysicalToMessage(Frame.NRegsTRIPPhysical*[0], Frame.InstrTRIPRead)
        sentMessage = sentMessageHeader + sentMessageData
        return WriteSendReceive(sentMessage, Frame.MessageDataLengthTRIPRead, self.Address, Frame.DeviceTRIP, theCROCChannel, useBLT=True)
    def TRIPWrite(self, theCROCChannel, theRegs, theTRIPIndex=None):
        if theTRIPIndex!=None:
            sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRi[theTRIPIndex])
        else:sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
                Frame.DeviceTRIP, Frame.FuncTRIPWRAll) 
        pRegs = self.ParseTRIPRegsLogicalToPhysical(theRegs)
        sentMessageData = self.ParseTRIPAllRegsPhysicalToMessage(pRegs, Frame.InstrTRIPWrite)
        sentMessage = sentMessageHeader + sentMessageData
        WriteSendReceive(sentMessage, Frame.MessageDataLengthTRIPWrite, self.Address, Frame.DeviceTRIP, theCROCChannel, useBLT=True)
    def FLASHMainMemPageRead(self, theCROCChannel, pageAddr):
        sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFLASH, Frame.FuncFLASHCommand)
        sentMessageDataOpCode = Flash().MakeOpCodeMessageMainMemPageRead(pageAddr)
        sentMessage = sentMessageHeader + sentMessageDataOpCode + Flash.NBytesPerPage*[0]
        rcvMessageData = WriteSendReceive(sentMessage, Frame.MessageDataLengthFLASHMMPRead, self.Address, Frame.DeviceFLASH, theCROCChannel, useBLT=True)
        return rcvMessageData[len(sentMessageDataOpCode):len(sentMessageDataOpCode)+Flash.NBytesPerPage]
    def FLASHMainMemPageProgThroughBuffer(self, theCROCChannel, pageAddr, pageBytes, bufferIndex=1):
        sentMessageHeader = Frame().MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFLASH, Frame.FuncFLASHCommand)
        sentMessageDataOpCode = Flash().MakeOpCodeMessageMainMemPageProgThroughBuffer(bufferIndex, pageAddr)
        sentMessage = sentMessageHeader + sentMessageDataOpCode + pageBytes
        WriteSendReceive(sentMessage, Frame.MessageDataLengthFLASHMMPPTB, self.Address, Frame.DeviceFLASH, theCROCChannel, appendData=pageBytes[0], useBLT=True)
        sentMessage = sentMessageHeader + [Flash.OpStatRegRead] + 8*[0]
        for i in range(100):
            rcvMessageData = WriteSendReceive(sentMessage, 9, self.Address, Frame.DeviceFLASH, theCROCChannel)
            if rcvMessageData[8]&0x80==0x80: break
        if i==50: raise Exception('MainMemPageProgThroughBuffer StatusBit NOT Ready')
    def WriteFileToFlash(self, theCROCChannel=None, theCROC=None, theVMECROCs=None,
            toThisFEB=False, toThisCH=False, toThisCROC=False, toAllCROCs=False, theFrame=None):
        dlg = wx.FileDialog(theFrame, message='READ Flash Configuration', defaultDir='', defaultFile='',
            wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
        if dlg.ShowModal()==wx.ID_OK:
            filename=dlg.GetFilename()
            dirname=dlg.GetDirectory()
            theFrame.SetStatusText('WriteFLASH FromFILE %s'%filename, 1)
            f=open(filename,'r')
            pagesAddrFile, pagesBytesFile = Flash().ParseFileLinesToMessages(f)
            f.close()
            if toThisFEB:
                self.WritePagesToFlash(self, theCROCChannel, theCROC, pagesAddrFile, pagesBytesFile, theFrame)     
            if toThisCH:
                for febAddress in theCROCChannel.FEBs:
                    theFEB=FEB(febAddress)
                    self.WritePagesToFlash(theFEB, theCROCChannel, theCROC, pagesAddrFile, pagesBytesFile, theFrame)
            if toThisCROC:
                for theCROCChannel in theCROC.Channels():
                    for febAddress in theCROCChannel.FEBs:
                        theFEB=FEB(febAddress)
                        self.WritePagesToFlash(theFEB, theCROCChannel, theCROC, pagesAddrFile, pagesBytesFile, theFrame)
            if toAllCROCs:
                for theCROC in theVMECROCs:
                    for theCROCChannel in theCROC.Channels():
                        for febAddress in theCROCChannel.FEBs:
                            theFEB=FEB(febAddress)
                            self.WritePagesToFlash(theFEB, theCROCChannel, theCROC, pagesAddrFile, pagesBytesFile, theFrame)
        dlg.Destroy()
    def WritePagesToFlash(self, theFEB, theCROCChannel, theCROC, pagesAddrFile, pagesBytesFile, theFrame):
        errPages=''
        msg="%s Writing %s ..."%(time.ctime(), theFEB.FLASHDescription('', theCROCChannel, theCROC))
        print msg; theFrame.SetStatusText(msg, 2)
        for iPage in range(Flash.NPages):
            theFEB.FLASHMainMemPageProgThroughBuffer(theCROCChannel, pagesAddrFile[iPage], pagesBytesFile[iPage])
            pageBytesRead=theFEB.FLASHMainMemPageRead(theCROCChannel, pagesAddrFile[iPage])
            if pageBytesRead!=pagesBytesFile[iPage]: errPages += '%s '%iPage
            if iPage%100==0:
                theFrame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
                theFrame.Refresh(); theFrame.Update()
        theFrame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
        if errPages:
            print "Write ERROR %s, page %s"%(theFEB.FLASHDescription('', theCROCChannel, theCROC), errPages)
            theFrame.SetStatusText("Write ERROR on %s"%theFEB.FLASHDescription('', theCROCChannel, theCROC), 2)
        else:
            msg="%s Write DONE %s"%(time.ctime(), theFEB.FLASHDescription('', theCROCChannel, theCROC))
            print msg; theFrame.SetStatusText(msg, 2)
    def AlignGateDelays(self, theCROC, theCROCChannel, theNumberOfMeas, theLoadTimerValue, theGateStartValue):
        if theCROCChannel.FEBs==[]: return
        print 'Reporting FEBs TPDelay measurements on %s %s'%(theCROC.Description(),theCROCChannel.Description())
        #Set LoadTimerValue and GateStartValue equal for ALL boards in this Channel
        for febAddress in theCROCChannel.FEBs:
            theFEB=FEB(febAddress)
            rcvMessage=theFEB.FPGARead(theCROCChannel)
            #message word 0-3: WR Timer, 32 bits
            rcvMessage[0] = (theLoadTimerValue) & 0xFF
            rcvMessage[1] = (theLoadTimerValue>>8) & 0xFF
            rcvMessage[2] = (theLoadTimerValue>>16) & 0xFF
            rcvMessage[3] = (theLoadTimerValue>>24) & 0xFF
            #message word 4-5: WR Gate Start, 16 bits
            rcvMessage[4] = (theGateStartValue) & 0xFF
            rcvMessage[5] = (theGateStartValue>>8) & 0xFF
            theFEB.FPGAWrite(theCROCChannel, rcvMessage)
        #Acquire TPDelay information
        TPDelay=[]
        for iMeas in range(theNumberOfMeas):
            theCROC.SendFastCommand(SC_Util.FastCmds['LoadTimer'])
            theCROC.WriteRSTTP(1<<theCROCChannel.Number())
            theCROC.SendTPOnly()
            #Get TP delay for ALL FEBs in this Channel
            FEBsTPDelay=[]
            for febAddress in theCROCChannel.FEBs:
                theFEB=FEB(febAddress)
                rcvMessage=theFEB.FPGARead(theCROCChannel)
                #message word 9, bit 6 - 7: R  TP Count2b, 2 bits
                tpCount2b=(rcvMessage[9]>>6)&0x03
                #message word 12-15: R  TP Count, 32 bits
                tpCount32b=rcvMessage[12]+(rcvMessage[13]<<8)+(rcvMessage[14]<<16)+(rcvMessage[15]<<24)
                if tpCount2b==0: tpCount=tpCount32b+1
                else: tpCount=tpCount32b+0.25*tpCount2b
                FEBsTPDelay.append([febAddress, tpCount])
                'first position == febAddress, second position == tpCount'
            thisMeasMinValue=FEBsTPDelay[0][1]
            for feb in FEBsTPDelay:
                if feb[1]<thisMeasMinValue: thisMeasMinValue=feb[1]
            for feb in FEBsTPDelay: feb[1]-=thisMeasMinValue
            TPDelay.append(FEBsTPDelay)
        #Clear RST and TP content 
        theCROC.WriteRSTTP(0)
        #Calculate average value of ALL measurements
        TPDelayAvg=[]
        for i in range(len(theCROCChannel.FEBs)): TPDelayAvg.append([0,0])
        for iFEB in range(len(theCROCChannel.FEBs)):
            TPDelayAvg[iFEB][0]=TPDelay[0][iFEB][0]
            for iMeas in range(theNumberOfMeas):
                TPDelayAvg[iFEB][1]+=TPDelay[iMeas][iFEB][1]
            TPDelayAvg[iFEB][1]/=theNumberOfMeas         
        for feb in TPDelayAvg:
            print 'FEB:%s, AvgDelay=%s'%(feb[0],feb[1])
        #Update new values to FPGA's Timer and GateStart
        for iFEB in TPDelayAvg:
            theFEB=FEB(iFEB[0])
            theDelay = int(round(float(iFEB[1])/2))
            rcvMessage=theFEB.FPGARead(theCROCChannel)
            #message word 0-3: WR Timer, 32 bits
            rcvMessage[0] -= (theDelay) & 0xFF
            rcvMessage[1] -= (theDelay>>8) & 0xFF
            rcvMessage[2] -= (theDelay>>16) & 0xFF
            rcvMessage[3] -= (theDelay>>24) & 0xFF
            #message word 4-5: WR Gate Start, 16 bits
            rcvMessage[4] -= (theDelay) & 0xFF
            rcvMessage[5] -= (theDelay>>8) & 0xFF
            theFEB.FPGAWrite(theCROCChannel, rcvMessage)
    def GetAllHVActual(self, vmeCROCs, devVal=0):
        hvVals=[]
        for theCROC in vmeCROCs:
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=FEB(febAddress)
                    rcvMessage=theFEB.FPGARead(theCROCChannel)
                    #message word 25-26: R  HV Actual, 16 bits
                    hvActual=rcvMessage[25]+(rcvMessage[26]<<8)
                    #message word 23-24: WR HV Target, 16 bits
                    hvTarget=rcvMessage[23]+(rcvMessage[24]<<8)
                    if abs(hvActual-hvTarget)>=devVal:
                        descr={'FEB':febAddress, 'Channel':theCROCChannel.chNumber, 'CROC':theCROC.baseAddr>>16}
                        hvVals.append({'FPGA':descr, 'Actual':hvActual, 'Target':hvTarget, 'A-T':hvActual-hvTarget})
        return hvVals    
    def SetAllHVTarget(self, vmeCROCs, hvVal):
        for theCROC in vmeCROCs:
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=FEB(febAddress)
                    rcvMessage=theFEB.FPGARead(theCROCChannel)
                    #message word 23-24: WR HV Target, 16 bits
                    rcvMessage[23] = (hvVal) & 0xFF
                    rcvMessage[24] = (hvVal>>8) & 0xFF
                    theFEB.FPGAWrite(theCROCChannel, rcvMessage)

    def ParseMessageToFPGAtxtRegs(self, msg, txtRegs):
        #message word 0-3: WR Timer, 32 bits
        txtRegs[14].SetValue(str(msg[0]+(msg[1]<<8)+(msg[2]<<16)+(msg[3]<<24)))
        #message word 4-5: WR Gate Start, 16 bits
        txtRegs[1].SetValue(str(msg[4]+(msg[5]<<8)))
        #message word 6-7: WR Gate Length, 16 bits
        txtRegs[2].SetValue(str(msg[6]+(msg[7]<<8)))
        #message word 8-9, bit 0: R  DCM2 PhaseTotal, 9 bits
        txtRegs[36].SetValue(str(msg[8]+((msg[9]&0x01)<<8)))
        #message word 9, bit 1: R  DCM2 PhaseDone, 1 bit
        txtRegs[35].SetValue(str((msg[9]>>1)&0x01))
        #message word 9, bit 2: R  DCM1 NoCLK(0), 1 bit
        txtRegs[33].SetValue(str((msg[9]>>2)&0x01))
        #message word 9, bit 3: R  DCM2 NoCLK(0), 1 bit
        txtRegs[34].SetValue(str((msg[9]>>3)&0x01))
        #message word 9, bit 4: R  DCM1 Lock(0), 1 bit
        txtRegs[31].SetValue(str((msg[9]>>4)&0x01))#message word 25-26: R  HV Actual, 16 bits
        txtRegs[5].SetValue(str(msg[25]+(msg[26]<<8)))
        #message word 9, bit 5: R  DCM2 Lock(0), 1 bit
        txtRegs[32].SetValue(str((msg[9]>>5)&0x01))
        #message word 9, bit 6 - 7: R  TP Count2b, 2 bits
        txtRegs[37].SetValue(str((msg[9]>>6)&0x03))
        #message word 10: WR Phase Ticks, 8 bits
        txtRegs[30].SetValue(str(msg[10]))
        #message word 11, bit 0: R  ExtTriggFound, 1 bit
        txtRegs[41].SetValue(str((msg[11])&0x01))
        #message word 11, bit 1: WR ExtTriggRearm, 1 bit
        txtRegs[42].SetValue(str((msg[11]>>1)&0x01))
        #message word 11, bit 2: R  SCmdErr(1), 1 bit
        txtRegs[48].SetValue(str((msg[11]>>2)&0x01))
        #message word 11, bit 3: R  FCmdErr(1), 1 bit
        txtRegs[49].SetValue(str((msg[11]>>3)&0x01))
        #message word 11, bit 4: WR Phase -(0)+(1), 1 bit
        txtRegs[29].SetValue(str((msg[11]>>4)&0x01))
        #message word 11, bit 5: WR Phase R(0)S(1), 1 bit
        txtRegs[28].SetValue(str((msg[11]>>5)&0x01))
        #message word 11, bit 6: R  RXSyncErr(1), 1 bit
        txtRegs[50].SetValue(str((msg[11]>>6)&0x01))
        #message word 11, bit 7: R  TXSyncErr(1), 1 bit
        txtRegs[51].SetValue(str((msg[11]>>7)&0x01))
        #message word 12-15: R  TP Count, 32 bits
        txtRegs[38].SetValue(str(msg[12]+(msg[13]<<8)+(msg[14]<<16)+(msg[15]<<24)))
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
        txtRegs[20].SetValue(str(msg[21]))#message word 0-3: WR Timer, 32 bits
        msg[0] = (int(txtRegs[14].GetValue())) & 0xFF
        msg[1] = (int(txtRegs[14].GetValue())>>8) & 0xFF
        msg[2] = (int(txtRegs[14].GetValue())>>16) & 0xFF
        msg[3] = (int(txtRegs[14].GetValue())>>24) & 0xFF
        #message word 4-5: WR Gate Start, 16 bits
        msg[4] = (int(txtRegs[1].GetValue())) & 0xFF
        msg[5] = (int(txtRegs[1].GetValue())>>8) & 0xFF
        #message word 22, bit 0-5: WR Trip PowOFF, 1 bit for each trip
        txtRegs[0].SetValue(str(msg[22]&0x3F))
        #message word 22, bit 6: WR HV Auto(0)Man(1), 1 bit 
        txtRegs[6].SetValue(str((msg[22]>>6)&0x01))
        #message word 22, bit 7: WR HV Enable(1), 1 bit
        txtRegs[3].SetValue(str((msg[22]>>7)&0x01))
        #message word 23-24: WR HV Target, 16 bits
        txtRegs[4].SetValue(str(msg[23]+(msg[24]<<8)))
        #message word 25-26: R  HV Actual, 16 bits
        txtRegs[5].SetValue(str(msg[25]+(msg[26]<<8)))
        #message word 27: R  HV Control, 8 bits
        txtRegs[27].SetValue(str(msg[27]))
        #message word 28-29, bits 0-3: WR InjDAC Value, 12 bits
        txtRegs[23].SetValue(str(msg[28]+((msg[29]&0x0F)<<8)))
        #message word 29, bits 4-5: WR InjDAC Mode(0), 2 bits
        txtRegs[24].SetValue(str((msg[29]>>4)&0x03))
        #message word 29, bits 6: R  InjDAC Done(1), 1 bit
        txtRegs[26].SetValue(str((msg[29]>>6)&0x01))
        #message word 29, bits 7: WR InjDAC R(0)S(1), 1 bit
        txtRegs[25].SetValue(str((msg[29]>>7)&0x01))
        #message word 30: WR TripX InjRange (bits 0-3)
        txtRegs[21].SetValue(str((msg[30])&0x0F))
        #message word 30: WR TripX InjPhase (bits 4-7)
        txtRegs[22].SetValue(str((msg[30]>>4)&0x0F))
        #message word 31: R  FE Board ID (bits 0-3)
        txtRegs[13].SetValue(str((msg[31])&0x0F))
        #message word 31: WR HV NumAvg (bits 4-7)
        txtRegs[7].SetValue(str((msg[31]>>4)&0x0F))
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
        txtRegs[39].SetValue(str(msg[40]))
        #message word 41: R  TripX Comparators, 8 bits
        txtRegs[40].SetValue(str(msg[41]))
        #message word 42-43: WR DiscMaskT0 (0x), 16 bits
        txtRegs[43].SetValue(hex(msg[42]+(msg[43]<<8))[2:])
        #message word 44-45: WR DiscMaskT1 (0x), 16 bits
        txtRegs[44].SetValue(hex(msg[44]+(msg[45]<<8))[2:])
        #message word 46-47: WR DiscMaskT2 (0x), 16 bits
        txtRegs[45].SetValue(hex(msg[46]+(msg[47]<<8))[2:])
        #message word 48-49: WR DiscMaskT3 (0x), 16 bits
        txtRegs[46].SetValue(hex(msg[48]+(msg[49]<<8))[2:])
        #message word 50-53: R  GateTimeStamp, 32 bits
        txtRegs[47].SetValue(str(msg[50]+(msg[51]<<8)+(msg[52]<<16)+(msg[53]<<24)))
    def ParseFPGARegsToMessage(sel, txtRegs):
        msg=Frame.NRegsFPGA*[0]
        #message word 0-3: WR Timer, 32 bits
        msg[0] = (int(txtRegs[14].GetValue())) & 0xFF
        msg[1] = (int(txtRegs[14].GetValue())>>8) & 0xFF
        msg[2] = (int(txtRegs[14].GetValue())>>16) & 0xFF
        msg[3] = (int(txtRegs[14].GetValue())>>24) & 0xFF
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
        msg[11] = ((int(txtRegs[42].GetValue()) & 0x01) << 1) + \
                  ((int(txtRegs[29].GetValue()) & 0x01) << 4) + \
                  ((int(txtRegs[28].GetValue()) & 0x01) << 5)
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
        #message word 22, bit 0-5: WR Trip PowOFF, 1 bit for each trip
        #message word 22, bit 6: WR HV Auto(0)Man(1), 1 bit
        #message word 22, bit 7: WR HV Enable(1), 1 bit
        msg[22] = ((int(txtRegs[0].GetValue()) & 0x3F)) + \
                  ((int(txtRegs[6].GetValue()) & 0x01) << 6) + \
                  ((int(txtRegs[3].GetValue()) & 0x01) << 7)
        #message word 23-24: WR HV Target, 16 bits
        msg[23] = (int(txtRegs[4].GetValue())) & 0xFF
        msg[24] = (int(txtRegs[4].GetValue())>>8) & 0xFF
        #message word 25-27: Read Only
        #message word 28-29, bits 0-3: WR InjDAC Value, 12 bits
        msg[28] = (int(txtRegs[23].GetValue())) & 0xFF
        #message word 28-29, bits 0-3: WR InjDAC Value, 12 bits
        #message word 29, bits 4-5: WR InjDAC Mode(0), 2 bits
        #message word 29, bits 7: WR InjDAC R(0)S(1), 1 bit
        msg[29] = ((int(txtRegs[23].GetValue()) & 0xF00) >> 8) + \
                  ((int(txtRegs[24].GetValue()) & 0x03) << 4) + \
                  ((int(txtRegs[25].GetValue()) & 0x01) << 7)
        #message word 30: WR TripX InjRange (bits 0-3)
        #message word 30: WR TripX InjPhase (bits 4-7)
        #a special case for InjectPhase register
        injPhase=int(txtRegs[22].GetValue())
        if injPhase==0 or injPhase==1 or injPhase==2 or injPhase==4 or injPhase==8:
            msg[30] = ((int(txtRegs[21].GetValue()) & 0x0F)) + \
                      ((int(txtRegs[22].GetValue()) & 0x0F) << 4)
        else: raise Exception(txtRegs[22].GetName() + ' must be 1, 2, 4 or 8')
        #message word 31: WR HV NumAvg (bits 4-7)
        msg[31] = ((int(txtRegs[7].GetValue()) & 0x0F) << 4)
        #message word 32: Read Only
        #message word 33-34: WR HV PeriodMan, 16 bits
        msg[33] = (int(txtRegs[8].GetValue())) & 0xFF
        msg[34] = (int(txtRegs[8].GetValue())>>8) & 0xFF
        #message word 35-36: Read Only
        #message word 37: WR HV PulseWidth, 8 bits
        msg[37] = (int(txtRegs[10].GetValue())) & 0xFF
        #message word 38-39: Read Only
        #message word 40: WR TripX Threshold, 8 bits
        msg[40] = (int(txtRegs[39].GetValue())) & 0xFF
        #message word 41: Read Only
        #message word 42-43: WR DiscMaskT0 (0x), 16 bits
        msg[42] = (int(txtRegs[43].GetValue(),16)) & 0xFF
        msg[43] = (int(txtRegs[43].GetValue(),16)>>8) & 0xFF
        #message word 44-45: WR DiscMaskT1 (0x), 16 bits
        msg[44] = (int(txtRegs[44].GetValue(),16)) & 0xFF
        msg[45] = (int(txtRegs[44].GetValue(),16)>>8) & 0xFF
        #message word 46-47: WR DiscMaskT2 (0x), 16 bits
        msg[46] = (int(txtRegs[45].GetValue(),16)) & 0xFF
        msg[47] = (int(txtRegs[45].GetValue(),16)>>8) & 0xFF
        #message word 48-49: WR DiscMaskT3 (0x), 16 bits
        msg[48] = (int(txtRegs[46].GetValue(),16)) & 0xFF
        msg[49] = (int(txtRegs[46].GetValue(),16)>>8) & 0xFF
        #message word 50-53: Read Only
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
    FuncMask=0x0F
    FuncNone=0x00
    FuncFPGAWrite=0x01
    FuncFPGARead=0x02
    FuncTRIPWRAll=0x01
    FuncTRIPWRi=[2,3,4,5,6,7]
    FuncFLASHCommand=0x01
    FuncFLASHSetReset=0x02
    StatusDeviceOK=0x01
    StatusFuncOK=0x02
    StatusCRCOK=0x01
    StatusEndHeaderOK=0x02
    StatusMaxLengthERR=0x04
    StatusSecondStartErr=0x08
    StatusNAHeaderErr=0x10
    NRegsFPGA=54
    NRegsTRIPLogical=20
    NRegsTRIPPhysical=14
    NTRIPs=6
    MessageHeaderLength=9
    MessageDataLengthFPGA=55
    MessageDataLengthTRIPRead=621
    MessageDataLengthTRIPWrite=725
    MessageDataLengthFLASHMMPRead=273
    MessageDataLengthFLASHMMPPTB=269
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
        if header[1]&Frame.DeviceMask!=device: err.append('Device!=%s'%device)
        if header[1]&Frame.StatusDeviceOK!=Frame.StatusDeviceOK: err.append('StatusDeviceOK=False')
        if header[1]&Frame.StatusFuncOK!=Frame.StatusFuncOK: err.append('StatusFuncOK=False')
        if header[2]&Frame.StatusCRCOK!=Frame.StatusCRCOK: err.append('StatusCRCOK=False')
        if header[2]&Frame.StatusEndHeaderOK!=Frame.StatusEndHeaderOK: err.append('StatusEndHeaderOK=False')
        if header[2]&Frame.StatusMaxLengthERR==Frame.StatusMaxLengthERR: err.append('StatusMaxLengthERR=True')
        if header[2]&Frame.StatusSecondStartErr==Frame.StatusSecondStartErr: err.append('StatusSecondStartErr=True')
        if header[2]&Frame.StatusNAHeaderErr==Frame.StatusNAHeaderErr: err.append('StatusNAHeaderErr=True')
        if header[3]&frameID0!=frameID0: err.append('frameI12D0!=%s'%frameID0)
        if header[4]&frameID1!=frameID1: err.append('frameID1!=%s'%frameID1)
        return err
def WriteSendReceive(sentMessage, rcvMessageLength, theFEBAddress, theFEBDevice, theCROCChannel, appendData=0, useBLT=False):
    ClearAndCheckStatusRegister(theCROCChannel)
    ResetAndCheckDPMPointer(theCROCChannel)
    WriteFIFOAndCheckStatus(sentMessage, theCROCChannel, appendData) 
    SendFIFOAndCheckStatus(theCROCChannel)
    if useBLT: rcvMessageHeader, rcvMessageData = GetRcvMessageHeaderAndDataBLT(theCROCChannel)
    else: rcvMessageHeader, rcvMessageData = GetRcvMessageHeaderAndData(theCROCChannel)
    ###print [hex(x) for x in sentMessage], len(sentMessage)
    ###print [hex(x) for x in rcvMessageHeader], len(rcvMessageHeader)
    ###print [hex(x) for x in rcvMessageData], len(rcvMessageData)
    rcvHeaderErr=Frame().GetReceivedHeaderErrors(rcvMessageHeader,
        Frame.DirectionS2M, Frame.BroadcastNone, theFEBAddress, theFEBDevice)
    if len(rcvHeaderErr)!=0: raise Exception(rcvHeaderErr)
    if len(rcvMessageData)!=rcvMessageLength: raise Exception(
        'Error rcvDataLength expected=%s, rcv=%s'%(rcvMessageLength, len(rcvMessageData)))
    return rcvMessageData
def ClearAndCheckStatusRegister(theCROCChannel, chk=True):
    theCROCChannel.ClearStatus()
    if chk:
        status=theCROCChannel.ReadStatus()
        if (status!=0x3700): raise Exception(
            "Error after clear STATUS register for channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
def ResetAndCheckDPMPointer(theCROCChannel, chk=True):
    theCROCChannel.DPMPointerReset()
    if chk:
        dpmPointer=theCROCChannel.DPMPointerRead()
        if (dpmPointer!=0x02): raise Exception(
            "Error after DPMPointerReset() for channel " + hex(theCROCChannel.chBaseAddr) + " DPMPointer=" + hex(dpmPointer))
def WriteFIFOAndCheckStatus(theMessage, theCROCChannel, appendData=0, chk=True):
    if len(theMessage)%2==1: theMessage.append(appendData)
    for i in range(0,len(theMessage),2):
        data = (theMessage[i]<<8) + theMessage[i+1]
        theCROCChannel.WriteFIFO(data)
    if chk:
        status=theCROCChannel.ReadStatus()
        if (status!=0x3710): raise Exception(
            "Error after fill FIFO for channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
def SendFIFOAndCheckStatus(theCROCChannel, chk=True):
    theCROCChannel.SendMessage()
    for i in range(100):
        status=theCROCChannel.ReadStatus()
        if (status==0x3703): break
    if (status!=0x3703): raise Exception(
        "Error after send message for channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
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
    if rcvLength!=(dpmPointer-2): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' DPMPointer=' + dpmPointer +' <> RcvMessageLength+2=' + rcvLength)
    if rcvLength<(2+Frame.MessageHeaderLength): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' RcvMessageHeaderLength=' + rcvLength +' (too short)')
    rcvMessageHeader=rcvMessage[2:11]
    if rcvLength>11: rcvMessageData=rcvMessage[11:rcvLength]
##    print 'NO BLT: %s %s'%(rcvLength, rcvMessageHeader+rcvMessageData)
##    blt=GetRcvMessageHeaderAndDataBLT(theCROCChannel)
##    print 'WITH BLT: %s'%(blt[0]+blt[1])  
    return (rcvMessageHeader, rcvMessageData)
def GetRcvMessageHeaderAndDataBLT(theCROCChannel):
    dpmPointer=theCROCChannel.DPMPointerRead()
    rcvLength=theCROCChannel.ReadDPM(0)
    rcvLength=((rcvLength&0xFF00)>>8) + ((rcvLength&0x00FF)<<8)
    if rcvLength!=(dpmPointer-2): raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' DPMPointer=' + dpmPointer +' <> RcvMessageLength+2=' + rcvLength)
    if rcvLength<(2+Frame.MessageHeaderLength) or rcvLength%2!=0: raise Exception(
        'Error for channel ' + hex(theCROCChannel.chBaseAddr) +
        ' RcvMessageLength=' + rcvLength)
    rcvMessageHeader=[]
    rcvMessageData=[]
    addr=theCROCChannel.RegRMemory
    size=rcvLength
    rcvMessage = theCROCChannel.controller.ReadCycleBLT(addr, size)
    rcvMessageHeader=rcvMessage[2:11]
    if rcvLength>11: rcvMessageData=rcvMessage[11:rcvLength]
    return rcvMessageHeader, rcvMessageData


   
