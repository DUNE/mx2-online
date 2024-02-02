import SC_MainObjects
import SC_Util
import CAENVMEwrapper
import V1720Config
import time
import sys

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
        print 'SWRelease=%s'%self.controller.SWRelease()
        print 'BoardFWRelease=%s'%self.controller.BoardFWRelease()
        self.vmeCRIMs=[]    
        self.vmeCROCs=[]
        self.vmeCROCEs=[]
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

    def FindCROCEs(self):
        '''Clear the current list of CROC objects and
        return a new (updated) list'''
        #CROCE mapping addr is 1 to 8, register is ResetTestPulse
        addrListCROCEs=[]
        crocEReg=0x0FF010
        for i in range(1,9,1):
            data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
            addr=((i<<24)|crocEReg) & 0xFFFFFFFF
            try:
                self.controller.WriteCycle(addr, data, am='A32_U_DATA', dw='D16')
                addrListCROCEs.append(i)
                self.controller.WriteCycle(addr, 0, am='A32_U_DATA', dw='D16')
            except: pass
        #now create object lists for CROCs
        self.vmeCROCEs=[]
        for addr in addrListCROCEs:
            self.vmeCROCEs.append(SC_MainObjects.CROCE(self.controller, addr<<24))
        return self.vmeCROCEs

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

    def FindCROCEFEBs(self, theCROCEs):
        '''Clear the current list of FEBs, in each channel, for each CROCE in the given
        list of CROCE object. Return a new (updated) list of FEB addresses, mostly for
        reporting use. The real use is to update the given CROCE instances with the FEBs
        that are currently in the system'''
        FEBs=[]
        for theCROCE in theCROCEs:
            for theCROCEChannelE in theCROCE.Channels():
                #clear the self.FEBs list
                theCROCEChannelE.FEBs=[]
                for febAddr in range(1,16):
                    for itry in range(1,5):
                        fails=0
                        #set configuration, clear status and check registers
                        theCROCEChannelE.WriteConfiguration(0x0000)
                        theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                        data=theCROCEChannelE.ReadAllRegisters()
                        if data!=[data[0]&0x03C0,0x0000,0x0000,0x4040,0x2410,0x0000]:
                            #print 'TRY#%s, FindCROCEFEBs, %s:%s: Error1 ReadAllRegisters1=%s, should be [0x0000,0x0000,0x0000,0x4040,0x2410,0x0000]'\
                            #    %(itry,theCROCE.Description(),theCROCEChannelE.Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data])
                            fails=fails+1
                        #write message and check registers
                        sndmsg=[febAddr<<8]
                        theCROCEChannelE.WriteSendMemory(sndmsg[0])
                        data=theCROCEChannelE.ReadAllRegisters()
                        if data!=[data[0]&0x03C0,0x0000,0x0000,0x0040,0x2410,0x0000]:
                            #print 'TRY#%s, FindCROCEFEBs, %s:%s: Error2 ReadAllRegisters2=%s, should be [0x0000,0x0000,0x0000,0x0040,0x2410,0x0006]'\
                            #    %(itry,theCROCE.Description(),theCROCEChannelE.Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data])
                            fails=fails+1
                        #send message and check registers
                        theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendMessage'])
                        data=theCROCEChannelE.ReadAllRegisters()
                        if (data[:-1]!=[data[0]&0x03C0,0x0000,0x0001,0x1010,0x2410]) or (data[-1]!=0x0006 and data[-1]!=0x000E):
                            #print 'TRY#%s, FindCROCEFEBs, %s:%s: Error3 ReadAllRegisters3=%s, should be [0x0000,0x0000,0x0001,0x1010,0x2410,0x0006/E]'\
                            #    %(itry,theCROCE.Description(),theCROCEChannelE.Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data])
                            fails=fails+1
                        #read received message and check it
                        word0Length=theCROCEChannelE.ReadReceiveMemory(0)
                        word1Status=theCROCEChannelE.ReadReceiveMemory(2)
                        word2RcvData=theCROCEChannelE.ReadReceiveMemory(4)
                        if word0Length!=0x0006 and word0Length!=0x000E:
                            #print 'TRY#%s, FindCROCEFEBs, %s:%s: Error4 RcvMemLengthBytes=%s, should be 0x0006 or 0x000E'\
                            #    %(itry,theCROCE.Description(),theCROCEChannelE.Description(),word0Length)
                            fails=fails+1
                        if word1Status!=0x1010:
                            #print 'TRY#%s, FindCROCEFEBs, %s:%s: Error5 RcvMemStatus=%s, should be 0x1010'\
                            #    %(itry,theCROCE.Description(),theCROCEChannelE.Description(),word1Status)
                            fails=fails+1
                        if word0Length==0x000E and word2RcvData==(sndmsg[0] | 0x8000):
                            if fails==0:
                                theCROCEChannelE.FEBs.append(febAddr) #FEB found at address febAddr
                                break
                        elif word0Length==0x0006 and word2RcvData==sndmsg[0]:
                            fails=fails+1 #NO FEB found at address febAddr
                        else:
                            fails=fails+1 #The received data is corupted...
                        #print '%s:%s febAddr=%s, TRY#%s, fail=%s'%(theCROCE.Description(),theCROCEChannelE.Description(),febAddr,itry,fails)
                FEBs.append('FEB %s %s %s'%(theCROCE.Description(),theCROCEChannelE.Description(),theCROCEChannelE.FEBs))
                theCROCEChannelE.WriteConfiguration(len(theCROCEChannelE.FEBs))
                #special requirement for CROCE in TRiggered/Sequencer mode -> all FEBs address must be consecutive, starting with 1
                cosecutiveTestResult=True
                for i in range(len(theCROCEChannelE.FEBs)):
                    if theCROCEChannelE.FEBs[i]!=i+1:
                        cosecutiveTestResult=False
                if cosecutiveTestResult==False: 
                    print '%s:%s Error FEBs address must be consecutive, starting with 1, found FEBs=%s'\
                        %(theCROCE.Description(),theCROCEChannelE.Description(),theCROCEChannelE.FEBs)
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
        for theCROCE in self.vmeCROCEs:
            f.write('%s:%s\n'%(theCROCE.Description(), theCROCE.GetWRRegValues()))
        for theCROCE in self.vmeCROCEs:
            for theCROCEChannelE in theCROCE.Channels():
                for febAddress in theCROCEChannelE.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    f.write('%s:%s\n'%(theFEB.FPGADescription(theCROCEChannelE, theCROCE, theType='CROCE'), \
                        [hex(val)[2:].rjust(2,'0') for val in theFEB.FPGARead(theCROCEChannelE, theType='CROCE')]))
        for theCROCE in self.vmeCROCEs:   
            for theCROCEChannelE in theCROCE.Channels():
                for febAddress in theCROCEChannelE.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    for theTRIPIndex in range(SC_MainObjects.Frame.NTRIPs):
                        rcvMessageData=theFEB.TRIPRead(theCROCEChannelE, theTRIPIndex, theType='CROCE')
                        pRegs = theFEB.ParseMessageToTRIPRegsPhysical(rcvMessageData, theTRIPIndex)
                        f.write('%s:%s\n'%(theFEB.TRIPDescription(theTRIPIndex, theCROCEChannelE, theCROCE, theType='CROCE'), \
                            [hex(val)[2:].rjust(3,'0') for val in pRegs]))
        f.close()

    def HWcfgFileLoad(self, fullpathname, theframe=None):
        '''Read a configuration file and write it into the current hardware'''
        fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[];fileCROCEs=[];fileFPGAEs=[];fileTRIPEs=[]
        f=open(fullpathname,'r')
        for line in f:
            lineList = line.split(':')
            if len(lineList)!=3: raise Exception('Wrong format in line %s wrong number of ":" characters'%line)
            # Configure CRIMs
            if lineList[0]==SC_Util.VMEdevTypes.CRIM:
                if len(lineList[2])!=321: raise Exception('Wrong format in line %s wrong data field length <> 321'%line)
                if SC_MainObjects.FindVMEdev(self.vmeCRIMs, int(lineList[1])<<16)==None:
                    raise Exception('Load ERROR: CRIM:%s not present in current configuration'%lineList[1])
                for i in range(16):
                    addr=str(lineList[2][3+i*20:9+i*20])
                    data=str(lineList[2][13+i*20:17+i*20])
                    self.controller.WriteCycle(int(addr,16), int(data,16))
                fileCRIMs.append(lineList[1])
            # Configure CROCs
            if lineList[0]==SC_Util.VMEdevTypes.CROC:
                if len(lineList[2])!=41: raise Exception('Wrong format in line %s wrong data field length <> 41'%line)
                if SC_MainObjects.FindVMEdev(self.vmeCROCs, int(lineList[1])<<16)==None:
                    raise Exception('Load ERROR: CROC:%s not present in current configuration'%lineList[1])
                for i in range(2):
                    addr=lineList[2][3+i*20:9+i*20]
                    data=lineList[2][13+i*20:17+i*20]
                    self.controller.WriteCycle(int(addr,16), int(data,16))
                fileCROCs.append(lineList[1])
            # Configure CROCEs
            if lineList[0]==SC_Util.VMEdevTypes.CROCE:
                if len(lineList[2])!=67: raise Exception('Wrong format in line %s wrong data field length <> 67'%line)
                if SC_MainObjects.FindVMEdev(self.vmeCROCEs, int(lineList[1])<<24)==None:
                    raise Exception('Load ERROR: CROCE:%s not present in current configuration'%lineList[1])
                for i in range(3):
                    addr=lineList[2][3+i*22:11+i*22]
                    data=lineList[2][15+i*22:19+i*22]
                    self.controller.WriteCycle(int(addr,16), int(data,16), am='A32_U_DATA', dw='D16')
                fileCROCEs.append(lineList[1])
            # Configure FPGAs and FPGAEs
            if lineList[0]==SC_Util.VMEdevTypes.FPGA:
                if len(lineList[2])!=331: raise Exception('Wrong format in line %s wrong data field length <> 331'%line)
                addresses = lineList[1].split(',')
                if len(addresses)!=3: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
                febNumber=int(addresses[0])
                chXNumber=int(addresses[1])
                crocXNumber=int(addresses[2])
                sentMessageData=SC_MainObjects.Frame.NRegsFPGA*[0]
                for i in range(SC_MainObjects.Frame.NRegsFPGA):
                    data=lineList[2][2+i*6:4+i*6]
                    sentMessageData[i]=int(data,16)
                theCROC=SC_MainObjects.FindVMEdev(self.vmeCROCs, crocXNumber<<16)
                theCROCE=SC_MainObjects.FindVMEdev(self.vmeCROCEs, crocXNumber<<24)
                assigned=False
                if (theCROC==None) and (theCROCE==None):
                    raise Exception('Load ERROR: FPGA:%s not present in current configuration'%lineList[1])
                if (theCROC!=None) and (theCROCE!=None):
                    raise Exception('Load ERROR: FPGA:%s unable to assign: CROC and CROCE with same base address=%s'%(lineList[1],crocXNumber))
                if (theCROC!=None) and (chXNumber in [0,1,2,3]) and (febNumber in theCROC.Channels()[chXNumber].FEBs):
                    theCROCXChannelX=theCROC.Channels()[chXNumber]
                    SC_MainObjects.FEB(febNumber).FPGAWrite(theCROCXChannelX, sentMessageData)
                    fileFPGAs.append(lineList[1])
                    assigned=True
                if (theCROCE!=None) and (chXNumber in [0,1,2,3]) and (febNumber in theCROCE.Channels()[chXNumber].FEBs):
                    theCROCXChannelX=theCROCE.Channels()[chXNumber]
                    SC_MainObjects.FEB(febNumber).FPGAWrite(theCROCXChannelX, sentMessageData, 'CROCE')
                    fileFPGAEs.append(lineList[1])
                    assigned=True
                if assigned==False:
                    raise Exception('Load ERROR: FPGA:%s not present in current configuration'%lineList[1])
            # Configure TRIPs and TRIPEs
            if lineList[0]==SC_Util.VMEdevTypes.TRIP:
                if len(lineList[2])!=99: raise Exception('Wrong format in line %s wrong data field length <> 99'%line)
                addresses = lineList[1].split(',')
                if len(addresses)!=4: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
                tripNumber=addresses[0]
                febNumber=int(addresses[1])
                chXNumber=int(addresses[2])
                crocXNumber=int(addresses[3])
                pRegs=SC_MainObjects.Frame.NRegsTRIPPhysical*[0]
                for i in range(SC_MainObjects.Frame.NRegsTRIPPhysical):
                    data=lineList[2][2+i*7:5+i*7]
                    pRegs[i]=int(data,16)
                theCROC=SC_MainObjects.FindVMEdev(self.vmeCROCs, crocXNumber<<16)
                theCROCE=SC_MainObjects.FindVMEdev(self.vmeCROCEs, crocXNumber<<24)
                assigned=False
                if (theCROC==None) and (theCROCE==None):
                    raise Exception('Load ERROR: TRIP:%s not present in current configuration'%lineList[1])
                if (theCROC!=None) and (theCROCE!=None):
                    raise Exception('Load ERROR: TRIP:%s unable to assign: CROC and CROCE with same base address=%s'%(lineList[1],crocXNumber))
                if (theCROC!=None) and (chXNumber in [0,1,2,3]) and (febNumber in theCROC.Channels()[chXNumber].FEBs) and (tripNumber in ['0','1','2','3','4','5','X']):
                    theCROCXChannelX=theCROC.Channels()[chXNumber]
                    theFEB=SC_MainObjects.FEB(febNumber)
                    if tripNumber!='X': sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                        SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                        SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRi[int(tripNumber)])
                    else: sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                        SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                        SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRAll) 
                    sentMessageData = theFEB.ParseTRIPAllRegsPhysicalToMessage(pRegs, SC_MainObjects.Frame.InstrTRIPWrite)
                    sentMessage = sentMessageHeader + sentMessageData
                    SC_MainObjects.WriteSendReceive(sentMessage, SC_MainObjects.Frame.MessageDataLengthTRIPWrite,
                        theFEB.Address, SC_MainObjects.Frame.DeviceTRIP, theCROCXChannelX, appendData=0, dw='D16', useBLT32=True)
                    fileTRIPs.append(lineList[1])
                    assigned=True
                if (theCROCE!=None) and (chXNumber in [0,1,2,3]) and (febNumber in theCROCE.Channels()[chXNumber].FEBs) and (tripNumber in ['0','1','2','3','4','5','X']):
                    theCROCXChannelX=theCROCE.Channels()[chXNumber]
                    theFEB=SC_MainObjects.FEB(febNumber)
                    if tripNumber!='X': sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                        SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                        SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRi[int(tripNumber)])
                    else: sentMessageHeader = SC_MainObjects.Frame().MakeHeader(
                        SC_MainObjects.Frame.DirectionM2S, SC_MainObjects.Frame.BroadcastNone, theFEB.Address,
                        SC_MainObjects.Frame.DeviceTRIP, SC_MainObjects.Frame.FuncTRIPWRAll) 
                    sentMessageData = theFEB.ParseTRIPAllRegsPhysicalToMessage(pRegs, SC_MainObjects.Frame.InstrTRIPWrite)
                    sentMessage = sentMessageHeader + sentMessageData
                    SC_MainObjects.WriteSendReceiveCROCE(sentMessage, SC_MainObjects.Frame.MessageDataLengthTRIPWrite,
                        theFEB.Address, SC_MainObjects.Frame.DeviceTRIP, theCROCXChannelX, appendData=0, dw='D16', useBLT32=True)
                    fileTRIPEs.append(lineList[1])
                    assigned=True
                if assigned==False:
                    raise Exception('Load ERROR: TRIP:%s not present in current configuration'%lineList[1])
            if theframe!=None: theframe.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
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
        for croce in self.vmeCROCEs:
            croceAdr=str((croce.BaseAddress()&0xFF000000)>>24)
            if not(croceAdr in fileCROCEs): matchError.append('CROCE:'+croceAdr)
            for che in croce.Channels():
                for feb in che.FEBs:
                    fpga='%s,%s,%s'%(feb, che.Number(), croceAdr)
                    if not(fpga in fileFPGAEs): matchError.append('FPGA:'+fpga)
                    if not('X,%s'%fpga in fileTRIPEs):
                        for i in range(6):
                            if not('%s,%s'%(i,fpga) in fileTRIPEs): matchError.append('TRIP:'+'%s,%s'%(i,fpga))
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
        #then check for NOT YET IMPLEMENTED settings...
        self.DIGCheckNotSupportedSettings(thisDIG)
        self.controller.dataWidth=prevDataWidth
        return flags, lines
    def DIGCheckNotSupportedSettings(self, thisDIG): 
        ZeroSuppressionAlgorithm=(self.controller.ReadCycle(thisDIG.BaseAddress()+0x8000) & 0x000F0000) >> 16
        if ZeroSuppressionAlgorithm != 0: raise Exception('ZeroSuppressionAlgorithm=%s NOT yet implemented'%(ZeroSuppressionAlgorithm))




