"""
MINERvA DAQ Slow Control GUI
Contains the main application code
Started October 21 2009
"""

import wx
import sys
import CAENVMEwrapper
import SC_Frames
import SC_Util
import random

from ctypes import *
#vme = windll.CAENVMElib             #use this on windows
#cdll.LoadLibrary("libCAENVME.so")   #use this on linux
#vme = CDLL("libCAENVME.so")         #use this on linux

class SCApp(wx.App):
    """SlowControl application. Subclass of wx.App"""
    def __init__(self):
        wx.App.__init__(self)                
        self.vmeCRIMs=[]
        self.vmeCROCs=[]
        self.reportErrorChoice={'display':True, 'msgBox':True}
        self.controller = CAENVMEwrapper.Controller()
        try:
            self.controller.Init(CAENVMEwrapper.CAENVMETypes.CVBoardTypes.cvV2718, 0, 0) 
            print('Controller initialized:')
            print('\thandle = ' + str(self.controller.handle))
            print('\tCAENVME software = ' + str(self.controller.SWRelease()))
            print('\tV2718   firmware = ' + str(self.controller.BoardFWRelease()))
        except : ReportException('controller.Init', self.reportErrorChoice)
        
        self.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)
        # Menu events ##########################################################
        self.Bind(wx.EVT_MENU, self.OnMenuLoadHardware, self.frame.menuFileLoadHardware)
        self.Bind(wx.EVT_MENU, self.OnMenuLoadFile, self.frame.menuFileLoadFromFile)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveFile, self.frame.menuFileSaveToFile)
        self.Bind(wx.EVT_MENU, self.OnMenuShowExpandAll, self.frame.menuShowExpandAll)
        self.Bind(wx.EVT_MENU, self.OnMenuShowCollapseAll, self.frame.menuShowCollapseAll)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsReadVoltages, self.frame.menuActionsReadVoltages)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsZeroHVAll, self.frame.menuActionsZeroHVAll)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsMonitorVoltages, self.frame.menuActionsMonitorVoltages)
        # VME pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnVMEbtnRead, self.frame.vme.VMEReadWrite.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnVMEbtnWrite, self.frame.vme.VMEReadWrite.btnWrite)
        # CROC pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnFlashFirst, self.frame.croc.FlashButtons.btnFlashFirst)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnFlashSecond, self.frame.croc.FlashButtons.btnFlashSecond)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteTimingSetup, self.frame.croc.TimingSetup.btnWriteTimingSetup)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadTimingSetup, self.frame.croc.TimingSetup.btnReadTimingSetup)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendFastCmd, self.frame.croc.FastCmd.btnSendFastCmd)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnClearLoopDelays, self.frame.croc.LoopDelays.btnClearLoopDelays)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadLoopDelays, self.frame.croc.LoopDelays.btnReadLoopDelays)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteRSTTP, self.frame.croc.ResetAndTestPulse.btnWriteRSTTP)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadRSTTP, self.frame.croc.ResetAndTestPulse.btnReadRSTTP)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendRSTOnly, self.frame.croc.ResetAndTestPulse.btnSendRSTOnly)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendTPOnly, self.frame.croc.ResetAndTestPulse.btnSendTPOnly)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllChains, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllChains)
        # CH pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnFlashFirst, self.frame.ch.FlashButtons.btnFlashFirst)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnFlashSecond, self.frame.ch.FlashButtons.btnFlashSecond)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnClearStatus, self.frame.ch.StatusRegister.btnClearStatus)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnReadStatus, self.frame.ch.StatusRegister.btnReadStatus)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnDPMPointerReset, self.frame.ch.DPMPointer.btnDPMPointerReset)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnDPMPointerRead, self.frame.ch.DPMPointer.btnDPMPointerRead)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnWriteFIFO, self.frame.ch.MessageRegisters.btnWriteFIFO)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnSendFrame, self.frame.ch.MessageRegisters.btnSendFrame)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnReadDPMWordsN, self.frame.ch.MessageRegisters.btnReadDPMWordsN)
        # FE pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnRead, self.frame.fe.fpga.Registers.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWrite, self.frame.fe.fpga.Registers.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALL, self.frame.fe.fpga.Registers.btnWriteALL)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnRead, self.frame.fe.trip.Registers.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWrite, self.frame.fe.trip.Registers.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALL, self.frame.fe.trip.Registers.btnWriteALL)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnFlashFirst, self.frame.fe.flash.FlashButtons.btnFlashFirst)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnFlashSecond, self.frame.fe.flash.FlashButtons.btnFlashSecond)
        
        self.OnMenuLoadHardware(None)
        self.OnMenuShowExpandAll(None)
        
    def OnInit(self):
        """Create instance of SC frame objects here"""
        #Called by the wx.App parent class when application starts
        #minervaPhoto = wx.Image('minerva.jpg', wx.BITMAP_TYPE_JPEG)
        self.frame = SC_Frames.SCMainFrame(title='Slow Control', logoPhoto=None)
        self.SetTopWindow(self.frame)
        self.frame.CenterOnScreen()
        self.frame.Show()
        return True

    # MENU events ##########################################################
    def OnMenuLoadHardware(self, event):      
        try:
            #addrListCRIMs=[128]
            #addrListCROCs=[5,15]
            addrListCRIMs=[]
            addrListCROCs=[]
            #CROC mapping addr is 1 to 8, register is ResetTestPulse
            #CRIM mapping addr is 9 to 255, register is InterruptMask
            crocReg=0xF010; crimReg=0xF000  
            for i in range(256):
                data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
                if (i<=8): addr=((i<<16)|crocReg) & 0xFFFFFF    #CROC addr
                else: addr=((i<<16)|crimReg) & 0xFFFFFF         #CRIM addr
                #print hex(i), hex(addr), hex(data), 
                try:
                    self.controller.WriteCycle(addr, data)
                    if (i<=8):
                        print "Found CROC at ", hex(i)
                        addrListCROCs.append(i)
                    else:
                        print "Found CRIM at ", hex(i)
                        addrListCRIMs.append(i)
                    self.controller.WriteCycle(addr, 0)
                except: pass
            #now create object lists for CRIMs and CROCs found
            self.vmeCRIMs=[]; self.vmeCROCs=[]
            for addr in addrListCRIMs: self.vmeCRIMs.append(CRIM(self.controller, addr<<16))        
            for addr in addrListCROCs: self.vmeCROCs.append(CROC(self.controller, addr<<16))

            #then take each CROC CH and find the FEBs
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    FindFEBs(theCROCChannel)
            
            #and then update self.frame.tree
            self.frame.tree.DeleteAllItems()
            treeRoot = self.frame.tree.AddRoot("VME-BRIDGE")
            for vmedev in self.vmeCRIMs:            
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
            for vmedev in self.vmeCROCs:
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
        except: ReportException('OnMenuLoadHardware', self.reportErrorChoice)
            
    def OnMenuLoadFile(self, event):
        dlg = wx.FileDialog(self.frame, message="Choose a file",
            defaultDir="", defaultFile="", wildcard="*.*")
        if dlg.ShowModal()==wx.ID_OK:
            filename=dlg.GetFilename()
            dirname=dlg.GetDirectory()
            print 'filename = ' + filename
            print 'dirname = ' + dirname
            f=open(dirname+'\\'+ filename,'r')
            print f.read()
            f.close()
        dlg.Destroy()
    def OnMenuSaveFile(self, event):
        wx.MessageBox('SaveFile...', wx.Frame.GetTitle(self),
            wx.OK | wx.ICON_INFORMATION)
    def OnMenuShowExpandAll(self, event): self.frame.tree.ExpandAll()
    def OnMenuShowCollapseAll(self, event): self.frame.tree.CollapseAll()
    def OnMenuActionsReadVoltages(self, event): wx.MessageBox('not yet implemented')
    def OnMenuActionsZeroHVAll(self, event): wx.MessageBox('not yet implemented')
    def OnMenuActionsMonitorVoltages(self, event): wx.MessageBox('not yet implemented')  

    # VME pannel events ##########################################################
    def OnVMEbtnWrite(self, event):
        try:
            addr=int(str(self.frame.vme.VMEReadWrite.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.vme.VMEReadWrite.txtWriteData.GetValue(), 16)
            self.controller.WriteCycle(addr, data)
        except: ReportException('OnVMEbtnWrite', self.reportErrorChoice)
    def OnVMEbtnRead(self, event):
        try:          
            addr=int(self.frame.vme.VMEReadWrite.txtReadAddr.GetValue(), 16)
            data=int(self.controller.ReadCycle(addr))
            data=hex(data)[2:]
            if data[-1]=='L': data=data[:-1]
            self.frame.vme.VMEReadWrite.txtReadData.SetValue(data)
        except: ReportException('OnVMEbtnRead', self.reportErrorChoice)

    # CROC pannel events ##########################################################
    def OnCROCbtnFlashFirst(self, event): wx.MessageBox('not yet implemented')
    def OnCROCbtnFlashSecond(self, event): wx.MessageBox('not yet implemented')
    def OnCROCbtnReadTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadTimingSetup()
            self.frame.croc.TimingSetup.choiceCLKSource.SetSelection((data & 0x8000)>>15)
            self.frame.croc.TimingSetup.choiceTPDelayEnable.SetSelection((data & 0x1000)>>12)
            self.frame.croc.TimingSetup.txtTPDelayValue.SetValue(str(data & 0x3FF))
        except: ReportException('OnCROCbtnReadTimingSetup', self.reportErrorChoice)
    def OnCROCbtnWriteTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data = self.frame.croc.TimingSetup.choiceCLKSource.GetSelection()<<15 | \
                self.frame.croc.TimingSetup.choiceTPDelayEnable.GetSelection()<<12 | \
                int(self.frame.croc.TimingSetup.txtTPDelayValue.GetValue()) & 0x3FF 
            theCROC.WriteTimingSetup(data)
        except: ReportException('OnCROCbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCROCbtnSendFastCmd(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            fcmd=self.frame.croc.FastCmd.choiceFastCmd.GetStringSelection()
            if (SC_Util.FastCmds.has_key(fcmd)):                
                theCROC.SendFastCommand(SC_Util.FastCmds[fcmd])
            else: wx.MessageBox('Please select a Fast Command')
        except: ReportException('OnCROCbtnSendFastCmd', self.reportErrorChoice)
    def OnCROCbtnClearLoopDelays(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, selfFindFEBs.frame.croc.crocNumber<<16)
            for ch in theCROC.Channels():
                ch.ClearStatus()
            self.OnCROCbtnReadLoopDelays(None)
        except: ReportException('OnCROCbtnClearLoopDelays', self.reportErrorChoice)
    def OnCROCbtnReadLoopDelays(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            for i in range(len(theCROC.Channels())):
                data=theCROC.Channels()[i].ReadLoopDelay()
                #data=random.randint(1,65535) & 0x007F; wx.MessageBox(hex(data))
                self.frame.croc.LoopDelays.LoopDelayValues[i].Label=hex(data)            
        except: ReportException('OnCROCbtnReadLoopDelays', self.reportErrorChoice)        
    def OnCROCbtnWriteRSTTP(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=0
            for i in range(4):
                ChXReset=self.frame.croc.ResetAndTestPulse.ChXReset[i].IsChecked()
                ChXTPulse=self.frame.croc.ResetAndTestPulse.ChXTPulse[i].IsChecked()
                data = data | (ChXReset<<(i+8)) | (ChXTPulse<<i)
                print i, ChXReset, ChXTPulse, hex(data)
            theCROC.WriteRSTTP(data)
        except: ReportException('OnCROCbtnWriteRSTTP', self.reportErrorChoice)
    def OnCROCbtnReadRSTTP(self, event): 
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadRSTTP()
            #data=random.randint(1,65535) & 0x0F0F; wx.MessageBox(hex(data))
            ParseDataToListCheckBoxs((data & 0x000F), self.frame.croc.ResetAndTestPulse.ChXTPulse)
            ParseDataToListCheckBoxs((data & 0x0F00)>>8, self.frame.croc.ResetAndTestPulse.ChXReset)
        except: ReportException('OnCROCbtnReadRSTTP', self.reportErrorChoice)
    def OnCROCbtnSendRSTOnly(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            theCROC.SendRSTOnly()
        except: ReportException('OnCROCbtnSendRSTOnly', self.reportErrorChoice)        
    def OnCROCbtnSendTPOnly(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            theCROC.SendTPOnly()
        except: ReportException('OnCROCbtnSendTPOnly', self.reportErrorChoice)        
    def OnCROCbtnReportAlignmentsAllChains(self, event):
        try:
            print self.frame.croc.FEBGateDelays.txtNumberOfMeas.GetValue()
            print self.frame.croc.FEBGateDelays.txtLoadTimerValue.GetValue()
            print self.frame.croc.FEBGateDelays.txtGateStartValue.GetValue()
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            addr=theCROC.BaseAddress()
            print hex(addr)
            #the code of the allignment method should pe placed here... 
            wx.MessageBox('not yet implemented')
        except: ReportException('btnReportAlignmentsAllChains', self.reportErrorChoice)        

    # CH pannel events ##########################################################
    def OnCHbtnFlashFirst(self, event): wx.MessageBox('not yet implemented')
    def OnCHbtnFlashSecond(self, event): wx.MessageBox('not yet implemented')
    def OnCHbtnClearStatus(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.ClearStatus()
        except: ReportException('OnCHbtnClearStatus', self.reportErrorChoice)        
    def OnCHbtnReadStatus(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            data=theCROCChannel.ReadStatus()
            #data=random.randint(1,65535)
            self.frame.ch.StatusRegister.lblStatus.Label=hex(data)
            ParseDataToListLabels(data, self.frame.ch.StatusRegister.RegValues)
        except: ReportException('OnCHbtnReadStatus', self.reportErrorChoice)
    def OnCHbtnDPMPointerReset(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.DPMPointerReset()
        except: ReportException('OnCHbtnDPMPointerReset', self.reportErrorChoice)
    def OnCHbtnDPMPointerRead(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            data=theCROCChannel.DPMPointerRead()
            self.frame.ch.DPMPointer.lblDPMPointerValue.Label=hex(data)
        except: ReportException('OnCHbtnDPMPointerRead', self.reportErrorChoice)
    def OnCHbtnWriteFIFO(self, event):
        try:
            msg=self.frame.ch.MessageRegisters.txtAppendMessage.GetValue()
            if ((len(msg) % 4) !=0): raise Exception(
                "A CROC message string must have a muliple of 4 hex characters")
            nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar 
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]           
            for i in range(nWords):
                data = msg[4*i:4*(i+1)]
                theCROCChannel.WriteFIFO(int(data,16))
        except: ReportException('OnCHbtnWriteFIFO', self.reportErrorChoice)
    def OnCHbtnSendFrame(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.SendMessage()
        except: ReportException('OnCHbtnSendFrame', self.reportErrorChoice)
    def OnCHbtnReadDPMWordsN(self, event):
        msg=''
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            nWords=int(self.frame.ch.MessageRegisters.txtReadDPMWordsN.GetValue())
            for i in range(nWords):
                data=hex(theCROCChannel.ReadDPM(2*i)).upper()
                msg += data[2:].rjust(4, '0')            
        except: ReportException('OnCHbtnReadDPMWordsN', self.reportErrorChoice)
        self.frame.ch.MessageRegisters.txtReadDPMContent.SetValue(msg)

    # FE pannel events ##########################################################
    def OnFEFPGAbtnRead(self, event): wx.MessageBox('not yet implemented')
    def OnFEFPGAbtnWrite(self, event): wx.MessageBox('not yet implemented')
    def OnFEFPGAbtnWriteALL(self, event): wx.MessageBox('not yet implemented')
    def OnFETRIPbtnRead(self, event): wx.MessageBox('not yet implemented')
    def OnFETRIPbtnWrite(self, event): wx.MessageBox('not yet implemented')
    def OnFETRIPbtnWriteALL(self, event): wx.MessageBox('not yet implemented')
    def OnFEFLASHbtnFlashFirst(self, event): wx.MessageBox('not yet implemented')
    def OnFEFLASHbtnFlashSecond(self, event): wx.MessageBox('not yet implemented')    

    # OTHER events ##########################################################
    def OnClose(self, event):
        #self.controller.End()
        self.Close(True)
        self.Destroy()
        
def FindVMEdev(vmeDevList, devAddr):
    for dev in vmeDevList:
        if (dev.BaseAddress()==devAddr): return dev
def FindFEBs(theCROCChannel):  
    #clear the self.FEBs list
    theCROCChannel.FEBs=[]
    for feb in range(1,16):
        for itry in range(1,3):
            #clear/check status register
            theCROCChannel.ClearStatus()
            status=theCROCChannel.ReadStatus()
            if (status!=0x3700): raise Exception(
                "Error after clear STATUS register for CROC channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
            #reset/check DPM pointer
            theCROCChannel.DPMPointerReset()
            dpmPointer=theCROCChannel.DPMPointerRead()
            if (dpmPointer!=0x02): raise Exception(
                "Error after DPMPointerReset() for CROC channel " + hex(theCROCChannel.chBaseAddr) + " DPMPointer=" + hex(dpmPointer))
            #write to FIFO and check status register
            theCROCChannel.WriteFIFO(feb<<8)
            status=theCROCChannel.ReadStatus()
            if (status!=0x3710): raise Exception(
                "Error after fill FIFO for CROC channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
            #send message and check status register
            theCROCChannel.SendMessage()
            for i in range(1000):
                status=theCROCChannel.ReadStatus()
                if (status==0x3703): break
            if (status!=0x3703): raise Exception(
                "Error after send message for CROC channel " + hex(theCROCChannel.chBaseAddr) + " status=" + hex(status))
            #decode first two words from DPM and check DPM pointer
            dpmPointer=theCROCChannel.DPMPointerRead()
            w1=theCROCChannel.ReadDPM(0)
            w2=theCROCChannel.ReadDPM(2)
            if (w2==(0x8000 | (feb<<8))) & (w1==0x0B00) & (dpmPointer==13):
                #print "Found feb#" + str(feb), "w1="+hex(w1), "dpmPointer="+str(dpmPointer)
                theCROCChannel.FEBs.append("FE:"+str(feb))
                break
            elif (w2==(0x0000 | (feb<<8))) & (w1==0x0400) & (dpmPointer==6): pass
                #print "NO    feb#" + str(feb), "w1="+hex(w1), "dpmPointer="+str(dpmPointer) 
            else: print "FindFEBs(" + hex(theCROCChannel.chBaseAddr) + ") wrong message " + "w1="+hex(w1) + "w2="+hex(w2), "dpmPointer="+str(dpmPointer) 
  
def ReportException(comment, choice):
    msg = comment + ' : ' + str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
    if (choice['display']): print msg
    if (choice['msgBox']): wx.MessageBox(msg)
def ParseDataToListLabels(data, ListLabels):
    for i in range(len(ListLabels)):
        ListLabels[i].Label=str((data & (1<<i))>>i)
def ParseDataToListCheckBoxs(data, ListCheckBoxs):
    for i in range(len(ListCheckBoxs)):
        ListCheckBoxs[i].SetValue((data & (1<<i))>>i)
        

class VMEDevice():
    def __init__(self, controller, baseAddr, moduleType):
        self.controller=controller
        self.baseAddr=baseAddr
        self.type=moduleType     
    def BaseAddress(self): return self.baseAddr
    def Type(self): return self.type
    def Description(self):
        if (self.type==SC_Util.VMDdevTypes.CROC or self.type==SC_Util.VMDdevTypes.CRIM):
            return self.type+':'+str((self.baseAddr & 0xFF0000)>>16)
        if (self.type==SC_Util.VMDdevTypes.CH):
            return self.type+':'+str(((self.baseAddr & 0x00F000)>>12)/4)

class CROCChannel(VMEDevice):
    def __init__(self, chNumber, baseAddr, controller):
        self.chBaseAddr=baseAddr+0x4000*chNumber
        self.chNumber=chNumber;
        VMEDevice.__init__(self, controller, self.chBaseAddr, SC_Util.VMDdevTypes.CH)
        self.RegRMemory      = self.chBaseAddr + SC_Util.CROCCHRegs.RegRMemory
        self.RegWInput       = self.chBaseAddr + SC_Util.CROCCHRegs.RegWInput
        self.RegWSendMessage = self.chBaseAddr + SC_Util.CROCCHRegs.RegWSendMessage
        self.RegRStatus      = self.chBaseAddr + SC_Util.CROCCHRegs.RegRStatus
        self.RegWClearStatus = self.chBaseAddr + SC_Util.CROCCHRegs.RegWClearStatus
        self.RegRLoopDelay   = self.chBaseAddr + SC_Util.CROCCHRegs.RegRLoopDelay
        self.RegRDPMPointer  = self.chBaseAddr + SC_Util.CROCCHRegs.RegRDPMPointer
        self.FEBs=[]
    def Number(self): return self.chNumber
    def NodeList(self): return [self.Description(), self.FEBs]
    def ReadDPM(self, offset):
        if (offset>0x1FFF): raise Exception("address " + hex(offset) + " is out of rnage")
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
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CROC)
        self.RegWRTimingSetup       = baseAddr + SC_Util.CROCRegs.RegWRTimingSetup
        self.RegWRResetAndTestMask  = baseAddr + SC_Util.CROCRegs.RegWRResetAndTestMask
        self.RegWChannelReset      = baseAddr + SC_Util.CROCRegs.RegWChannelReset
        self.RegWFastCommand       = baseAddr + SC_Util.CROCRegs.RegWFastCommand
        self.RegWTestPulse         = baseAddr + SC_Util.CROCRegs.RegWTestPulse 
        self.channels=[]
        for chNumber in range(4):
            self.channels.append(CROCChannel(chNumber, baseAddr, controller))
        self.channels[0].FEBs=['FE:1','FE:2','FE:3']
        self.channels[1].FEBs=['FE:4','FE:5']
        self.channels[2].FEBs=[]
        self.channels[3].FEBs=['FE:15','FE:14','FE:13']        
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
    

    
    
class CRIM(VMEDevice):
    def __init__(self, controller, baseAddr):
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CRIM)
    def NodeList(self): return [self.Description(), []]



    
def main():
    """Instantiates the Slow Control GUI."""
    try:
        app = SCApp()
        app.MainLoop()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]

if __name__ == "__main__":
    main()
