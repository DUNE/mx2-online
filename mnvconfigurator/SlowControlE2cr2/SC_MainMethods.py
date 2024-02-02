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
        try:
            self.controller = CAENVMEwrapper.Controller()
            self.controller.Init(boardType, linkNum, boardNum)
            self.linkNum=linkNum
            self.boardNum=boardNum
            self.vmeCRIMs=[]    
            self.vmeCROCs=[]
            self.vmeCROCEs=[]
            self.vmeDIGs=[]
        except:
            print 'Unable to find V2718 controller with linkNum=%s and boardNum=%s'%(linkNum,boardNum)
            print str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
            self.controller = None
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
    def Description(self):
        return 'V2718:%s'%(self.boardNum)
    
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
        #CROC mapping addr is 1 to 32, register is ResetTestPulse
        addrListCROCs=[]
        crocReg=0xF010
        for i in range(1,32,1):
            data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
            addr=((i<<16)|crocReg) & 0xFFFFFF
            try:
                self.controller.WriteCycle(addr, data, am='A24_U_DATA', dw='D16')
                addrListCROCs.append(i)
                self.controller.WriteCycle(addr, 0, am='A24_U_DATA', dw='D16')
            except: pass
                #print 'FindCROCs : ' + str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
        #now create object lists for CROCs
        self.vmeCROCs=[]
        for addr in addrListCROCs:
            self.vmeCROCs.append(SC_MainObjects.CROC(self.controller, addr<<16))
        return self.vmeCROCs

    def FindCROCEs(self):
        '''Clear the current list of CROC objects and
        return a new (updated) list'''
        #CROCE mapping addr is 1 to 32, register is ResetTestPulse
        addrListCROCEs=[]
        crocEReg=0x0FF010
        for i in range(1,32,1):
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

    def ConfigCROCEsREFE(self, verbose):
        '''Send all valid Encoded Commands and check the TX/RX ChannelE for errors.
            Based on error absence/presence set the EncClkMon_REFE bit in
            ChannelE configuration register to 0/1'''
        theConfigsEncClkMonitorFE=[0x0000,0x0800]   #RE,FE
        for theCROCE in self.vmeCROCEs:
            for refe in range(0,2):                 #0==RE, 1==FE
                fails=[0,0,0,0]
                if refe==0:
                    for iche in range(4):
                        theCROCE.Channels()[iche].WriteConfiguration(theConfigsEncClkMonitorFE[0])                
                for itry in range(50):              #repeat the test 10 times
                    for fcmd in SC_Util.FastCmds:
                        if fcmd=='ResetFPGA':
                            pass
                        else:
                            for iche in range(4):
                                theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus'])
                                statusTXRX=theCROCE.Channels()[iche].ReadStatusTXRX()
                                if statusTXRX!=0x2410:
                                    if verbose: print 'iREFE#%s, TRY#%s, fcmd=%s, ConfigCROCEsREFE %s:%s: Error1 after ClearStatus() statusTXRX=0x%s, should be 0x2410'\
                                        %(refe,itry,fcmd.ljust(12,' '),theCROCE.Description(),theCROCE.Channels()[iche].Description(),
                                          hex(statusTXRX)[2:].rjust(4,'0'))
                                    fails[iche]=fails[iche]+1
                            theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
                            for iche in range(4):
                                statusTXRX=theCROCE.Channels()[iche].ReadStatusTXRX()
                                if statusTXRX!=0x2570:
                                    if verbose: print 'iREFE#%s, TRY#%s, fcmd=%s, ConfigCROCEsREFE %s:%s: Error2 after SendFastCommand() statusTXRX=0x%s, should be 0x2570'\
                                        %(refe,itry,fcmd.ljust(12,' '),theCROCE.Description(),theCROCE.Channels()[iche].Description(),
                                          hex(statusTXRX)[2:].rjust(4,'0'))
                                    fails[iche]=fails[iche]+1
                if fails==[0,0,0,0]:
                    print '******** ConfigCROCEsREFE %s: DONE: CH0=0x%s, CH1=0x%s, CH2=0x%s, CH3=0x%s ********'\
                        %(theCROCE.Description(),
                          hex(theCROCE.Channels()[0].ReadConfiguration())[2:].rjust(4,'0'),
                          hex(theCROCE.Channels()[1].ReadConfiguration())[2:].rjust(4,'0'),
                          hex(theCROCE.Channels()[2].ReadConfiguration())[2:].rjust(4,'0'),
                          hex(theCROCE.Channels()[3].ReadConfiguration())[2:].rjust(4,'0'))
                    break #breaks to next theCROCE
                if refe==0:
                    for iche in range(4):
                        if fails[iche]!=0:
                            theCROCE.Channels()[iche].WriteConfiguration(theConfigsEncClkMonitorFE[1])
                            if verbose: print 'iREFE#%s, ConfigCROCEsREFE %s:%s: found %d errors with RE=0x0000, config changed to FE=0x0x0800: '\
                                %(refe,theCROCE.Description(),theCROCE.Channels()[iche].Description(),fails[iche])
                if refe==1:
                    for iche in range(4):
                        if fails[iche]!=0:
                            print '******** ConfigCROCEsREFE %s:%s: found %d errors with FE=0x0000, unable to set reliable RE/FE ********'\
                                %(theCROCE.Description(),theCROCE.Channels()[iche].Description(),fails[iche])
        return
    
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

    def FindCROCEFEBs(self, theCROCEs, useChRst, verbose):
        '''Clear the current list of FEBs, in each channel, for each CROCE in the given
        list of CROCE object. Return a new (updated) list of FEB addresses, mostly for
        reporting use. The real use is to update the given CROCE instances with the FEBs
        that are currently in the system'''
        #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
        FEBs=[]
        for theCROCE in theCROCEs:
            for theCROCEChannelE in theCROCE.Channels():
                theHeader=theCROCEChannelE.ReadHeaderData()
                for chtry in range(1,3):
                    theCROCEChannelE.FEBs=[]
                    for febAddr in range(1,16):
                        for itry in range(1,5):
                            fails=0
                            #clear status and check registers
                            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            data=theCROCEChannelE.ReadAllRegisters()
                            if data!=[data[0]&0x0DC0,0x0000,0x0000,0x4040,0x2410,0x0000,theHeader]:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error1 ReadAllRegisters=%s, should be [0x%s,0x0000,0x0000,0x4040,0x2410,0x0000,0x%s]'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(), 
                                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                                      hex(data[0]&0x0DC0)[2:].rjust(4,'0'),hex(theHeader)[2:].rjust(4,'0'))
                                fails=fails+1
                            #write message and check registers
                            sndmsg=[febAddr<<8]
                            theCROCEChannelE.WriteSendMemory(sndmsg[0])
                            data=theCROCEChannelE.ReadAllRegisters()
                            if data!=[data[0]&0x0DC0,0x0000,0x0000,0x0040,0x2410,0x0000,theHeader]:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error2 ReadAllRegisters=%s, should be [0x%s,0x0000,0x0000,0x0040,0x2410,0x0006,0x%s]'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                                      hex(data[0]&0x0DC0)[2:].rjust(4,'0'),hex(theHeader)[2:].rjust(4,'0'))
                                fails=fails+1
                            #send message and check registers
                            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendMessage'])
                            data=theCROCEChannelE.ReadAllRegisters()
                            if ((data[:-2]!=[data[0]&0x0DC0,0x0000,0x0001,0x1010,0x2410]) or
                                (data[-2]!=0x000C and data[-2]!=0x0014) or data[-1]!=theHeader):
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error3 ReadAllRegisters=%s, should be [0x%s,0x0000,0x0001,0x1010,0x2410,0x000C/14,0x%s]'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                                      hex(data[0]&0x0DC0)[2:].rjust(4,'0'),hex(theHeader)[2:].rjust(4,'0'))
                                fails=fails+1
                            #read received message and check it. NOTE: v2 header has 10 bytes, March 2013
                            rcvfrmsDataLengthBytes =theCROCEChannelE.ReadReceiveMemory(0)
                            rcvfrmsStatus          =theCROCEChannelE.ReadReceiveMemory(2)
                            rcvfrmsFirmwareDevFunc =theCROCEChannelE.ReadReceiveMemory(4)
                            rcvfrmsSourceID        =theCROCEChannelE.ReadReceiveMemory(6)
                            rcvfrmsDataLengthBytes2=theCROCEChannelE.ReadReceiveMemory(8)
                            rcvfrmsFrameDataWord01 =theCROCEChannelE.ReadReceiveMemory(10)
                            if rcvfrmsDataLengthBytes!=0x000C and rcvfrmsDataLengthBytes!=0x0014:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error4 RcvMemLengthBytes=%s, should be 0x000C or 0x0014'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      rcvfrmsDataLengthBytes)
                                fails=fails+1
                            if rcvfrmsStatus!=0x1010:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error5 RcvMemStatus=0x%s, should be 0x1010'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      hex(rcvfrmsStatus)[2:].rjust(4,'0'))
                                fails=fails+1
                            crateid =(0x1000&theHeader)>>12
                            croceid =(0x0F00&theHeader)>>8
                            febvers =(0x00FF&theHeader)
                            devfunc =0
                            sourceid=(crateid<<14)+(croceid<<9)+(theCROCEChannelE.cheNumber<<7)+(febAddr<<3)
                            if rcvfrmsFirmwareDevFunc!=((febvers<<8)+(devfunc)):
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error6 rcvfrmsFirmwareDevFunc=0x%s, should be 0x%s'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      hex(rcvfrmsFirmwareDevFunc)[2:].rjust(4,'0'),hex((crateid<<14)+(croceid<<9))[2:].rjust(4,'0'))
                                fails=fails+1
                            if rcvfrmsSourceID!=sourceid:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error7 rcvfrmsSourceID=0x%s, should be 0x%s'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      hex(rcvfrmsSourceID)[2:].rjust(4,'0'),hex(sourceid)[2:].rjust(4,'0'))
                                fails=fails+1
                            if rcvfrmsDataLengthBytes!=rcvfrmsDataLengthBytes2:
                                if verbose: print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error8 RcvMemLengthBytes=%s, RcvMemLengthBytes2=%s'\
                                    %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description(),
                                      rcvfrmsDataLengthBytes,rcvfrmsDataLengthBytes2)
                                fails=fails+1
                            if rcvfrmsDataLengthBytes==0x0014 and rcvfrmsFrameDataWord01==(sndmsg[0] | 0x8000):
                                if fails==0:
                                    theCROCEChannelE.FEBs.append(febAddr) #FEB found at address febAddr
                                    break
                            elif rcvfrmsDataLengthBytes==0x000C and rcvfrmsFrameDataWord01==sndmsg[0]:
                                fails=fails+1 #NO FEB found at address febAddr
                            else:
                                fails=fails+1 #The received data is corupted...
                            #print '%s:%s febAddr=%s, TRY#%s, fail=%s'%(theCROCE.Description(),theCROCEChannelE.Description(),febAddr,itry,fails)
                    if theCROCEChannelE.FEBs!=[]:
                        break
                    else:
                        if useChRst==True:
                            #reset theCROCEChannelE and try again to find FEBs
                            if verbose:
                                print 'TRY1#%s, TRY2#%s, FindCROCEFEBs %s:%s: Error9 NO FEBs, reset this channel and try again'\
                                %(chtry,itry,theCROCE.Description(),theCROCEChannelE.Description())
                            theCROCE.WriteRSTTP(0x0100)
                            theCROCEChannelEConfiguration=theCROCEChannelE.ReadConfiguration()
                            theCROCEChannelE.WriteConfiguration(0x0010 | theCROCEChannelEConfiguration)
                            theCROCE.SendRSTOnly()
                            time.sleep(3)
                            theCROCE.WriteRSTTP(0x0000)
                            theCROCEChannelE.WriteConfiguration(theCROCEChannelEConfiguration)
                FEBs.append('FEB %s %s %s'%(theCROCE.Description(),theCROCEChannelE.Description(),theCROCEChannelE.FEBs)) 
                theCROCEChannelE.WriteConfiguration((len(theCROCEChannelE.FEBs) & 0xF) | (theCROCEChannelE.ReadConfiguration() & 0xFFF0))
                #special requirement for CROCE in TRiggered/Sequencer mode -> all FEBs address must be consecutive, starting with 1
                cosecutiveTestResult=True
                for i in range(len(theCROCEChannelE.FEBs)):
                    if theCROCEChannelE.FEBs[i]!=i+1:
                        cosecutiveTestResult=False
                if cosecutiveTestResult==False: 
                    print '%s:%s Error FEBs address must be consecutive, starting with 1, found FEBs=%s'\
                        %(theCROCE.Description(),theCROCEChannelE.Description(),theCROCEChannelE.FEBs)
        return FEBs

    def HWcfgFileSave(self, f):
        '''Read the current hardware configuration and write it into a file'''
        #update the cofiguration
        for theCRIM in self.vmeCRIMs:
            f.write('%s,%s:%s\n'%(theCRIM.Description(),self.boardNum,theCRIM.GetWRRegValues()))
        #CAUTION: For CROC, the WriteSendReceiveCROC() from SC_MainObjects.py returns (rcvMessageData,[])
        for theCROC in self.vmeCROCs:
            f.write('%s,%s:%s\n'%(theCROC.Description(),self.boardNum,theCROC.GetWRRegValues()))
        for theCROC in self.vmeCROCs:   
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    f.write('%s:%s\n'%(theFEB.FPGADescription(theCROCChannel, theCROC, theType='CROC'), \
                        [hex(val)[2:].rjust(2,'0') for val in theFEB.FPGARead(theCROCChannel, theType='CROC')[0]]))
        for theCROC in self.vmeCROCs:   
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    for theTRIPIndex in range(SC_MainObjects.Frame.NTRIPs):
                        rcvMessageData=theFEB.TRIPRead(theCROCChannel, theTRIPIndex, theType='CROC')[0]
                        pRegs = theFEB.ParseMessageToTRIPRegsPhysical(rcvMessageData, theTRIPIndex)
                        f.write('%s:%s\n'%(theFEB.TRIPDescription(theTRIPIndex, theCROCChannel, theCROC, theType='CROC'), \
                            [hex(val)[2:].rjust(3,'0') for val in pRegs]))
        #CAUTION: For CROCE2, the WriteSendReceiveCROCE() from SC_MainObjects.py returns (rcvMessageData,rcvMFH_10bytes)
        for theCROCE in self.vmeCROCEs:
            f.write('%s,%s:%s\n'%(theCROCE.Description(),self.boardNum,theCROCE.GetWRRegValues()))
        for theCROCE in self.vmeCROCEs:
            for theCROCEChannelE in theCROCE.Channels():
                f.write('%s,%s,%s:%s\n'%(theCROCEChannelE.Description(),theCROCE.Description().split(':')[1],self.boardNum,theCROCEChannelE.GetWRRegValues()))
                for febAddress in theCROCEChannelE.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    f.write('%s:%s\n'%(theFEB.FPGADescription(theCROCEChannelE, theCROCE, theType='CROCE'), \
                        [hex(val)[2:].rjust(2,'0') for val in theFEB.FPGARead(theCROCEChannelE, theType='CROCE')[0]])) 
        for theCROCE in self.vmeCROCEs:   
            for theCROCEChannelE in theCROCE.Channels():
                for febAddress in theCROCEChannelE.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    for theTRIPIndex in range(SC_MainObjects.Frame.NTRIPs):
                        rcvMessageData=theFEB.TRIPRead(theCROCEChannelE, theTRIPIndex, theType='CROCE')[0] 
                        pRegs = theFEB.ParseMessageToTRIPRegsPhysical(rcvMessageData, theTRIPIndex)
                        f.write('%s:%s\n'%(theFEB.TRIPDescription(theTRIPIndex, theCROCEChannelE, theCROCE, theType='CROCE'), \
                            [hex(val)[2:].rjust(3,'0') for val in pRegs]))

    def HWcfgFileLoad(self, f, theframe=None, scsNumbers=1):
        '''Read a configuration file and write it into the current hardware'''
        fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[];fileCROCEs=[];fileFPGAEs=[];fileTRIPEs=[]
        for line in f:
            lineList = line.split(':')
            if len(lineList)!=3:
                raise Exception('Load ERROR: Wrong format in line %s wrong number of ":" characters'%line)
            addresses = lineList[1].split(',')
            if int(addresses[-1])==self.boardNum:
                # the line contains a device from the current (self) controller
                # Configure CRIMs
                if lineList[0]==SC_Util.VMEdevTypes.CRIM:
                    if len(lineList[2])!=321: raise Exception('Wrong format in line %s wrong data field length <> 321'%line)
                    if SC_MainObjects.FindVMEdev(self.vmeCRIMs, int(addresses[0])<<16)==None:
                        raise Exception('Load ERROR: CRIM:%s not present in current configuration'%lineList[1])
                    for i in range(16):
                        addr=str(lineList[2][3+i*20:9+i*20])
                        data=str(lineList[2][13+i*20:17+i*20])
                        self.controller.WriteCycle(int(addr,16), int(data,16))
                    fileCRIMs.append(lineList[1])
                # Configure CROCs
                if lineList[0]==SC_Util.VMEdevTypes.CROC:
                    if len(lineList[2])!=41: raise Exception('Wrong format in line %s wrong data field length <> 41'%line)
                    if SC_MainObjects.FindVMEdev(self.vmeCROCs, int(addresses[0])<<16)==None:
                        raise Exception('Load ERROR: CROC:%s not present in current configuration'%lineList[1])
                    for i in range(2):
                        addr=lineList[2][3+i*20:9+i*20]
                        data=lineList[2][13+i*20:17+i*20]
                        self.controller.WriteCycle(int(addr,16), int(data,16))
                    fileCROCs.append(lineList[1])
                # Configure CROCEs
                if lineList[0]==SC_Util.VMEdevTypes.CROCE:
                    if len(lineList[2])!=67: raise Exception('Wrong format in line %s wrong data field length <> 67'%line)
                    if SC_MainObjects.FindVMEdev(self.vmeCROCEs, int(addresses[0])<<24)==None:
                        raise Exception('Load ERROR: CROCE:%s not present in current configuration'%lineList[1])
                    for i in range(3):
                        addr=lineList[2][3+i*22:11+i*22]
                        data=lineList[2][15+i*22:19+i*22]
                        self.controller.WriteCycle(int(addr,16), int(data,16), am='A32_U_DATA', dw='D16')
                    fileCROCEs.append(lineList[1])
                # Configure CHEs on CROCEs
                if lineList[0]==SC_Util.VMEdevTypes.CHE:
                    if len(lineList[2])!=45: raise Exception('Wrong format in line %s wrong data field length <> 45'%line)
                    if SC_MainObjects.FindVMEdev(self.vmeCROCEs, int(addresses[1])<<24)==None:
                        raise Exception('Load ERROR: CROCE-CHE:%s not present in current configuration'%lineList[1])
                    for i in range(2):
                        addr=lineList[2][3+i*22:11+i*22]
                        data=lineList[2][15+i*22:19+i*22]
                        self.controller.WriteCycle(int(addr,16), int(data,16), am='A32_U_DATA', dw='D16')                        
                # Configure FPGAs and FPGAEs
                if lineList[0]==SC_Util.VMEdevTypes.FPGA:
                    if len(lineList[2])!=331: raise Exception('Wrong format in line %s wrong data field length <> 331'%line)
                    if len(addresses)!=4: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
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
                        SC_MainObjects.FEB(febNumber).FPGAWrite(theCROCXChannelX, sentMessageData, 'CROC')
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
                    if len(addresses)!=5: raise Exception('Wrong format in line %s wrong number of "," characters'%line)
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
                            theFEB.Address, SC_MainObjects.Frame.DeviceTRIP, theCROCXChannelX, appendData=0, dw='D32', useBLT32=True)
                        fileTRIPEs.append(lineList[1])
                        assigned=True
                    if assigned==False:
                        raise Exception('Load ERROR: TRIP:%s not present in current configuration'%lineList[1])
                # Update theframe.SetStatusText
                if theframe!=None: theframe.SetStatusText('%s:%s...done'%(lineList[0], lineList[1]), 0)
            else:
                if int(addresses[-1])>(scsNumbers-1):
                    raise Exception('Load ERROR: CRATE:%s not present in current configuration'%addresses[-1])
        matchError=[]
        for crim in self.vmeCRIMs:
            crimAddr='%s,%s'%(str((crim.BaseAddress()&0xFF0000)>>16),str(self.boardNum))
            if not(crimAddr in fileCRIMs):
                matchError.append('CRIM:'+crimAddr)
        for croc in self.vmeCROCs:
            crocAddr='%s,%s'%(str((croc.BaseAddress()&0xFF0000)>>16),str(self.boardNum))
            if not(crocAddr in fileCROCs):
                matchError.append('CROC:'+crocAddr)
            for ch in croc.Channels():
                for feb in ch.FEBs:
                    fpgAddr='%s,%s,%s'%(feb,ch.Number(),crocAddr)
                    if not(fpgAddr in fileFPGAs):
                        matchError.append('FPGA:'+fpgAddr)
                    if not('X,%s'%fpgAddr in fileTRIPs):
                        for i in range(6):
                            if not('%s,%s'%(i,fpgAddr) in fileTRIPs):
                                matchError.append('TRIP:'+'%s,%s'%(i,fpgAddr))
        for croce in self.vmeCROCEs:
            croceAddr='%s,%s'%(str((croce.BaseAddress()&0xFF000000)>>24),str(self.boardNum))
            if not(croceAddr in fileCROCEs):
                matchError.append('CROCE:'+croceAddr)
            for che in croce.Channels():
                for feb in che.FEBs:
                    fpgAddr='%s,%s,%s'%(feb,che.Number(),croceAddr)
                    if not(fpgAddr in fileFPGAEs):
                        matchError.append('FPGA:'+fpgAddr)
                    if not('X,%s'%fpgAddr in fileTRIPEs):
                        for i in range(6):
                            if not('%s,%s'%(i,fpgAddr) in fileTRIPEs):
                                matchError.append('TRIP:'+'%s,%s'%(i,fpgAddr))
        return matchError
    
    def HVReadAll(self, devVal):
        '''Read the HV of all FEBs and return a list with those FEBs 
        on which abs(HVActual-HVTarget) > devVal'''
        #return SC_MainObjects.FEB(0).GetAllHVParams(self.vmeCROCs, int(devVal))
        hvCROCs=SC_MainObjects.FEB(0).GetAllHVParams(self.vmeCROCs, 'CROC', int(devVal))
        hvCROCEs=SC_MainObjects.FEB(0).GetAllHVParams(self.vmeCROCEs, 'CROCE', int(devVal))
        return hvCROCs,hvCROCEs
    def HVSetAll(self, setVal):
        '''Set the HVTarget of all FEBs to setVal'''
        SC_MainObjects.FEB(0).SetAllHVTarget(self.vmeCROCs, 'CROC', int(setVal))
        SC_MainObjects.FEB(0).SetAllHVTarget(self.vmeCROCEs, 'CROCE', int(setVal))

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