def DAQReadRcvMem(theCROCXDescription, theCROCXChannelX, theType):
    #print 'inside SC_MainMethods: DAQReadRcvMem'
    source='%s:%s'%(theCROCXDescription, theCROCXChannelX.Description())
    if theType=='CROC':
        rcvmem=theCROCXChannelX.ReadFullDPMBLT()
    if theType=='CROCE':
        rcvmem=theCROCXChannelX.ReadFullDPMBLT()
    return [source, rcvmem]
def DAQSpitRcvmemInFrames(rcvmem, theType):
    #print 'inside SC_MainMethods: DAQSpitRcvmemInFrames: rcvmem=%s'%rcvmem
    frms=[]
    if theType=='CROC':
        for iCrocjChRcvMem in rcvmem:
            k=0
            source=iCrocjChRcvMem[0]
            while (k+1<len(iCrocjChRcvMem[1])):
                frmlength=(iCrocjChRcvMem[1][k+1]<<8)+(iCrocjChRcvMem[1][k])
                if k+frmlength<=len(iCrocjChRcvMem[1]):
                    frm=[source, iCrocjChRcvMem[1][k+2:k+frmlength]]
                    frms.append(frm)
                k=k+frmlength
    if theType=='CROCE':
        for iCrocjChRcvMem in rcvmem:
            ifrm=0
            k=0
            source=iCrocjChRcvMem[0]
            while (k+3<len(iCrocjChRcvMem[1])):
                frmlength=(iCrocjChRcvMem[1][k]<<8)+(iCrocjChRcvMem[1][k+1])
                frmstatus=(iCrocjChRcvMem[1][k+2]<<8)+(iCrocjChRcvMem[1][k+3])
