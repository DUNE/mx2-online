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
        self.Bind(wx.EVT_BUTTON, self.OnVMEbtnRead, self.frame.vme.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnVMEbtnWrite, self.frame.vme.btnWrite)
        # CROC pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnFlashFirst, self.frame.croc.FlashButtons.btnFlashFirst)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnFlashSecond, self.frame.croc.FlashButtons.btnFlashSecond)
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
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnAppendMessage, self.frame.ch.MessageRegisters.btnAppendMessage)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnWriteFIFO, self.frame.ch.MessageRegisters.btnWriteFIFO)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnSendFrame, self.frame.ch.MessageRegisters.btnSendFrame)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnReadDPMBytesN, self.frame.ch.MessageRegisters.btnReadDPMBytesN)

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
        addrListCRIMs=[128]
        addrListCROCs=[5,15]
        '''
        addrListCRIMs=[]
        addrListCROCs=[]
        #CROC mapping addr is 1 to 8, register is ResetTestPulse
        #CRIM mapping addr is 9 to 255, register is InterruptMask
        crocReg=0xF010; crimReg=0xF000  
        for i in range(256):
            data=( ((i&0xF0)<<8) | ((i&0x0F)<<4) ) & 0xF0F0
            if (i<=8): addr=((i<<16)|crocReg) & 0xFFFFFF
            else: addr=((i<<16)|crimReg) & 0xFFFFFF
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
            except:
                pass
                #print str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1]) 
        '''
        #now create object lists for CRIMs and CROCs found
        self.vmeCRIMs=[]; self.vmeCROCs=[]
        for addr in addrListCRIMs: self.vmeCRIMs.append(CRIM(self.controller, addr<<16))        
        for addr in addrListCROCs: self.vmeCROCs.append(CROC(self.controller, addr<<16))
        
        #and then update self.frame.tree
        self.frame.tree.DeleteAllItems()
        treeRoot = self.frame.tree.AddRoot("VME-BRIDGE")
        for vmedev in self.vmeCRIMs:            
            SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
        for vmedev in self.vmeCROCs:
            SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()]) 
            
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
            addr=int(str(self.frame.vme.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.vme.txtWriteData.GetValue(), 16)
            self.controller.WriteCycle(addr, data)
        except: ReportException('OnVMEbtnWrite', self.reportErrorChoice)
    def OnVMEbtnRead(self, event):
        try:          
            addr=int(self.frame.vme.txtReadAddr.GetValue(), 16)
            data=int(self.controller.ReadCycle(addr))
            data=hex(data)[2:]
            if data[-1]=='L': data=data[:-1]
            self.frame.vme.txtReadData.SetValue(data)
        except: ReportException('OnVMEbtnRead', self.reportErrorChoice)

    # CROC pannel events ##########################################################
    def OnCROCbtnFlashFirst(self, event): wx.MessageBox('not yet implemented')
    def OnCROCbtnFlashSecond(self, event): wx.MessageBox('not yet implemented')
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
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
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
    def OnCHbtnAppendMessage(self, event): wx.MessageBox('not yet implemented')
    def OnCHbtnWriteFIFO(self, event): wx.MessageBox('not yet implemented')
    def OnCHbtnSendFrame(self, event): wx.MessageBox('not yet implemented')
    def OnCHbtnReadDPMBytesN(self, event): wx.MessageBox('not yet implemented')

    # OTHER events ##########################################################
    def OnClose(self, event):
        #self.controller.End()
        self.Close(True)
        self.Destroy()
        
def FindVMEdev(vmeDevList, devAddr):
    for dev in vmeDevList:
        if (dev.BaseAddress()==devAddr): return dev
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
    def ClearStatus(self):
        print hex(self.RegWClearStatus), hex(0x0202)
        self.controller.WriteCycle(self.RegWClearStatus, 0x0202)
    def ReadStatus(self):
        print hex(self.RegRStatus)
        return int(self.controller.ReadCycle(self.RegRStatus))
    def ReadLoopDelay(self):
        print hex(self.RegRLoopDelay)
        return int(self.controller.ReadCycle(self.RegRLoopDelay)) 
    def DPMPointerReset(self):
        print hex(self.RegWClearStatus), hex(0x0808)
        self.controller.WriteCycle(self.RegWClearStatus, 0x0808)
    def DPMPointerRead(self):
        print hex(self.RegRDPMPointer)
        return int(self.controller.ReadCycle(self.RegRDPMPointer)) 

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
    def WriteRSTTP(self, data):
        print hex(self.RegWRResetAndTestMask), hex(data)
        self.controller.WriteCycle(self.RegWRResetAndTestMask, data)
    def ReadRSTTP(self):
        print hex(self.RegWRResetAndTestMask)
        return int(self.controller.ReadCycle(self.RegWRResetAndTestMask))
    def SendRSTOnly(self):
        print hex(self.RegWChannelReset), hex(0x0202)
        self.controller.WriteCycle(self.RegWChannelReset, 0x0202)
    def SendTPOnly(self):
        print hex(self.RegWTestPulse), hex(0x0404)
        self.controller.WriteCycle(self.RegWTestPulse, 0x0404)
    def SendFastCommand(self, data):
        print hex(self.RegWFastCommand), hex(data)
        self.controller.WriteCycle(self.RegWFastCommand, data)

    
    
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