def DAQReadRcvMem(crateNum, theCROCXDescription, theCROCXChannelX, theType):
    #print 'inside SC_MainMethods: DAQReadRcvMem'
    source='CRATE:%s:%s:%s'%(crateNum, theCROCXDescription, theCROCXChannelX.Description())
    if theType=='CROC':
        rcvmem=theCROCXChannelX.ReadFullDPMBLT()
    if theType=='CROCE':
        rcvmem=theCROCXChannelX.ReadFullDPMBLT()
    return [source, rcvmem]
def DAQSplitRcvmemInFrames(rcvmem, theType):
    #print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: rcvmem=%s'%rcvmem
    frms=[]
    if theType=='CROC':
        for iCrocjChRcvMem in rcvmem:
            k=0
            source=iCrocjChRcvMem[0]
            rcvmem=iCrocjChRcvMem[1]
            while (k+1<len(rcvmem)):
                frmlength=(rcvmem[k+1]<<8)+(rcvmem[k])
                if k+frmlength<=len(rcvmem):
                    frm=[source, rcvmem[k+2:k+frmlength], []]
                    frms.append(frm)
                k=k+frmlength
    if theType=='CROCE':
        for iCrocjChRcvMem in rcvmem:
            source=iCrocjChRcvMem[0]
            rcvmem=iCrocjChRcvMem[1]
            #print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: source=%s'%source
            #print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: length=%d, rcvmem=%s'%(len(rcvmem),[hex(d)[2:].rjust(2,'0') for d in rcvmem])
            k=0
            while (k+19<len(rcvmem)):
                frmMFH_10bytes  =rcvmem[k+0:k+10]
                frmMessageLength=(rcvmem[k+0]<<8)+(rcvmem[k+1])
                frmMessageStatus=(rcvmem[k+2]<<8)+(rcvmem[k+3])
                frmMessageHeader=rcvmem[k+10:k+19]
                frmMessageData  =rcvmem[k+19:k+frmMessageLength]