##                print 'inside DAQSpitRcvmemInFrames: frmstatus=%s'%hex(frmstatus)
##                if ifrm==0 and frmstatus!=0x5811: frmsource=source+':FRMSTATUSERROR'
##                elif ifrm==intermediate and frmstatus!=0x5810: frmsource=source+':FRMSTATUSERROR'
##                elif ifrm==last_frame and frmstatus!=0x5410: frmsource=source+':FRMSTATUSERROR'
                if k+frmlength<=len(iCrocjChRcvMem[1]):
                    frm=[source, iCrocjChRcvMem[1][k+4:k+frmlength]]
                    frms.append(frm)
                k=k+frmlength 
    return frms
def DAQReadRcvMemory(iEvent, theCROCX, theCROCXChannelX, theType, theCROCXs, theReadType, theWriteType, theWFile, theFrame):
    #print 'inside SC_MainMethods: DAQReadRcvMemory'
    rcvmem=[]
    if theReadType==0 or theReadType==1:    # RO one FEB | RO one CH
        rcvmem.append(DAQReadRcvMem(theCROCX.Description(), theCROCXChannelX, theType))
        #theFrame.SetStatusText('%s %s...done'%(theCROCX.Description(), theCROCXChannelX.Description()), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            rcvmem.append(DAQReadRcvMem(theCROCX.Description(), theCHX, theType))
            #theFrame.SetStatusText('%s %s...done'%(theCROCX.Description(), theCHX.Description()), 0)          
    elif theReadType==3:                    # RO all CTRLs
        for theCTRLX in theCROCXs:
            for theCHX in theCTRLX.Channels():
                rcvmem.append(DAQReadRcvMem(theCTRLX.Description(), theCHX, theType))
                #theFrame.SetStatusText('%s %s...done'%(theCTRLX.Description(), theCHX.Description()), 0)
    frms=DAQSpitRcvmemInFrames(rcvmem, theType)
    DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, theType)
def DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, theType):
    #print 'inside SC_MainMethods: DAQReadRcvMemReportFrames'
    #print 'frms:%s'%frms   
    for frm in frms:
        #print 'frm:%s'%frm
        #print '%05d %s %s length=%sbytes'%(iEvent,frm[0],''.join([hex(d)[2:].rjust(2,'0') for d in frm[1]]),len(frm[1]))
        #theFrame.fe.daq.display.AppendText('\nfrm:%s'%frm)
        #theFrame.fe.daq.display.AppendText('\n%05d %s %s length=%sbytes'%(iEvent,frm[0],''.join([hex(d)[2:].rjust(2,'0') for d in frm[1]]),len(frm[1])))
        if (theType=='CROC'  and (frm[1][1]&0xF0==0x20 and len(frm[1])==64)) or \
           (theType=='CROCE' and (frm[1][1]&0xF0==0x20 and len(frm[1])==64)):       #FPGA Device Register Frame (read or write)     
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FPGA:%s:FPGAREG:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FPGA:%s:FPGAREG:%s:HEADERERROR'%(febAddress,direction)
            DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and ((frm[1][1]&0xF0==0x10 and len(frm[1])==630) or \
                                  (frm[1][1]&0xF0==0x10 and len(frm[1])==734))) or \
             (theType=='CROCE' and ((frm[1][1]&0xF0==0x10 and len(frm[1])==630) or \
                                  (frm[1][1]&0xF0==0x10 and len(frm[1])==734))):    #Trip Device Frame Read=630, Write=734
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FPGA:%s:TRIPPRG:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FPGA:%s:TRIPPRG:%s:HEADERERROR'%(febAddress,direction)
            DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and (frm[1][1]&0xF0==0x30 and len(frm[1])==587)) or \
             (theType=='CROCE' and (frm[1][1]&0xF0==0x30 and len(frm[1])==588)):    #BRAM ReadTrip Device Frame
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FPGA:%s:ADCTRIP:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FPGA:%s:ADCTRIP:%s:HEADERERROR'%(febAddress,direction)
            #DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
            theFEB=SC_MainObjects.FEB(febAddress)
            triphits=theFEB.DecodeBRAMTrips(frm[1][9:], frm[0], '?')
            #theFrame.fe.daq.display.AppendText('\ntriphits=%s'%(triphits))
            DAQBRAMReportTrip(iEvent, triphits, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and (frm[1][1]&0xF0==0x30 and len(frm[1])==441)) or \
             (theType=='CROCE' and (frm[1][1]&0xF0==0x30 and len(frm[1])==442)):    #BRAM ReadHit Device Frame
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FPGA:%s:ADCHITS:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FPGA:%s:ADCHITS:%s:HEADERERROR'%(febAddress,direction)
            #DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
            theFEB=SC_MainObjects.FEB(febAddress)
            hittrips=theFEB.DecodeBRAMHits(frm[1][9:], frm[0], str(adchitnumber))
            #theFrame.fe.daq.display.AppendText('\nhittrips=%s'%(hittrips))
            DAQBRAMReportHit(iEvent, hittrips, theWriteType, theWFile, theFrame)
            adchitnumber=adchitnumber+1                     #increment Hit# after each Hit frame
        elif (theType=='CROC'  and (frm[1][1]&0xF0==0x30 and len(frm[1])%80==13)) or \
             (theType=='CROCE' and (frm[1][1]&0xF0==0x30 and len(frm[1])%80==14)):  #BRAM ReadDiscrim Device Frame
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FPGA:%s:DISCRIM:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FPGA:%s:DISCRIM:%s:HEADERERROR'%(febAddress,direction)
            #DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
            theFEB=SC_MainObjects.FEB(febAddress)
            discrims=theFEB.DecodeBRAMDiscrims(frm[1][9:], frm[0])
            #theFrame.fe.daq.display.AppendText('\ndiscrims=%s'%(discrims))
            DAQBRAMReportDiscrim(iEvent, discrims, theWriteType, theWFile, theFrame)
            adchitnumber=0                                  #reset Hit# after each Discrim frame
        else:
            frm[0]=frm[0]+':UNKNOWN'
            #DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
