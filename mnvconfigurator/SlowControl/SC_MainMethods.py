import SC_MainObjects
import SC_Util
import CAENVMEwrapper
import V1720Config

class SC():
    '''This SlowControll class should be used for non GUI interface with
    the hardware. See also __init__() for more details'''
    def __init__(self, boardType=CAENVMEwrapper.CAENVMETypes.CVBoardTypes.cvV2718,
        linkNum=0, boardNum=0):
        '''Open and initialize a VME Controller.
        CAUTION: The CAEN VME suports only one instance of Controller() at any time.
        It must be initialised with Init() and closed with End(), then another
        Controller() can be created, if necessary.'''
        self.controller = CAENVMEwrapper.Controller()
        self.controller.Init(boardType, linkNum, boardNum)
        # Lists of CRIM, CROC, DIGitizer objects (VME modules)
        # which are present in this Controller's VME Crate
        self.vmeCRIMs=[]    
        self.vmeCROCs=[]
        self.vmeDIGs=[]
        
    def GetController(self):
        '''The GUI version (and some advanced users) might need 
        direct access to the Controller instance...'''
        return self.controller
    def CloseController(self):
        '''Call this method when you're done with a SC instance.
        You'll get a CAEN VME error if you try to open a new one
        without closing the current one.
        See also __init__() for more details'''
        self.controller.End()
    
    def FindCRIMs(self):
        '''Clear the current list of CRIM objects and
        return a new (updated) list'''
        #CRIM mapping addr is 9 to 255, register is InterruptMask
        addrListCRIMs=[]
        crimReg=0xF000
        for i in range(9,256,1):
            data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
            addr=((i<<16)|crimReg) & 0xFFFFFF
            try:
                self.controller.WriteCycle(addr, data)
                addrListCRIMs.append(i)
                self.controller.WriteCycle(addr, 0)
            except: pass
        #now create object lists for CRIMs
        self.vmeCRIMs=[]
        for addr in addrListCRIMs:
            self.vmeCRIMs.append(SC_MainObjects.CRIM(self.controller, addr<<16))
        return self.vmeCRIMs
    
    def FindCROCs(self):
        '''Clear the current list of CROC objects and
        return a new (updated) list'''
        #CROC mapping addr is 1 to 8, register is ResetTestPulse
        addrListCROCs=[]
        crocReg=0xF010
        for i in range(1,9,1):
            data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
            addr=((i<<16)|crocReg) & 0xFFFFFF
            try:
                self.controller.WriteCycle(addr, data)
                addrListCROCs.append(i)
                self.controller.WriteCycle(addr, 0)
            except: pass
        #now create object lists for CROCs
        self.vmeCROCs=[]
        for addr in addrListCROCs:
            self.vmeCROCs.append(SC_MainObjects.CROC(self.controller, addr<<16))
        return self.vmeCROCs

    def FindDIGs(self):
        '''Clear the current list of DIGitizer objects and
        return a new (updated) list'''
        #DIG mapping addres is ??? register is VMEScratch=0xEF20
        addrListDIGs=[]
        digReg=0xEF20; wdata=0x1234
        for i in range(256):
            try:
                addr=((i<<16)|digReg) & 0xFFFFFF
                self.controller.WriteCycle(addr, wdata)
                if wdata==self.controller.ReadCycle(addr): addrListDIGs.append(i)
            except: pass
        #now create object lists for DIGs
        self.vmeDIGs=[]
        for addr in addrListDIGs:
            self.vmeDIGs.append(SC_MainObjects.DIG(self.controller, addr<<16))
        return self.vmeDIGs

    def FindFEBs(self, theCROCs):
        '''Clear the current list of FEBs, in each channel, for each CROC in the given
        list of CROC object. Return a new (updated) list of FEB addresses, mostly for
        reporting use. The real use is to update the given CROC instances with the FEBs
        that are currently in the system'''
        FEBs=[]
        for theCROC in theCROCs:
            for theCROCChannel in theCROC.Channels():
                #clear the self.FEBs list
                theCROCChannel.FEBs=[]
                for febAddr in range(1,16):
                    for itry in range(1,4):
                        SC_MainObjects.ClearAndCheckStatusRegister(theCROCChannel)
                        SC_MainObjects.ResetAndCheckDPMPointer(theCROCChannel)
                        SC_MainObjects.WriteFIFOAndCheckStatus([febAddr], theCROCChannel) 
                        SC_MainObjects.SendFIFOAndCheckStatus(theCROCChannel)
                        #decode first two words from DPM and check DPM pointer
                        dpmPointer=theCROCChannel.DPMPointerRead()
                        w1=theCROCChannel.ReadDPM(0)
                        w2=theCROCChannel.ReadDPM(2)
                        if (w2==(0x8000 | (febAddr<<8))) & (w1==0x0B00) & (dpmPointer==13):
                            #print "Found feb#" + str(febAddr), "w1="+hex(w1), "dpmPointer="+str(dpmPointer)
                            theCROCChannel.FEBs.append(febAddr)
                            break
                        elif (w2==(0x0000 | (febAddr<<8))) & (w1==0x0400) & (dpmPointer==6): pass
                            #print "NO    feb#" + str(feb), "w1="+hex(w1), "dpmPointer="+str(dpmPointer) 
                        else: pass
                            #print "FindFEBs(%s) wrong message w1=%s w2=%s dpmPointer=%s" % (hex(theCROCChannel.chBaseAddr), hex(w1), hex(w2), str(dpmPointer))   
                FEBs.append('FEB %s %s %s'%(theCROC.Description(), theCROCChannel.Description(), theCROCChannel.FEBs))
        return FEBs

    def HWcfgFileSave(self, fullpathname):
        '''Read the current hardware configuration and write it into a file'''
        #update the cofiguration
        f=open(fullpathname,'w')
        for theCRIM in self.vmeCRIMs:
            f.write('%s:%s\n'%(theCRIM.Description(), theCRIM.GetWRRegValues()))
        for theCROC in self.vmeCROCs:
            f.write('%s:%s\n'%(theCROC.Description(), theCROC.GetWRRegValues()))
        for theCROC in self.vmeCROCs:   
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    f.write('%s:%s\n'%(theFEB.FPGADescription(theCROCChannel, theCROC), \
                        [hex(val)[2:].rjust(2,'0') for val in theFEB.FPGARead(theCROCChannel)]))
        for theCROC in self.vmeCROCs:   
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    for theTRIPIndex in range(SC_MainObjects.Frame.NTRIPs):
                        rcvMessageData=theFEB.TRIPRead(theCROCChannel, theTRIPIndex)
                        pRegs = theFEB.ParseMessageToTRIPRegsPhysical(rcvMessageData, theTRIPIndex)
                        f.write('%s:%s\n'%(theFEB.TRIPDescription(theTRIPIndex, theCROCChannel, theCROC), \
                            [hex(val)[2:].rjust(3,'0') for val in pRegs]))
        f.close()

    def HWcfgFileLoad(self, fullpathname):
        '''Read a configuration file and write it into the current hardware'''
        fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[]
        f=open(fullpathname,'r')
        for line in f:
            lineList = line.split(':')
            if len(lineList)!=3: raise Exception('Wrong format in line %s wrong number of ":" characters'%line)
            if lineList[0]==SC_Util.VMEdevTypes.CRIM:
                if len(lineList[2])!=321: raise Exception('Wrong format in line %s wrong data field length <> 321'%line)
                if SC_MainObjects.FindVMEdev(self.vmeCRIMs, int(lineList[1])<<16)==None:
                    raise Exception('Load ERROR: CRIM:%s not present in current configuration'%lineList[1])
                for i in range(16):
                    addr=str(lineList[2][3+i*20:9+i*20])
                    data=str(lineList[2][13+i*20:17+i*20])
                    self.controller.WriteCycle(int(addr,16), int(data,16))
                #self.frame.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
                fileCRIMs.append(lineList[1])
            if lineList[0]==SC_Util.VMEdevTypes.CROC:
                if len(lineList[2])!=41: raise Exception('Wrong format in line %s wrong data field length <> 41'%line)
                if SC_MainObjects.FindVMEdev(self.vmeCROCs, int(lineList[1])<<16)==None:
                    raise Exception('Load ERROR: CROC:%s not present in current configuration'%lineList[1])
                for i in range(2):
                    addr=lineList[2][3+i*20:9+i*20]
                    data=lineList[2][13+i*20:17+i*20]
                    self.controller.WriteCycle(int(addr,16), int(data,16))
                #self.frame.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
                fileCROCs.append(lineList[1])
            if lineList[0]==SC_Util.VMEdevTypes.FPGA:
                if len(lineList[2])!=331: raise Exception('Wrong format in line %s wrong data field length <> 331'%line)
                addresses = lineList[1].split(',')
                if len(addresses)!=3: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
                febNumber=int(addresses[0])
                chNumber=int(addresses[1])
                crocNumber=int(addresses[2])
                sentMessageData=SC_MainObjects.Frame.NRegsFPGA*[0]
                for i in range(SC_MainObjects.Frame.NRegsFPGA):
                    data=lineList[2][2+i*6:4+i*6]
                    sentMessageData[i]=int(data,16)
                theCROC=SC_MainObjects.FindVMEdev(self.vmeCROCs, crocNumber<<16)
                if (theCROC==None) or not(chNumber in [0,1,2,3]) or not(febNumber in theCROC.Channels()[chNumber].FEBs):
                    raise Exception('Load ERROR: FPGA:%s not present in current configuration'%lineList[1])
                theCROCChannel=theCROC.Channels()[chNumber]
                SC_MainObjects.FEB(febNumber).FPGAWrite(theCROCChannel, sentMessageData)
                #self.frame.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
                fileFPGAs.append(lineList[1])
            if lineList[0]==SC_Util.VMEdevTypes.TRIP:
                if len(lineList[2])!=99: raise Exception('Wrong format in line %s wrong data field length <> 99'%line)
                addresses = lineList[1].split(',')
                if len(addresses)!=4: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
                tripNumber=addresses[0]
                febNumber=int(addresses[1])
                chNumber=int(addresses[2])
                crocNumber=int(addresses[3])
                pRegs=SC_MainObjects.Frame.NRegsTRIPPhysical*[0]
                for i in range(SC_MainObjects.Frame.NRegsTRIPPhysical):
                    data=lineList[2][2+i*7:5+i*7]
                    pRegs[i]=int(data,16)
                theCROC=SC_MainObjects.FindVMEdev(self.vmeCROCs, crocNumber<<16)
                if (theCROC==None) or not(chNumber in [0,1,2,3]) or not(febNumber in theCROC.Channels()[chNumber].FEBs) or not(tripNumber in ['0','1','2','3','4','5','X']):
                    raise Exception('Load ERROR: TRIP:%s not present in current configuration'%lineList[1])
                theCROCChannel=theCROC.Channels()[chNumber]
                theFEB=SC_MainObjects.FEB(febNumber)
                if tripNumber!='X': sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                    SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                    SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRi[int(tripNumber)])
                else:sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                    SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                    SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRAll) 
                sentMessageData = theFEB.ParseTRIPAllRegsPhysicalToMessage(pRegs, SC_MainObjects.Frame.InstrTRIPWrite)
                sentMessage = sentMessageHeader + sentMessageData
                SC_MainObjects.WriteSendReceive(sentMessage, SC_MainObjects.Frame.MessageDataLengthTRIPWrite, theFEB.Address, SC_MainObjects.Frame.DeviceTRIP, theCROCChannel)
                #self.frame.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
                fileTRIPs.append(lineList[1])
        f.close()
        matchError=[]
        for crim in self.vmeCRIMs:
            crimAddr=str((crim.BaseAddress()&0xFF0000)>>16)
            if not(crimAddr in fileCRIMs): matchError.append('CRIM:'+crimAddr)
        for croc in self.vmeCROCs:
            crocAdr=str((croc.BaseAddress()&0xFF0000)>>16)
            if not(crocAdr in fileCROCs): matchError.append('CROC:'+crocAdr)
            for ch in croc.Channels():
                for feb in ch.FEBs:
                    fpga='%s,%s,%s'%(feb, ch.Number(), crocAdr)
                    if not(fpga in fileFPGAs): matchError.append('FPGA:'+fpga)
                    if not('X,%s'%fpga in fileTRIPs):
                        for i in range(6):
                            if not('%s,%s'%(i,fpga) in fileTRIPs): matchError.append('TRIP:'+'%s,%s'%(i,fpga))
        if matchError!=[]: raise Exception('The following devices were NOT found in file %s:\n%s'%(fullpathname, '\n'.join(matchError)))

    def HVReadAll(self, devVal):
        '''Read the HV of all FEBs and return a list with those FEBs 
        on which abs(HVActual-HVTarget) > devVal'''
        return SC_MainObjects.FEB(0).GetAllHVParams(self.vmeCROCs, int(devVal))

    def HVSetAll(self, setVal):
        '''Set the HVTarget of all FEBs to setVal'''
        SC_MainObjects.FEB(0).SetAllHVTarget(self.vmeCROCs, int(setVal))

    def DIGcfgFileLoad(self, fullpathname, thisDIG):
        '''Read a V1720 configuration file.
        Return tuple (flags, lines) where lines is a list of all config file's (parsed) lines and flags is a dictionary
        flags={FileKeyWriteToFile:None, FileKeyAppendMode:None, FileKeyReadoutMode:None,
           FileKeyBLTSize:None, FileKeyOutputFormat:None, FileKeyWriteRegister:[]}'''
        #first call the parsing method
        flags, lines = V1720Config.DIGcfgFileLoad(fullpathname)
        #then write into V170 registers. Note that V1720 needs 32bit data width!!!
        prevDataWidth=self.controller.dataWidth
        self.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD32
        for (addr, data) in flags[V1720Config.FileKeyWriteRegister]:
            self.controller.WriteCycle(thisDIG.BaseAddress()+addr, data)
        self.controller.dataWidth=prevDataWidth
        return flags, lines
        