##                print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: length=%s, frmMFH_10bytes  =%s'%(str(len(frmMFH_10bytes)).rjust(3,'0'),[hex(x)[2:].rjust(2,'0') for x in frmMFH_10bytes])
##                MFH_10bytes_decode(frmMFH_10bytes)
##                print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: length=%s, frmMessageHeader=%s'%(str(len(frmMessageHeader)).rjust(3,'0'),[hex(x)[2:].rjust(2,'0') for x in frmMessageHeader])
##                print 'inside SC_MainMethods: DAQSplitRcvmemInFrames: length=%s, frmMessageData  =%s'%(str(len(frmMessageData)).rjust(3,'0'),[hex(x)[2:].rjust(2,'0') for x in frmMessageData])              
##                if ifrm==0 and frmstatus!=0x5811: frmsource=source+':FRMSTATUSERROR'
##                elif ifrm==intermediate and frmstatus!=0x5810: frmsource=source+':FRMSTATUSERROR'
##                elif ifrm==last_frame and frmstatus!=0x5410: frmsource=source+':FRMSTATUSERROR'
                if k+frmMessageLength<=len(rcvmem):
                    frm=[source, rcvmem[k+10:k+frmMessageLength], frmMFH_10bytes]
                    frms.append(frm)
                k=k+frmMessageLength
    return frms