def BRAMReadDiscrim(theCROCXDescription, theCROCXChannelX, theFEB, theType):
    rcvMessageData=theFEB.BRAMReadDiscrim(theCROCXChannelX, theType)
    source='%s:%s:%s:%s'%(theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FPGA, theFEB.Address)
    return theFEB.DecodeBRAMDiscrims(rcvMessageData, source)
def BRAMReadTrip(theCROCXDescription, theCROCXChannelX, theFEB, index, theType):
    rcvMessageData=theFEB.BRAMReadTrip(theCROCXChannelX, index, theType)
    source='%s:%s:%s:%s'%(theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FPGA, theFEB.Address)
    return theFEB.DecodeBRAMTrips(rcvMessageData, source, index)
def BRAMReadHit(theCROCXDescription, theCROCXChannelX, theFEB, index, theType):
    rcvMessageData=theFEB.BRAMReadHit(theCROCXChannelX, index, theType)
    source='%s:%s:%s:%s'%(theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FPGA, theFEB.Address)
    return theFEB.DecodeBRAMHits(rcvMessageData, source, index)
def OpenGate(theCTRL, theReadType, theCTRLs):
    if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
        theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])
    elif theReadType==3:                                        # RO all CTRLs          vmeCROCXs
        for theCTRL in theCTRLs:
            theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])            
