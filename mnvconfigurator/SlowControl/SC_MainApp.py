"""
MINERvA DAQ Slow Control GUI
Contains the main application code
Started October 21 2009
"""
from ctypes import *
cdll.LoadLibrary("/usr/local/lib/liblog4cpp.so.4")
log4cpp = CDLL("/usr/local/lib/liblog4cpp.so.4")
#cdll.LoadLibrary("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")
#hardware = CDLL("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")
#cdll.LoadLibrary("/lib64/libc.so.6")
#libc = CDLL("/lib64/libc.so.6")

import wx
import sys
import CAENVMEwrapper
import SC_Frames
import SC_Util
import random
#import feb

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
        # CRIM Timing pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteTimingSetup, self.frame.crim.TimingModule.TimingSetupRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadTimingSetup, self.frame.crim.TimingModule.TimingSetupRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteGateWidth, self.frame.crim.TimingModule.GateWidthRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadGateWidth, self.frame.crim.TimingModule.GateWidthRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteTCALBDelay, self.frame.crim.TimingModule.TCALBDelayRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadTCALBDelay, self.frame.crim.TimingModule.TCALBDelayRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteTRIGGERSend, self.frame.crim.TimingModule.TRIGGERSendRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteTCALBSend, self.frame.crim.TimingModule.TCALBSendRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteGATEStart, self.frame.crim.TimingModule.GATERegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteGATEStop, self.frame.crim.TimingModule.GATERegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteSeqCNTRST, self.frame.crim.TimingModule.CNTRSTRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteSeqCNTRSTSGATETCALB, self.frame.crim.TimingModule.CNTRSTRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteScrap, self.frame.crim.TimingModule.ScrapRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadScrap, self.frame.crim.TimingModule.ScrapRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadGateTimestamp, self.frame.crim.TimingModule.GateTimestampRegisters.btnRead)
        # CRIM CH pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnClearStatus, self.frame.crim.ChannelModule.StatusRegister.btnClearStatus)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnReadStatus, self.frame.crim.ChannelModule.StatusRegister.btnReadStatus)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbbtnDPMPointerReset, self.frame.crim.ChannelModule.DPMPointer.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnDPMPointerRead, self.frame.crim.ChannelModule.DPMPointer.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnWriteFIFO, self.frame.crim.ChannelModule.MessageRegisters.btnWriteFIFO)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnSendFrame, self.frame.crim.ChannelModule.MessageRegisters.btnSendFrame)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnReadDPMWordsN, self.frame.crim.ChannelModule.MessageRegisters.btnReadDPMWordsN)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnClearStatus, self.frame.crim.ChannelModule.StatusRegister.btnClearStatus)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnWriteMode, self.frame.crim.ChannelModule.ModeRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnReadMode, self.frame.crim.ChannelModule.ModeRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnFIFOFlagReset, self.frame.crim.ChannelModule.MiscRegisters.btnFIFOFlagReset)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnTimingCmdRead, self.frame.crim.ChannelModule.MiscRegisters.btnTimingCmdRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMCHbtnSendSYNC, self.frame.crim.ChannelModule.MiscRegisters.btnSendSYNC)
        # CRIM INTERRUPTER pannel events ##########################################################
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnWriteMaskRegister, self.frame.crim.InterrupterModule.MaskRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnReadMaskRegister, self.frame.crim.InterrupterModule.MaskRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnWriteStatusRegister, self.frame.crim.InterrupterModule.StatusRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnReadStatusRegister, self.frame.crim.InterrupterModule.StatusRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnWriteIntConfigRegister, self.frame.crim.InterrupterModule.IntConfigRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnReadIntConfigRegister, self.frame.crim.InterrupterModule.IntConfigRegister.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnWriteClearInterruptRegister, self.frame.crim.InterrupterModule.ClearInterruptRegister.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnWriteVectorTableRegister, self.frame.crim.InterrupterModule.VectorTableRegisters.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCRIMINTbtnReadVectorTableRegister, self.frame.crim.InterrupterModule.VectorTableRegisters.btnRead)
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
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnDPMPointerReset, self.frame.ch.DPMPointer.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnCHbtnDPMPointerRead, self.frame.ch.DPMPointer.btnRead)
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
        for crim in self.vmeCRIMs:
            print crim.type, crim.GetWRRegValues()
        for croc in self.vmeCROCs:
            print croc.type, croc.GetWRRegValues()
        febPrint()
        wx.MessageBox('SaveFile...', wx.Frame.GetTitle(self.frame),
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

    # CRIM Timing pannel events ##########################################################
    def OnCRIMTimingbtnWriteTimingSetup(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            mode = SC_Util.CRIMTimingModes[self.frame.crim.TimingModule.TimingSetupRegister.choiceMode.GetStringSelection()]
            freq = SC_Util.CRIMTimingFrequencies[self.frame.crim.TimingModule.TimingSetupRegister.choiceFrequency.GetStringSelection()]
            data = mode | freq
            theCRIM.TimingModule.WriteTimingSetup(data)         
        except: ReportException('OnCRIMTimingbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCRIMTimingbtnReadTimingSetup(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data=theCRIM.TimingModule.ReadTimingSetup()
            for k in SC_Util.CRIMTimingModes.keys():
                if SC_Util.CRIMTimingModes[k]==(data & 0xF000):
                    self.frame.crim.TimingModule.TimingSetupRegister.choiceMode.SetStringSelection(k)
            for k in SC_Util.CRIMTimingFrequencies.keys():
                if SC_Util.CRIMTimingFrequencies[k]==(data&0x0FFF):
                    self.frame.crim.TimingModule.TimingSetupRegister.choiceFrequency.SetStringSelection(k)
        except: ReportException('OnCRIMTimingbtnReadTimingSetup', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteGateWidth(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            gateWidth = int(self.frame.crim.TimingModule.GateWidthRegister.txtGateWidthData.GetValue()) & 0x7F
            enableBit = self.frame.crim.TimingModule.GateWidthRegister.chkCNTRSTEnable.IsChecked() << 15               
            theCRIM.TimingModule.WriteGateWidth(gateWidth | enableBit)         
        except: ReportException('OnCRIMTimingbtnWriteGateWidth', self.reportErrorChoice)
    def OnCRIMTimingbtnReadGateWidth(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadGateWidth()
            self.frame.crim.TimingModule.GateWidthRegister.txtGateWidthData.SetValue(str(data & 0x7F))
            self.frame.crim.TimingModule.GateWidthRegister.chkCNTRSTEnable.SetValue((data & 0x8000) >> 15)
        except: ReportException('OnCRIMTimingbtnReadGateWidth', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTCALBDelay(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.TimingModule.TCALBDelayRegister.txtData.GetValue()) & 0x3FF         
            theCRIM.TimingModule.WriteTCALBDelay(data)         
        except: ReportException('OnCRIMTimingbtnWriteTCALBDelay', self.reportErrorChoice)
    def OnCRIMTimingbtnReadTCALBDelay(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadTCALBDelay()
            self.frame.crim.TimingModule.TCALBDelayRegister.txtData.SetValue(str(data & 0x3FF))
        except: ReportException('OnCRIMTimingbtnReadTCALBDelay', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTRIGGERSend(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendTRIGGER()         
        except: ReportException('OnCRIMTimingbtnWriteTRIGGERSend', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTCALBSend(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendTCALB()         
        except: ReportException('OnCRIMTimingbtnWriteTCALBSend', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteGATEStart(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendGateStart()         
        except: ReportException('OnCRIMTimingbtnWriteGATEStart', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteGATEStop(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendGateStop()         
        except: ReportException('OnCRIMTimingbtnWriteGATEStop', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteSeqCNTRST(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendSequenceCNTRST()         
        except: ReportException('OnCRIMTimingbtnWriteSeqCNTRST', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteSeqCNTRSTSGATETCALB(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendSequenceCNTRSTSGATETCALB()         
        except: ReportException('OnCRIMTimingbtnWriteSeqCNTRSTSGATETCALB', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteScrap(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.TimingModule.ScrapRegister.txtData.GetValue())
            theCRIM.TimingModule.WriteScrap(data)         
        except: ReportException('OnCRIMTimingbtnWriteScrap', self.reportErrorChoice)
    def OnCRIMTimingbtnReadScrap(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadScrap()
            self.frame.crim.TimingModule.ScrapRegister.txtData.SetValue(str(data))
        except: ReportException('OnCRIMTimingbtnReadScrap', self.reportErrorChoice)
    def OnCRIMTimingbtnReadGateTimestamp(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadGateTimestamp()
            self.frame.crim.TimingModule.GateTimestampRegisters.txtData.SetValue(str(data))
        except: ReportException('OnCRIMTimingbtnReadGateTimestamp', self.reportErrorChoice)

    # CRIM CH pannel events ##########################################################
    def OnCRIMCHbtnClearStatus(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.ClearStatus()
        except: ReportException('OnCRIMCHbtnClearStatus', self.reportErrorChoice) 
    def OnCRIMCHbtnReadStatus(self, event): 
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadStatus()
            self.frame.crim.ChannelModule.StatusRegister.txtReadStatusData.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.crim.ChannelModule.StatusRegister.RegValues)
        except: ReportException('OnCRIMCHbtnReadStatus', self.reportErrorChoice)        
    def OnCRIMCHbbtnDPMPointerReset(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.DPMPointerReset()
        except: ReportException('OnCRIMCHbbtnDPMPointerReset', self.reportErrorChoice) 
    def OnCRIMCHbtnDPMPointerRead(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.DPMPointerRead()
            self.frame.crim.ChannelModule.DPMPointer.txtData.SetValue(hex(data))
        except: ReportException('OnCRIMCHbtnDPMPointerRead', self.reportErrorChoice)        
    def OnCRIMCHbtnWriteFIFO(self, event):
        try:
            msg=self.frame.crim.ChannelModule.MessageRegisters.txtAppendMessage.GetValue()
            if ((len(msg) % 4) !=0): raise Exception("A CROC/CRIM message string must have a muliple of 4 hex characters")
            nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar 
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            #theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]           
            for i in range(nWords):
                data = msg[4*i:4*(i+1)]
                theCRIM.ChannelModule.WriteFIFO(int(data,16))
        except: ReportException('OnCRIMCHbtnWriteFIFO', self.reportErrorChoice)        
    def OnCRIMCHbtnSendFrame(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.SendMessage()
        except: ReportException('OnCRIMCHbtnSendFrame', self.reportErrorChoice)  
    def OnCRIMCHbtnReadDPMWordsN(self, event):
        msg=''
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            nWords=int(self.frame.crim.ChannelModule.MessageRegisters.txtReadDPMWordsN.GetValue())
            for i in range(nWords):
                data=hex(theCRIM.ChannelModule.ReadDPM(2*i)).upper()
                msg += data[2:].rjust(4, '0')            
        except: ReportException('OnCRIMCHbtnReadDPMWordsN', self.reportErrorChoice)
        self.frame.crim.ChannelModule.MessageRegisters.txtReadDPMContent.SetValue(msg)             
    def OnCRIMCHbtnWriteMode(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            chkReTransmit = self.frame.crim.ChannelModule.ModeRegister.chkReTransmit.IsChecked() << 15
            chkSendMessage = self.frame.crim.ChannelModule.ModeRegister.chkSendMessage.IsChecked() << 14
            chkCRCErrorEnabled = self.frame.crim.ChannelModule.ModeRegister.chkCRCErrorEnabled.IsChecked() << 13
            chkFETriggerEnabled = self.frame.crim.ChannelModule.ModeRegister.chkFETriggerEnabled.IsChecked() << 12          
            theCRIM.ChannelModule.WriteMode(chkReTransmit | chkSendMessage | chkCRCErrorEnabled | chkFETriggerEnabled)         
        except: ReportException('OnCRIMCHbtnWriteMode', self.reportErrorChoice)
    def OnCRIMCHbtnReadMode(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadMode()
            chkReTransmit = self.frame.crim.ChannelModule.ModeRegister.chkReTransmit.SetValue((data & 0x8000) >> 15)
            chkSendMessage = self.frame.crim.ChannelModule.ModeRegister.chkSendMessage.SetValue((data & 0x4000) >> 14)
            chkCRCErrorEnabled = self.frame.crim.ChannelModule.ModeRegister.chkCRCErrorEnabled.SetValue((data & 0x2000) >> 13)
            chkFETriggerEnabled = self.frame.crim.ChannelModule.ModeRegister.chkFETriggerEnabled.SetValue((data & 0x1000) >> 12) 
        except: ReportException('OnCRIMCHbtnReadMode', self.reportErrorChoice)        
    def OnCRIMCHbtnFIFOFlagReset(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.ResetFIFO()
        except: ReportException('OnCRIMCHbtnFIFOFlagReset', self.reportErrorChoice)  
    def OnCRIMCHbtnTimingCmdRead(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadDecodTmgCmd()
            self.frame.crim.ChannelModule.MiscRegisters.txtTimingCmdReadData.SetValue(hex(data))
        except: ReportException('OnCRIMCHbtnTimingCmdRead', self.reportErrorChoice)      
    def OnCRIMCHbtnSendSYNC(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.SendSYNC()
        except: ReportException('OnCRIMCHbtnSendSYNC', self.reportErrorChoice)  
       
    # CRIM INTERRUPTER pannel events ##########################################################
    def OnCRIMINTbtnWriteMaskRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.InterrupterModule.MaskRegister.txtData.GetValue(), 16)
            theCRIM.InterrupterModule.WriteMask(data)         
        except: ReportException('OnCRIMINTbtnWriteMaskRegister', self.reportErrorChoice)        
    def OnCRIMINTbtnReadMaskRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadMask()
            self.frame.crim.InterrupterModule.MaskRegister.txtData.SetValue(hex(data)[2:])
        except: ReportException('OnCRIMINTbtnReadMaskRegister', self.reportErrorChoice) 
    def OnCRIMINTbtnWriteStatusRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.InterrupterModule.StatusRegister.txtData.GetValue(), 16)
            theCRIM.InterrupterModule.WriteStatus(data)         
        except: ReportException('OnCRIMINTbtnWriteStatusRegister', self.reportErrorChoice)
    def OnCRIMINTbtnReadStatusRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadStatus()
            self.frame.crim.InterrupterModule.StatusRegister.txtData.SetValue(hex(data)[2:])
        except: ReportException('OnCRIMINTbtnReadStatusRegister', self.reportErrorChoice) 
    def OnCRIMINTbtnWriteIntConfigRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            level = int(self.frame.crim.InterrupterModule.IntConfigRegister.txtVMEIntLevelData.GetValue()) & 0x7
            enableBit = self.frame.crim.InterrupterModule.IntConfigRegister.chkGlobalIntEnable.IsChecked() << 7               
            theCRIM.InterrupterModule.WriteIntConfig(level | enableBit)         
        except: ReportException('OnCRIMINTbtnWriteIntConfigRegister', self.reportErrorChoice)
    def OnCRIMINTbtnReadIntConfigRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadIntConfig()
            self.frame.crim.InterrupterModule.IntConfigRegister.txtVMEIntLevelData.SetValue(str(data & 0x7))
            self.frame.crim.InterrupterModule.IntConfigRegister.chkGlobalIntEnable.SetValue((data & 0x80) >> 7)
        except: ReportException('OnCRIMINTbtnReadIntConfigRegister', self.reportErrorChoice)
    def OnCRIMINTbtnWriteClearInterruptRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.InterrupterModule.SendClearInterrupt()         
        except: ReportException('OnCRIMINTbtnWriteClearInterruptRegister', self.reportErrorChoice)
    def OnCRIMINTbtnWriteVectorTableRegister(self, event): 
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = []
            for txt in self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues:
                data.append(int(txt.GetValue(), 16))
            theCRIM.InterrupterModule.WriteVectorTable(data)         
        except: ReportException('OnCRIMINTbtnWriteVectorTableRegister', self.reportErrorChoice)       
    def OnCRIMINTbtnReadVectorTableRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadVectorTable()
            for i in range(len(self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues)):
                self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues[i].SetValue(hex(data[i])[2:])
        except: ReportException('OnCRIMINTbtnReadVectorTableRegister', self.reportErrorChoice)   
    
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
                self.frame.croc.LoopDelays.txtLoopDelayValues[i].SetValue(hex(data))            
        except: ReportException('OnCROCbtnReadLoopDelays', self.reportErrorChoice)        
    def OnCROCbtnWriteRSTTP(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=0
            for i in range(4):
                ChXReset=self.frame.croc.ResetAndTestPulse.ChXReset[i].IsChecked()
                ChXTPulse=self.frame.croc.ResetAndTestPulse.ChXTPulse[i].IsChecked()
                data = data | (ChXReset<<(i+8)) | (ChXTPulse<<i)
                #print i, ChXReset, ChXTPulse, hex(data)
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
            self.frame.ch.StatusRegister.txtReadStatusData.SetValue(hex(data))
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
            self.frame.ch.DPMPointer.txtData.SetValue(hex(data))
        except: ReportException('OnCHbtnDPMPointerRead', self.reportErrorChoice)
    def OnCHbtnWriteFIFO(self, event):
        try:
            msg=self.frame.ch.MessageRegisters.txtAppendMessage.GetValue()
            if ((len(msg) % 4) !=0): raise Exception("A CROC/CRIM message string must have a muliple of 4 hex characters")
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
    def OnFEFPGAbtnRead(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            rcvMessageData=FEB(self.frame.fe.febNumber).FPGARead(theCROCChannel) 
            ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnRead', self.reportErrorChoice)  
    def OnFEFPGAbtnWrite(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            sentMessageData=ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            rcvMessageData=FEB(self.frame.fe.febNumber).FPGAWrite(theCROCChannel, sentMessageData)
            ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnWrite', self.reportErrorChoice)  
    def OnFEFPGAbtnWriteALL(self, event):
        try:
            sentMessageData=ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    for theFEB in theCROCChannel.FEBs:
                        theFEB.FPGAWrite(theCROCChannel, sentMessageData)
        except: ReportException('OnFEFPGAbtnWriteALL', self.reportErrorChoice)  
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

class Frame():
    DirectionM2S=0x00
    DirectionS2M=0x80
    BroadcastNone=0x00
    BroadcastLoadTimer=0x10
    BroadcastResetTimer=0x20
    BroadcastOpenGate=0x30
    BroadcastSoftReset=0x40
    DeviceNone=0x00
    DeviceTRIP=0x10
    DeviceFPGA=0x20
    DeviceBRAM=0x30
    DeviceFLASH=0x40
    FuncNone=0x00
    FuncFPGAWrite=0x01
    FuncFPGARead=0x02
    FuncTRIPWrite=0x01
    FuncTRIPRead=0x02
    StatusDeviceOK=0x01
    StatusFuncOK=0x02
    StatusCRCOK=0x01
    StatusEndHeaderOK=0x02
    StatusMaxLengthERR=0x04
    StatusSecondStartErr=0x08
    StatusNAHeaderErr=0x10
    NFPGARegisters=54
    MessageHeaderLength=9
    MessageDataLengthFPGA=55

def MakeHeader(direction, broadcast, febAddress, device, function, frameID0=0, frameID1=0):
    return [direction+broadcast+febAddress, device+function, 0, frameID0, frameID1, 0, 0, 0, 0]

def GetReceivedHeaderErrors(header, direction, broadcast, febAddress, device, frameID0=0, frameID1=0):
    err=[]
    if len(header)!=Frame.MessageHeaderLength: err.append('HeaderLenth!=%s'%Frame.MessageHeaderLength)
    if header[0]&direction!=direction: err.append('Direction!=%s'%direction)
    if header[0]&broadcast!=broadcast: err.append('Broadcast!=%s'%broadcast)
    if header[0]&febAddress!=febAddress: err.append('FEBAddress!=%s'%febAddress)
    if header[1]&device!=device: err.append('Device!=%s'%device)
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

def ParseMessageToFPGAtxtRegs(msg, txtRegs):
    if len(msg)!=Frame.MessageDataLengthFPGA: raise Exception('Datalength!=%s'%Frame.MessageDataLengthFPGA)
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
    txtRegs[31].SetValue(str((msg[9]>>4)&0x01))
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
    txtRegs[20].SetValue(str(msg[21]))
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

def ParseFPGARegsToMessage(txtRegs):
    msg=Frame.NFPGARegisters*[0]
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
    #message word 50-53: 
    return msg    

def FindVMEdev(vmeDevList, devAddr):
    for dev in vmeDevList:
        if (dev.BaseAddress()==devAddr): return dev

##def GetFEB(theCROCChannel, theFEBNumber):
##    feb=None
##    for theFEB in theCROCChannel.FEBs:
##        if theFEB.Address==theFEBNumber:
##            feb=theFEB; break
##    return feb
def WriteSendReceive(sentMessage, theFEBAddress, theCROCChannel):
    ClearAndCheckStatusRegister(theCROCChannel)
    ResetAndCheckDPMPointer(theCROCChannel)
    WriteFIFOAndCheckStatus(sentMessage, theCROCChannel) 
    SendFIFOAndCheckStatus(theCROCChannel)
    rcvMessageHeader, rcvMessageData = GetRcvMessageHeaderAndData(theCROCChannel)
    #print [hex(x) for x in rcvMessageHeader], len(rcvMessageHeader)
    #print [hex(x) for x in rcvMessageData], len(rcvMessageData)
    rcvHeaderErr=GetReceivedHeaderErrors(rcvMessageHeader,
        Frame.DirectionM2S, Frame.BroadcastNone, theFEBAddress, Frame.DeviceFPGA)
    if len(rcvHeaderErr)!=0: print rcvHeaderErr; raise Exception(rcvHeaderErr)
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
def WriteFIFOAndCheckStatus(theMessage, theCROCChannel, chk=True):
    if len(theMessage)%2==1: theMessage.append(0)
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
    return (rcvMessageHeader, rcvMessageData)

def FindFEBs(theCROCChannel):
    #clear the self.FEBs list
    theCROCChannel.FEBs=[]
    for febAddr in range(1,16):
        for itry in range(1,3):
            ClearAndCheckStatusRegister(theCROCChannel)
            ResetAndCheckDPMPointer(theCROCChannel)
            WriteFIFOAndCheckStatus([febAddr], theCROCChannel) 
            SendFIFOAndCheckStatus(theCROCChannel)
            #decode first two words from DPM and check DPM pointer
            dpmPointer=theCROCChannel.DPMPointerRead()
            w1=theCROCChannel.ReadDPM(0)
            w2=theCROCChannel.ReadDPM(2)
            if (w2==(0x8000 | (febAddr<<8))) & (w1==0x0B00) & (dpmPointer==13):
                #print "Found feb#" + str(febAddr), "w1="+hex(w1), "dpmPointer="+str(dpmPointer)
                theCROCChannel.FEBs.append(FEB(febAddr))
                break
            elif (w2==(0x0000 | (febAddr<<8))) & (w1==0x0400) & (dpmPointer==6): pass
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
    def NodeList(self):
        FEBsAddresses=[]
        for feb in self.FEBs: FEBsAddresses.append("FE:"+str(feb.Address))
        return [self.Description(), FEBsAddresses]
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
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CRIM)
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
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CRIM)
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
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CRIM)
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
        VMEDevice.__init__(self, controller, baseAddr, SC_Util.VMDdevTypes.CRIM)
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
    def FPGARead(self, theCROCChannel):
        sentMessage = MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGARead) + Frame.NFPGARegisters*[0]
        return WriteSendReceive(sentMessage, self.Address, theCROCChannel)
    def FPGAWrite(self, theCROCChannel, sentMessageData):
        sentMessage = MakeHeader(Frame.DirectionM2S, Frame.BroadcastNone, self.Address,
            Frame.DeviceFPGA, Frame.FuncFPGAWrite) + sentMessageData
        return WriteSendReceive(sentMessage, self.Address, theCROCChannel)
   
def febPrint():
    print 'Broadcast = %s' % feb.Broadcast
    print 'MasterToSlave = %s' % feb.MasterToSlave
    print 'SlaveToMaster = %s' % feb.SlaveToMaster
    print 'LoadTimer = %s' % feb.LoadTimer
    print 'ResetTimer = %s' % feb.ResetTimer
    print 'OpenGate = %s' % feb.OpenGate
    print 'SoftReset = %s' % feb.SoftReset
    print 'NoDevices = %s' % feb.NoDevices
    print 'TRiP = %s' % feb.TRiP
    print 'FPGA = %s' % feb.FPGA
    print 'RAM = %s' % feb.RAM
    print 'Flash = %s' % feb.Flash
    print 'NoFPGA = %s' % feb.NoFPGA
    print 'Write = %s' % feb.Write
    print 'Read = %s' % feb.Read
    print 'NoRAM = %s' % feb.NoRAM
    print 'ReadHit0 = %s' % feb.ReadHit0
    print 'ReadHit1 = %s' % feb.ReadHit1
    print 'ReadHit2 = %s' % feb.ReadHit2
    print 'ReadHit3 = %s' % feb.ReadHit3
    print 'ReadHit4 = %s' % feb.ReadHit4
    print 'ReadHit5 = %s' % feb.ReadHit5
    print 'ReadHitDiscr = %s' % feb.ReadHitDiscr
    print 'ReadHit6 = %s' % feb.ReadHit6
    print 'ReadHit7 = %s' % feb.ReadHit7
    print 'NoChip = %s' % feb.NoChip
    print 'ReadChip0 = %s' % feb.ReadChip0
    print 'ReadChip1 = %s' % feb.ReadChip1
    print 'ReadChip2 = %s' % feb.ReadChip2
    print 'ReadChip3 = %s' % feb.ReadChip3
    print 'ReadChip4 = %s' % feb.ReadChip4
    print 'ReadChip5 = %s' % feb.ReadChip5
    print 'ReadDigital0 = %s' % feb.ReadDigital0
    print 'ReadDigital1 = %s' % feb.ReadDigital1
    print 'NoFlash = %s' % feb.NoFlash
    print 'Command = %s' % feb.Command
    print 'SetReset = %s' % feb.SetReset
    print 'ResponseLength0 = %s' % feb.ResponseLength0
    print 'ResponseLength1 = %s' % feb.ResponseLength1
    print 'FrameStart = %s' % feb.FrameStart
    print 'DeviceStatus = %s' % feb.DeviceStatus
    print 'FrameStatus = %s' % feb.FrameStatus
    print 'FrameID0 = %s' % feb.FrameID0
    print 'FrameID1 = %s' % feb.FrameID1
    print 'Timestamp0 = %s' % feb.Timestamp0
    print 'Timestamp1 = %s' % feb.Timestamp1
    print 'Timestamp2 = %s' % feb.Timestamp2
    print 'Timestamp3 = %s' % feb.Timestamp3
    print 'Data = %s' % feb.Data
    print 'hwFrameStart = %s' % feb.hwFrameStart
    print 'hwDeviceFunction = %s' % feb.hwDeviceFunction
    print 'hWord2 = %s' % feb.hWord2
    print 'hwFrameID0 = %s' % feb.hwFrameID0
    print 'hwFrameID1 = %s' % feb.hwFrameID1
    print 'hWord5 = %s' % feb.hWord5
    print 'hWord6 = %s' % feb.hWord6
    print 'hWord7 = %s' % feb.hWord7
    print 'hWord8 = %s' % feb.hWord8
    print 'Direction = %s' % feb.Direction
    print 'Broadcast = %s' % feb.Broadcast
    print 'DeviceOK = %s' % feb.DeviceOK
    print 'FunctionOK = %s' % feb.FunctionOK
    print 'CRCOK = %s' % feb.CRCOK
    print 'EndHeader = %s' % feb.EndHeader
    print 'MaxLen = %s' % feb.MaxLen
    print 'SecondStart = %s' % feb.SecondStart
    print 'NAHeader = %s' % feb.NAHeader
    print 'febAll = %s' % feb.febAll
    print 'FE1 = %s' % feb.FE1
    print 'FE2 = %s' % feb.FE2
    print 'FE3 = %s' % feb.FE3
    print 'FE4 = %s' % feb.FE4
    print 'FE5 = %s' % feb.FE5
    print 'FE6 = %s' % feb.FE6
    print 'FE7 = %s' % feb.FE7
    print 'FE8 = %s' % feb.FE8
    print 'FE9 = %s' % feb.FE9
    print 'FE10 = %s' % feb.FE10
    print 'FE11 = %s' % feb.FE11
    print 'FE12 = %s' % feb.FE12
    print 'FE13 = %s' % feb.FE13
    print 'FE14 = %s' % feb.FE14
    print 'FE15 = %s' % feb.FE15
    
    
def main():
    """Instantiates the Slow Control GUI."""
    try:
        app = SCApp()
        app.MainLoop()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]

if __name__ == "__main__":
    main()
