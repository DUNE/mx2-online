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
import threading

import CAENVMEwrapper
import SC_Frames
import SC_Util
from SC_MainObjects import *
import SC_MainMethods
import V1720Config

class SCApp(wx.App):
    """SlowControl application. Subclass of wx.App"""
    def __init__(self):
        try:
            wx.App.__init__(self)                
            self.vmeCRIMs=[]
            self.vmeCROCs=[]
            self.vmeCROCEs=[]
            self.vmeDIGs=[]
            self.daqWFile=None
            self.thrd=None
            self.threads=[]
            self.DAQLock=threading.Lock()
            self.DAQStopEvent=threading.Event()
            self.reportErrorChoice={'display':True, 'msgBox':True}
            try:
                self.sc=SC_MainMethods.SC()
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
            self.Bind(wx.EVT_BUTTON, self.OnVMEbtnRunBoardTest, self.frame.vme.BoardTest.btnRunBoardTest)
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
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteRSTTP, self.frame.croc.ResetAndTestPulse.btnWriteRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadRSTTP, self.frame.croc.ResetAndTestPulse.btnReadRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendRSTOnly, self.frame.croc.ResetAndTestPulse.btnSendRSTOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendTPOnly, self.frame.croc.ResetAndTestPulse.btnSendTPOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnClearLoopDelays, self.frame.croc.LoopDelays.btnClearLoopDelays)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadLoopDelays, self.frame.croc.LoopDelays.btnReadLoopDelays)
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
            # CROCE pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteTimingSetup, self.frame.croce.TimingSetup.btnWriteTimingSetup)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadTimingSetup, self.frame.croce.TimingSetup.btnReadTimingSetup)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnSendFastCmd, self.frame.croce.FastCmd.btnSendFastCmd)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteRSTTP, self.frame.croce.ResetAndTestPulse.btnWriteRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadRSTTP, self.frame.croce.ResetAndTestPulse.btnReadRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnSendRSTOnly, self.frame.croce.ResetAndTestPulse.btnSendRSTOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnSendTPOnly, self.frame.croce.ResetAndTestPulse.btnSendTPOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteRDFEPulseDelay, self.frame.croce.RDFESetup.btnWriteRDFEPulseDelay)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadRDFEPulseDelay, self.frame.croce.RDFESetup.btnReadRDFEPulseDelay)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnSendRDFESoftware, self.frame.croce.RDFESetup.btnSendRDFESoftware)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnClearLoopDelays, self.frame.croce.LoopDelays.btnClearLoopDelays)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadLoopDelays, self.frame.croce.LoopDelays.btnReadLoopDelays)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReportAlignmentsAllCHEs, self.frame.croce.FEBGateDelays.btnReportAlignmentsAllCHs)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReportAlignmentsAllCROCEs, self.frame.croce.FEBGateDelays.btnReportAlignmentsAllCROCs)
            # CHE pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteConfig, self.frame.che.ConfigurationRegister.btnWriteConfig)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadConfig, self.frame.che.ConfigurationRegister.btnReadConfig)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteCommands, self.frame.che.CommandsRegister.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRcvMemWPointerRegister, self.frame.che.RcvMemWPointerRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRcvMemFramesCounterRegister, self.frame.che.RcvMemFramesCounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRDFECounterRegister, self.frame.che.RDFECounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadTXRstTpInDelayCounterRegister, self.frame.che.TXRstTpInDelayCounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadStatusFrame, self.frame.che.StatusFrameRegister.btnReadStatusFrame)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadStatusTXRX, self.frame.che.StatusTXRXRegister.btnReadStatusTXRX)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteHeaderData, self.frame.che.HeaderDataRegister.btnWriteHeaderData)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadHeaderData, self.frame.che.HeaderDataRegister.btnReadHeaderData)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadAllRegs, self.frame.che.ReadAllRegisters.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteSendMemory, self.frame.che.SendMemory.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadReceiveMemory, self.frame.che.ReceiveMemory.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadFramePointersMemory, self.frame.che.FramePointersMemory.btn1)
            # FE pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnRead, self.frame.fe.fpga.Registers.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnDumpRead, self.frame.fe.fpga.Registers.btnDumpRead)
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
            # FE DAQ pannel events ##########################################################
            self.Bind(wx.EVT_RADIOBOX, self.OnFEDAQradioWriteType, self.frame.fe.daq.radioWriteType)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnOpenGateWrite, self.frame.fe.daq.btnBRAMCtrlOpenGate)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnSoftRDFEWrite, self.frame.fe.daq.btnBRAMCtrlSoftRDFE)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnDiscrimBRAMRead, self.frame.fe.daq.btnBRAMCtrlReadDiscrimBRAM)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnTripBRAMRead, self.frame.fe.daq.btnBRAMCtrlReadTripBRAM)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnHitBRAMRead, self.frame.fe.daq.btnBRAMCtrlReadHitBRAM)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnReadRcvMem, self.frame.fe.daq.btnReadRcvMem)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnAcqCtrlStart, self.frame.fe.daq.btnAcqCtrlStart)