def MFH_10bytes_decode(mfh):
    print '\tFrameLength    =0x%s'%hex((mfh[0]<<8)+mfh[1])[2:].rjust(2,'0')
    print '\tChannelStatus  =0x%s'%hex((mfh[2]<<8)+mfh[3])[2:].rjust(2,'0')
    print '\tFirmwareVersion=0x%s'%hex(mfh[4])[2:].rjust(2,'0')
    print '\tDeviceFunction =0x%s'%hex(mfh[5])[2:].rjust(2,'0')
    print '\tSourceID       =0x%s,CRATE#=%s,CROCE#=%s,CHANNEL#=%s,FEB#=%s,HIT#=%s'%(
        hex((mfh[6]<<8)+mfh[7])[2:].rjust(2,'0'),(mfh[6]&0x40)>>6,(mfh[6]&0x1E)>>1,(((mfh[6]&0x01)<<1)+((mfh[7]&0x80)>>7)),
        (mfh[7]&0x78)>>3,(((mfh[6]&0x80)>>3)+((mfh[6]&0x20)>>2)+(mfh[7]&0x07)) )
    print '\tFrameLength    =0x%s'%hex((mfh[8]<<8)+mfh[9])[2:].rjust(2,'0')
def DAQReadRcvMemory(iEvent, theCROCX, theCROCXChannelX, theType, theCROCXs, theCROCXsAllCRATEs,
    theReadType, theWriteType, theWFile, theFrame, theDataType23Hits):
    #print 'inside SC_MainMethods: DAQReadRcvMemory'
    rcvmem=[]
    if theReadType==0 or theReadType==1:    # RO one FEB | RO one CH
        rcvmem.append(DAQReadRcvMem(theCROCX.controller.boardNum, theCROCX.Description(), theCROCXChannelX, theType))
        #theFrame.SetStatusText('%s %s...done'%(theCROCX.Description(), theCROCXChannelX.Description()), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            rcvmem.append(DAQReadRcvMem(theCROCX.controller.boardNum, theCROCX.Description(), theCHX, theType))
            #theFrame.SetStatusText('%s %s...done'%(theCROCX.Description(), theCHX.Description()), 0)          
    elif theReadType==3:                    # RO all CTRLs this CRATE
        for theCROCX in theCROCXs:
            for theCHX in theCROCX.Channels():
                rcvmem.append(DAQReadRcvMem(theCROCX.controller.boardNum, theCROCX.Description(), theCHX, theType))
                #theFrame.SetStatusText('%s %s...done'%(theCTRLX.Description(), theCHX.Description()), 0)
    elif theReadType==4:                    # RO all CTRLs all CRATEs
        for theCROCX in theCROCXsAllCRATEs:
            for theCHX in theCROCX.Channels():
                rcvmem.append(DAQReadRcvMem(theCROCX.controller.boardNum, theCROCX.Description(), theCHX, theType))
                #theFrame.SetStatusText('%s %s...done'%(theCTRLX.Description(), theCHX.Description()), 0)
    frms=DAQSplitRcvmemInFrames(rcvmem, theType)
    DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, theType, theDataType23Hits)
def DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, theType, theDataType23Hits):
    #print 'inside SC_MainMethods: DAQReadRcvMemReportFrames'
    #print 'frms:%s'%frms   
    for frm in frms:
        #print 'frm:%s'%frm
        #print '%05d %s %s length=%sbytes'%(iEvent,frm[0],''.join([hex(d)[2:].rjust(2,'0') for d in frm[1]]),len(frm[1]))
        #theFrame.fe.daq.display.AppendText('\nfrm:%s'%frm)
        #theFrame.fe.daq.display.AppendText('\n%05d %s %s length=%sbytes'%(iEvent,frm[0],''.join([hex(d)[2:].rjust(2,'0') for d in frm[1]]),len(frm[1])))
        if (theType=='CROC'  and (frm[1][1]&0xF0==0x20 and len(frm[1])==64)) or \
           (theType=='CROCE' and (frm[1][1]&0xF0==0x20 and len(frm[1])==64)):
            #This is FPGA Device FPGAREG Frame (read or write)     
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FE:%s:FPGAREG:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FE:%s:FPGAREG:%s:HEADERERROR'%(febAddress,direction)
            DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and ((frm[1][1]&0xF0==0x10 and len(frm[1])==630) or \
                                    (frm[1][1]&0xF0==0x10 and len(frm[1])==734))) or \
             (theType=='CROCE' and ((frm[1][1]&0xF0==0x10 and len(frm[1])==630) or \
                                    (frm[1][1]&0xF0==0x10 and len(frm[1])==734))):
            #This is Trip Device TRIPREG Frame Read=630, Write=734
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FE:%s:TRIPPRG:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FE:%s:TRIPPRG:%s:HEADERERROR'%(febAddress,direction)
            DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and theDataType23Hits==False and (frm[1][1]&0xF0==0x30 and len(frm[1])==587)) or \
             (theType=='CROCE' and theDataType23Hits==False and (frm[1][1]&0xF0==0x30 and len(frm[1])==588)) or \
             (theType=='CROCE' and theDataType23Hits==True  and (frm[1][1]&0xF0==0x30 and len(frm[1])==1740)):
            #This is BRAM ReadTrip Device Frame - Read ONLY
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FE:%s:ADCTRIP:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FE:%s:ADCTRIP:%s:HEADERERROR'%(febAddress,direction)
            #DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
            theFEB=SC_MainObjects.FEB(febAddress)
            tripindex='?'
            if theType=='CROCE':
                theDevice=(frm[2][5]&0xF0)>>4               #retrieve device from MFH (10 bytes)
                theFunctn=(frm[2][5]&0x0F)                  #retrieve function from MFH (10 bytes)
                conv_dev3func_to_tripindex=['?','?','?','?','?','?','?','?','0','1','2','3','4','5','?','?']
                if theDevice==3: tripindex=conv_dev3func_to_tripindex[theFunctn]
            triphits=theFEB.DecodeBRAMTrips(frm[1][9:], frm[0], tripindex, theDataType23Hits)
            #theFrame.fe.daq.display.AppendText('\ntriphits=%s'%(triphits))
            DAQBRAMReportTrip(iEvent, triphits, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and theDataType23Hits==False and frm[1][1]&0xF0==0x30 and len(frm[1])==441) or \
             (theType=='CROCE' and theDataType23Hits==False and frm[1][1]&0xF0==0x30 and len(frm[1])==442) or \
             (theType=='CROCE' and theDataType23Hits==True  and (frm[1][1]&0xF0==0x30 or frm[1][1]&0xF0==0x50) and len(frm[1])==444):
            #This is BRAM ReadHit Device Frame - Read ONLY
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FE:%s:ADCHITS:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FE:%s:ADCHITS:%s:HEADERERROR'%(febAddress,direction)
            theFEB=SC_MainObjects.FEB(febAddress)
            hitindex='?'
            if theType=='CROCE':
                theDevice=(frm[2][5]&0xF0)>>4               #retrieve device from MFH (10 bytes)
                theFunctn=(frm[2][5]&0x0F)                  #retrieve function from MFH (10 bytes)
                conv_dev3func_to_hitindex=['?','0','1','2','3','4','5','?','?','?','?','?','?','?','6','7']
                conv_dev5func_to_hitindex=['?','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22']
                if theDevice==3: hitindex=conv_dev3func_to_hitindex[theFunctn]
                if theDevice==5: hitindex=conv_dev5func_to_hitindex[theFunctn]
            hittrips=theFEB.DecodeBRAMHits(frm[1][9:], frm[0], hitindex, theDataType23Hits)
            #theFrame.fe.daq.display.AppendText('\nhittrips=%s'%(hittrips))
            DAQBRAMReportHit(iEvent, hittrips, theWriteType, theWFile, theFrame)
        elif (theType=='CROC'  and (frm[1][1]&0xF0==0x30 and len(frm[1])%80==13)) or \
             (theType=='CROCE' and (frm[1][1]&0xF0==0x30 and len(frm[1])%80==14)):
            #This is BRAM ReadDiscrim Device Frame - Read ONLY
            if frm[1][0]&0x80==0x80: direction='S'          #frame comming from Slave (FEB) 
            else: direction='M'                             #frame comming from Master (CROCChannel) 
            febAddress=frm[1][0]&0x0F                       #retrieve febAddress
            if frm[1][0]&0x70==0x00 and frm[1][1]&0x0F==0x03 and frm[1][2]==0x03: #no frame header errors
                frm[0]=frm[0]+':FE:%s:DISCRIM:%s'%(febAddress,direction)
            else:                                           #frame header errors
                frm[0]=frm[0]+':FE:%s:DISCRIM:%s:HEADERERROR'%(febAddress,direction)
            theFEB=SC_MainObjects.FEB(febAddress)
            discrims=theFEB.DecodeBRAMDiscrims(frm[1][9:], frm[0], theDataType23Hits)
            #theFrame.fe.daq.display.AppendText('\ndiscrims=%s'%(discrims))
            DAQBRAMReportDiscrim(iEvent, discrims, theWriteType, theWFile, theFrame)
        else:
            frm[0]=frm[0]+':UNKNOWN'
            DAQBRAMReportNotDecodedFrame(iEvent, frm, theWriteType, theWFile, theFrame)