def DAQBRAMReadDiscrim(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, noNumber, theCROCXs, theReadType, theWriteType, theWFile, theFrame):
    discrims=[]
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        discrims.extend(BRAMReadDiscrim(theCROCX.Description(), theCROCXChannelX, theFEB, theType))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            discrims.extend(BRAMReadDiscrim(theCROCX.Description(), theCROCXChannelX, theFEB, theType))           
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                discrims.extend(BRAMReadDiscrim(theCROCX.Description(), theCHX, theFEB, theType))           
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs
        for theCTRLX in theCROCXs:
            for theCHX in theCTRLX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    discrims.extend(BRAMReadDiscrim(theCTRLX.Description(), theCHX, theFEB, theType))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCTRLX, theType), 0)
    DAQBRAMReportDiscrim(iEvent, discrims, theWriteType, theWFile, theFrame)
def DAQBRAMReportDiscrim(iEvent, discrims, theWriteType, theWFile, theFrame):
    if theWriteType==0:                     # display
        for trip in discrims:
            for hit in trip:
                theFrame.fe.daq.display.AppendText('\n%05d %s %010d %s'%(iEvent,hit[0],hit[1],' '.join(['%05.2f'%d for d in hit[2]])))
            #if trip==[]: theFrame.fe.daq.display.AppendText('\n%05d There are NO discriminators'%(iEvent))
    elif theWriteType==1:                   # file
        for trip in discrims:
            for hit in trip:
                theWFile.write('\n%05d %s %010d %s'%(iEvent,hit[0],hit[1],' '.join(['%05.2f'%d for d in hit[2]])))
            #if trip==[]: theWFile.write('\n%05d  There are NO discriminators'%(iEvent))
    else:                                   # both
        for trip in discrims:
            for hit in trip:
                theFrame.fe.daq.display.AppendText('\n%05d %s %010d %s'%(iEvent,hit[0],hit[1],' '.join(['%05.2f'%d for d in hit[2]])))
                theWFile.write('\n%05d %s %010d %s'%(iEvent,hit[0],hit[1],' '.join(['%05.2f'%d for d in hit[2]])))
            #if trip==[]:
            #    theFrame.fe.daq.display.AppendText('\n%05d There are NO discriminators'%(iEvent))
            #    theWFile.write('\n%05d  There are NO discriminators'%(iEvent))