##            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnAcqCtrlStop, self.frame.fe.daq.btnAcqCtrlStop)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnAcqCtrlStartThread, self.frame.fe.daq.btnAcqCtrlStartThread)
            self.Bind(wx.EVT_BUTTON, self.OnFEDAQbtnAcqCtrlStopThread, self.frame.fe.daq.btnAcqCtrlStopThread)
            # DIG pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnDIGbtnLoadConfigFile, self.frame.dig.btnLoadConfigFile)
            self.Bind(wx.EVT_BUTTON, self.OnDIGbtnReadAllRegs, self.frame.dig.btnReadAllRegs)
            self.Bind(wx.EVT_BUTTON, self.OnDIGbtnTakeNEvents, self.frame.dig.btnTakeNEvents)
            self.Bind(wx.EVT_BUTTON, self.OnDIGbtnRegRead, self.frame.dig.VMEReadWrite.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnDIGbtnRegWrite, self.frame.dig.VMEReadWrite.btnWrite)
            
            self.OnMenuLoadHardware(None)
            self.OnMenuShowExpandAll(None)
        except: ReportException('__init__', self.reportErrorChoice)
        
    def OnInit(self):
        """Create instance of SC frame objects here"""
        #Called by the wx.App parent class when application starts
        self.frame = SC_Frames.SCMainFrame(title='Slow Control')
        self.SetTopWindow(self.frame)
        self.frame.CenterOnScreen()
        self.frame.Show()
        return True
    def OnClose(self, event):
        self.StopThreads()
        self.frame.Close(True)

    # MENU events ##########################################################
    def OnMenuLoadHardware(self, event):      
        try:
            self.vmeCRIMs=[]
            self.vmeCROCs=[]
            self.vmeCROCEs=[]
            FEBs=[]
            FEBsCROCE=[]
            #find vme (hardware) devics
            self.vmeCRIMs=self.sc.FindCRIMs()
            self.vmeCROCs=self.sc.FindCROCs()
            self.vmeCROCEs=self.sc.FindCROCEs()
            self.vmeDIGs=self.sc.FindDIGs()
            FEBs=self.sc.FindFEBs(self.vmeCROCs)
            FEBsCROCE=self.sc.FindCROCEFEBs(self.vmeCROCEs)
            if self.vmeCRIMs!=[]: print '\n'.join(['Found '+crim.Description() for crim in self.vmeCRIMs])
            if self.vmeCROCs!=[]: print '\n'.join(['Found '+croc.Description() for croc in self.vmeCROCs])
            if self.vmeCROCEs!=[]: print '\n'.join(['Found '+croce.Description() for croce in self.vmeCROCEs])
            if self.vmeDIGs!=[]: print '\n'.join(['Found '+dig.Description() for dig in self.vmeDIGs])
            if FEBs!=[]: print '\n'.join(['Found '+feb for feb in FEBs])
            if FEBsCROCE!=[]: print '\n'.join(['Found '+feb for feb in FEBsCROCE])
            #and then update self.frame.tree
            self.frame.tree.DeleteAllItems()
            treeRoot = self.frame.tree.AddRoot("VME-BRIDGE")
            for vmedev in self.vmeCRIMs + self.vmeCROCs + self.vmeCROCEs  + self.vmeDIGs:            
                SC_Util.AddTreeNodes(self.frame.tree, treeRoot, [vmedev.NodeList()])
        except: ReportException('OnMenuLoadHardware', self.reportErrorChoice)        
    def OnMenuLoadFile(self, event):
        try:
            fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[]
            dlg = wx.FileDialog(self.frame, message='READ Hardware Configuration', defaultDir='', defaultFile='',
                wildcard='HW Config (*.hwcfg)|*.hwcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                self.sc.HWcfgFileLoad(wx.FileDialog.GetPath(dlg), self.frame)
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
                hvs=FEB(0).GetAllHVParams(self.vmeCROCs, 'CROC', int(dlg.GetValue()))
                hvEs=FEB(0).GetAllHVParams(self.vmeCROCEs, 'CROCE', int(dlg.GetValue()))
                hv=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                    (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], \
                     dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                     dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvs]
                hvE=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                    (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROCE'], \
                     dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                     dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvEs]
                print '\n'.join(hv)
                print '\n'.join(hvE)
            dlg.Destroy()            
        except: ReportException('OnMenuActionsReadVoltages', self.reportErrorChoice)
    def OnMenuActionsSetAllHV(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter HV Value in ADC counts',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                self.frame.nb.ChangeSelection(0)
                FEB(0).SetAllHVTarget(self.vmeCROCs, 'CROC', int(dlg.GetValue()))
                FEB(0).SetAllHVTarget(self.vmeCROCEs, 'CROCE', int(dlg.GetValue()))
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
                    self.monitorArgs=FEB(0), self.vmeCROCs, 'CROC', int(dlgADC.GetValue())
                    self.monitorArgEs=FEB(0), self.vmeCROCEs, 'CROCE', int(dlgADC.GetValue())
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
            hvEs=self.monitorFunc(*(self.monitorArgEs))
            hv=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], \
                 dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                 dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvs]
            hvE=['FPGA:%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROCE'], \
                 dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                 dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvEs]
            print '\n'.join(hv)
            print '\n'.join(hvE)
        except: ReportException('OnMonitor', self.reportErrorChoice)

    # VME pannel events ##########################################################
    def OnVMEbtnWrite(self, event):
        try:
            am=str(self.frame.vme.VMEReadWrite.choiceAddressModifier.GetStringSelection())
            dw=str(self.frame.vme.VMEReadWrite.choiceDataWidth.GetStringSelection())
            addr=int(str(self.frame.vme.VMEReadWrite.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.vme.VMEReadWrite.txtWriteData.GetValue(), 16)
            self.sc.controller.WriteCycle(addr, data, am, dw)
        except: ReportException('OnVMEbtnWrite', self.reportErrorChoice)
    def OnVMEbtnRead(self, event):
        try:
            am=str(self.frame.vme.VMEReadWrite.choiceAddressModifier.GetStringSelection())
            dw=str(self.frame.vme.VMEReadWrite.choiceDataWidth.GetStringSelection())
            bltsz=int(self.frame.vme.VMEReadWrite.txtBLTSize.GetValue(), 16)
            addr=int(self.frame.vme.VMEReadWrite.txtReadAddr.GetValue(), 16)
            if am=='A32_U_DATA' or am=='A24_U_DATA':
                data=int(self.sc.controller.ReadCycle(addr, am, dw))
                if dw=='D16' or dw=='D16sw': data=hex(data)[2:].rjust(4,'0')
                if dw=='D32' or dw=='D32sw': data=hex(data)[2:].rjust(8,'0')
                self.frame.vme.VMEReadWrite.txtReadData.SetValue(data)
            if am=='A32_U_BLT' or am=='A24_U_BLT':
                data=self.sc.controller.ReadCycleBLT(addr, bltsz, am, dw)
                hexdata=[hex(d)[2:].rjust(2,'0') for d in data]
                print 'am=%s: data=%s'%(am,''.join(hexdata))
                self.frame.vme.VMEReadWrite.txtReadData.SetValue(''.join(hexdata))
        except: ReportException('OnVMEbtnRead', self.reportErrorChoice)
    def OnVMEbtnRunBoardTest(self, event):
        try:
            if self.frame.vme.BoardTest.chkWriteToFile.IsChecked():
                dlg = wx.FileDialog(self.frame, message='SAVE DAQ Data', defaultDir='', defaultFile='',
                        wildcard='DAQ Data (*.btest)|*.btest|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
                if dlg.ShowModal()==wx.ID_OK:
                    filename=dlg.GetFilename()+'.btest'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                    self.daqWFile=open(wx.FileDialog.GetPath(dlg),'w')
                dlg.Destroy()
            self.frame.nb.ChangeSelection(0)
            ntry=int(self.frame.vme.BoardTest.txtNtimes.GetValue(),10)
            includeRAMMode=self.frame.vme.BoardTest.chkIncludeRAMMode.IsChecked()
            useRandomData=self.frame.vme.BoardTest.chkUseRandomData.IsChecked()
            theRAMData=int(self.frame.vme.BoardTest.txtRAMData.GetValue(),16)
            theREGHeader=0x1FFF&int(self.frame.vme.BoardTest.txtREGHeader.GetValue(),16)
            theREGTestData=int(self.frame.vme.BoardTest.txtREGTestData.GetValue(),16)
            self.frame.vme.BoardTest.txtREGHeader.SetValue('0x'+str(hex(theREGHeader)[2:].rjust(4,'0')))
            for theCROCE in self.vmeCROCEs:
                for iche in range(4): theCROCE.Channels()[iche].WriteHeaderData(theREGHeader)
            errmsg='********************************'+\
                   '\n* CROCE BOARD TEST RUN RESULTS *'+\
                   '\n********************************'+\
                   '\nStart: %s'%time.ctime()
            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
            else: print errmsg
            for theCROCE in self.vmeCROCEs:
                fails=[0,0,0,0,0,0,0,0,0,0]
                bitErrFreqCHXTest4=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
                bitErrFreqCHXTest5=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
                bitErrFreqCHXTest6=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
                bitErrFreqCHXTest7=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
                bitErrFreqCHXTest8=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                               [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
                for itry in range(ntry):
                    #if itry%100==0:
                    self.frame.description.text.Refresh(); self.frame.description.text.Update()
                    self.frame.SetStatusText('Testing...%s'%itry, 0)
                    #TEST#1 Fast Commands
                    if self.frame.vme.BoardTest.chkTest1.IsChecked():
                        fails[1]=self.TestFastCommands(itry,theCROCE,fails[1],self.daqWFile)
                        self.frame.SetStatusText('%s: TEST#1: Fast Command: Fails=%s'%(theCROCE.Description(),fails[1]), 1)
                    #TEST#2 Test Pulse
                    if self.frame.vme.BoardTest.chkTest2.IsChecked():
                        fails[2]=self.TestRSTTP(itry,theCROCE,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=False,enCHE=False)
                        fails[2]=self.TestRSTTP(itry,theCROCE,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=False,enCHE=True)
                        fails[2]=self.TestRSTTP(itry,theCROCE,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=True,enCHE=False)
                        fails[2]=self.TestRSTTP(itry,theCROCE,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=True,enCHE=True)
                        self.frame.SetStatusText('%s: TEST#2: Test Pulse: Fails=%s'%(theCROCE.Description(),fails[2]), 1)
                    #TEST#3 Reset Pulse
                    if self.frame.vme.BoardTest.chkTest3.IsChecked():
                        fails[3]=self.TestRSTTP(itry,theCROCE,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=False,enCHE=False)
                        fails[3]=self.TestRSTTP(itry,theCROCE,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=False,enCHE=True)
                        fails[3]=self.TestRSTTP(itry,theCROCE,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=True,enCHE=False)
                        fails[3]=self.TestRSTTP(itry,theCROCE,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=True,enCHE=True)
                        self.frame.SetStatusText('%s: TEST#3: Reset Pulse: Fails=%s'%(theCROCE.Description(),fails[3]), 1)
                    #CAUTION: For TEST#4,5,6,7 nwords>=nsend, nwords16%2==1 and SndMemIsFull if addr=1020
                    #because of VME D32 readout restriction when crossing 0FF to 100 address space
                    #which means nBYTES%4=0 <=> nWORDS16bits%2=0 thus (header=10words16)+(data=?nwords16) MUST BE EVEN number 
                    #TEST#4 Write/Send/ReceiveD16 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest4.IsChecked():
                        fails[4]=self.TestWSRfrmsFIFO(itry,theCROCE,fails[4],self.daqWFile,bitErrFreqCHXTest4,nwords16=505,nsend=128,
                            dw='D16',useBLT=False,useRAMMode=includeRAMMode,useRandom=useRandomData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader)
                        self.frame.SetStatusText('%s: TEST#4: Memories D16: Fails=%s'%(theCROCE.Description(),fails[4]), 1)
                    #TEST#5 Write/Send/ReceiveD32 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest5.IsChecked():
                        fails[5]=self.TestWSRfrmsFIFO(itry,theCROCE,fails[5],self.daqWFile,bitErrFreqCHXTest5,nwords16=505,nsend=128,
                            dw='D32',useBLT=False,useRAMMode=includeRAMMode,useRandom=useRandomData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader)
                        self.frame.SetStatusText('%s: TEST#5: Memories D32: Fails=%s'%(theCROCE.Description(),fails[5]), 1)
                    #TEST#6 Write/Send/ReceiveBLT16 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest6.IsChecked():
                        fails[6]=self.TestWSRfrmsFIFO(itry,theCROCE,fails[6],self.daqWFile,bitErrFreqCHXTest6,nwords16=505,nsend=128,
                            dw='D16',useBLT=True,useRAMMode=includeRAMMode,useRandom=useRandomData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader)
                        self.frame.SetStatusText('%s: TEST#6: Memories D16 BLT: Fails=%s'%(fails[6],theCROCE.Description()), 1)
                    #TEST#7 Write/Send/ReceiveBLT32 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest7.IsChecked():
                        fails[7]=self.TestWSRfrmsFIFO(itry,theCROCE,fails[7],self.daqWFile,bitErrFreqCHXTest7,nwords16=505,nsend=128,
                            dw='D32',useBLT=True,useRAMMode=includeRAMMode,useRandom=useRandomData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader)
                        self.frame.SetStatusText('%s: TEST#7: Memories D32 BLT: Fails=%s'%(theCROCE.Description(),fails[7]), 1)
                    #TEST#8 Write/Read random data to Header Register D16 mode
                    if self.frame.vme.BoardTest.chkTest8.IsChecked():
##                        fails[8]=self.TestRegWR(itry,theCROCE,fails[8],theREGAddr)
##                        self.frame.SetStatusText('%s: TEST#8: Register D16: Fails=%s'%(theCROCE.Description(),fails[8]), 1)
##                        if fails[8]!=0: return
                        if useRandomData==False:
                            for iche in range(4):                         
                                theCROCE.Channels()[iche].WriteHeaderData(theREGTestData)
                                for ix in range(1000):
                                    rdata=theCROCE.Channels()[iche].ReadHeaderData()
                                    if rdata!=theREGTestData:
                                        errmsg='TRY#%s, TEST#8: Test Register D16 Error: write=0x%s, read=0x%s'\
                                            %(itry,hex(theREGTestData)[2:].rjust(4,'0'),hex(rdata)[2:].rjust(4,'0'))
                                        UpdateBitErrorFrequency(bitErrFreqCHXTest8[iche],rdata,RegWRHeaderData,self.daqWFile)
                                        fails[8]=fails[8]+1
                                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                        else: print errmsg                                        
                        else:
                            wRndData=int(random.Random().uniform(0,65536))
                            for iche in range(4):                         
                                theCROCE.Channels()[iche].WriteHeaderData(wRndData)
                                for ix in range(1000):
                                    rdata=theCROCE.Channels()[iche].ReadHeaderData()
                                    if rdata!=wRndData:
                                        errmsg='TRY#%s, TEST#8: Test Register D16 Error: write=0x%s, read=0x%s'\
                                            %(itry,hex(wRndData)[2:].rjust(4,'0'),hex(rdata)[2:].rjust(4,'0'))
                                        UpdateBitErrorFrequency(bitErrFreqCHXTest8[iche],rdata,wRndData,self.daqWFile)
                                        fails[8]=fails[8]+1
                                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                        else: print errmsg
                        # Leave all register in default state 
                        for iche in range(4):
                            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
                            theCROCE.Channels()[iche].WriteConfiguration(0x0000)
                            theCROCE.Channels()[iche].WriteHeaderData(0x0000)
                        self.frame.SetStatusText('%s: TEST#8: Test Register D16: Fails=%s'%(theCROCE.Description(),fails[8]), 1)
                    #TEST#9 Test Sequencer
                    if self.frame.vme.BoardTest.chkTest9.IsChecked():
                        if itry==0:
                            for iche in range(4):
                                theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
                        nfebs=itry%16
                        rdfeCounters=[]
                        theCROCE.SendFastCommand(SC_Util.FastCmds['OpenGate'])                          #1
                        for iche in range(4):
                            rdfeCounters.append(theCROCE.Channels()[iche].ReadRDFECounter())            #2
                            theCROCE.Channels()[iche].WriteConfiguration(0xA000+nfebs)                  #3
                        theCROCE.SendSoftwareRDFE()                                                     #4
                        for iche in range(4):
                            for timeout in range(100):
                                if theCROCE.Channels()[iche].ReadRDFECounter()==rdfeCounters[iche]+1:   #5
                                    break
                            if timeout==100:
                                errmsg='TRY#%s, TEST#9.1: Sequencer, %s:%s: ERROR RDFE Counter increment timeout'%(itry,
                                        theCROCE.Description(),theCROCE.Channels()[iche].Description())
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            rcvmem=theCROCE.Channels()[iche].ReadFullDPMBLT()
                            #checking rcvmem length and data content
                            if len(rcvmem)!=nfebs*60:
                                errmsg='TRY#%s, TEST#9.2: Sequencer, %s:%s: ERROR ReceiveMem lenth=%s, should be %s'%(itry,
                                        theCROCE.Description(),theCROCE.Channels()[iche].Description(),len(rcvmem),nfebs*60)
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            #checking registers content after sequencer end
                            framesCounter=theCROCE.Channels()[iche].ReadRcvMemFramesCounter()
                            statusFrame=theCROCE.Channels()[iche].ReadStatusFrame()
                            statusTXRX=theCROCE.Channels()[iche].ReadStatusTXRX()
                            rcvMemWPointer=theCROCE.Channels()[iche].ReadRcvMemWPointer()
                            if framesCounter!=nfebs*3: #discrim+hit0+fpgaregs
                                errmsg='TRY#%s, TEST#9.3: Sequencer, %s:%s: ERROR RcvMemFramesCounter=%s, should be %s'%(itry,
                                    theCROCE.Description(),theCROCE.Channels()[iche].Description(),framesCounter,nfebs*3)
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            if ((nfebs==0 and statusFrame!=0x4440 and statusFrame!=0x5450) or
                                (nfebs!=0 and statusFrame!=0x5410)): 
                                errmsg='TRY#%s, TEST#9.4: Sequencer, %s:%s: ERROR StatusFrame=%s, should be 0x4440/0x5410'%(itry,
                                    theCROCE.Description(),theCROCE.Channels()[iche].Description(),hex(statusFrame))
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            if statusTXRX!=0x2570: 
                                errmsg='TRY#%s, TEST#9.5: Sequencer, %s:%s: ERROR StatusTXRX=%s, should be 0x2570'%(itry,
                                    theCROCE.Description(),theCROCE.Channels()[iche].Description(),hex(statusTXRX))
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            if rcvMemWPointer!=nfebs*60:
                                errmsg='TRY#%s, TEST#9.6: Sequencer, %s:%s: ERROR RcvMemWPointer=%s, should be %s'%(itry,
                                    theCROCE.Description(),theCROCE.Channels()[iche].Description(),rcvMemWPointer,nfebs*60)
                                fails[9]=fails[9]+1
                                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                                else: print errmsg
                            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: length=%s, rcvmem=%s'%(itry,
                            #    theCROCE.Description(),theCROCE.Channels()[iche].Description(),
                            #    len(rcvmem),[hex(d)[2:].rjust(2,'0') for d in rcvmem])
                            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: framesCounter =%s'%(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),framesCounter)
                            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: statusFrame   =%s'%(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),hex(statusFrame))
                            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: statusTXRX    =%s'%(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),hex(statusTXRX))
                            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: rcvMemWPointer=%s'%(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),rcvMemWPointer)
                        # Leave all register in default state 
                        for iche in range(4):
                            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
                            theCROCE.Channels()[iche].WriteConfiguration(0x0000)
                            theCROCE.Channels()[iche].WriteHeaderData(0x0000)
                        self.frame.SetStatusText('%s: TEST#9: Test Sequencer: Fails=%s'%(theCROCE.Description(),fails[9]), 1)
                    #Flush the write file - for each itry in range(ntry)
                    if self.daqWFile!=None: self.daqWFile.flush()
                nfails=0
                for itest in range(1,len(fails)):
                    if fails[itest]!=0:
                        errmsg='%s: TEST#%s FAIL %s times in %s runs'%(theCROCE.Description(),itest,fails[itest],ntry)
                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                        else: print errmsg
                        nfails=nfails+fails[itest]
                        if itest==4:
                            errmsg='BitErrorFrequencyTest4 CH0=%s'%bitErrFreqCHXTest4[0]+\
                                '\nBitErrorFrequencyTest4 CH1=%s'%bitErrFreqCHXTest4[1]+\
                                '\nBitErrorFrequencyTest4 CH2=%s'%bitErrFreqCHXTest4[2]+\
                                '\nBitErrorFrequencyTest4 CH3=%s'%bitErrFreqCHXTest4[3]
                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                            else: print errmsg
                        if itest==5:
                            errmsg='BitErrorFrequencyTest5 CH0=%s'%bitErrFreqCHXTest5[0]+\
                                '\nBitErrorFrequencyTest5 CH1=%s'%bitErrFreqCHXTest5[1]+\
                                '\nBitErrorFrequencyTest5 CH2=%s'%bitErrFreqCHXTest5[2]+\
                                '\nBitErrorFrequencyTest5 CH3=%s'%bitErrFreqCHXTest5[3]
                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                            else: print errmsg
                        if itest==6:
                            errmsg='BitErrorFrequencyTest6 CH0=%s'%bitErrFreqCHXTest6[0]+\
                                '\nBitErrorFrequencyTest6 CH1=%s'%bitErrFreqCHXTest6[1]+\
                                '\nBitErrorFrequencyTest6 CH2=%s'%bitErrFreqCHXTest6[2]+\
                                '\nBitErrorFrequencyTest6 CH3=%s'%bitErrFreqCHXTest6[3]
                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                            else: print errmsg
                        if itest==7:
                            errmsg='BitErrorFrequencyTest7 CH0=%s'%bitErrFreqCHXTest7[0]+\
                                '\nBitErrorFrequencyTest7 CH1=%s'%bitErrFreqCHXTest7[1]+\
                                '\nBitErrorFrequencyTest7 CH2=%s'%bitErrFreqCHXTest7[2]+\
                                '\nBitErrorFrequencyTest7 CH3=%s'%bitErrFreqCHXTest7[3]
                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                            else: print errmsg
                        if itest==8:
                            errmsg='BitErrorFrequencyTest8 CH0=%s'%bitErrFreqCHXTest8[0]+\
                                '\nBitErrorFrequencyTest8 CH1=%s'%bitErrFreqCHXTest8[1]+\
                                '\nBitErrorFrequencyTest8 CH2=%s'%bitErrFreqCHXTest8[2]+\
                                '\nBitErrorFrequencyTest8 CH3=%s'%bitErrFreqCHXTest8[3]
                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                            else: print errmsg
                if nfails==0:
                    errmsg='*** %s: PASS ALL TESTS (%s runs) ***'%(theCROCE.Description(),ntry)
                    if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                    else: print errmsg
                    self.frame.SetStatusText('*** %s: PASS ALL TESTS (%s runs) ***'%(theCROCE.Description(),ntry), 1)
                else:
                    errmsg='%s: TOTAL FAILS %s times in %s runs'%(theCROCE.Description(),nfails,ntry)
                    if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                    else: print errmsg
                    self.frame.SetStatusText('%s: TOTAL FAILS %s times in %s runs'%(theCROCE.Description(),nfails,ntry), 1)
            errmsg='End  : %s'%time.ctime()+'\n********************************'
            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
            else: print errmsg
            if self.daqWFile!=None:
                self.daqWFile.close()
                self.daqWFile=None
        except: ReportException('OnVMEbtnRunBoardTest', self.reportErrorChoice)
    def TestFastCommands(self,itry,theCROCE,fails,daqWFile):
        nfails=fails
        for fcmd in SC_Util.FastCmds:
            for iche in range(4):
                theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus'])
                data=theCROCE.Channels()[iche].ReadAllRegisters()
                #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
                if data[2:6]!=[0x0000,0x4040,0x2410,0x0000]: #FramesCounter,StatusFrame,StatusTXRX,RcvMemWPointer
                    errmsg='TRY#%s, TEST#1.1 Fast Commands=%s, %s:%s: Error ReadAllRegisters=%s, should be [0x0000,0x4040,0x2410,0x0000]'\
                        %(itry,fcmd.ljust(12),theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data[2:6]])
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg                    
            theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
            for iche in range(4):
                if theCROCE.Channels()[iche].ReadStatusTXRX()!=0x2570:
                    errmsg='TRY#%s, TEST#1.2 Fast Commands=%s, %s:%s: Error TXRSStatus=%s, should be 0x2570'\
                        %(itry,fcmd.ljust(12),theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data])
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg
        # Leave all register in default state 
        for iche in range(4):
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0000)
            theCROCE.Channels()[iche].WriteHeaderData(0x0000)
        return nfails
    def TestRSTTP(self,itry,theCROCE,fails,daqWFile,testTP,testRST,enCROCE,enCHE,timeout=10):
        nfails=fails
        if (testTP and testRST) or (not(testTP) and not(testRST)): return nfails
        if testTP: tn1='2'; tn2='Test  Pulse'
        elif testRST: tn1='3'; tn2='Reset Pulse'
        for iche in range(4):
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus'])
            data=theCROCE.Channels()[iche].ReadAllRegisters()
            #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
            if data[2:6]!=[0x0000,0x4040,0x2410,0x0000]: #FramesCounter,StatusFrame,StatusTXRX,RcvMemWPointer
                errmsg='TRY#%s, TEST#%s.1 %s, %s:%s: Error ReadAllRegisters=%s, should be [0x0000,0x4040,0x2410,0x0000]'\
                    %(itry,tn1,tn2,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data[2:6]])
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
        if enCROCE:
            if testTP:  maskcroce=0x0001
            if testRST: maskcroce=0x0100
        else: maskcroce=0x0000
        if enCHE:
            if testTP:  maskche=0x0020
            if testRST: maskche=0x0010
        else: maskche=0x0000
        if (enCROCE and enCHE):
            if testTP: txrxdata=[0x241A,0x241A,0x241A,0x241A]
            if testRST: txrxdata=[0x6C1A,0x6C1A,0x6C1A,0x6C1A]
        else: txrxdata=[0x2410,0x2410,0x2410,0x2410]
        theCROCE.WriteRSTTP(maskcroce)
        data=theCROCE.ReadRSTTP()
        if data!=maskcroce:
            errmsg='TRY#%s, TEST#%s.1 %s, %s: Error RSTTP register: W=%s, R=%s'\
                %(itry,tn1,tn2,theCROCE.Description(),'0x'+hex(maskcroce)[2:].rjust(4,'0'),'0x'+hex(data)[2:].rjust(4,'0'))
            nfails=nfails+1
            if daqWFile!=None: daqWFile.write('\n'+errmsg)
            else: print errmsg            
        for iche in range(4):
            config=(0x000F&theCROCE.Channels()[iche].ReadConfiguration()) | maskche
            theCROCE.Channels()[iche].WriteConfiguration(config)
            data=theCROCE.Channels()[iche].ReadConfiguration()
            if data&0xFC3F!=config:
                errmsg='TRY#%s, TEST#%s.2 %s, txtRAMData%s:%s: Error Configuration register: W=%s, R=%s'\
                    %(itry,tn1,tn2,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),'0x'+hex(config)[2:].rjust(4,'0'),'0x'+hex(data)[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg                
            if (data&0x000F)==0 and enCROCE==True and enCHE==True: txrxdata[iche]=0x241A
        if testTP:
            theCROCE.SendTPOnly()
        if testRST:
            theCROCE.SendRSTOnly()
            if (0x6C1A in txrxdata): time.sleep(3)
            else: time.sleep(0.01)
        for iche in range(4):
            data=theCROCE.Channels()[iche].ReadStatusTXRX()
            if data!=txrxdata[iche]:
                errmsg='TRY#%s, TEST#%s.3 %s, %s:%s: Error TXRSStatus=%s, should be %s'\
                    %(itry,tn1,tn2,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),'0x'+hex(data)[2:].rjust(4,'0'),'0x'+hex(txrxdata[iche])[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
        # Leave all register in default state 
        for iche in range(4):
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0000)
            theCROCE.Channels()[iche].WriteHeaderData(0x0000)
        return nfails
    def TestWSRfrmsFIFO(self,itry,theCROCE,fails,daqWFile,bitErrFreqCHX,nwords16=508,nsend=127,dw='D16',
            useBLT=False,useRAMMode=True,useRandom=False,theRAMData=0xFFFF,theREGHeader=0x1234,timeout=100):
        #V1 channel firmware, Prototype Boards, November 2012, LFE2M20E-5F256C, 
        #BRAMS=1(send)+1(frmstat)+32(receive)=34 out of 66 available
        #nwords16=508=ok, nwords16=510=fail
        #nsend=64 how many times the test sends the frame message
        #CHECK: 64*(4+2*508) = 65280 bytes = 0xFF00 < 0xFFFF=65535 bytes
        #V2 channel firmware, Production Boards, February 2013, LFE2M35E-7F256C, 
        #BRAMS=1(send)+1(frmstat)+64(receive)=66 out of 114 available
        #nwords16=506=ok, nwords16=507=fail
        #nsend=128 how many times the test sends the frame message
        #CHECK: 64*(10+2*506) =  65408 bytes = 0x0FF80 < 0x1FFFF=131071 bytes (message length is 1012+10=1022bytes)
        #CHECK:128*(10+2*506) = 130816 bytes = 0x1FF00 < 0x1FFFF=131071 bytes (message length is 1012+10=1022bytes)
        #CHECK:128*(10+2*505) = 130560 bytes = 0x1FE00 < 0x1FFFF=131071 bytes (message length is 1010+10=1020bytes)
        nfails=fails
        if dw=='D16' and useBLT==False: tn=4
        if dw=='D32' and useBLT==False: tn=5
        if dw=='D16' and useBLT==True: tn=6
        if dw=='D32' and useBLT==True: tn=7
        RndObj=random.Random()
        dev3functiohitnum=[0,1,2,3,4,5,6,0,0,0,0,0,0,0,7,8]
        dev5functiohitnum=[0,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        dev6functiohitnum=[0,24,25,26,27,28,29,30,31,0,0,0,0,0,0,0]
        rcvfrmDataIndex     ='             %s'%[str(d).rjust(4,'0') for d in range(nwords16)]
        frmPointersDataIndex='             %s'%[str(d).rjust(4,'0') for d in range(nsend)]
        #The construction of msgsnd was moved here (from step#4, to be the same message for all channels - 03.07.2013
        if useRandom==False:msgsnd=[d for d in range(nwords16)]
        if useRandom==True: msgsnd=[int(RndObj.uniform(0,65536)) for d in range(nwords16)]
        for iche in range(4):
            theCROCEChannelE=theCROCE.Channels()[iche]
            #1. Set configuration (FIFO mode)
            config=0x03FF & theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration(config)
            #2. Clear status
            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
            #3. Read all registers -> report errors
            #   data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
            data=theCROCEChannelE.ReadAllRegisters()
            if data!=[config,0x0000,0x0000,0x4040,0x2410,0x0000,theREGHeader]:
                errmsg='TRY#%s, TEST#%s.1 Write/Send/Receive Frames, %s:%s: Error ReadAllRegisters=%s, should be [%s,0x0000,0x0000,0x4040,0x2410,0x0000,%s]'\
                    %(itry,tn,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),
                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                      hex(config)[2:].rjust(4,'0'),hex(theREGHeader)[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg                
            #4. Write the message to SndMem in FIFO mode
            for data in msgsnd: theCROCEChannelE.WriteSendMemory(data)
            #5. Read all registers -> report errors
            data=theCROCEChannelE.ReadAllRegisters()
            if data!=[config,0x0000,0x0000,0x0040,0x2410,0x0000,theREGHeader]: 
                errmsg='TRY#%s, TEST#%s.2 Write/Send/Receive Frames, %s:%s: Error ReadAllRegisters=%s, should be [%s,0x0000,0x0000,0x0040,0x2410,0x0000,%s]'\
                    %(itry,tn,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),
                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                      hex(config)[2:].rjust(4,'0'),hex(theREGHeader)[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
            #6. Send the message, nsend times
            for isend in range(nsend):
                #6.1. Change/update the data[isend] from SndMem, in RAM mode, before sending. Do this only for isend>0 
                if isend>0 and useRAMMode==True:
                    theCROCEChannelE.WriteConfiguration(config | 0x4000)
                    theCROCEChannelE.WriteSendMemory(theRAMData, 2*isend)           #change this word16
                    theCROCEChannelE.WriteSendMemory(msgsnd[isend-1], 2*(isend-1))  #recover previous word
                    theCROCEChannelE.WriteConfiguration(config)
                #6.2. Send the message
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendMessage'])
                #6.3. Wait for message received
                for i in range(timeout):
                    data=theCROCEChannelE.ReadAllRegisters()
                    if (data==[config,0x0000+((0x10000&((10+2*nwords16)*(isend+1)))>>1),isend+1,0x1010,0x2410,0xFFFF&((10+2*nwords16)*(isend+1)),theREGHeader]): break
                if (data!=[config,0x0000+((0x10000&((10+2*nwords16)*(isend+1)))>>1),isend+1,0x1010,0x2410,0xFFFF&((10+2*nwords16)*(isend+1)),theREGHeader]):
                    errmsg='TRY#%s, TEST#%s.3 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, ReadAllRegisters=%s, should be [%s,0x0000,%s,0x1010,0x2410,%s,%s]'\
                        %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                          ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                          hex(config)[2:].rjust(4,'0'),'0x'+hex(isend+1)[2:].rjust(4,'0'),
                          '0x'+hex((4+2*nwords16)*(isend+1))[2:].rjust(4,'0'),hex(theREGHeader)[2:].rjust(4,'0'))
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg
            #7.n Repeat READ/CHECK loop BEGIN
            for repeat in range(2):
                #7. Read all nsend received messages (checking readout from ReceiveMemory)
                ibyte=0
                for isend in range(data[2]): #nsend frames, data[2]==RRcvMemFramesCounter
                    #reading frame number "isend"
                    rcvfrmData=[]
                    #7.1. Case D16 
                    if dw=='D16':
                        rcvfrmsDataLengthBytes =theCROCEChannelE.ReadReceiveMemory(ibyte)
                        rcvfrmsStatus          =theCROCEChannelE.ReadReceiveMemory(ibyte+2)
                        rcvfrmsFirmwareDevFunc =theCROCEChannelE.ReadReceiveMemory(ibyte+4)
                        rcvfrmsSourceID        =theCROCEChannelE.ReadReceiveMemory(ibyte+6)
                        rcvfrmsDataLengthBytes2=theCROCEChannelE.ReadReceiveMemory(ibyte+8)
                        if useBLT==False:
                            for i16word in range(ibyte+10, ibyte+rcvfrmsDataLengthBytes, 2):
                                rcvfrmData.append(theCROCEChannelE.ReadReceiveMemory(i16word))
                        if useBLT==True:
                            data16=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RRcvMemory|(ibyte+10),rcvfrmsDataLengthBytes-10,am='A32_U_BLT',dw='D16sw')
                            for i in range(0,len(data16),2):
                                rcvfrmData.append((data16[i+0]<<8) | data16[i+1])
                    #7.2. Case D32 
                    if dw=='D32':
                        data32=theCROCEChannelE.ReadReceiveMemory(ibyte,dw='D32')
                        rcvfrmsDataLengthBytes =(data32&0xFFFF0000)>>16
                        rcvfrmsStatus          =(data32&0x0000FFFF)
                        data32=theCROCEChannelE.ReadReceiveMemory(ibyte+4,dw='D32')
                        rcvfrmsFirmwareDevFunc =(data32&0xFFFF0000)>>16
                        rcvfrmsSourceID        =(data32&0x0000FFFF)
                        data32=theCROCEChannelE.ReadReceiveMemory(ibyte+8,dw='D32')
                        rcvfrmsDataLengthBytes2=(data32&0xFFFF0000)>>16
                        rcvfrmData.append       (data32&0x0000FFFF) #CAUTION on VME D32 restriction when crossing FF address boundaries
                        if useBLT==False:
                            for i32word in range(ibyte+12, ibyte+rcvfrmsDataLengthBytes, 4):
                                data32=theCROCEChannelE.ReadReceiveMemory(i32word,dw='D32')
                                rcvfrmData.append((data32&0xFFFF0000)>>16)
                                rcvfrmData.append((data32&0x0000FFFF))
                            rcvfrmData=rcvfrmData[:((rcvfrmsDataLengthBytes-10)/2)] #truncate for real data because of the above "CAUTION on VME D32"
                        if useBLT==True:
                            data32=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RRcvMemory|(ibyte+12),rcvfrmsDataLengthBytes-12,am='A32_U_BLT',dw='D32sw')
                            for i in range(0,len(data32),4):
                                rcvfrmData.append((data32[i+0]<<8) | data32[i+1])
                                rcvfrmData.append((data32[i+2]<<8) | data32[i+3])
                            rcvfrmData=rcvfrmData[:((rcvfrmsDataLengthBytes-10)/2)] #truncate for real data because of the above "CAUTION on VME D32"
                    #checking frame number "isend"
                    crateid =(0x1000&theREGHeader)>>12
                    croceid =(0x0F00&theREGHeader)>>8
                    febvers =(0x00FF&theREGHeader)
                    febmum  =(0x0F00&msgsnd[0])>>8
                    devfunc =(0x00FF&msgsnd[0])
                    dev     =(0xF0&devfunc)>>4
                    func    =(0x0F&devfunc)
                    hitnum  =0
                    if dev==3: hitnum=dev3functiohitnum[func]
                    if dev==5: hitnum=dev5functiohitnum[func]
                    if dev==6: hitnum=dev6functiohitnum[func]
                    sourceid=((hitnum&0x10)<<15)+(crateid<<14)+((hitnum&0x08)<<15)+(croceid<<9)+(iche<<7)+(febmum<<3)+(hitnum&0x07)
                    #7.3. Checking header bytes of frame number "isend"
                    if rcvfrmsDataLengthBytes!=10+2*nwords16:
                        errmsg='TRY#%s.%s, TEST#%s.4 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word0==RcvFrameLengthBytes=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              rcvfrmsDataLengthBytes,10+2*nwords16)
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    if rcvfrmsStatus!=0x1010:
                        errmsg='TRY#%s.%s, TEST#%s.5 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word1==RcvFrameStatus=%s, should be 0x1010'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              hex(rcvfrmsStatus))
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    if rcvfrmsFirmwareDevFunc!=((febvers<<8)+(devfunc)):
                        errmsg='TRY#%s.%s, TEST#%s.6 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word2==RcvFrameFirmwareDevFunc=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              hex(rcvfrmsFirmwareDevFunc),hex((febvers<<8)+(devfunc)))
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
##                    #CAUTION! can not check the sourceid with V2 header
##                    if rcvfrmsSourceID!=sourceid:
##                        print 'TRY#%s, TEST#%s.7 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word3==RcvFrameSourceID=%s, should be %s'\
##                            %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
##                              hex(rcvfrmsSourceID),hex(sourceid))
##                        print 'crateid=%d, croceid=%d, febvers=%d, febmum=%d, devfunc=%d, hitnum=%d'%(crateid,croceid,febvers,febmum,devfunc,hitnum)
##                        nfails=nfails+1
                    if rcvfrmsDataLengthBytes2!=10+2*nwords16:
                        errmsg='TRY#%s.%s, TEST#%s.8 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word4==RcvFrameLengthBytes=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              rcvfrmsDataLengthBytes2,10+2*nwords16)
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    #7.4. Checking data bytes of frame number "isend"
                    if isend==0:
                        if rcvfrmData!=msgsnd:
                            errmsg='TRY#%s.%s, TEST#%s.9 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, \nSndFrameData=%s, \nRcvFrameData=%s, \n%s'\
                                %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                                  [hex(d)[2:].rjust(4,'0') for d in msgsnd],
                                  [hex(d)[2:].rjust(4,'0') for d in rcvfrmData],rcvfrmDataIndex)
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
                            for i in range(len(rcvfrmData)):
                                if rcvfrmData[i]!=msgsnd[i]:
                                    errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'%(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
                                    UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                    else: print errmsg
                            nfails=nfails+1
                    else:                        
                        if (rcvfrmData[:isend]!=msgsnd[:isend] or rcvfrmData[isend+1:]!=msgsnd[isend+1:] or
                            (useRAMMode==True and rcvfrmData[isend]!=theRAMData) or
                            (useRAMMode==False and rcvfrmData[isend]!=msgsnd[isend])):
                                errmsg='TRY#%s.%s, TEST#%s.10 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, \nSndFrameData=%s, \nRcvFrameData=%s, \n%s'\
                                    %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                                      [hex(d)[2:].rjust(4,'0') for d in msgsnd],
                                      [hex(d)[2:].rjust(4,'0') for d in rcvfrmData],rcvfrmDataIndex)
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                for i in range(len(rcvfrmData)):
                                    if i==isend and useRAMMode==True and rcvfrmData[i]!=theRAMData:
                                        errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'%(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(theRAMData)[2:].rjust(4,'0'))
                                        UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],theRAMData,daqWFile)
                                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                        else: print errmsg
                                    if i==isend and useRAMMode==False and rcvfrmData[i]!=msgsnd[i]:
                                        errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'%(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
                                        UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
                                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                        else: print errmsg
                                    if i!=isend and rcvfrmData[i]!=msgsnd[i]:
                                        errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'%(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
                                        UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
                                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                        else: print errmsg
                                nfails=nfails+1         
                    #7.5. Update pointer ibyte for next frame isend+1
                    ibyte=ibyte+rcvfrmsDataLengthBytes
                    #print '#7.5. Update pointer ibyte for next frame isend=%s+1: ibyte=%s'%(str(isend),str(ibyte)) 
                #8. Read all nsend frame pointers (checking readout from FramePointersMemory)
                frmPointersData=[]
                #8.1. Case D16 
                if dw=='D16':
                    if useBLT==False:
                        for ifrmPointer in range(data[2]):  #data[2]==RRcvMemFramesCounter
                            frmPointersData.append(theCROCEChannelE.ReadFramePointersMemory(2*ifrmPointer))
                    if useBLT==True:
                        data16=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RFramePointersMemory,2*data[2],am='A32_U_BLT',dw='D16sw')
                        for i in range(0,len(data16),2):
                            frmPointersData.append((data16[i+0]<<8) | data16[i+1])       
                #8.2. Case D32 
                if dw=='D32':
                    if useBLT==False:
                        for ifrmPointer in range(0,data[2],2):
                            data32=theCROCEChannelE.ReadFramePointersMemory(2*ifrmPointer,dw='D32')
                            frmPointersData.append((data32&0xFFFF0000)>>16)
                            frmPointersData.append((data32&0x0000FFFF))
                    if useBLT==True:
                        if data[2]%2==0:
                            data32=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RFramePointersMemory,2*data[2],am='A32_U_BLT',dw='D32sw')
                            for i in range(0,len(data32),4):
                                frmPointersData.append((data32[i+0]<<8) | data32[i+1])
                                frmPointersData.append((data32[i+2]<<8) | data32[i+3])
                        else:
                            data32=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RFramePointersMemory,2*(data[2]+1),am='A32_U_BLT',dw='D32sw')
                            for i in range(0,len(data32),4):
                                frmPointersData.append((data32[i+0]<<8) | data32[i+1])
                                frmPointersData.append((data32[i+2]<<8) | data32[i+3])
                            frmPointersData=frmPointersData[:-1]       
                #8.3. Check FramePointersMemory data
                frmpointeris17bits=False
                for ifrmPointer in range(data[2]):
                    if ifrmPointer==0 and frmPointersData[ifrmPointer]!=0x0000:
                        errmsg='TRY#%s.%s, TEST#%s.12 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, \nPointersMemo=%s, \n%s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
                              [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                        errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                            %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*2*(nwords16+5)))
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                        nfails=nfails+1
                    else:
                        if frmPointersData[ifrmPointer]>frmPointersData[ifrmPointer-1]:
                            if ((frmpointeris17bits==False and frmPointersData[ifrmPointer]!=ifrmPointer*2*(nwords16+5)) or
                                (frmpointeris17bits==True  and frmPointersData[ifrmPointer]!=0xFFFF&ifrmPointer*2*(nwords16+5))):
                                errmsg='TRY#%s.%s, TEST#%s.13 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, \nPointersMemo=%s, \n%s'\
                                    %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
                                      [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                                    %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*2*(nwords16+5)))
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                nfails=nfails+1  
                        else:
                            frmpointeris17bits=True
                            if frmPointersData[ifrmPointer]!=0xFFFF&ifrmPointer*2*(nwords16+5):
                                errmsg='TRY#%s.%s, TEST#%s.14 Write/Send/Receive Frames, %s:%s: Error FrameNumber=%s, \nPointersMemo=%s, \n%s'\
                                    %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
                                      [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                                    %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*2*(nwords16+5)))
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                nfails=nfails+1
            #7.n Repeat READ/CHECK loop END
                    
        # Leave all register in default state 
        for iche in range(4):
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0000)
            theCROCE.Channels()[iche].WriteHeaderData(0x0000)
        return nfails
    def TestRegWR(self,itry,theCROCE,fails,theREGAddr):
        RndObj=random.Random()
        nfails=fails
        #baseAddr=theCROCE.controller.baseAddr
        #theAddr=baseAddr+theREGAddr
        #print 'baseAddr='%('0x'+hex(baseAddr)[2:].rjust(8,'0'))
        #print 'theAddr='%('0x'+hex(theAddr)[2:].rjust(8,'0'))
        wdata=int(RndObj.uniform(0,65536))
        theCROCE.controller.WriteCycle(theREGAddr, wdata, am='A32_U_DATA', dw='D16')
        rdata=int(theCROCE.controller.ReadCycle(theREGAddr, am='A32_U_DATA', dw='D16'))
        if wdata!=rdata:
            print 'TRY#%s, TEST#8: Register D16: REGAddr=%s: Error write=%s, read=%s'\
            %(itry,'0x'+hex(theREGAddr)[2:].rjust(8,'0'),'0x'+hex(wdata)[2:].rjust(4,'0'),'0x'+hex(rdata)[2:].rjust(4,'0'))
            nfails=nfails+1
        return nfails

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
    def OnCROCbtnWriteTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data = self.frame.croc.TimingSetup.choiceCLKSource.GetSelection()<<15 | \
                self.frame.croc.TimingSetup.choiceTPDelayEnable.GetSelection()<<12 | \
                int(self.frame.croc.TimingSetup.txtTPDelayValue.GetValue()) & 0x3FF 
            theCROC.WriteTimingSetup(data)
        except: ReportException('OnCROCbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCROCbtnReadTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadTimingSetup()
            self.frame.croc.TimingSetup.choiceCLKSource.SetSelection((data & 0x8000)>>15)
            self.frame.croc.TimingSetup.choiceTPDelayEnable.SetSelection((data & 0x1000)>>12)
            self.frame.croc.TimingSetup.txtTPDelayValue.SetValue(str(data & 0x3FF))
        except: ReportException('OnCROCbtnReadTimingSetup', self.reportErrorChoice)
    def OnCROCbtnSendFastCmd(self, event):
        try:
            theCROC=FindVMEdev(self.vmeCROCs, self.frame.croc.crocNumber<<16)
            fcmd=self.frame.croc.FastCmd.choiceFastCmd.GetStringSelection()
            if (SC_Util.FastCmds.has_key(fcmd)):                
                theCROC.SendFastCommand(SC_Util.FastCmds[fcmd])
            else: wx.MessageBox('Please select a Fast Command')
        except: ReportException('OnCROCbtnSendFastCmd', self.reportErrorChoice)        
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

    # CROCE pannel events ##########################################################
    def OnCROCEbtnWriteTimingSetup(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            data = self.frame.croce.TimingSetup.choiceCLKSource.GetSelection()<<15 | \
                self.frame.croce.TimingSetup.choiceTPDelayEnable.GetSelection()<<12 | \
                int(self.frame.croce.TimingSetup.txtTPDelayValue.GetValue()) & 0x1FF 
            theCROCE.WriteTimingSetup(data)
        except: ReportException('OnCROCEbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCROCEbtnReadTimingSetup(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadTimingSetup()
            self.frame.croce.TimingSetup.choiceCLKSource.SetSelection((data & 0x8000)>>15)
            self.frame.croce.TimingSetup.choiceTPDelayEnable.SetSelection((data & 0x1000)>>12)
            self.frame.croce.TimingSetup.txtTPDelayValue.SetValue(str(data & 0x1FF))
        except: ReportException('OnCROCEbtnReadTimingSetup', self.reportErrorChoice)
    def OnCROCEbtnSendFastCmd(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            fcmd=self.frame.croce.FastCmd.choiceFastCmd.GetStringSelection()
            theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
        except: ReportException('OnCROCEbtnSendFastCmd', self.reportErrorChoice)
    def OnCROCEbtnWriteRSTTP(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            ChXReset=self.frame.croce.ResetAndTestPulse.ChXReset[0].IsChecked()
            ChXTPulse=self.frame.croce.ResetAndTestPulse.ChXTPulse[0].IsChecked()
            data = (ChXReset<<8) | (ChXTPulse<<0)
            theCROCE.WriteRSTTP(data)
        except: ReportException('OnCROCEbtnWriteRSTTP', self.reportErrorChoice)
    def OnCROCEbtnReadRSTTP(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadRSTTP()
            self.frame.croce.ResetAndTestPulse.ChXTPulse[0].SetValue(data & 0x0001)
            self.frame.croce.ResetAndTestPulse.ChXReset[0].SetValue((data & 0x0100) >> 8)
        except: ReportException('OnCROCEbtnReadRSTTP', self.reportErrorChoice)
    def OnCROCEbtnSendRSTOnly(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            theCROCE.SendRSTOnly()
        except: ReportException('OnCROCEbtnSendRSTOnly', self.reportErrorChoice)        
    def OnCROCEbtnSendTPOnly(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            theCROCE.SendTPOnly()
        except: ReportException('OnCROCEbtnSendTPOnly', self.reportErrorChoice)
    def OnCROCEbtnWriteRDFEPulseDelay(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            data = self.frame.croce.RDFESetup.choiceRDFEDelayEnable.GetSelection()<<15 | \
                int(self.frame.croce.RDFESetup.txtRDFEPulseDelayValue.GetValue()) & 0x1FF 
            theCROCE.WriteRDFEPulseDelay(data)
        except: ReportException('OnCROCEbtnWriteRDFEPulseDelay', self.reportErrorChoice)
    def OnCROCEbtnReadRDFEPulseDelay(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadRDFEPulseDelay()
            self.frame.croce.RDFESetup.choiceRDFEDelayEnable.SetSelection((data & 0x8000)>>15)
            self.frame.croce.RDFESetup.txtRDFEPulseDelayValue.SetValue(str(data & 0x1FF))
        except: ReportException('OnCROCEbtnReadRDFEPulseDelay', self.reportErrorChoice)
    def OnCROCEbtnSendRDFESoftware(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            theCROCE.SendSoftwareRDFE()
        except: ReportException('OnCROCEbtnSendRDFESoftware', self.reportErrorChoice)
    def OnCROCEbtnClearLoopDelays(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
            self.OnCROCEbtnReadLoopDelays(None)
        except: ReportException('OnCROCEbtnClearLoopDelays', self.reportErrorChoice)
    def OnCROCEbtnReadLoopDelays(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            for i in range(len(theCROCE.Channels())):
                data=theCROCE.Channels()[i].ReadTXRstTpInDelayCounter()
                self.frame.croce.LoopDelays.txtLoopDelayValues[i].SetValue(str(data))            
        except: ReportException('OnCROCEbtnReadLoopDelays', self.reportErrorChoice)        
    def OnCROCEbtnReportAlignmentsAllCHEs(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.croce.croceNumber<<24)
            theNumberOfMeas=int(self.frame.croce.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croce.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croce.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROCEChannelE in theCROCE.Channels():
                FEB(0).AlignGateDelays(theCROCE,theCROCEChannelE,theNumberOfMeas,theLoadTimerValue,theGateStartValue,theType='CROCE')
        except: ReportException('OnCROCEbtnReportAlignmentsAllCHEs', self.reportErrorChoice)
    def OnCROCEbtnReportAlignmentsAllCROCEs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croc.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croc.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croc.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROCE in self.vmeCROCEs:
                for theCROCEChannelE in theCROCE.Channels():
                    FEB(0).AlignGateDelays(theCROCE,theCROCEChannelE,theNumberOfMeas,theLoadTimerValue,theGateStartValue,theType='CROCE')
        except: ReportException('OnCROCEbtnReportAlignmentsAllCROCEs', self.reportErrorChoice)

    # CHE pannel events ##########################################################
    def OnCHEbtnWriteConfig(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=int(self.frame.che.ConfigurationRegister.txtValueConfig.GetValue(),16) & 0xFFFF
            theCROCEChannelE.WriteConfiguration(data)
        except: ReportException('OnCHEbtnWriteConfig', self.reportErrorChoice)  
    def OnCHEbtnReadConfig(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadConfiguration()
            self.frame.che.ConfigurationRegister.txtValueConfig.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.ConfigurationRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadConfig', self.reportErrorChoice)
    def OnCHEbtnWriteCommands(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            #cmd=0
            cmd=int(self.frame.che.CommandsRegister.chkClearStatus.IsChecked())<<15 | \
                int(self.frame.che.CommandsRegister.chkSendMessage.IsChecked())<<14 | \
                int(self.frame.che.CommandsRegister.chkClearSndMemWPointer.IsChecked())<<13 | \
                int(self.frame.che.CommandsRegister.chkClearRcvMemWPointer.IsChecked())<<12 | \
                int(self.frame.che.CommandsRegister.chkClearRDFECounter.IsChecked())<<11 | \
                int(self.frame.che.CommandsRegister.chkTXSendSyncWords.IsChecked())<<0
            theCROCEChannelE.WriteCommands(cmd)
        except: ReportException('OnCHEbtnWriteCommands', self.reportErrorChoice)
    def OnCHEbtnReadRcvMemWPointerRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRcvMemWPointer()
            self.frame.che.RcvMemWPointerRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRcvMemWPointerRegister', self.reportErrorChoice)
    def OnCHEbtnReadRcvMemFramesCounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRcvMemFramesCounter()
            self.frame.che.RcvMemFramesCounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRcvMemFramesCounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadRDFECounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRDFECounter()
            self.frame.che.RDFECounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRDFECounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadTXRstTpInDelayCounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadTXRstTpInDelayCounter()
            self.frame.che.TXRstTpInDelayCounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadTXRstTpInDelayCounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadStatusFrame(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadStatusFrame()
            self.frame.che.StatusFrameRegister.txtValueStatusFrame.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.StatusFrameRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadStatusFrame', self.reportErrorChoice)
    def OnCHEbtnReadStatusTXRX(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadStatusTXRX()
            self.frame.che.StatusTXRXRegister.txtValueStatusTXRX.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.StatusTXRXRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadStatusTXRX', self.reportErrorChoice)
    def OnCHEbtnWriteHeaderData(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=int(self.frame.che.HeaderDataRegister.txtValueHeaderData.GetValue(),16) & 0xFFFF
            theCROCEChannelE.WriteHeaderData(data)
        except: ReportException('OnCHEbtnWriteHeaderData', self.reportErrorChoice)  
    def OnCHEbtnReadHeaderData(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadHeaderData()
            self.frame.che.HeaderDataRegister.txtValueHeaderData.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.HeaderDataRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadHeaderData', self.reportErrorChoice)
    def OnCHEbtnReadAllRegs(self, event):
        try:
            self.OnCHEbtnReadConfig(None)
            self.OnCHEbtnReadRcvMemWPointerRegister(None)
            self.OnCHEbtnReadRcvMemFramesCounterRegister(None)
            self.OnCHEbtnReadRDFECounterRegister(None)
            self.OnCHEbtnReadTXRstTpInDelayCounterRegister(None)
            self.OnCHEbtnReadStatusFrame(None)
            self.OnCHEbtnReadStatusTXRX(None)
            self.OnCHEbtnReadHeaderData(None)
        except: ReportException('OnCHEbtnReadAllRegs', self.reportErrorChoice)
    def OnCHEbtnWriteSendMemory(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            configBit14=((1<<14) & theCROCEChannelE.ReadConfiguration()) >> 14
            addr=int(self.frame.che.SendMemory.txt3.GetValue(), 10)
            msg=self.frame.che.SendMemory.txt5.GetValue()
            if ((len(msg) % 4) !=0): raise Exception('SendMemory: Data message string must have a muliple of 4 hex characters')
            if configBit14==0:
                #SendMemory is in FIFO mode. Write ALL data words (16bits) at address 0
                if addr!=0: ReportException('SendMemory: Address is ignored in FIFO mode', self.reportErrorChoice)
                nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar
                for i in range(nWords):
                    data = msg[4*i:4*(i+1)]
                    theCROCEChannelE.WriteSendMemory(int(data,16))
            else:
                #SendMemory is in RNDM access mode. Write ONE data word (16bits) at given address
                if ((addr%2)!=0):raise Exception('SendMemory: Address must be a multiple of 2 in RNDM mode')
                if (addr>2040):raise Exception('SendMemory: Address must be less than 2K bytes in RNDM mode')
                if (len(msg)!=4):raise Exception('SendMemory: Data message string must have 4 hex characters in RNDM mode')
                theCROCEChannelE.WriteSendMemory(int(msg,16), addr)
        except: ReportException('OnCHEbtnWriteSendMemory', self.reportErrorChoice)
    def OnCHEbtnReadReceiveMemory(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            msg=''
            nwords=int(self.frame.che.ReceiveMemory.txt3.GetValue(), 10)
            if (nwords>=32768):raise Exception('ReceiveMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadReceiveMemory(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnReadReceiveMemory', self.reportErrorChoice)
        self.frame.che.ReceiveMemory.txt5.SetValue(msg)
    def OnCHEbtnReadFramePointersMemory(self, event):
        try:
            theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            msg=''
            nwords=int(self.frame.che.FramePointersMemory.txt3.GetValue(), 10)
            if (nwords>32768):raise Exception('ReceiveMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadFramePointersMemory(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnReadFramePointersMemory', self.reportErrorChoice)
        self.frame.che.FramePointersMemory.txt5.SetValue(msg)

    # FE pannel events ##########################################################
    def OnFEFPGAbtnRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType) 
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnRead', self.reportErrorChoice)
    def OnFEFPGAbtnDumpRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGADumpRead(theCROCXChannelX, theType)
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnDumpRead', self.reportErrorChoice)  
    def OnFEFPGAbtnWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            sentMessageData=theFEB.ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType)
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnWrite', self.reportErrorChoice)  
    def OnFEFPGAbtnWriteALLThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for febAddress in theCROCXChannelX.FEBs:
                theFEB=FEB(febAddress)
                theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType)
                self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALLThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType)
                    self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALL(self, event):
        try:
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            for theCROCX in vmeCROCXs:
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType)
                        self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALL', self.reportErrorChoice)
    def OnFETRIPbtnRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            rcvMessageData,rcvMFH_10bytes=theFEB.TRIPRead(theCROCXChannelX, theTRIPIndex, theType)
            theFEB.ParseMessageToTRIPtxtRegs(rcvMessageData, theTRIPIndex, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead', self.reportErrorChoice)
    def OnFETRIPbtnRead6(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.TRIPRead(theCROCXChannelX, None, theType)
            theFEB.ParseMessageToTRIPtxtRegs6(rcvMessageData, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead6', self.reportErrorChoice)
    def OnFETRIPbtnWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCXChannelX, theRegs, theTRIPIndex, theType)
        except: ReportException('OnFETRIPbtnWrite', self.reportErrorChoice)
    def OnFETRIPbtnWrite6(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType)
        except: ReportException('OnFETRIPbtnWrite6', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for febAddress in theCROCXChannelX.FEBs:
                theFEB=FEB(febAddress)
                theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType)
                self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType)
                    self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFETRIPbtnWriteALL(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCX in vmeCROCXs:
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType)
                        self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALL', self.reportErrorChoice)
    def OnFETRIPbtnPRGRST(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.TRIPProgramRST(theCROCXChannelX, theType)
        except: ReportException('OnFETRIPbtnPRGRST', self.reportErrorChoice)  
    def OnFETRIPbtnPRGRSTALL(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            for theCROCX in vmeCROCXs:
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        FEB(febAddress).TRIPProgramRST(theCROCXChannelX, theType)
        except: ReportException('OnFETRIPbtnPRGRSTALL', self.reportErrorChoice)  
    def OnFEFLASHbtnReadFlashToFile(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            dlg = wx.FileDialog(self.frame, message='SAVE Flash Configuration', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH WriteFILE %s'%filename, 1)
                f=open(filename,'w')
                for iPage in range(Flash.NPages):
                    pageBytes=theFEB.FLASHMainMemPageRead(theCROCXChannelX, iPage, theType)
                    f.write('%s '%str(iPage).rjust(4,'0').upper())
                    for iByte in pageBytes:
                        f.write('%s'%hex(iByte)[2:].rjust(2,'0').upper())
                    f.write('\n')
                    if iPage%100==0:
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                self.frame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                f.close()
            dlg.Destroy()              
        except: ReportException('OnFEFLASHbtnReadFlashToFile', self.reportErrorChoice)
    def OnFEFLASHbtnCompareFileToFlash(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
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
                    pageBytesRead=theFEB.FLASHMainMemPageRead(theCROCXChannelX, pagesAddrFile[iPage], theType)
                    if pageBytesRead!=pagesBytesFile[iPage]: errPages += '%s '%iPage
                    if iPage%100==0:
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                self.frame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                if errPages!='': raise Exception('ReadFLASH CompFILE Error on page %s'%errPages)                
            dlg.Destroy()              
        except: ReportException('OnFEFLASHbtnCompareFileToFlash', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlash(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=theCROCXChannelX, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=True, toThisCHX=False, toThisCROCX=False, toAllCROCXs=False, theFrame=self.frame, theType=theType)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlash', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=theCROCXChannelX, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=False, toThisCHX=True, toThisCROCX=False, toAllCROCXs=False, theFrame=self.frame, theType=theType)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCH', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=None, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=False, toThisCHX=False, toThisCROCX=True, toAllCROCXs=False, theFrame=self.frame, theType=theType)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCROC', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashALL(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=None, theCROCX=None, theVMECROCXs=self.vmeCROCXs,
                toThisFEB=False, toThisCHX=False, toThisCROCX=False, toAllCROCXs=True, theFrame=self.frame, theType=theType)             
        except: ReportException('OnFEFLASHbtnWriteFileToFlashALL', self.reportErrorChoice)

    # FE DAQ pannel events ##########################################################
    def OnFEDAQradioWriteType(self, event):
        try:
            if self.frame.fe.daq.radioWriteType.GetSelection()==0:
                if self.daqWFile!=None: self.daqWFile.close()
                self.daqWFile=None
            else:
                if self.daqWFile!=None: self.daqWFile.close()
                dlg = wx.FileDialog(self.frame, message='SAVE DAQ Data', defaultDir='', defaultFile='',
                    wildcard='DAQ Data (*.daq)|*.daq|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
                if dlg.ShowModal()==wx.ID_OK:
                    filename=dlg.GetFilename()+'.daq'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                    self.daqWFile=open(wx.FileDialog.GetPath(dlg),'w')
                else:
                    self.frame.fe.daq.radioWriteType.SetSelection(0)
                dlg.Destroy()  
        except: ReportException('OnFEDAQradioWriteType', self.reportErrorChoice)
    def OnFEDAQbtnAcqCtrlStartThread(self, event):
        try:
            #get configuration parameters from GUI
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnAcqCtrlStart - START Acquisition is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                if len(self.threads)==1:
                    self.LogMessage('A thread is running on CROCE, wait to finish or press "STOP Thread" button')
                    return
                theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); theType='CROCE'
                theCROCEChannelE=theCROCE.Channels()[self.frame.fe.chNumber]
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                self.theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
                nEvents=int(self.frame.fe.daq.txtAcqCtrlNEvents.GetValue())
                #1. Setup Channels for RDFE based acquisition: execute 'ClearStatus' and 'ClearRDFECounter'
                #   commands in WriteCommands register and enable RDFE mode (set bit15) in Configuration Register
                if theReadType==0 or theReadType==1:    # RO one FEB | RO one CHE
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                    theCROCEChannelE.WriteConfiguration(0x8000|theCROCEChannelE.ReadConfiguration())
                elif theReadType==2:                    # RO one CROCE
                    for ich in range(4):
                        theCROCE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                        theCROCE.Channels()[ich].WriteConfiguration(0x8000|theCROCE.Channels()[ich].ReadConfiguration())
                elif theReadType==3:                    # RO all CROCEs 
                    for theCTRLE in self.vmeCROCEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                #2. Create and star acquisition thread
                threadNumber=len(self.threads)+1
                thread=WorkerThreadCROCE(threadNumber, self, nEvents,
                    theCROCE, theCROCEChannelE, self.vmeCROCEs, theReadType)
                self.threads.append(thread)
                #self.UpdateThreadCount()
                thread.start()
        except: ReportException('OnFEDAQbtnAcqCtrlStartThread', self.reportErrorChoice)
    def OnFEDAQbtnAcqCtrlStopThread(self, event):
        self.StopThreads()
        #self.UpdateThreadCount()
    def StopThreads(self):
        while self.threads!=[]:
            thread=self.threads[0]
            thread.stop()
            self.threads.remove(thread)
    def LogMessage(self,msg):
        if self.theWriteType==0:
            self.frame.fe.daq.display.AppendText('\n%s'%msg)
        if self.theWriteType==1:
            self.daqWFile.write('\n%s'%msg)
            self.daqWFile.flush()
        if self.theWriteType==2:
            self.frame.fe.daq.display.AppendText('\n%s'%msg)
            self.daqWFile.write('\n%s'%msg)
            self.daqWFile.flush()
    def ThreadFinished(self,thread):
        if thread in self.threads: self.threads.remove(thread)
        self.frame.fe.daq.display.AppendText('\nThread done')
        #self.UpdateThreadCount()
    #def UpdateThreadCount(self):
    #    self.frame.fe.daq.display.AppendText('\nWorkerThreadCROCE: running threads=%d'%len(self.threads))
##    def OnFEDAQbtnAcqCtrlStop(self, event):
##        self.frame.nb.ChangeSelection(0)
##        self.DAQStopEvent.set()
    def OnFEDAQbtnAcqCtrlStart(self, event):
        self.DAQStopEvent.clear()
        try:
            #get configuration parameters from GUI
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnAcqCtrlStart - START Acquisition is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCE=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCEs=self.vmeCROCEs; theType='CROCE'
                theCROCEChannelE=theCROCE.Channels()[self.frame.fe.chNumber]
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
                nEvents=int(self.frame.fe.daq.txtAcqCtrlNEvents.GetValue())
                # This is an RDFE based acquisition:
                #1. Execute 'ClearStatus' and 'ClearRDFECounter' commands in WriteCommands register
                #   and enable RDFE mode (set bit15) in Configuration Register
                if theReadType==0 or theReadType==1:    # RO one FEB | RO one CHE
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                    theCROCEChannelE.WriteConfiguration(0x8000|theCROCEChannelE.ReadConfiguration())
                elif theReadType==2:                    # RO one CROCE
                    for ich in range(4):
                        theCROCE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                        theCROCE.Channels()[ich].WriteConfiguration(0x8000|theCROCE.Channels()[ich].ReadConfiguration())
                elif theReadType==3:                    # RO all CROCEs 
                    for theCTRLE in self.vmeCROCEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                SC_MainMethods.workerDAQSimple(nEvents, self.DAQLock, self.DAQStopEvent,
                    theCROCEChannelE, theCROCE, self.vmeCROCEs, self.frame, theReadType, theWriteType, self.daqWFile)
##                self.thrd=threading.Thread(
##                    target=SC_MainMethods.workerDAQSimple,
##                    name='workerDAQSimple',
##                    args=(nEvents, self.DAQLock, self.DAQStopEvent, theCROCEChannelE, theCROCE, self.vmeCROCEs,
##                          self.frame, theReadType, theWriteType, self.daqWFile))
##                self.thrd.start()
        except: ReportException('OnFEDAQbtnAcqCtrlStart', self.reportErrorChoice)
    def OnFEDAQbtnOpenGateWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16); vmeCROCXs=self.vmeCROCs
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24); vmeCROCXs=self.vmeCROCEs
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            SC_MainMethods.OpenGate(theCROCX, theReadType, vmeCROCXs)
        except: ReportException('OnFEDAQbtnOpenGateWrite', self.reportErrorChoice)
    def OnFEDAQbtnSoftRDFEWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnSoftRDFEWrite - RDFE is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
                theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            #1. Send OpenGate to simulate a new event
            #2. Read the current RDFE trigger counter value
            #3. Enable RDFE bit in Channel's Configuration Register
            #4. Send the RDFE trigger signal
            #5. Check the current RDFE trigger counter value is incremented
            #6. Read the RcvMemory Content
            #7. Disable RDFE bit in Channel's Configuration Register
            if theReadType==0 or theReadType==1:    # RO one FEB | RO one CH
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                          #1
                rdfeCounters=[]
                rdfeCounters.append(theCROCXChannelX.ReadRDFECounter())                         #2
                theCROCXChannelX.WriteConfiguration(0x8000|theCROCXChannelX.ReadConfiguration())#3
                theCROCX.SendSoftwareRDFE()                                                     #4
                for timeout in range(100):
                    if theCROCXChannelX.ReadRDFECounter()==rdfeCounters[0]+1:                   #5
                        break
                SC_MainMethods.DAQReadRcvMemory(rdfeCounters[0]+1, theCROCX, theCROCXChannelX, theType,             
                    vmeCROCXs, theReadType, theWriteType, self.daqWFile, self.frame)            #6
                theCROCXChannelX.WriteConfiguration(0x7FFF&theCROCXChannelX.ReadConfiguration())#7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            elif theReadType==2:                    # RO one CTRL
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                                              #1
                rdfeCounters=[]
                for ich in range(4):
                    rdfeCounters.append(theCROCX.Channels()[ich].ReadRDFECounter())                                 #2
                    theCROCX.Channels()[ich].WriteConfiguration(0x8000|theCROCX.Channels()[ich].ReadConfiguration())#3
                theCROCX.SendSoftwareRDFE()                                                                         #4
                for ich in range(4):
                    for timeout in range(100):
                        if theCROCX.Channels()[ich].ReadRDFECounter()==rdfeCounters[ich]+1:                         #5
                            break
                    SC_MainMethods.DAQReadRcvMemory(rdfeCounters[ich]+1, theCROCX, theCROCX.Channels()[ich], theType,
                        vmeCROCXs, 1, theWriteType, self.daqWFile, self.frame)                                      #6
                    theCROCX.Channels()[ich].WriteConfiguration(0x7FFF&theCROCX.Channels()[ich].ReadConfiguration())#7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            elif theReadType==3:                    # RO all CTRLs
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                for theCTRLX in self.vmeCROCEs:
                    theCTRLX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                                              #1
                    rdfeCounters=[]
                    for ich in range(4):
                        rdfeCounters.append(theCTRLX.Channels()[ich].ReadRDFECounter())                                 #2
                        theCTRLX.Channels()[ich].WriteConfiguration(0x8000|theCTRLX.Channels()[ich].ReadConfiguration())#3
                    theCTRLX.SendSoftwareRDFE()                                                                         #4
                    for ich in range(4):
                        for timeout in range(100):
                            if theCTRLX.Channels()[ich].ReadRDFECounter()==rdfeCounters[ich]+1:                         #5
                                break
                        SC_MainMethods.DAQReadRcvMemory(rdfeCounters[ich]+1, theCTRLX, theCTRLX.Channels()[ich], theType,
                            vmeCROCXs, 1, theWriteType, self.daqWFile, self.frame)                                      #6
                        theCTRLX.Channels()[ich].WriteConfiguration(0x7FFF&theCTRLX.Channels()[ich].ReadConfiguration())#7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            if self.daqWFile!=None: self.daqWFile.flush() 
        except: ReportException('OnFEDAQbtnSoftRDFEWrite', self.reportErrorChoice)
    def OnFEDAQbtnDiscrimBRAMRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            SC_MainMethods.DAQBRAMReadDiscrim(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, 0,
                vmeCROCXs, theReadType, theWriteType, self.daqWFile, self.frame)
            if self.daqWFile!=None: self.daqWFile.flush() 
        except: ReportException('OnFEDAQbtnDiscrimBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnTripBRAMRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            theTripNumber=int(self.frame.fe.daq.txtDataTypeTripNumber.GetValue())
            if not(theTripNumber in range(len(Frame.FuncBRAMReadTripx))) and theTripNumber!=-1:
                raise Exception('Trip number %d is out of range. Select %s or -1 to read all'% \
                    (theTripNumber, range(len(Frame.FuncBRAMReadTripx))))
            SC_MainMethods.DAQBRAMReadTrip(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, theTripNumber,
                vmeCROCXs, theReadType, theWriteType, self.daqWFile, self.frame)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnTripBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnHitBRAMRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            theHitNumber=int(self.frame.fe.daq.txtDataTypeHitNumber.GetValue())
            if not(theHitNumber in range(len(Frame.FuncBRAMReadHitx))) and theHitNumber!=-1:
                raise Exception('Hit number %d is out of range. Select %s or -1 to read all'% \
                    (theHitNumber, range(len(Frame.FuncBRAMReadHitx))))
            SC_MainMethods.DAQBRAMReadHit(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, theHitNumber,
                vmeCROCXs, theReadType, theWriteType, self.daqWFile, self.frame)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnHitBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnReadRcvMem(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.vmeCROCs; theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.vmeCROCEs; theType='CROCE'
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            SC_MainMethods.DAQReadRcvMemory(0, theCROCX, theCROCXChannelX, theType,
                vmeCROCXs, theReadType, theWriteType, self.daqWFile, self.frame)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnReadRcvMem', self.reportErrorChoice)

    # DIG pannel events ##########################################################
    def OnDIGbtnLoadConfigFile(self, event):
        try:            
            thisDIG=FindVMEdev(self.vmeDIGs, self.frame.dig.digNumber<<16)
            dlg = wx.FileDialog(self.frame, message='READ V1720 Configuration', defaultDir='', defaultFile='',
                wildcard='DIG Config (*.digcfg)|*.digcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                flags, lines = self.sc.DIGcfgFileLoad(wx.FileDialog.GetPath(dlg), thisDIG)
                self.frame.dig.display.WriteText('\n'.join(lines)+'\n')
                self.frame.dig.choiceWriteToFile.SetStringSelection(V1720Config.WriteToFile[flags[V1720Config.FileKeyWriteToFile]])
                #self.frame.dig.choiceAppendMode.SetStringSelection(V1720Config.AppendMode[flags[V1720Config.FileKeyAppendMode]])
                self.frame.dig.choiceReadoutMode.SetStringSelection(V1720Config.ReadoutMode[flags[V1720Config.FileKeyReadoutMode]])
                self.frame.dig.chkOutputData.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatData])
                self.frame.dig.chkOutputHeader.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatHeader])
                self.frame.dig.chkOutputConfigInfo.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatConfigInfo])
                self.frame.dig.chkOutputOneLineCH.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatOneLineCH])
                self.frame.dig.chkOutputEventData.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatEventData])
                self.frame.dig.chkOutputEventStat.SetValue(flags[V1720Config.FileKeyOutputFormat] & V1720Config.OutputFormat[V1720Config.FormatEventStat])
            dlg.Destroy()
        except:
            self.sc.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD16
            ReportException('OnDIGbtnLoadConfigFile', self.reportErrorChoice)  
    def OnDIGbtnReadAllRegs(self, event):
        try:
            theDIG=FindVMEdev(self.vmeDIGs, self.frame.dig.digNumber<<16)
            if self.frame.dig.digchNumber in range(8):
                dReadAll=theDIG.Channels()[self.frame.dig.digchNumber].ReadAll()
            else : dReadAll=theDIG.ReadAll()                
            for line in DIGDictOfRegsToString(dReadAll): self.frame.dig.display.WriteText(line+'\n')
        except:
            self.sc.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD16
            ReportException('OnDIGbtnReadAllRegs', self.reportErrorChoice)
    def OnDIGbtnTakeNEvents(self, event):
        event=[]
        try:
            f=None
            if self.frame.dig.choiceWriteToFile.GetStringSelection()!=V1720Config.WriteToFile[0]:
                dlg = wx.FileDialog(self.frame, message='Write Event to File', defaultDir='', defaultFile='',
                    wildcard='Event File (*.evt)|*.evt|All files (*)|*', style=wx.SAVE|wx.CHANGE_DIR)
                if dlg.ShowModal()==wx.ID_OK:
                    OutputFilePath=wx.FileDialog.GetPath(dlg)#+'.evt'
                    if OutputFilePath[-4:]!='.evt': OutputFilePath+='.evt'
                    self.frame.dig.display.WriteText('\nSaving Events to File %s'%OutputFilePath)
                    if self.frame.dig.choiceWriteToFile.GetStringSelection()==V1720Config.WriteToFile[1]:
                        f=open(OutputFilePath,'w')
                    if self.frame.dig.choiceWriteToFile.GetStringSelection()==V1720Config.WriteToFile[2]:
                        f=open(OutputFilePath,'a')   
                dlg.Destroy()
            theDIG=FindVMEdev(self.vmeDIGs, self.frame.dig.digNumber<<16)
            ReadoutMode=self.frame.dig.choiceReadoutMode.GetStringSelection()
            NEvents=int(self.frame.dig.txtNEvents.GetValue())
            iEvent=0; iTry=0
            #check the selected ReadoutMode={0:'Single D32', 1:'BLT32', 2:'MBLT64'}
            if ReadoutMode==V1720Config.ReadoutMode[0]:
                #check for already stored events
                nEventsStored=theDIG.ReadNEventsStored()
                while nEventsStored!=0:
                    event=theDIG.ReadOneEvent()
                    self.frame.dig.display.WriteText('\nEVENTS STORED = %s'%nEventsStored)
                    DIGReportOneEvent(event, f)
                    iEvent+=1
                    if iEvent==NEvents: return
                    nEventsStored=theDIG.ReadNEventsStored()
                NEvents-=iEvent   
                #START aquisition cycle
                theDIG.AcquisitionControlRUN()
                for iEvent in range(NEvents):
                    self.frame.dig.display.WriteText('\nSending one software trigger...')
                    theDIG.SendSoftwareTrigger()
                    event=theDIG.ReadOneEvent()
                    self.DIGReportOneEvent(event, f)
                #STOP aquisition cycle
                theDIG.AcquisitionControlSTOP()
            else : 
                wx.MessageBox('the %s readout mode is not yet implemented'%ReadoutMode)
            if f!=None: f.close()
        except:
            self.frame.dig.display.WriteText('\nEXCEPTION:\n'+ str(event))
            self.sc.controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD16
            theDIG.AcquisitionControlSTOP()
            ReportException('OnDIGbtnTakeNEvents', self.reportErrorChoice)  
    def DIGReportOneEvent(self, event, f):
        if self.frame.dig.chkOutputHeader.GetValue():
            self.frame.dig.display.WriteText('\nHEADER:\n%s'%event.ToStringHeader(0))
            if f!=None: f.write('\nHEADER:\n%s'%event.ToStringHeader(0))
        if self.frame.dig.chkOutputOneLineCH.GetValue(): nCols=1024*1024
        else: nCols=32
        if self.frame.dig.chkOutputData.GetValue():
            self.frame.dig.display.WriteText('\nDATA  :\n'+'\n'.join(event.ToStringData(nValuesPerLine=nCols, typeHex=True)))
            if f!=None: f.write('\nDATA  :\n'+'\n'.join(event.ToStringData(nValuesPerLine=nCols, typeHex=True)))
    def OnDIGbtnRegRead(self, event):
        try:
            theDIG=FindVMEdev(self.vmeDIGs, self.frame.dig.digNumber<<16) 
            addr=int(self.frame.dig.VMEReadWrite.txtReadAddr.GetValue(), 16)
            data=theDIG.ReadRegister(addr)
            data=hex(data)[2:]
            if data[-1]=='L': data=data[:-1]
            self.frame.dig.VMEReadWrite.txtReadData.SetValue(data)
            ##theDIG.RegsWR[regAddr]['value']=regData
            ##theDict={}; theDict[regAddr]=theDIG.RegsWR[regAddr]
            ##for line in DIGDictOfRegsToString(theDict): self.frame.dig.display.WriteText(line+'\n')
        except: ReportException('OnDIGbtnRegRead', self.reportErrorChoice)
    def OnDIGbtnRegWrite(self, event):
        try:
            theDIG=FindVMEdev(self.vmeDIGs, self.frame.dig.digNumber<<16)
            addr=int(str(self.frame.dig.VMEReadWrite.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.dig.VMEReadWrite.txtWriteData.GetValue(), 16)
            theDIG.WriteRegister(addr, data)
        except: ReportException('OnDIGbtnRegWrite', self.reportErrorChoice)

def ReportException(comment, choice):
    msg = comment + ' : ' + str(sys.exc_info()[0]) + ", " + str(sys.exc_info()[1])
    if (choice['display']): print msg
    if (choice['msgBox']): wx.MessageBox(msg)
def ParseDataToListLabels(data, ListLabels, reverse=False):
    if reverse==False:
        for i in range(len(ListLabels)):
            ListLabels[i].Label=str((data & (1<<i))>>i)
    else:
        for i in range(len(ListLabels)):
            ListLabels[len(ListLabels)-1-i].Label=str((data & (1<<i))>>i)
def ParseDataToListCheckBoxs(data, ListCheckBoxs):
    for i in range(len(ListCheckBoxs)):
        ListCheckBoxs[i].SetValue((data & (1<<i))>>i)

def UpdateBitErrorFrequency(bitErrorFrequency,word1,word2,daqWFile):
    index=1
    for bitn in range(16):
        if (index & word1) != (index & word2):
            bitErrorFrequency[15-bitn]=1+bitErrorFrequency[15-bitn]
        index=index<<1
    errmsg='bitErrorFrequency=%s, word1=0x%s, word2=0x%s'%(bitErrorFrequency,hex(word1),hex(word2))
    if daqWFile!=None: daqWFile.write('\n'+errmsg)
    else: print errmsg


        
##def workerDAQSimple(nEvents,theStopEvent,theCTRL,theCTRLChannel,theReadType):
##    try:
##        iEvent=0
##        while (iEvent<nEvents):
##            if theStopEvent.isSet():
##                print 'BREAKING at iEvents=%d, %s'%(iEvent, time.ctime())
##                break
##            #send OpenGate to simulate a new event
##            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
##                theCTRL.SendFastCommand(SC_Util.FastCmds['OpenGate'])
##            elif theReadType==3:                                        # RO all CTRLs
##                for ctrl in theCTRLs:
##                    ctrl.SendFastCommand(SC_Util.FastCmds['OpenGate'])
##            # gives FEBs time to digitize hits: minimum 300microsecs
##            time.sleep(0.001)
##            #send SoftwareRDFE signal
##            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
##                theCTRL.SendSoftwareRDFE()
##            elif theReadType==3:                                        # RO all CTRLs
##                for ctrl in theCTRLs:
##                    ctrl.SendSoftwareRDFE()
##            #pooling RDFE done
##            if theReadType==0 or theReadType==1:                        # RO one FEB or one CH
##                for timeout in range(100):
##                    if theCTRLChannel.ReadRDFECounter()==iEvent+1:
##                        break
##            elif theReadType==2:                                        # RO one CTRL
##                for ich in range(4):
##                    for timeout in range(100):
##                        if theCTRL.Channels()[ich].ReadRDFECounter()==iEvent+1:
##                            break
##            elif theReadType==3:                                        # RO all CTRLs
##                for ctrl in theCTRLs:
##                    for ich in range(4):
##                        for timeout in range(100):
##                            if ctrl.Channels()[ich].ReadRDFECounter()==iEvent+1:
##                                break
##            #readout data...
##            rcvmem=[]
##            if theReadType==0 or theReadType==1:                        # RO one FEB or RO one CH
##                rcvmem.append(['%s:%s'%(theCTRL.Description(), theCTRLChannel.Description()), theCTRLChannel.ReadFullDPMBLT()])
##            elif theReadType==2:                                        # RO one CTRL
##                for ich in range(4):
##                    rcvmem.append(['%s:%s'%(theCTRL.Description(), theCTRL.Channels()[ich].Description()), theCTRL.Channels()[ich].ReadFullDPMBLT()])         
##            elif theReadType==3:                                        # RO all CTRLs
##                for ctrl in theCTRLs:
##                    for ich in range(4):
##                        rcvmem.append(['%s:%s'%(ctrl.Description(), ctrl.Channels()[ich].Description()), ctrl.Channels()[ich].ReadFullDPMBLT()])
##            if iEvent%10==0: print 'iEvents=%d, %s'%(iEvent, time.ctime())
##            time.sleep(0.1)
##            iEvent=iEvent+1
##    except: ReportException('workerDAQSimple', self.reportErrorChoice)     
##


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