def BRAMReadDiscrim(crateNum, theCROCXDescription, theCROCXChannelX, theFEB, theType, theDataType23Hits):
    rcvMessageData,rcvMFH_10bytes=theFEB.BRAMReadDiscrim(theCROCXChannelX, theType)
    source='CRATE:%s:%s:%s:%s:%s'%(crateNum, theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FE, theFEB.Address)
    return theFEB.DecodeBRAMDiscrims(rcvMessageData, source, theDataType23Hits)
def BRAMReadTrip(crateNum, theCROCXDescription, theCROCXChannelX, theFEB, index, theType, theDataType23Hits):
    rcvMessageData,rcvMFH_10bytes=theFEB.BRAMReadTrip(theCROCXChannelX, index, theType, theDataType23Hits)
    source='CRATE:%s:%s:%s:%s:%s'%(crateNum, theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FE, theFEB.Address)
    return theFEB.DecodeBRAMTrips(rcvMessageData, source, index, theDataType23Hits)
def BRAMReadHit(crateNum, theCROCXDescription, theCROCXChannelX, theFEB, index, theType, theDataType23Hits):
    rcvMessageData,rcvMFH_10bytes=theFEB.BRAMReadHit(theCROCXChannelX, index, theType, theDataType23Hits)
    source='CRATE:%s:%s:%s:%s:%s'%(crateNum, theCROCXDescription, theCROCXChannelX.Description(), SC_Util.VMEdevTypes.FE, theFEB.Address)
    return theFEB.DecodeBRAMHits(rcvMessageData, source, index, theDataType23Hits)