def DAQBRAMReadTrip(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, tripNumber, theCROCXs, theReadType, theWriteType, theWFile, theFrame):
    triphits=[]
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        if tripNumber==-1:                  # all Trips
            for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                triphits.extend(BRAMReadTrip(theCROCX.Description(), theCROCXChannelX, theFEB, tripIndex, theType))
        else:                               # one Trip
            triphits.extend(BRAMReadTrip(theCROCX.Description(), theCROCXChannelX, theFEB, tripNumber, theType))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            if tripNumber==-1:
                for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                    triphits.extend(BRAMReadTrip(theCROCX.Description(), theCROCXChannelX, theFEB, tripIndex, theType))
            else:
                triphits.extend(BRAMReadTrip(theCROCX.Description(), theCROCXChannelX, theFEB, tripNumber, theType))
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                if tripNumber==-1:
                    for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                        triphits.extend(BRAMReadTrip(theCROCX.Description(), theCHX, theFEB, tripIndex, theType))
                else:
                    triphits.extend(BRAMReadTrip(theCROCX.Description(), theCHX, theFEB, tripNumber, theType))
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs
        for theCTRLX in theCROCXs:
            for theCHX in theCTRLX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if tripNumber==-1:
                        for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                            triphits.extend(BRAMReadTrip(theCTRLX.Description(), theCHX, theFEB, tripIndex, theType))
                    else:
                        triphits.extend(BRAMReadTrip(theCTRLX.Description(), theCHX, theFEB, tripNumber, theType))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCTRLX, theType), 0)
    DAQBRAMReportTrip(iEvent, triphits, theWriteType, theWFile, theFrame)   
def DAQBRAMReportTrip(iEvent, triphits, theWriteType, theWFile, theFrame):    
    if theWriteType==0:                     # display
        for hit in triphits:
            theFrame.fe.daq.display.AppendText('\n%05d %s %s'%(iEvent,hit[0],' '.join(['%04d'%d for d in hit[1]])))
    elif theWriteType==1:                   # file
        for hit in triphits:
            theWFile.write('\n%05d %s %s'%(iEvent,hit[0],' '.join(['%04d'%d for d in hit[1]])))
    else:                                   # both
        for hit in triphits:
            theFrame.fe.daq.display.AppendText('\n%05d %s %s'%(iEvent,hit[0],' '.join(['%04d'%d for d in hit[1]])))
            theWFile.write('\n%05d %s %s'%(iEvent,hit[0],' '.join(['%04d'%d for d in hit[1]])))
def DAQBRAMReadHit(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, hitNumber, theCROCXs, theReadType, theWriteType, theWFile, theFrame):
    hittrips=[]
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        if hitNumber==-1:                   # all Hits
            for hitIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadHitx)):
                hittrips.extend(BRAMReadHit(theCROCX.Description(), theCROCXChannelX, theFEB, hitIndex, theType))
        else:                               # one Hit
            hittrips.extend(BRAMReadHit(theCROCX.Description(), theCROCXChannelX, theFEB, hitNumber, theType))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            if hitNumber==-1:
                for hitIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadHitx)):
                    hittrips.extend(BRAMReadHit(theCROCX.Description(), theCROCXChannelX, theFEB, hitIndex, theType))
            else: 
                hittrips.extend(BRAMReadHit(theCROCX.Description(), theCROCXChannelX, theFEB, hitNumber, theType))
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                if hitNumber==-1:
                    for hitIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadHitx)):
                        hittrips.extend(BRAMReadHit(theCROCX.Description(), theCHX, theFEB, hitIndex, theType))
                else: 
                    hittrips.extend(BRAMReadHit(theCROCX.Description(), theCHX, theFEB, hitNumber, theType))
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs
        for theCTRLX in theCROCXs:
            for theCHX in theCTRLX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if hitNumber==-1:
                        for hitIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadHitx)):
                            hittrips.extend(BRAMReadHit(theCTRLX.Description(), theCHX, theFEB, hitIndex, theType))
                    else: 
                        hittrips.extend(BRAMReadHit(theCTRLX.Description(), theCHX, theFEB, hitNumber, theType))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCTRLX, theType), 0)         
    DAQBRAMReportHit(iEvent, hittrips, theWriteType, theWFile, theFrame)
