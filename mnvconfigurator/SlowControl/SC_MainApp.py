"""
MINERvA DAQ Slow Control GUI
Contains the main application code
Started October 21 2009
"""
#from ctypes import *
#cdll.LoadLibrary("/usr/local/lib/liblog4cpp.so.4")
#log4cpp = CDLL("/usr/local/lib/liblog4cpp.so.4")
#cdll.LoadLibrary("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")
#hardware = CDLL("/work/software/mnvsingle/mnvdaq/lib/libhardware.so")
#cdll.LoadLibrary("/lib64/libc.so.6")
#libc = CDLL("/lib64/libc.so.6")

import wx
import sys
import random
import time

import CAENVMEwrapper
import SC_Frames
import SC_Util
from SC_MainObjects import *
from SC_MainMethods import SC

class SCApp(wx.App):
    """SlowControl application. Subclass of wx.App"""
    def __init__(self):
        wx.App.__init__(self)                
        self.vmeCRIMs=[]
        self.vmeCROCs=[]
        self.vmeDIGs=[]
        self.reportErrorChoice={'display':True, 'msgBox':True}
        try:
            self.sc=SC()
        except: ReportException('controller.Init', self.reportErrorChoice)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)
        self.Bind(wx.EVT_TIMER, self.OnMonitor)
        # Menu events ##########################################################
        self.Bind(wx.EVT_MENU, self.OnMenuLoadHardware, self.frame.menuFileLoadHardware)
        self.Bind(wx.EVT_MENU, self.OnMenuLoadFile, self.frame.menuFileLoadFromFile)
        self.Bind(wx.EVT_MENU, self.OnMenuSaveFile, self.frame.menuFileSaveToFile)
        self.Bind(wx.EVT_MENU, self.OnMenuReset, self.frame.menuFileReset)
        self.Bind(wx.EVT_MENU, self.OnClose, self.frame.menuFileQuit)
        self.Bind(wx.EVT_MENU, self.OnMenuShowExpandAll, self.frame.menuShowExpandAll)
        self.Bind(wx.EVT_MENU, self.OnMenuShowCollapseAll, self.frame.menuShowCollapseAll)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsReadAllHV, self.frame.menuActionsReadAllHV)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsSetAllHV, self.frame.menuActionsSetAllHV)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsSTARTMonitorAllHV, self.frame.menuActionsSTARTMonitorAllHV)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsSTOPMonitor, self.frame.menuActionsSTOPMonitor)
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
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteTimingSetup, self.frame.croc.TimingSetup.btnWriteTimingSetup)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadTimingSetup, self.frame.croc.TimingSetup.btnReadTimingSetup)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendFastCmd, self.frame.croc.FastCmd.btnSendFastCmd)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnClearLoopDelays, self.frame.croc.LoopDelays.btnClearLoopDelays)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadLoopDelays, self.frame.croc.LoopDelays.btnReadLoopDelays)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteRSTTP, self.frame.croc.ResetAndTestPulse.btnWriteRSTTP)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadRSTTP, self.frame.croc.ResetAndTestPulse.btnReadRSTTP)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendRSTOnly, self.frame.croc.ResetAndTestPulse.btnSendRSTOnly)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendTPOnly, self.frame.croc.ResetAndTestPulse.btnSendTPOnly)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllCHs, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllCHs)
        self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllCROCs, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllCROCs)
        # CH pannel events ##########################################################
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
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALLThisCH, self.frame.fe.fpga.Registers.btnWriteALLThisCH)
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALLThisCROC, self.frame.fe.fpga.Registers.btnWriteALLThisCROC)
        self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALL, self.frame.fe.fpga.Registers.btnWriteALL)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnRead, self.frame.fe.trip.Registers.btnRead)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnRead6, self.frame.fe.trip.Registers.btnRead6)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWrite, self.frame.fe.trip.Registers.btnWrite)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWrite6, self.frame.fe.trip.Registers.btnWrite6)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALLThisCH, self.frame.fe.trip.Registers.btnWriteALLThisCH)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALLThisCROC, self.frame.fe.trip.Registers.btnWriteALLThisCROC)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALL, self.frame.fe.trip.Registers.btnWriteALL)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRST, self.frame.fe.trip.Registers.btnPRGRST)
        self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRSTALL, self.frame.fe.trip.Registers.btnPRGRSTALL)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnReadFlashToFile, self.frame.fe.flash.FlashButtons.btnReadFlashToFile)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnCompareFileToFlash, self.frame.fe.flash.FlashButtons.btnCompareFileToFlash)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlash, self.frame.fe.flash.FlashButtons.btnWriteFileToFlash)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashThisCH, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashThisCH)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashThisCROC, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashThisCROC)
        self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashALL, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashALL)
        
        self.OnMenuLoadHardware(None)
        self.OnMenuShowExpandAll(None)        
        
    def OnInit(self):
        """Create instance of SC frame objects here"""
        #Called by the wx.App parent class when application starts
        self.frame = SC_Frames.SCMainFrame(title='Slow Control')
        self.SetTopWindow(self.frame)
        self.frame.CenterOnScreen()
        self.frame.Show()
        return True
    def OnClose(self, event):
        self.frame.Close(True)

    # MENU events ##########################################################
    def OnMenuLoadHardware(self, event):      
        try:
            #find vme (hardware) devics
            self.vmeCRIMs=self.sc.FindCRIMs()
            self.vmeCROCs=self.sc.FindCROCs()
            self.vmeDIGs=self.sc.FindDIGs()
            FEBs=self.sc.FindFEBs(self.vmeCROCs)
            print '\n'.join(['Found '+crim.Description() for crim in self.vmeCRIMs])
            print '\n'.join(['Found '+croc.Description() for croc in self.vmeCROCs])
            print '\n'.join(['Found '+dig.Description() for dig in self.vmeDIGs])
            print '\n'.join(['Found '+feb for feb in FEBs])
            #and then update self.frame.tree
            self.frame.tree.DeleteAllItems()
            treeRoot = self.frame.tree.AddRoot("VME-BRIDGE")
            for vmedev in self.vmeCRIMs:            
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
            for vmedev in self.vmeCROCs:
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
            for vmedev in self.vmeDIGs:
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [[vmedev.Description(), []]])
        except: ReportException('OnMenuLoadHardware', self.reportErrorChoice)        
    def OnMenuLoadFile(self, event):
        try:
            fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[]
            dlg = wx.FileDialog(self.frame, message='READ Hardware Configuration', defaultDir='', defaultFile='',
                wildcard='HW Config (*.hwcfg)|*.hwcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                self.sc.HWcfgFileLoad(wx.FileDialog.GetPath(dlg))
            dlg.Destroy()
        except: ReportException('OnMenuLoadFile', self.reportErrorChoice)
    def OnMenuSaveFile(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='SAVE Hardware Configuration', defaultDir='', defaultFile='',
                wildcard='HW Config (*.hwcfg)|*.hwcfg|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                #filename=dlg.GetFilename()+'.hwcfg'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                self.sc.HWcfgFileSave(wx.FileDialog.GetPath(dlg))
            dlg.Destroy()              
        except: ReportException('OnMenuSaveFile', self.reportErrorChoice)
    def OnMenuReset(self, event):
        try: self.sc.controller.SystemReset()
        except: ReportException('OnMenuReset', self.reportErrorChoice)
    def OnMenuShowExpandAll(self, event): self.frame.tree.ExpandAll()
    def OnMenuShowCollapseAll(self, event): self.frame.tree.CollapseAll()
    def OnMenuActionsReadAllHV(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter HV Deviation from Target Value in ADC counts',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                self.frame.nb.ChangeSelection(0)
                hvs=FEB(0).GetAllHVParams(self.vmeCROCs, int(dlg.GetValue()))
                hv=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s'% \
                    (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], \
                    dictHV['Actual'], dictHV['Target'], dictHV['A-T']) for dictHV in hvs]
                print '\n'.join(hv)
            dlg.Destroy()            
        except: ReportException('OnMenuActionsReadVoltages', self.reportErrorChoice)
    def OnMenuActionsSetAllHV(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter HV Value in ADC counts',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                self.frame.nb.ChangeSelection(0)
                FEB(0).SetAllHVTarget(self.vmeCROCs, int(dlg.GetValue()))
            dlg.Destroy()
        except: ReportException('OnMenuActionsReadVoltages', self.reportErrorChoice)
    def OnMenuActionsSTARTMonitorAllHV(self, event):
        try:
            dlgADC = wx.TextEntryDialog(self.frame, message='Enter HV Deviation from Target Value in ADC counts',
                caption=self.frame.GetTitle(), defaultValue='100')
            dlgTime = wx.TextEntryDialog(self.frame, message='Enter Monitor interval in seconds',
                caption=self.frame.GetTitle(), defaultValue='1')
            if dlgADC.ShowModal()==wx.ID_OK:
                if dlgTime.ShowModal()==wx.ID_OK:
                    self.frame.nb.ChangeSelection(0)
                    self.monitor=wx.Timer()
                    self.monitor.Start(max(1000, float(dlgTime.GetValue())*1000))
                    self.monitorFunc=FEB.GetAllHVParams
                    self.monitorArgs=FEB(0), self.vmeCROCs, int(dlgADC.GetValue())
                    self.monitorTitle='Monitor ALL FEBs HV Actual outside the Target with more than %s counts'%(int(dlgADC.GetValue()))
                dlgTime.Destroy()
            dlgADC.Destroy()            
        except: ReportException('OnMenuActionsSTARTMonitorAllHV', self.reportErrorChoice)
    def OnMenuActionsSTOPMonitor(self, event): self.monitor=None
    def OnMonitor(self, event):
        try:
            self.frame.description.text.SetValue('')
            print self.monitorTitle
            print time.ctime()
            hvs=self.monitorFunc(*(self.monitorArgs))
            hv=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s'% \
                (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], \
                dictHV['Actual'], dictHV['Target'], dictHV['A-T']) for dictHV in hvs]
            print '\n'.join(hv)
        except: ReportException('OnMonitor', self.reportErrorChoice)

    # VME pannel events ##########################################################
    def OnVMEbtnWrite(self, event):
        try:
            addr=int(str(self.frame.vme.VMEReadWrite.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.vme.VMEReadWrite.txtWriteData.GetValue(), 16)
            self.sc.controller.WriteCycle(addr, data)
        except: ReportException('OnVMEbtnWrite', self.reportErrorChoice)
    def OnVMEbtnRead(self, event):
        try:          
            addr=int(self.frame.vme.VMEReadWrite.txtReadAddr.GetValue(), 16)
            data=int(self.sc.controller.ReadCycle(addr))
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
                self.frame.croc.LoopDelays.txtLoopDelayValues[i].SetValue(str(data))            
        except: ReportException('OnCROCbtnReadLoopDelays', self.reportErrorChoice)        
    def OnCROCbtnWriteRSTTP(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=0
            for i in range(4):
                ChXReset=self.frame.croc.ResetAndTestPulse.ChXReset[i].IsChecked()
                ChXTPulse=self.frame.croc.ResetAndTestPulse.ChXTPulse[i].IsChecked()
                data = data | (ChXReset<<(i+8)) | (ChXTPulse<<i)
            theCROC.WriteRSTTP(data)
        except: ReportException('OnCROCbtnWriteRSTTP', self.reportErrorChoice)
    def OnCROCbtnReadRSTTP(self, event): 
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadRSTTP()
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
    def OnCROCbtnReportAlignmentsAllCHs(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            theNumberOfMeas=int(self.frame.croc.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croc.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croc.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROCChannel in theCROC.Channels():
                FEB(0).AlignGateDelays(theCROC, theCROCChannel, theNumberOfMeas, theLoadTimerValue, theGateStartValue)
        except: ReportException('OnCROCbtnReportAlignmentsAllCHs', self.reportErrorChoice)
    def OnCROCbtnReportAlignmentsAllCROCs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croc.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croc.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croc.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    FEB(0).AlignGateDelays(theCROC, theCROCChannel, theNumberOfMeas, theLoadTimerValue, theGateStartValue)
        except: ReportException('OnCROCbtnReportAlignmentsAllCROCs', self.reportErrorChoice)

    # CH pannel events ##########################################################
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
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData=theFEB.FPGARead(theCROCChannel) 
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnRead', self.reportErrorChoice)  
    def OnFEFPGAbtnWrite(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            sentMessageData=theFEB.ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            rcvMessageData=theFEB.FPGAWrite(theCROCChannel, sentMessageData)
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnWrite', self.reportErrorChoice)  
    def OnFEFPGAbtnWriteALLThisCH(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for febAddress in theCROCChannel.FEBs:
                theFEB=FEB(febAddress)
                theFEB.FPGAWrite(theCROCChannel, sentMessageData)
                self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCChannel, theCROC), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALLThisCROC(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.FPGAWrite(theCROCChannel, sentMessageData)
                    self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCChannel, theCROC), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALL(self, event):
        try:
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    for febAddress in theCROCChannel.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.FPGAWrite(theCROCChannel, sentMessageData)
                        self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCChannel, theCROC), 0)
        except: ReportException('OnFEFPGAbtnWriteALL', self.reportErrorChoice)  
    def OnFETRIPbtnRead(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            rcvMessageData=theFEB.TRIPRead(theCROCChannel, theTRIPIndex)
            theFEB.ParseMessageToTRIPtxtRegs(rcvMessageData, theTRIPIndex, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead', self.reportErrorChoice)
    def OnFETRIPbtnRead6(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData=theFEB.TRIPRead(theCROCChannel)
            theFEB.ParseMessageToTRIPtxtRegs6(rcvMessageData, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead6', self.reportErrorChoice)   
    def OnFETRIPbtnWrite(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCChannel, theRegs, theTRIPIndex)
        except: ReportException('OnFETRIPbtnWrite', self.reportErrorChoice)
    def OnFETRIPbtnWrite6(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCChannel, theRegs)
        except: ReportException('OnFETRIPbtnWrite6', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCH(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for febAddress in theCROCChannel.FEBs:
                theFEB=FEB(febAddress)
                theFEB.TRIPWrite(theCROCChannel, theRegs)
                self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCChannel, theCROC), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCROC(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCChannel in theCROC.Channels():
                for febAddress in theCROCChannel.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.TRIPWrite(theCROCChannel, theRegs)
                    self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCChannel, theCROC), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFETRIPbtnWriteALL(self, event):
        try:
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    for febAddress in theCROCChannel.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.TRIPWrite(theCROCChannel, theRegs)
                        self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCChannel, theCROC), 0)
        except: ReportException('OnFETRIPbtnWriteALL', self.reportErrorChoice)
    def OnFETRIPbtnPRGRST(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.TRIPProgramRST(theCROCChannel)
        except: ReportException('OnFETRIPbtnPRGRST', self.reportErrorChoice)  
    def OnFETRIPbtnPRGRSTALL(self, event):
        try:
            for theCROC in self.vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    for febAddress in theCROCChannel.FEBs:
                        FEB(febAddress).TRIPProgramRST(theCROCChannel)
        except: ReportException('OnFETRIPbtnPRGRSTALL', self.reportErrorChoice)  
    def OnFEFLASHbtnReadFlashToFile(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber) 
            dlg = wx.FileDialog(self.frame, message='SAVE Flash Configuration', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH WriteFILE %s'%filename, 1)
                f=open(filename,'w')
                for iPage in range(Flash.NPages):
                    pageBytes=theFEB.FLASHMainMemPageRead(theCROCChannel, iPage)
                    f.write('%s '%str(iPage).rjust(4,'0').upper())
                    for iByte in pageBytes:
                        f.write('%s'%hex(iByte)[2:].rjust(2,'0').upper())
                    f.write('\n')
                    if iPage%100==0:
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
                self.frame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
                f.close()
            dlg.Destroy()              
        except: ReportException('OnFEFLASHbtnReadFlashToFile', self.reportErrorChoice)
    def OnFEFLASHbtnCompareFileToFlash(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber) 
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH CompFILE %s'%filename, 1)
                f=open(filename,'r')
                pagesAddrFile, pagesBytesFile = Flash().ParseFileLinesToMessages(f)
                f.close()
                errPages=''
                for iPage in range(Flash.NPages):
                    pageBytesRead=theFEB.FLASHMainMemPageRead(theCROCChannel, pagesAddrFile[iPage])
                    if pageBytesRead!=pagesBytesFile[iPage]: errPages += '%s '%iPage
                    if iPage%100==0:
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
                self.frame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCChannel, theCROC), 0)
                if errPages!='': raise Exception('ReadFLASH CompFILE Error on page %s'%errPages)                
            dlg.Destroy()              
        except: ReportException('OnFEFLASHbtnCompareFileToFlash', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlash(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCChannel=theCROCChannel, theCROC=theCROC, theVMECROCs=None,
                toThisFEB=True, toThisCH=False, toThisCROC=False, toAllCROCs=False, theFrame=self.frame)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlash', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCH(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCChannel=theCROCChannel, theCROC=theCROC, theVMECROCs=None,
                toThisFEB=False, toThisCH=True, toThisCROC=False, toAllCROCs=False, theFrame=self.frame)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCH', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCROC(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCChannel=None, theCROC=theCROC, theVMECROCs=None,
                toThisFEB=False, toThisCH=False, toThisCROC=True, toAllCROCs=False, theFrame=self.frame)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCROC', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashALL(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCChannel=None, theCROC=None, theVMECROCs=self.vmeCROCs,
                toThisFEB=False, toThisCH=False, toThisCROC=False, toAllCROCs=True, theFrame=self.frame)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashALL', self.reportErrorChoice)

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


def main():
    """Instantiates the Slow Control GUI."""
    try:
        #theArgs = sys.argv[1:]; print theArgs
        app = SCApp() 
        app.MainLoop()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]

if __name__ == "__main__":
    main()