def OpenGate(theCTRL, theReadType, theCTRLs):
    if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
        theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])
    elif theReadType==3:                                        # RO all CTRLs          vmeCROCXs
        for theCTRL in theCTRLs:
            theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])            
def DAQBRAMReadDiscrim(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, noNumber, theCROCXs, theCROCXsAllCRATEs,
    theReadType, theWriteType, theWFile, theFrame, theDataType23Hits):
    discrims=[]
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        discrims.extend(BRAMReadDiscrim(theCROCX.controller.boardNum, theCROCX.Description(),
            theCROCXChannelX, theFEB, theType, theDataType23Hits))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            discrims.extend(BRAMReadDiscrim(theCROCX.controller.boardNum, theCROCX.Description(),
                theCROCXChannelX, theFEB, theType, theDataType23Hits))           
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                discrims.extend(BRAMReadDiscrim(theCROCX.controller.boardNum, theCROCX.Description(),
                    theCHX, theFEB, theType, theDataType23Hits))           
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs this CRATE
        for theCROCX in theCROCXs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    discrims.extend(BRAMReadDiscrim(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==4:                    # RO all CTRLs all CRATEs
        for theCROCX in theCROCXsAllCRATEs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    discrims.extend(BRAMReadDiscrim(theCROCX.controller.boardNum, theCROCX.Description(),
                        theCHX, theFEB, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
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
def DAQBRAMReadTrip(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, tripNumber, theCROCXs, theCROCXsAllCRATEs,
    theReadType, theWriteType, theWFile, theFrame, theDataType23Hits):
    triphits=[]
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        if tripNumber==-1:                  # all Trips
            for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                    theCROCXChannelX, theFEB, tripIndex, theType, theDataType23Hits))
        else:                               # one Trip
            triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                theCROCXChannelX, theFEB, tripNumber, theType, theDataType23Hits))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            if tripNumber==-1:
                for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                    triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                        theCROCXChannelX, theFEB, tripIndex, theType, theDataType23Hits))
            else:
                triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                    theCROCXChannelX, theFEB, tripNumber, theType, theDataType23Hits))
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                if tripNumber==-1:
                    for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                        triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, tripIndex, theType, theDataType23Hits))
                else:
                    triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                        theCHX, theFEB, tripNumber, theType, theDataType23Hits))
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs this CRATE
        for theCROCX in theCROCXs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if tripNumber==-1:
                        for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                            triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                                theCHX, theFEB, tripIndex, theType, theDataType23Hits))
                    else:
                        triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, tripNumber, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==4:                    # RO all CTRLs all CRATEs
        for theCROCX in theCROCXsAllCRATEs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if tripNumber==-1:
                        for tripIndex in range(len(SC_MainObjects.Frame.FuncBRAMReadTripx)):
                            triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                                theCHX, theFEB, tripIndex, theType, theDataType23Hits))
                    else:
                        triphits.extend(BRAMReadTrip(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, tripNumber, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
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
def DAQBRAMReadHit(iEvent, theCROCX, theCROCXChannelX, theType, febNumber, hitNumber, theCROCXs, theCROCXsAllCRATEs,
    theReadType, theWriteType, theWFile, theFrame, theDataType23Hits):
    hittrips=[]
    if theDataType23Hits==False: hitIndexRange=range(len(SC_MainObjects.Frame.FuncBRAMReadHitx))
    else: hitIndexRange=range(len(SC_MainObjects.Frame.FuncBRAM2ReadHitx))
    if theReadType==0:                      # RO one FEB
        theFEB=SC_MainObjects.FEB(febNumber)
        if hitNumber==-1:                   # all Hits
            for hitIndex in hitIndexRange:
                hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                    theCROCXChannelX, theFEB, hitIndex, theType, theDataType23Hits))
        else:                               # one Hit
            hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                theCROCXChannelX, theFEB, hitNumber, theType, theDataType23Hits))
        theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==1:                    # RO one CH
        for febAddress in theCROCXChannelX.FEBs:
            theFEB=SC_MainObjects.FEB(febAddress)
            if hitNumber==-1:
                for hitIndex in hitIndexRange:
                    hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                        theCROCXChannelX, theFEB, hitIndex, theType, theDataType23Hits))
            else: 
                hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                    theCROCXChannelX, theFEB, hitNumber, theType, theDataType23Hits))
            theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==2:                    # RO one CTRL
        for theCHX in theCROCX.Channels():
            for febAddress in theCHX.FEBs:
                theFEB=SC_MainObjects.FEB(febAddress)
                if hitNumber==-1:
                    for hitIndex in hitIndexRange:
                        hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, hitIndex, theType, theDataType23Hits))
                else: 
                    hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                        theCHX, theFEB, hitNumber, theType, theDataType23Hits))
                theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
    elif theReadType==3:                    # RO all CTRLs this CRATE
        for theCROCX in theCROCXs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if hitNumber==-1:
                        for hitIndex in hitIndexRange:
                            hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                                theCHX, theFEB, hitIndex, theType, theDataType23Hits))
                    else: 
                        hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, hitNumber, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
    elif theReadType==4:                    # RO all CTRLs all CRATEs
        for theCROCX in theCROCXsAllCRATEs:
            for theCHX in theCROCX.Channels():
                for febAddress in theCHX.FEBs:
                    theFEB=SC_MainObjects.FEB(febAddress)
                    if hitNumber==-1:
                        for hitIndex in hitIndexRange:
                            hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                                theCHX, theFEB, hitIndex, theType, theDataType23Hits))
                    else: 
                        hittrips.extend(BRAMReadHit(theCROCX.controller.boardNum, theCROCX.Description(),
                            theCHX, theFEB, hitNumber, theType, theDataType23Hits))
                    theFrame.SetStatusText('%s...done'%theFEB.FPGADescription(theCHX, theCROCX, theType), 0)
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
def workerDAQSimple(nEvents, theLock, theStopEvent, theCTRLChannel, theCTRL, theCTRLs, theCTRLsAllCRATEs,
    theFrame, theReadType, theWriteType, theWFile, theType, theDataType23Hits):
    theLock.acquire()
    iEvent=0
    theFrame.SetStatusText('workerDAQSimple, nEvents=%d'%nEvents, 0)
    theFrame.SetStatusText('', 1)
    tt1=time.time()
    while iEvent<nEvents:
        if theStopEvent.isSet(): break
        try:
            # 1. Send OpenGate to simulate a new event
            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
                theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif theReadType==3:                                        # RO all CTRLs this CRATE
                for ctrl in theCTRLs:
                    ctrl.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif theReadType==4:                                        # RO all CTRLs all CRATEs
                for ctrl in theCTRLsAllCRATEs:
                    ctrl.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            # ... gives FEBs time to digitize hits: minim 300microsecs for 8 hits digitized, ~1.2milisec for 23 hits digitized
            time.sleep(0.002)
            # 2. Send SoftwareRDFE signal
            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
                theCTRL.SendSoftwareRDFE()
            elif theReadType==3:                                        # RO all CTRLs this CRATE
                for ctrl in theCTRLs:
                    ctrl.SendSoftwareRDFE()
            elif theReadType==4:                                        # RO all CTRLs all CRATEs
                for ctrl in theCTRLsAllCRATEs:
                    ctrl.SendSoftwareRDFE()
            # 3. Pooling RDFE done <=> RDFECounter incremented
            if theReadType==0 or theReadType==1:                        # RO one FEB or one CH
                for timeout in range(100):
                    if theCTRLChannel.ReadRDFECounter()==iEvent+1:
                        break
            elif theReadType==2:                                        # RO one CTRL
                for ich in range(4):
                    for timeout in range(100):
                        if theCTRL.Channels()[ich].ReadRDFECounter()==iEvent+1:
                            break
            elif theReadType==3:                                        # RO all CTRLs this CRATE
                for ctrl in theCTRLs:
                    for ich in range(4):
                        for timeout in range(100):
                            if ctrl.Channels()[ich].ReadRDFECounter()==iEvent+1:
                                break
            elif theReadType==4:                                        # RO all CTRLs all CRATEs
                for ctrl in theCTRLsAllCRATEs:
                    for ich in range(4):
                        for timeout in range(100):
                            if ctrl.Channels()[ich].ReadRDFECounter()==iEvent+1:
                                break
            #readout data...
            rcvmem=[]
            if theReadType==0 or theReadType==1:                        # RO one FEB or RO one CH
                rcvmem.append(['CRATE:%s:%s:%s'%(theCTRL.controller.boardNum, theCTRL.Description(),
                    theCTRLChannel.Description()), theCTRLChannel.ReadFullDPMBLT()])
            elif theReadType==2:                                        # RO one CTRL
                for ich in range(4):
                    rcvmem.append(['CRATE:%s:%s:%s'%(theCTRL.controller.boardNum, theCTRL.Description(),
                        theCTRL.Channels()[ich].Description()), theCTRL.Channels()[ich].ReadFullDPMBLT()])
            elif theReadType==3:                                        # RO all CTRLs this CRATE
                for ctrl in theCTRLs:
                    for ich in range(4):
                        rcvmem.append(['CRATE:%s:%s:%s'%(ctrl.controller.boardNum, ctrl.Description(),
                            ctrl.Channels()[ich].Description()), ctrl.Channels()[ich].ReadFullDPMBLT()])
            elif theReadType==4:                                        # RO all CTRLs all CRATEs
                for ctrl in theCTRLsAllCRATEs:
                    for ich in range(4):
                        rcvmem.append(['CRATE:%s:%s:%s'%(ctrl.controller.boardNum, ctrl.Description(),
                            ctrl.Channels()[ich].Description()), ctrl.Channels()[ich].ReadFullDPMBLT()])
            frms=DAQSplitRcvmemInFrames(rcvmem, theType)
            DAQReadRcvMemReportFrames(iEvent, frms, theWriteType, theWFile, theFrame, theType, theDataType23Hits)
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

    