def DAQBRAMReportHit(iEvent, hittrips, theWriteType, theWFile, theFrame):
    if theWriteType==0:                     # display
        for trip in hittrips:
            theFrame.fe.daq.display.AppendText('\n%05d %s %s'%(iEvent,trip[0],' '.join(['%04d'%d for d in trip[1]])))
    elif theWriteType==1:                   # file
        for trip in hittrips:
            theWFile.write('\n%05d %s %s'%(iEvent,trip[0],' '.join(['%04d'%d for d in trip[1]])))
    else:                                   # both
        for trip in hittrips:
            theFrame.fe.daq.display.AppendText('\n%05d %s %s'%(iEvent,trip[0],' '.join(['%04d'%d for d in trip[1]])))
            theWFile.write('\n%05d %s %s'%(iEvent,trip[0],' '.join(['%04d'%d for d in trip[1]])))
def DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame):
    theText=str('\n%05d %s %s length=%sbytes'%(iEvent,frm[0],''.join([hex(d)[2:].rjust(2,'0') for d in frm[1]]),len(frm[1])))
    if theWriteType==0:                     # display
        theFrame.fe.daq.display.AppendText(theText)
    elif theWriteType==1:                   # file
        theWFile.write(theText)
    else:                                   # both
        theFrame.fe.daq.display.AppendText(theText)
        theWFile.write(theText)
def workerDAQSimple(nEvents, theLock, theStopEvent, theCTRLChannel, theCTRL, theCTRLs, theFrame, theReadType, theWriteType, theWFile):
    theLock.acquire()
    iEvent=0
    theFrame.SetStatusText('workerDAQSimple, nEvents=%d'%nEvents, 0)
    theFrame.SetStatusText('', 1)
    tt1=time.time()
    while iEvent<nEvents:
        if theStopEvent.isSet(): break
        try:
            #send OpenGate to simulate a new event
            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
                theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif theReadType==3:                                        # RO all CTRLs
                for ctrl in theCTRLs:
                    ctrl.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            # gives FEBs time to digitize hits: minimum 300microsecs
            time.sleep(0.001)
            #send SoftwareRDFE signal
            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
                theCTRL.SendSoftwareRDFE()
            elif theReadType==3:                                        # RO all CTRLs
                for ctrl in theCTRLs:
                    ctrl.SendSoftwareRDFE()
            #pooling RDFE done
            if theReadType==0 or theReadType==1:                        # RO one FEB or one CH
                for timeout in range(100):
                    if theCTRLChannel.ReadRDFECounter()==iEvent+1:
                        break
            elif theReadType==2:                                        # RO one CTRL
                for ich in range(4):
                    for timeout in range(100):
                        if theCTRL.Channels()[ich].ReadRDFECounter()==iEvent+1:
                            break
            elif theReadType==3:                                        # RO all CTRLs
                for ctrl in theCTRLs:
                    for ich in range(4):
                        for timeout in range(100):
                            if ctrl.Channels()[ich].ReadRDFECounter()==iEvent+1:
                                break
            #readout data...
            rcvmem=[]
            if theReadType==0 or theReadType==1:                        # RO one FEB or RO one CH
                rcvmem.append(['%s:%s'%(theCTRL.Description(), theCTRLChannel.Description()), theCTRLChannel.ReadFullDPMBLT()])
            elif theReadType==2:                                        # RO one CTRL
                for ich in range(4):
                    rcvmem.append(['%s:%s'%(theCTRL.Description(), theCTRL.Channels()[ich].Description()), theCTRL.Channels()[ich].ReadFullDPMBLT()])         
            elif theReadType==3:                                        # RO all CTRLs
                for ctrl in theCTRLs:
                    for ich in range(4):
                        rcvmem.append(['%s:%s'%(ctrl.Description(), ctrl.Channels()[ich].Description()), ctrl.Channels()[ich].ReadFullDPMBLT()])
            frms=DAQSpitRcvmemInFrames(rcvmem, 'CROCE')
            DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, 'CROCE')
            if iEvent!=0 and iEvent%10==0: theFrame.SetStatusText('Event=%d done'%(iEvent), 0)
        except:
            msg = 'EXCEPTION: iEvent=%d, %s, %s'%(iEvent, str(sys.exc_info()[0]), str(sys.exc_info()[1]))
            print msg
            theFrame.SetStatusText(msg, 1)
            if theWFile!=None: theWFile.write('\n%s'%(msg))
        iEvent=iEvent+1
    tt2=time.time()
    if theStopEvent.isSet():
        msg='FORCED to EXIT at iEvent=%d, elapsed time = %f'%(iEvent, tt2-tt1)
    else:
      msg='DONE: nEvents=%d, elapsed time = %f'%(nEvents, tt2-tt1)
    print msg
    theFrame.SetStatusText(msg, 1)
    if theWFile!=None:
        theWFile.write('\n%s'%(msg))
        theWFile.flush()
    theLock.release()

    
