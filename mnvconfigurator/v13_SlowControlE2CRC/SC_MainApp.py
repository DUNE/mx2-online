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
    def __init__(self, theArgs):
        try:
            wx.App.__init__(self)
            self.debug=False
            self.verbose=False
            self.version='v:2.0.13.'
##            for x in theArgs:
##                if x=='d': self.debug=True
##                if x=='v': self.verbose=True
            self.ncrates=2
            self.scs=[]
            self.daqWFile=None
            self.descriptionWFile=None
            self.thrd=None
            self.threads=[]
            self.DAQLock=threading.Lock()
            self.DAQStopEvent=threading.Event()
            self.reportErrorChoice={'display':True, 'msgBox':True}
            self.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)
            self.Bind(wx.EVT_TIMER, self.OnMonitor)
            # Menu events ##########################################################
            self.Bind(wx.EVT_MENU, self.OnMenuLoadHardware, self.frame.menuFileLoadHardware)
            self.Bind(wx.EVT_MENU, self.OnMenuLoadHardwareWithChReset, self.frame.menuFileLoadHardwareWithChReset)            
            self.Bind(wx.EVT_MENU, self.OnMenuLoadFile, self.frame.menuFileLoadFromFile)
            self.Bind(wx.EVT_MENU, self.OnMenuSaveFile, self.frame.menuFileSaveToFile)
            self.Bind(wx.EVT_MENU, self.OnMenuGetHierFromFile, self.frame.menuFileGetHierFromFile)
            self.Bind(wx.EVT_MENU, self.OnMenuUpdateHierToFile, self.frame.menuFileUpdateHierToFile)
            self.Bind(wx.EVT_MENU, self.OnMenuConfigREFE, self.frame.menuConfigREFE)            
            self.Bind(wx.EVT_MENU, self.OnMenuReset, self.frame.menuFileReset)
            self.Bind(wx.EVT_MENU, self.OnClose, self.frame.menuFileQuit)
            self.Bind(wx.EVT_MENU, self.OnMenuShowExpandAll, self.frame.menuShowExpandAll)
            self.Bind(wx.EVT_MENU, self.OnMenuShowCollapseAll, self.frame.menuShowCollapseAll)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsReadAllHV, self.frame.menuActionsReadAllHV)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsSetAllHV, self.frame.menuActionsSetAllHV)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsSTARTMonitorAllHV, self.frame.menuActionsSTARTMonitorAllHV)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsSTOPMonitor, self.frame.menuActionsSTOPMonitor)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsSaveDescription, self.frame.menuActionsSaveDescription)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsWriteDescription, self.frame.menuActionsWriteDescription)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsFontSizeDescription, self.frame.menuActionsFontSizeDescription)
            self.Bind(wx.EVT_MENU, self.OnMenuActionsAbout, self.frame.menuActionsAbout)
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
            self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteSequencerReset, self.frame.crim.TimingModule.SEQUENCERResetRegister.btnWrite)            
            self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnWriteMTMTimingViolationsClear, self.frame.crim.TimingModule.MTMTimingViolationsRegister.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnCRIMTimingbtnReadMTMTimingViolations, self.frame.crim.TimingModule.MTMTimingViolationsRegister.btnRead)
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
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendFastCmdAll, self.frame.croc.FastCmd.btnSendFastCmdAll)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnWriteRSTTP, self.frame.croc.ResetAndTestPulse.btnWriteRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadRSTTP, self.frame.croc.ResetAndTestPulse.btnReadRSTTP)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendRSTOnly, self.frame.croc.ResetAndTestPulse.btnSendRSTOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnSendTPOnly, self.frame.croc.ResetAndTestPulse.btnSendTPOnly)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnClearLoopDelays, self.frame.croc.LoopDelays.btnClearLoopDelays)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReadLoopDelays, self.frame.croc.LoopDelays.btnReadLoopDelays)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllCHs, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllCHs)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllCROCs, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllCROCs)
            self.Bind(wx.EVT_BUTTON, self.OnCROCbtnReportAlignmentsAllCRATEs, self.frame.croc.FEBGateDelays.btnReportAlignmentsAllCRATEs)
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
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnSendFastCmdAll, self.frame.croce.FastCmd.btnSendFastCmdAll)
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
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReportAlignmentsAllCRATEs, self.frame.croce.FEBGateDelays.btnReportAlignmentsAllCRATEs)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReportLoopDelaysStatistic, self.frame.croce.LoopDelaysStatistic.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReportLoopDelaysStatisticALLCROCEs, self.frame.croce.LoopDelaysStatistic.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteStatusAndVersion, self.frame.croce.StatusAndVersionRegister.btnWriteStatusAndVersion)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadStatusAndVersion, self.frame.croce.StatusAndVersionRegister.btnReadStatusAndVersion)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnReadFlashToFile, self.frame.croce.FlashButtons.btnReadFlashToFile)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnCompareFileToFlash, self.frame.croce.FlashButtons.btnCompareFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteFileToFlash, self.frame.croce.FlashButtons.btnWriteFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteFileToFlashThisCRATE, self.frame.croce.FlashButtons.btnWriteFileToFlashThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnCROCEbtnWriteFileToFlashALL, self.frame.croce.FlashButtons.btnWriteFileToFlashALL)
            # CHE pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteConfig, self.frame.che.regs.ConfigurationRegister.btnWriteConfig)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadConfig, self.frame.che.regs.ConfigurationRegister.btnReadConfig)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteCommands, self.frame.che.regs.CommandsRegister.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRcvMemWPointerRegister, self.frame.che.regs.RcvMemWPointerRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRcvMemFramesCounterRegister, self.frame.che.regs.RcvMemFramesCounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadRDFECounterRegister, self.frame.che.regs.RDFECounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadTXRstTpInDelayCounterRegister, self.frame.che.regs.TXRstTpInDelayCounterRegister.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadStatusFrame, self.frame.che.regs.StatusFrameRegister.btnReadStatusFrame)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadStatusTXRX, self.frame.che.regs.StatusTXRXRegister.btnReadStatusTXRX)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteHeaderData, self.frame.che.regs.HeaderDataRegister.btnWriteHeaderData)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadHeaderData, self.frame.che.regs.HeaderDataRegister.btnReadHeaderData)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadAllRegs, self.frame.che.regs.ReadAllRegisters.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnResetThisCHE, self.frame.che.regs.CHEResets.btnResetThisCHE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnResetThisCROCE, self.frame.che.regs.CHEResets.btnResetThisCROCE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnResetThisCRATE, self.frame.che.regs.CHEResets.btnResetThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnResetAllCRATEs, self.frame.che.regs.CHEResets.btnResetAllCRATEs)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnClearStatusThisCHE, self.frame.che.regs.CHEClearStatus.btnResetThisCHE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnClearStatusThisCROCE, self.frame.che.regs.CHEClearStatus.btnResetThisCROCE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnClearStatusThisCRATE, self.frame.che.regs.CHEClearStatus.btnResetThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnClearStatusAllCRATEs, self.frame.che.regs.CHEClearStatus.btnResetAllCRATEs)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteSendMemory, self.frame.che.mems.SendMemory.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadReceiveMemory, self.frame.che.mems.ReceiveMemory.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadFramePointersMemory, self.frame.che.mems.FramePointersMemory.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashMemoryWrite, self.frame.che.mems.FlashMemoryWrite.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashMemoryReadTop, self.frame.che.mems.FlashMemoryReadTop.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashMemoryReadBottom, self.frame.che.mems.FlashMemoryReadBottom.btn1)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnReadFlashToFile, self.frame.che.mems.FlashButtons.btnReadFlashToFile)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnCompareFileToFlash, self.frame.che.mems.FlashButtons.btnCompareFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteFileToFlash, self.frame.che.mems.FlashButtons.btnWriteFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteFileToFlashThisCRATE, self.frame.che.mems.FlashButtons.btnWriteFileToFlashThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnWriteFileToFlashALL, self.frame.che.mems.FlashButtons.btnWriteFileToFlashALL)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdWriteEnable, self.frame.che.mems.FlashBasicCommands.btnFlashCmdWriteEnable)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdWriteDisable, self.frame.che.mems.FlashBasicCommands.btnFlashCmdWriteDisable)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReadStatus, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReadStatus)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdWriteStatus, self.frame.che.mems.FlashBasicCommands.btnFlashCmdWriteStatus)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReadData, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReadData)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdSectorErase, self.frame.che.mems.FlashBasicCommands.btnFlashCmdSectorErase)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdBlockErase, self.frame.che.mems.FlashBasicCommands.btnFlashCmdBlockErase)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdChipErase, self.frame.che.mems.FlashBasicCommands.btnFlashCmdChipErase)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdPageProgram, self.frame.che.mems.FlashBasicCommands.btnFlashCmdPageProgram)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdDeepPowerDown, self.frame.che.mems.FlashBasicCommands.btnFlashCmdDeepPowerDown)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReleaseDPD, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReleaseDPD)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReadID, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReadID)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReadEMandID, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReadEMandID)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdReadSecurity, self.frame.che.mems.FlashBasicCommands.btnFlashCmdReadSecurity)
            self.Bind(wx.EVT_BUTTON, self.OnCHEbtnFlashCmdWriteSecurity, self.frame.che.mems.FlashBasicCommands.btnFlashCmdWriteSecurity)            
            # FE pannel events ##########################################################
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnRead, self.frame.fe.fpga.Registers.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnDumpRead, self.frame.fe.fpga.Registers.btnDumpRead)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWrite, self.frame.fe.fpga.Registers.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALLThisCH, self.frame.fe.fpga.Registers.btnWriteALLThisCH)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALLThisCROC, self.frame.fe.fpga.Registers.btnWriteALLThisCROC)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALLThisCRATE, self.frame.fe.fpga.Registers.btnWriteALLThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnFEFPGAbtnWriteALL, self.frame.fe.fpga.Registers.btnWriteALL)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnRead, self.frame.fe.trip.Registers.btnRead)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnRead6, self.frame.fe.trip.Registers.btnRead6)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWrite, self.frame.fe.trip.Registers.btnWrite)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWrite6, self.frame.fe.trip.Registers.btnWrite6)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALLThisCH, self.frame.fe.trip.Registers.btnWriteALLThisCH)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALLThisCROC, self.frame.fe.trip.Registers.btnWriteALLThisCROC)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALLThisCRATE, self.frame.fe.trip.Registers.btnWriteALLThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnWriteALL, self.frame.fe.trip.Registers.btnWriteALL)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRST, self.frame.fe.trip.Registers.btnPRGRST)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRSTALLThisCH, self.frame.fe.trip.Registers.btnPRGRSTALLThisCH)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRSTALLThisCROC, self.frame.fe.trip.Registers.btnPRGRSTALLThisCROC)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRSTALLThisCRATE, self.frame.fe.trip.Registers.btnPRGRSTALLThisCRATE)
            self.Bind(wx.EVT_BUTTON, self.OnFETRIPbtnPRGRSTALL, self.frame.fe.trip.Registers.btnPRGRSTALL)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnReadFlashToFile, self.frame.fe.flash.FlashButtons.btnReadFlashToFile)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnCompareFileToFlash, self.frame.fe.flash.FlashButtons.btnCompareFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlash, self.frame.fe.flash.FlashButtons.btnWriteFileToFlash)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashThisCH, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashThisCH)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashThisCROC, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashThisCROC)
            self.Bind(wx.EVT_BUTTON, self.OnFEFLASHbtnWriteFileToFlashThisCRATE, self.frame.fe.flash.FlashButtons.btnWriteFileToFlashThisCRATE)
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
            
            #self.OnMenuLoadHardware(None)
            #self.OnMenuShowExpandAll(None)

            self.frame.SetTitle(self.frame.GetTitle()+self.version)
            
        except: ReportException('__init__', self.reportErrorChoice)
        
    def OnInit(self):
        """Create instance of SC frame objects here"""
        #Called by the wx.App parent class when application starts
        self.frame = SC_Frames.SCMainFrame(title='Slow Control - two VME crates ')
        self.SetTopWindow(self.frame)
        self.frame.CenterOnScreen()
        self.frame.Show()
        return True
    def OnClose(self, event):
        self.StopThreads()
        self.frame.Close(True)
        for sc in self.scs: sc.controller.End()

    # MENU events ##########################################################
    def ResetTreeObjects(self):                             #CG v2.0.10
        theThree=self.frame.tree
        theThree.DeleteAllItems()
        theRoot = theThree.AddRoot("VME-BRIDGE")
        for sc in self.scs:
            theSC=theThree.AppendItem(theRoot, sc.Description())
            for dev in sc.vmeCRIMs + sc.vmeCROCs + sc.vmeCROCEs  + sc.vmeDIGs:
                SC_Util.AddTreeNodes(theThree, theSC, [dev.NodeList()])
    def FindAllControllerObjects(self):                     #CG v2.0.10
        for sc in self.scs: sc.controller.End()
        self.scs=[]
        for i in range(self.ncrates):
            sc=SC_MainMethods.SC(linkNum=0, boardNum=i)
            if sc.controller!=None: self.scs.append(sc)
        if self.scs!=[]:
            print '\n'.join(['Found '+sc.Description()+'\nSWRelease='+sc.controller.SWRelease()+\
                '\nBoardFWRelease='+sc.controller.BoardFWRelease()+'\nCAENVME_GetTimeout='+sc.controller.GetTimeout() for sc in self.scs])
    def LoadHardware(self, useChRst):
        """#find CRIMs, CROCs, FEBs, CROEs, FEBsCROCEs for each controller object"""
        try:
            #1. Find all controller objects
            self.FindAllControllerObjects()                
            #2. Find controller's objects lists
            for sc in self.scs:
                sc.FindCRIMs()
                sc.FindCROCs()
                sc.FindCROCEs()
                sc.ConfigCROCEsREFE(self.verbose, ntry=1000, frame=self.frame)
                sc.FindDIGs()
                if sc.vmeCRIMs!=[]:
                    print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCRIMs])
                if sc.vmeCROCs!=[]:
                    print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCROCs])
                    FEBs=sc.FindFEBs(sc.vmeCROCs)
                    if FEBs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+feb for feb in FEBs])
                if sc.vmeCROCEs!=[]:
                    print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCROCEs])
                    FEBs=sc.FindCROCEFEBs(sc.vmeCROCEs, useChRst, self.verbose)
                    if FEBs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+feb for feb in FEBs])
                if sc.vmeDIGs!=[]:
                    print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeDIGs])
            #3. Update self.frame.tree
            self.ResetTreeObjects()
        except: ReportException('LoadHardware', self.reportErrorChoice)
    def OnMenuLoadHardware(self, event):
        """#find CRIMs, CROCs, FEBs, CROEs, FEBsCROCEs for each controller object"""
        self.LoadHardware(useChRst=False)
    def OnMenuLoadHardwareWithChReset(self, event):
        """#find CRIMs, CROCs, FEBs, CROEs, FEBsCROCEs for each controller object"""
        self.LoadHardware(useChRst=True)
    def OnMenuLoadFile(self, event):
        try:
            fileCRIMs=[];fileCROCs=[];fileFPGAs=[];fileTRIPs=[]
            dlg = wx.FileDialog(self.frame, message='READ Hardware Configuration', defaultDir='', defaultFile='',
                wildcard='HW Config (*.hwcfg)|*.hwcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                matchError=[]
                theFile=open(wx.FileDialog.GetPath(dlg),'r')
                for sc in self.scs:
                    matchError.extend(sc.HWcfgFileLoad(theFile, self.frame, len(self.scs)))
                    theFile.seek(0)
                theFile.close()
                if matchError!=[]:
                    raise Exception('The following devices were NOT found in file %s:\n%s'
                        %(wx.FileDialog.GetPath(dlg), '\n'.join(matchError)))
            dlg.Destroy()
        except: ReportException('OnMenuLoadFile', self.reportErrorChoice)
    def OnMenuSaveFile(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='SAVE Hardware Configuration', defaultDir='', defaultFile='',
                wildcard='HW Config (*.hwcfg)|*.hwcfg|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                #filename=dlg.GetFilename()+'.hwcfg'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                theFile=open(wx.FileDialog.GetPath(dlg),'w')
                for sc in self.scs:
                    sc.HWcfgFileSave(theFile)
                theFile.close()
            dlg.Destroy()              
        except: ReportException('OnMenuSaveFile', self.reportErrorChoice)
    def OnMenuGetHierFromFile(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='READ Hierarcy Configuration from File', defaultDir='', defaultFile='',
                wildcard='Hierarchy (*.hier)|*.hier|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                theFile=open(wx.FileDialog.GetPath(dlg),'r')
                #1. Find all controller objects
                line=theFile.readline()
                if line[0:7]=='CRATES:':
                    if int(line[7])>=1 and int(line[7])<=2:
                        self.ncrates=int(line[7])
                    else:
                        raise Exception('Load ERROR: Wrong format in first line %s maximum two crates allowed'%line)
                else:
                    raise Exception('Load ERROR: Wrong format in first line %s must be CRATES:0 or CRATES:1'%line)
                theFile.seek(0)
                self.FindAllControllerObjects()
                if len(self.scs)!=self.ncrates:
                    raise Exception('Load ERROR: Unabble to match the number of VME crates given by hierarchy file %s found %s crates'%(line,len(self.scs)))
                #2. Find controller's objects lists
                for sc in self.scs:
                    sc.GetHierFromFile(theFile, len(self.scs))
                    if sc.vmeCRIMs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCRIMs])
                    if sc.vmeCROCs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCROCs])
                    for theCROC in sc.vmeCROCs:
                        for theCROCChannel in theCROC.Channels():
                            print 'Found %s FEB %s %s %s'%(sc.Description(), theCROC.Description(), theCROCChannel.Description(), theCROCChannel.FEBs) 
                    if sc.vmeCROCEs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeCROCEs])
                    for theCROCE in sc.vmeCROCEs:
                        for theCROCEChannelE in theCROCE.Channels():
                            print 'Found %s FEB %s %s %s'%(sc.Description(), theCROCE.Description(), theCROCEChannelE.Description(), theCROCEChannelE.FEBs)
                            #special requirement for CROCE in TRiggered/Sequencer mode -> all FEBs address must be consecutive, starting with 1
                            cosecutiveTestResult=True
                            for i in range(len(theCROCEChannelE.FEBs)):
                                if theCROCEChannelE.FEBs[i]!=i+1:
                                    cosecutiveTestResult=False
                            if cosecutiveTestResult==False: 
                                print '%s:%s Error FEBs address must be consecutive, starting with 1, found FEBs=%s'\
                                    %(theCROCE.Description(),theCROCEChannelE.Description(),theCROCEChannelE.FEBs)
                    if sc.vmeDIGs!=[]:
                        print '\n'.join(['Found '+sc.Description()+' '+dev.Description() for dev in sc.vmeDIGs])
                    theFile.seek(0)
                theFile.close()
                #3. Update self.frame.tree
                self.ResetTreeObjects()
            dlg.Destroy()            
        except: ReportException('OnMenuGetHierFromFile', self.reportErrorChoice)        
    def OnMenuUpdateHierToFile(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='SAVE Hierarchy Configuration to File', defaultDir='', defaultFile='',
                wildcard='Hierarchy (*.hier)|*.hier|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                #filename=dlg.GetFilename()+'.hwcfg'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                theFile=open(wx.FileDialog.GetPath(dlg),'w')
                theFile.write('CRATES:%s\n'%(len(self.scs)))
                for sc in self.scs:
                    sc.UpdateHierToFile(theFile)
                theFile.close()
            dlg.Destroy()              
        except: ReportException('OnMenuUpdateHierToFile', self.reportErrorChoice)
    def OnMenuConfigREFE(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter a large number for RE/FE FastCmds measurements statistic:',
                caption=self.frame.GetTitle(), defaultValue='5000')
            if dlg.ShowModal()==wx.ID_OK:
                theNumberOfMeas=int(dlg.GetValue())
                self.frame.nb.ChangeSelection(0)
                if theNumberOfMeas<1:
                    raise Exception('N of Meas mut be greater than one')
                for sc in self.scs:
                    sc.ConfigCROCEsREFE(self.verbose, theNumberOfMeas, self.frame)
        except: ReportException('OnMenuConfigREFE', self.reportErrorChoice)
    def OnMenuReset(self, event):
        try:
            for sc in self.scs:
                sc.controller.SystemReset()
        except: ReportException('OnMenuReset', self.reportErrorChoice)
    def OnMenuShowExpandAll(self, event): self.frame.tree.ExpandAll()
    def OnMenuShowCollapseAll(self, event): self.frame.tree.CollapseAll()
    def OnMenuActionsReadAllHV(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter HV Deviation from Target Value in ADC counts',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                self.frame.nb.ChangeSelection(0)
                hvsCROCs=[]
                hvsCROCEs=[]
                for sc in self.scs:
                    hv1,hv2=sc.HVReadAll(int(dlg.GetValue()))
                    hvsCROCs.extend(hv1)
                    hvsCROCEs.extend(hv2)
                hv=['FPGA:%s,%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                    (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], dictHV['FPGA']['CRATE'], \
                     dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                     dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvsCROCs]
                hvE=['FPGA:%s,%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodMan=%s, PeriodAuto=%s, PulseWidth=%s'% \
                    (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROCE'], dictHV['FPGA']['CRATE'], \
                     dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodMan'], \
                     dictHV['PeriodAuto'], dictHV['PulseWidth']) for dictHV in hvsCROCEs]
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
                for sc in self.scs:
                    sc.HVSetAll(int(dlg.GetValue()))
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
                    allCROCs=[];allCROCEs=[]
                    for sc in self.scs:
                        allCROCs.extend(sc.vmeCROCs)
                        allCROCEs.extend(sc.vmeCROCEs)
                    self.frame.nb.ChangeSelection(0)
                    self.monitor=wx.Timer()
                    self.monitor.Start(max(1000, float(dlgTime.GetValue())*1000))
                    self.monitorFunc=FEB.GetAllHVParams
                    self.monitorArgs=FEB(0), allCROCs, 'CROC', int(dlgADC.GetValue())
                    self.monitorArgEs=FEB(0), allCROCEs, 'CROCE', int(dlgADC.GetValue())
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
            hv=['FPGA:%s,%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodAuto=%s'% \
                (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROC'], dictHV['FPGA']['CRATE'], \
                 dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodAuto']) for dictHV in hvs]
            hvE=['FPGA:%s,%s,%s,%s: Actual=%s, Target=%s, A-T=%s, PeriodAuto=%s'% \
                (dictHV['FPGA']['FEB'], dictHV['FPGA']['Channel'], dictHV['FPGA']['CROCE'], dictHV['FPGA']['CRATE'], \
                 dictHV['Actual'], dictHV['Target'], dictHV['A-T'], dictHV['PeriodAuto']) for dictHV in hvEs]
            print '\n'.join(hv)
            print '\n'.join(hvE)
        except: ReportException('OnMonitor', self.reportErrorChoice)
    def OnMenuActionsSaveDescription(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='SAVE Current Description Tab', defaultDir='', defaultFile='',
                wildcard='Description text (*.txt)|*.txt|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                #filename=dlg.GetFilename()+'.hwcfg'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                theFile=open(wx.FileDialog.GetPath(dlg),'w')
                theFile.write(self.frame.description.text.GetValue())
                theFile.close()
            dlg.Destroy()              
        except: ReportException('OnMenuActionsSaveDescription', self.reportErrorChoice)
    def OnMenuActionsWriteDescription(self, event):
        try:
            if self.descriptionWFile!=None: self.descriptionWFile.close()
            self.descriptionWFile=None; self.frame.description.SetWriteFile(self.descriptionWFile)
            dlg = wx.FileDialog(self.frame, message='Write Description to File', defaultDir='', defaultFile='',
                wildcard='Description text (*.txt)|*.txt|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                filename=dlg.GetFilename()+'.txt'; dirname=dlg.GetDirectory(); fullpath=wx.FileDialog.GetPath(dlg)
                self.descriptionWFile=open(wx.FileDialog.GetPath(dlg),'w')
                self.frame.description.SetWriteFile(self.descriptionWFile)
            dlg.Destroy()                
        except: ReportException('OnMenuActionsWriteDescription', self.reportErrorChoice)
    def OnMenuActionsFontSizeDescription(self, event):
        try:
            dlg = wx.TextEntryDialog(self.frame, message='Enter Font Size for Description Tab',
                caption=self.frame.GetTitle(), defaultValue='8')
            if dlg.ShowModal()==wx.ID_OK: self.frame.description.text.SetFont(wx.Font(
                pointSize=int(dlg.GetValue()),family=wx.MODERN,style=wx.NORMAL,weight=wx.NORMAL))
            dlg.Destroy()
        except: ReportException('OnMenuActionsFontSizeDescription', self.reportErrorChoice)
    def OnMenuActionsAbout(self, event):
        try:
            self.frame.nb.ChangeSelection(0)
            print '\n********************************************************************************'
            print '* MINERVA SLOW CONTROL                                                         *'
            print '* Author  : Cristian Gingu, gingu@fnal.gov, x6817                              *'
            print '* Version : %s Release Date: July 27 2015                               *'%(self.version)
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.13. Release Date: July 27 2015                            *'
            print '* 1. Introducing shortcut Action->ClearDescription  CTRL+D                     *'
            print '* 2. In SC_MainObjects->WriteSendReceiveCROCE introducing:                     *'
            print '*    if len(rcvHeaderErr)!=0:                                                  *'
            print '*       print "FrameHeaderError from %s: %s"%(theDescription, rcvHeaderErr)    *'
            print '*       raise Exception(rcvHeaderErr)                                          *'
            print '*    such as to provide with more information when exception is thrown.        *'            
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.12. Release Date: May 01 2015                             *'
            print '* Upgrade for FEB v96 firmware capability -> independent Trip push option.     *'
            print '* Upgrade CROCE_Channel firmware to v5 (file v5_1a_ch1234_ufw.mcs).            *'
            print '* No upgrade necessary on CROCE_Control firmware.                              *'
            print '* 1. The following acquisition modes are now available; set them using         *'
            print '*    WR TripX ACQ Mode in FE->FPGA tab:                                        *'
            print '*    b"00"= Minerva detector mode (v95, v96, TripTs ADC digization is done     *'
            print '*      after each Open Gate.                                                   *'
            print '*    b"01"= MTBF cosmic mode (v95, v96, TripTs ADC digization is done          *'
            print '*      after an open gate ONLY if an External Trigger is sent to FEBs.         *'
            print '*    b"10" = mode b"00" above, only now Trips push independently, new in v96.  *'
            print '*    b"11" = mode b"01" above, only now Trips push independently, new in v96.  *'
            print '* 2. FE->FPGA frame: add 4 new registers, 8-bits, read-only. Thus the total    *'
            print '*    number of regs is increased in v96 from 55 to 59.                         *'
            print '*    R Trip20HitCnt (16-bits) = reg#56 & reg#55 =                              *'
            print '*      = ACQ_MODE(1) & NHitsTrip4(4..3) & NHitsTrip2(4..0) &                   *'
            print '*                      NHitsTrip4(2..0) & NHitsTrip0(4..0)                     *'
            print '*    R Trip31HitCnt (16-bits) = reg#58 & reg#57 =                              *'
            print '*      = ACQ_MODE(1) & NHitsTrip5(4..3) & NHitsTrip3(4..0) &                   *'
            print '*                      NHitsTrip5(2..0) & NHitsTrip1(4..0)                     *'
            print '*    Note that NHitsTripX is a 5-bit number, to accomodate up to 23 hits/Trip  *'
            print '*    Also, both NHitsTrip4 and NHitsTrip5 are currently zero, since these Trips*'
            print '*    are pushing ONLY after the gate closes - zero pushes inside the gate.     *'
            print '*    Also, the WR Spare 8b is still at the end of frame, which is now reg#59.  *'
            print '* 3. Discriminator frame. Up to v95 the NHitsTripX was encoded using two bytes *'
            print '*    at the top of the discriminator frame, data part, second and third byte:  *'
            print '*    NHitsTripX = "000" & NHitsTrip32 & "000" & NHitsTrip10 where              *'
            print '*      NHitsTrip32 = NHitsTrip3 = NHitsTrip2 since they push together, and     *'
            print '*      NHitsTrip10 = NHitsTrip1 = NHitsTrip0 since they push together.         *'
            print '*    With v96, Trips can push independently. A new 16 bit word was introduced  *'
            print '*    labeled NHitsTripX2, following the above NHitsTripX. These two extra bytes*'
            print '*    are present ONLY if ACQ_MODE(1)="1" i.e. independent push mode is selected*'
            print '*    In any cases, NHitsTripX and NHitsTripX2 encoding is as follows:          *'
            print '*    NHitsTripX  = R Trip20HitCnt (16-bits) = reg#56 & reg#55 =                *'
            print '*      = ACQ_MODE(1) & NHitsTrip4(4..3) & NHitsTrip2(4..0) &                   *'
            print '*                      NHitsTrip4(2..0) & NHitsTrip0(4..0)                     *'
            print '*    NHitsTripX2 = R Trip31HitCnt (16-bits) = reg#58 & reg#57 =                *'
            print '*      = ACQ_MODE(1) & NHitsTrip5(4..3) & NHitsTrip3(4..0) &                   *'
            print '*                      NHitsTrip5(2..0) & NHitsTrip1(4..0)                     *'
            print '*    It can be seen that for NHitsTrip4=NHitsTrip5="00000" the NHitsTripX has  *'
            print '*    the same encoding as in v95, where ACQ_MODE(1) bit was not used (0).      *'
            print '*    If NHitsTripX has the MSB set due to ACQ_MODE(1)="1",then Slow Control and*'
            print '*    other DAC software will have a hint that the next two bytes (NHitsTripX2) *'
            print '*    MUST be parsed as Hits Counters too, and then the frame can be decoded as *'
            print '*    usual. The same info is used by the CROCE_Channel firmware in sequencer   *'
            print '*    mode; v5 firmware changes are transparent to users, no need to change any *'
            print '*    related application software.                                             *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.11. Release Date: February 12 2015                        *'
            print '* 1. Updating procedure OnVMEbtnRunBoardTest, #TEST#9 Test Sequencer such as to*'
            print '*    check the Minerva Frame Header bytes.                                     *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.10. Release Date: December 18 2014                        *'
            print '* 1. Removing the call OnMenuLoadHardware() at application startup. Thus the   *'
            print '*    left pane is empty, no CRIM, CROCE or other modules will show up.         *'
            print '* 2. Introducing File->ConfigREFE        CTRL+F                                *'
            print '* 3. Introducing File->UpdateHierToFile  CTRL+U                                *'
            print '* 4. Introducing File->GetHierFromFile   CTRL+G                                *'
            print '* 5. The File->FindHardware still calls ConfigCROCEsREFE, with interface modif *'
            print '*    to include ntry1 for a fixed default of 1000. The new File->ConfigREFE is *'
            print '*    introduced to keep things independent; here the ntry1 is user defined.    *'
            print '*    It is suggested to run the later one time, with very large statistic (at  *'
            print '*    least 5000 meas) for a given hardware setup (i.e. loop cable length) and  *'
            print '*    then save this info, together with all devices settings, into the .hwcfg. *'
            print '*    The Status bar indicates the progress.                                    *'
            print '* 6. The new File->UpdateHierToFile and File->GetHierFromFile use a *.hier file*'
            print '*    which is quite similar with *.hwcfg except no parameter values are written*'
            print '*    into modules, either CRIM, CROC, CROCE, FPGA or Trip. It is meant mostly  *'
            print '*    for fixed system setups like the one underground. The advantage of File-> *'
            print '*    GetHierFromFile is the Slow Control is "loaded" with a given hierarchy    *'
            print '*    (in the left pane) without an effective hardware scan.                    *'
            print '* 7. Introducing two LoopDelaysStatistic buttons in CROCE tab:                 *'
            print '*    7.1. "Report Delays this CROCE": It does a statistic of Loop Delay        *'
            print '*    measurements on all 4 ChannelEs over NMeas times. The average values are  *'
            print '*    displayed in the LoopDelays text boxes above the button, for each channel,*'
            print '*    and also in the Description tab where, for convenience, the ConfigREFE  is*'
            print '*    also reported. The Status bar indicates the progress. The units are 6*53= *'
            print '*    318MHz clock cycles (~3.14ns). For CAT5E cable I measured ~1.5ns/ft.      *'
            print '*    7.2. "Report Delays All CROCEs": It does a statistic of Loop Delay        *'
            print '*    measurements on all CROCEs in the system over NMeas times. The average    *'
            print '*    values are displayed, for each channel and each CROCE,in the Description  *'
            print '*    tab where, for convenience, the ConfigREFE is also reported. The Status   *'
            print '*    bar indicates  the progress.                                              *'
            print '* 8. Add button SendFastCmdAll in CROC tab and CROCE tab. For example use the  *'
            print '*    ResetFPGA FastCmd to reset all FEBs in the system after power up.         *'
            print '* 9. After a power up it is also required to send a File->SysyemReset to reset *'
            print '*    all CROCE and CRIM modules.                                               *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.9. Release Date: December 3 2014                          *'
            print '* 1. Update CAENVMEwrapper.py with the following:                              *'
            print '*    1.1. CAENVMETypes.cvErrorsDict with -5:cvTimeoutError                     *'
            print '*    1.2. CAENVMETypes.cvTimeoutDict = {0:"50us", 1:"400us"}                   *'
            print '*    1.3. Add class CAENVMETypes.CVVMETimeouts                                 *'
            print '*    1.4. Add function Controller.GetTimeout()                                 *'
            print '*    1.5. Add function Controller.SetTimeout(timeouttype)                      *'
            print '* 2. Introducing time.sleep(0.002) in CROCE and CROCEChannelE FlashRead methods*'
            print '*    in an attempt to correct errors seen at Minerva Test Beam Facility setup. *'
            print '* 3. Introducing multiple "ClearStatusOptions" buttons in CHE tab.             *'
            print '* 4. Introducing the following Menu Shortcuts:                                 *'
            print '*    4.1.Find Hardware          CTRL+W                                         *'
            print '*    4.2.Load from File         CTRL+L                                         *'
            print '*    4.3.Save to File           CTRL+S                                         *'
            print '*    4.4.System Reset           CTRL+R                                         *'
            print '*    4.5.Quit                   CTRL+Q                                         *'
            print '*    4.6.Expand All             CTRL+E                                         *'
            print '*    4.7.Collapse All           CTRL+O                                         *'
            print '*    4.8.Read All HVs           CTRL+M                                         *'
            print '*    4.9.Set All HVs            CTRL+N                                         *'
            print '*    4.10.START Monitor All HVs CTRL+H                                         *'
            print '*    4.11.STOP Monitor All HVs  CTRL+K                                         *'
            print '*    4.12.About                 CTRL+A                                         *'           
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.8. Release Date: October 28 2014                          *'
            print '* 1. Update GUI for CRIM->TimingModule tab: (i) add Sequencer Register RESET   *'
            print '*    button (write0x0202 to address 0xC070) and (ii) add MTM Timing Violations *'
            print '*    Register at address 0xC090 with Clear (write0x1001) and Read buttons.     *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.7. Release Date: August 05 2014                           *'
            print '* 1. Cosmetic chage in VME->CROCE Board Test tab: adding Ch0,1,2,3 check boxes *'
            print '*    (default checked) to select channel(s) on which to perform the tests.     *'
            print '* 2. Control FPGA firmware is revised (using Diamond software)                 *'
            print '* 3. Introducing online FLASH programming for Control FPGA.                    *'
            print '*    New Control FPGA componets are:                                           *'
            print '*    (i)  RW Register "FLASH Control" @ 0x0FF070 and                           *'
            print '*    (ii) RW FLASH Memory (as in Channel FPGA), 2048KBytes, starting @ 0x0FF800*'
            print '* 4. Current firmware files are:                                               *'
            print '*    channel: v3_1b_ch1234_ufw.mcs (same, v3)                                  *'
            print '*    control: cvme_05c_3.bit       (updated, v3)                               *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.6. Release Date: January 21st 2014                        *'
            print '* 1. Introducing the QUERY_FPGA command that should be instrumental in online  *'
            print '*    debug when chain communication is lost.                                   *'
            print '* 2. All FEBs send a "PREVIEWDATA" frame (5 bytes) when an ecoded QUERY_FPGA   *'
            print '*    command is sent by the CROCE (simultaneously on all 4 Channels):          *'
            print '*    byte1 == "1000" & FEB_ID;                                                 *'
            print '*    byte2 == TRIP_10_HITCNT;                                                  *'
            print '*    byte3 == TRIP_32_HITCNT;                                                  *'
            print '*    byte4 == HV_READDATA low byte;                                            *'
            print '*    byte5 == HV_READDATA high byte;                                           *'
            print '* 3. The above frame from each FEB in the chain is stored in the CRCE_CHANNEL  *'
            print '*    Receive Memory (see SlowControl GUI tab CHE->Memories) right after the ten*'
            print '*    bytes of a dummy (previous) MFH. Also, the values in tab CHE->Registers   *'
            print '*    will be updated and can be readout. For example RcvMemWPointer=15 and the *'
            print '*    RcvMemFrmConterif=3 if there are 3 FEBs in the chain.                     *'
            print '* 4. The PREVIEW DATA encoded frame is constrained by this logic condition:    *'
            print '*    a. FCMD_QUERY||(EN_PREVIEW_DATA&&TRIPX_ADC_DONE_RE) on FEB v95 and next.  *'
            print '*    b. FCMD_QUERY&&(EN_PREVIEW_DATA&&TRIPX_ADC_DONE_RE) on FEB v91 and prev.  *'
            print '*    (see also tab FE->DAQ->DataType->23Hits for compatibility between discrim *'
            print '*    encoding differences on v95 and v91)                                      *'
            print '* 5. Current firmware files are:                                               *'
            print '*    channel: v3_1b_ch1234_ufw.mcs (updated)                                   *'
            print '*    control: croce_vme_v9a.bit    (same)                                      *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.5. Release Date: December 12th 2013                       *'
            print '* 1. Introducing two CRC bytes at the end of each received frame.              *'
            print '*    The frame length in MFH includes 10 bytes header plus the twoCRC bytes.   *'
            print '* 2. Introducing online FLASH programming for Channels.                        *'
            print '* 3. Current (updated) firmware files are:                                     *'
            print '*    channel: v3_1a_ch1234_ufw.mcs                                             *'
            print '*    control: croce_vme_v9a.bit                                                *'
            print '* 4. Compatible with previous firmware files:                                  *'
            print '*    channel: v2_3e2_ch1234_ufw.mcs                                            *'
            print '*    control: croce_vme_v8n.bit                                                *'
            print '* 5. Compatible with FEB firmware files:                                       *'
            print '*    v91 : currently used                                                      *'
            print '*    v95 : updated version with 23 Hits capability: v95_23anahits.spidata      *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.4. Release Date: August 23rd 2013                         *'
            print '* 1. New Menu option File-> Find Hardware ChRST.                               *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.3. Release Date: August 14th 2013                         *'
            print '* 1. Removed fcmd=ResetFPGA in ConfigCROCEsREFE() because an FPGA reset sets   *'
            print '* GateStart and GateLength regs to defaul values - which is user unconvenient. *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.2. Release Date: August 6th 2013                          *'
            print '* Upgraded CROCE firmwares: croce_vme_v8n.bit and v2_3e2_ch1234_ufw.mcs        *'
            print '* New menu items under "Actions":                                              *'
            print '* 1. "Save Current Description" will save the current text into file.          *'
            print '* 2. "Write Description to File" will start saving new text into a file or stop*'
            print '*     saving if "Cancel" is selected in the pop up window.                     *'
            print '* 3. "Change Font Size" changes "Description" font size.                       *'
            print '* 4. "About" will print this "About" information.                              *'
            print '*------------------------------------------------------------------------------*'
            print '* NOTES: Version 2.0.1.                                                        *'
            print '* Major version upgrade (2.0.x) for two VME crates and CROCEs modules.         *'
            print '********************************************************************************'
        except: ReportException('OnMenuActionsAbout', self.reportErrorChoice)

    # VME pannel events ##########################################################
    def OnVMEbtnWrite(self, event):
        try:
            am=str(self.frame.vme.VMEReadWrite.choiceAddressModifier.GetStringSelection())
            dw=str(self.frame.vme.VMEReadWrite.choiceDataWidth.GetStringSelection())
            addr=int(str(self.frame.vme.VMEReadWrite.txtWriteAddr.GetValue()), 16)
            data=int(self.frame.vme.VMEReadWrite.txtWriteData.GetValue(), 16)
            self.scs[self.frame.vme.crateNumber].controller.WriteCycle(addr, data, am, dw)
        except: ReportException('OnVMEbtnWrite', self.reportErrorChoice)
    def OnVMEbtnRead(self, event):
        try:
            am=str(self.frame.vme.VMEReadWrite.choiceAddressModifier.GetStringSelection())
            dw=str(self.frame.vme.VMEReadWrite.choiceDataWidth.GetStringSelection())
            bltsz=int(self.frame.vme.VMEReadWrite.txtBLTSize.GetValue(), 16)
            addr=int(self.frame.vme.VMEReadWrite.txtReadAddr.GetValue(), 16)
            if am=='A32_U_DATA' or am=='A24_U_DATA':
                data=int(self.scs[self.frame.vme.crateNumber].controller.ReadCycle(addr, am, dw))
                if dw=='D16' or dw=='D16sw': data=hex(data)[2:].rjust(4,'0')
                if dw=='D32' or dw=='D32sw': data=hex(data)[2:].rjust(8,'0')
                self.frame.vme.VMEReadWrite.txtReadData.SetValue(data)
            if am=='A32_U_BLT' or am=='A24_U_BLT':
                data=self.scs[self.frame.vme.crateNumber].controller.ReadCycleBLT(addr, bltsz, am, dw)
                hexdata=[hex(d)[2:].rjust(2,'0') for d in data]
                print 'am=%s: data=%s'%(am,''.join(hexdata))
                self.frame.vme.VMEReadWrite.txtReadData.SetValue(''.join(hexdata))
        except: ReportException('OnVMEbtnRead', self.reportErrorChoice)
    def OnVMEbtnRunBoardTest(self, event):
        try:
            if (self.frame.vme.BoardTest.chkTest4.IsChecked() or
                self.frame.vme.BoardTest.chkTest5.IsChecked() or
                self.frame.vme.BoardTest.chkTest6.IsChecked() or
                self.frame.vme.BoardTest.chkTest7.IsChecked() or
                self.frame.vme.BoardTest.chkTest9.IsChecked()):
                dlg = wx.TextEntryDialog(self.frame, message='Memory and Sequencer tests run ONLY without FEBs connected',
                caption=self.frame.GetTitle(), defaultValue='')
                if dlg.ShowModal()==wx.ID_OK: pass
                else:
                    dlg.Destroy()
                    return
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
            useErrorData=self.frame.vme.BoardTest.chkUseErrorData.IsChecked()
            theRAMData=int(self.frame.vme.BoardTest.txtRAMData.GetValue(),16)
            theREGHeader=0x1FFF&int(self.frame.vme.BoardTest.txtREGHeader.GetValue(),16)
            theREGTestData=int(self.frame.vme.BoardTest.txtREGTestData.GetValue(),16)
            self.frame.vme.BoardTest.txtREGHeader.SetValue('0x'+str(hex(theREGHeader)[2:].rjust(4,'0')))
            theCheckCRC=self.frame.vme.BoardTest.chkIncludeCRCCheck.IsChecked()
            theCheckCh=[]
            for i in range(4):
                if self.frame.vme.BoardTest.chkCh[i].IsChecked():
                    theCheckCh.append(i)
            if theCheckCh==[]:
                errmsg='At least one channel must be selected tor testing'
                print errmsg
                wx.MessageBox(errmsg)
                return;
            for theCROCE in self.scs[self.frame.vme.crateNumber].vmeCROCEs:
                for iche in theCheckCh: theCROCE.Channels()[iche].WriteHeaderData(theREGHeader)
            errmsg='********************************'+\
                   '\n* CROCE BOARD TEST RUN RESULTS *'+\
                   '\n********************************'+\
                   '\nStart: %s'%time.ctime()
            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
            else: print errmsg
            for theCROCE in self.scs[self.frame.vme.crateNumber].vmeCROCEs:
                #---------------------------------------------------------------
                #BEGIN loop over all theCROCE in self.scs[this crate]
                fails=10*[0]
                tests=10*[False]
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
                    #-----------------------------------------------------------
                    #BEGIN itry loop with all active TEST#X tests
                    #if itry%100==0:
                    self.frame.description.text.Refresh(); self.frame.description.text.Update()
                    self.frame.SetStatusText('Testing...%s'%itry, 0)
                    #TEST#1 Fast Commands
                    if self.frame.vme.BoardTest.chkTest1.IsChecked():
                        tests[1]=True
                        fails[1]=self.TestFastCommands(itry,theCROCE,theCheckCh,fails[1],self.daqWFile)
                        self.frame.SetStatusText('%s: TEST#1: Fast Command: Fails=%s'%(theCROCE.Description(),fails[1]), 1)
                    #TEST#2 Test Pulse
                    if self.frame.vme.BoardTest.chkTest2.IsChecked():
                        tests[2]=True
                        fails[2]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=False,enCHE=False)
                        fails[2]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=False,enCHE=True)
                        fails[2]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=True,enCHE=False)
                        fails[2]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[2],self.daqWFile,testTP=True,testRST=False,enCROCE=True,enCHE=True)
                        self.frame.SetStatusText('%s: TEST#2: Test Pulse: Fails=%s'%(theCROCE.Description(),fails[2]), 1)
                    #TEST#3 Reset Pulse
                    if self.frame.vme.BoardTest.chkTest3.IsChecked():
                        tests[3]=True
                        fails[3]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=False,enCHE=False)
                        fails[3]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=False,enCHE=True)
                        fails[3]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=True,enCHE=False)
                        fails[3]=self.TestRSTTP(itry,theCROCE,theCheckCh,fails[3],self.daqWFile,testTP=False,testRST=True,enCROCE=True,enCHE=True)
                        self.frame.SetStatusText('%s: TEST#3: Reset Pulse: Fails=%s'%(theCROCE.Description(),fails[3]), 1)
                    #-----------------------------------------------------------
                    #As of November 2013:
                    #CAUTION D32 compatibility: if theCROCE.includeCRC==False : 0x1FFFF=131071 > nsend*(10+2*nwords16+0) % 4 == 0 
                    #CAUTION D32 compatibility: if theCROCE.includeCRC==True  : 0x1FFFF=131071 > nsend*(10+2*nwords16+2) % 4 == 0
                    #-----------------------------------------------------------
                    nsend=128
                    if theCROCE.includeCRC==True: nwords16=504  #10+2*504+2=1020 % 4 == 0
                    else: nwords16=505                          #10+2*505+0=1020 % 4 == 0
                    #TEST#4 Write/Send/ReceiveD16 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest4.IsChecked():
                        tests[4]=True
                        fails[4]=self.TestWSRfrmsFIFO(itry,theCROCE,theCheckCh,fails[4],self.daqWFile,bitErrFreqCHXTest4,nwords16,nsend,
                            dw='D16',useBLT=False,useRAMMode=includeRAMMode,useRandom=useRandomData,useErrorData=useErrorData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader,theCheckCRC=theCheckCRC)
                        self.frame.SetStatusText('%s: TEST#4: Memories D16: Fails=%s'%(theCROCE.Description(),fails[4]), 1)
                    #TEST#5 Write/Send/ReceiveD32 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest5.IsChecked():
                        tests[5]=True
                        fails[5]=self.TestWSRfrmsFIFO(itry,theCROCE,theCheckCh,fails[5],self.daqWFile,bitErrFreqCHXTest5,nwords16,nsend,
                            dw='D32',useBLT=False,useRAMMode=includeRAMMode,useRandom=useRandomData,useErrorData=useErrorData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader,theCheckCRC=theCheckCRC)
                        self.frame.SetStatusText('%s: TEST#5: Memories D32: Fails=%s'%(theCROCE.Description(),fails[5]), 1)
                    #TEST#6 Write/Send/ReceiveBLT16 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest6.IsChecked():
                        tests[6]=True
                        fails[6]=self.TestWSRfrmsFIFO(itry,theCROCE,theCheckCh,fails[6],self.daqWFile,bitErrFreqCHXTest6,nwords16,nsend,
                            dw='D16',useBLT=True,useRAMMode=includeRAMMode,useRandom=useRandomData,useErrorData=useErrorData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader,theCheckCRC=theCheckCRC)
                        self.frame.SetStatusText('%s: TEST#6: Memories D16 BLT: Fails=%s'%(fails[6],theCROCE.Description()), 1)
                    #TEST#7 Write/Send/ReceiveBLT32 Frames in FIFO/RAM mode
                    if self.frame.vme.BoardTest.chkTest7.IsChecked():
                        tests[7]=True
                        fails[7]=self.TestWSRfrmsFIFO(itry,theCROCE,theCheckCh,fails[7],self.daqWFile,bitErrFreqCHXTest7,nwords16,nsend,
                            dw='D32',useBLT=True,useRAMMode=includeRAMMode,useRandom=useRandomData,useErrorData=useErrorData,
                            theRAMData=theRAMData,theREGHeader=theREGHeader,theCheckCRC=theCheckCRC)
                        self.frame.SetStatusText('%s: TEST#7: Memories D32 BLT: Fails=%s'%(theCROCE.Description(),fails[7]), 1)
                    #TEST#8 Write/Read random data to Header Register D16 mode
                    if self.frame.vme.BoardTest.chkTest8.IsChecked():
                        tests[8]=True
                        fails[8]=self.TestRegWR(itry,theCROCE,theCheckCh,fails[8],theREGTestData,theREGHeader,useRandomData,bitErrFreqCHXTest8)
                        self.frame.SetStatusText('%s: TEST#8: Test Register D16: Fails=%s'%(theCROCE.Description(),fails[8]), 1)
                    #TEST#9 Test Sequencer
                    if self.frame.vme.BoardTest.chkTest9.IsChecked():
                        tests[9]=True
                        fails[9]=self.TestSequencer(itry,theCROCE,theCheckCh,fails[9],theREGHeader)
                        self.frame.SetStatusText('%s: TEST#9: Sequencer: Fails=%s'%(theCROCE.Description(),fails[9]), 1)
                    #
                    #Flush the write file - for each itry in range(ntry)
                    if self.daqWFile!=None: self.daqWFile.flush()
                    #END itry loop with all active TEST#X tests
                    #-----------------------------------------------------------
                nfails=0
                for itest in range(1,len(fails)):
                    if fails[itest]==0 and tests[itest]==True:
                        errmsg='%s: TEST#%s PASS %s times in %s runs'%(theCROCE.Description(),itest,ntry,ntry)
                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                        else: print errmsg                        
                    if fails[itest]!=0 and tests[itest]==True:
                        errmsg='%s: TEST#%s FAIL %s times in %s runs'%(theCROCE.Description(),itest,fails[itest],ntry)
                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                        else: print errmsg
                        nfails=nfails+fails[itest]
##                        if itest==4:
##                            errmsg='BitErrorFrequencyTest4 CH0=%s'%bitErrFreqCHXTest4[0]+\
##                                '\nBitErrorFrequencyTest4 CH1=%s'%bitErrFreqCHXTest4[1]+\
##                                '\nBitErrorFrequencyTest4 CH2=%s'%bitErrFreqCHXTest4[2]+\
##                                '\nBitErrorFrequencyTest4 CH3=%s'%bitErrFreqCHXTest4[3]
##                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
##                            else: print errmsg
##                        if itest==5:
##                            errmsg='BitErrorFrequencyTest5 CH0=%s'%bitErrFreqCHXTest5[0]+\
##                                '\nBitErrorFrequencyTest5 CH1=%s'%bitErrFreqCHXTest5[1]+\
##                                '\nBitErrorFrequencyTest5 CH2=%s'%bitErrFreqCHXTest5[2]+\
##                                '\nBitErrorFrequencyTest5 CH3=%s'%bitErrFreqCHXTest5[3]
##                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
##                            else: print errmsg
##                        if itest==6:
##                            errmsg='BitErrorFrequencyTest6 CH0=%s'%bitErrFreqCHXTest6[0]+\
##                                '\nBitErrorFrequencyTest6 CH1=%s'%bitErrFreqCHXTest6[1]+\
##                                '\nBitErrorFrequencyTest6 CH2=%s'%bitErrFreqCHXTest6[2]+\
##                                '\nBitErrorFrequencyTest6 CH3=%s'%bitErrFreqCHXTest6[3]
##                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
##                            else: print errmsg
##                        if itest==7:
##                            errmsg='BitErrorFrequencyTest7 CH0=%s'%bitErrFreqCHXTest7[0]+\
##                                '\nBitErrorFrequencyTest7 CH1=%s'%bitErrFreqCHXTest7[1]+\
##                                '\nBitErrorFrequencyTest7 CH2=%s'%bitErrFreqCHXTest7[2]+\
##                                '\nBitErrorFrequencyTest7 CH3=%s'%bitErrFreqCHXTest7[3]
##                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
##                            else: print errmsg
##                        if itest==8:
##                            errmsg='BitErrorFrequencyTest8 CH0=%s'%bitErrFreqCHXTest8[0]+\
##                                '\nBitErrorFrequencyTest8 CH1=%s'%bitErrFreqCHXTest8[1]+\
##                                '\nBitErrorFrequencyTest8 CH2=%s'%bitErrFreqCHXTest8[2]+\
##                                '\nBitErrorFrequencyTest8 CH3=%s'%bitErrFreqCHXTest8[3]
##                            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
##                            else: print errmsg
                if nfails==0:
                    errmsg='\t%s: PASS ALL TESTS (%s runs) ***'%(theCROCE.Description(),ntry)
                    if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                    else: print errmsg
                    self.frame.SetStatusText('*** %s: PASS ALL TESTS (%s runs) ***'%(theCROCE.Description(),ntry), 1)
                else:
                    errmsg='\t%s: TOTAL FAILS %s times in %s runs'%(theCROCE.Description(),nfails,ntry)
                    if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                    else: print errmsg
                    self.frame.SetStatusText('%s: TOTAL FAILS %s times in %s runs'%(theCROCE.Description(),nfails,ntry), 1)
                #END loop over all theCROCE in self.scs[this crate]
                #---------------------------------------------------------------
            errmsg='End  : %s'%time.ctime()+'\n******************************'
            if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
            else: print errmsg
            if self.daqWFile!=None:
                self.daqWFile.close()
                self.daqWFile=None
        except: ReportException('OnVMEbtnRunBoardTest', self.reportErrorChoice)

    def TestFastCommands(self,itry,theCROCE,theCheckCh,fails,daqWFile):
        nfails=fails
        for fcmd in SC_Util.FastCmds:
            for iche in theCheckCh:
                theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus'])
                data=theCROCE.Channels()[iche].ReadAllRegisters()
                #data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
                if data[2:6]!=[0x0000,0x4040,0x2410,0x0000]: #FramesCounter,StatusFrame,StatusTXRX,RcvMemWPointer
                    errmsg='TRY#%s, TEST#1.1 Fast Commands=%s, %s:%s: Error ClearStatus ReadAllRegisters=%s, should be [0x0000,0x4040,0x2410,0x0000]'\
                        %(itry,fcmd.ljust(12),theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data[2:6]])
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg                    
            theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
            for iche in theCheckCh:
                if theCROCE.Channels()[iche].ReadStatusTXRX()!=0x2570:
                    errmsg='TRY#%s, TEST#1.2 Fast Commands=%s, %s:%s: Error TXRSStatus=%s, should be 0x2570'\
                        %(itry,fcmd.ljust(12),theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),['0x'+hex(d)[2:].rjust(4,'0') for d in data])
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg
        # Leave all register in default state 
        for iche in theCheckCh:
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0BC0&theCROCE.Channels()[iche].ReadConfiguration())
        return nfails
    def TestRSTTP(self,itry,theCROCE,theCheckCh,fails,daqWFile,testTP,testRST,enCROCE,enCHE,timeout=10):
        nfails=fails
        if (testTP and testRST) or (not(testTP) and not(testRST)): return nfails
        if testTP: tn1='2'; tn2='Test  Pulse'
        elif testRST: tn1='3'; tn2='Reset Pulse'
        for iche in theCheckCh:
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
        for iche in theCheckCh:
            config=(0xFC0F&theCROCE.Channels()[iche].ReadConfiguration()) | maskche
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
        for iche in theCheckCh:
            data=theCROCE.Channels()[iche].ReadStatusTXRX()
            if data!=txrxdata[iche]:
                errmsg='TRY#%s, TEST#%s.3 %s, %s:%s: Error TXRSStatus=%s, should be %s'\
                    %(itry,tn1,tn2,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),'0x'+hex(data)[2:].rjust(4,'0'),'0x'+hex(txrxdata[iche])[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
        # Leave all register in default state 
        for iche in theCheckCh:
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0BC0&theCROCE.Channels()[iche].ReadConfiguration())            
        return nfails
    def TestWSRfrmsFIFO(self,itry,theCROCE,theCheckCh,fails,daqWFile,bitErrFreqCHX,nwords16=508,nsend=127,
            dw='D16',useBLT=False,useRAMMode=True,useRandom=False,useErrorData=False,
            theRAMData=0xFFFF,theREGHeader=0x1234,theCheckCRC=False,timeout=100):
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
        #CHECK:128*(10+2*505) = 130560 bytes = 0x1FE00 < 0x1FFFF=131071 bytes (message length is 1010+10=1020bytes % 4 == 0, good)
        #CHECK:1*(10+2*12+2) = 130560 bytes = 0x1FE00 < 0x1FFFF=131071 bytes (message length is 1010+10=1020bytes % 4 == 0, good)
        #CHECK:128*(10+2*504+2) = 130560 bytes = 0x1FE00 < 0x1FFFF=131071 bytes (message length is 1008+10+2=1020bytes % 4 == 0, good)
        #-----------------------------------------------------------
        #As of November 2013:
        #CAUTION D32 compatibility: if theCROCE.includeCRC==False : 0x1FFFF=131071 > nsend*(10+2*nwords16+0) % 4 == 0 
        #CAUTION D32 compatibility: if theCROCE.includeCRC==True  : 0x1FFFF=131071 > nsend*(10+2*nwords16+2) % 4 == 0 
        #-----------------------------------------------------------
        nfails=fails
        repeatRead=1
        forceCorrectValues=False
        quitFirstError=True
        if dw=='D16' and useBLT==False: tn=4
        if dw=='D32' and useBLT==False: tn=5
        if dw=='D16' and useBLT==True:  tn=6
        if dw=='D32' and useBLT==True:  tn=7
        RndObj=random.Random()
        dev3functiohitnum=[0,1,2,3,4,5,6,0,0,0,0,0,0,0,7,8]
        dev5functiohitnum=[0,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
        rcvfrmDataIndex     ='             %s'%[str(d).rjust(4,'0') for d in range(nwords16)]
        frmPointersDataIndex='             %s'%[str(d).rjust(4,'0') for d in range(nsend)]
        #!!!CAUTION!!! The FLASH Page has 528 hex charactes == 264bytes.
        #The received frame will be 10+264=274bytes % 4 = 2 => MUST ADD two bytes at the end for D32 reading compatibility
        #The received frame will be 10+264+2=276bytes % 4 = 0 => has D32 reading compatibility
        '                                                                                                                      100                                                                                                 200                                                                                                 300                                                                                                 400                                                                                                 500                           '                                                                          
        '                             10        20        30        40        50        60        70        80        90         0        10        20        30        40        50        60        70        80        90         0        10        20        30        40        50        60        70        80        90         0        10        20        30        40        50        60        70        80        90         0        10        20        30        40        50        60        70        80        90         0        10        20       '
        '                    012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567'
        #The Page#41 from FLASH with firmware FEB version v91 (264bytes) is:
        theErrorDataV91P041='000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFAA55FFFF00000000FFFFFFFFFFFFFFFFF00FFFFFFFFFFFFF0000000000000000000000000000000000C000000000000000000000000000000000000000000000000000000000C060040200000000000000000000000000000000000000004820040A00000DC00020040A0940080C5020000A19000C0C5020040A0881000040200603000000000000040A000000000020040A08000000000000000000000040200402000000005000040B0000000050000400'
        #The Page#595 and 711 from FLASH with firmware FEB version v95 (264bytes) are:
        theErrorDataV95P595='0000FFFFFFFFAAE2AEA2FFFFFFFFFFFFFFFF00000000B000FFFFFFFFFFFF0000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFBFFFFF7FFFFFFFF8000FFFF7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF8000FFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFF0000000000000000000000000000000000000000000000000000000000000000000000120000000000000000000000000402310009A0300009A0300009A030000128300000000000000000000120300009203000000000000000000009283000000030001328300400047800000030000004780000047800120478040124700001203000012C700001203000000000000000000001283000000000000D22'
        theErrorDataV95P711='000000000000CC33FFFF00000000FFFFFFFF33CCFFFFC040FFFFDDDDFFFFFF55FFFF00000000AA55FFFFAA55FFFFFFFFFFFFDDDD33CCFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF80A0FFFFDDDDFFFF0FF0FFFF9999FFFFFFFFFFFFFFFFFFFFFFFF8000FFFFFFFFAA55FFFFFFFFFFFFFFBFFFFFFFFFFFFF00000000FFFFFFFFC3C3FFFFFFFFFFFF00000000FFFFFFFFFFFF8000FFFFFFFF0000000000000000000000000000000000000000006000000100000001010000000000000000000001AC000001050000000000000400000000000000040B00000000D0200000000000000000040A00000000A080040300000000500000000000000050000000000000004020040A'
        theErrorData=theErrorDataV91P041
        #The construction of msgsnd was moved here (from step#4, to be the same message for all channels - 03.07.2013
        msgsnd=[]
        if useRandom==True  and useErrorData==True:
            raise Exception('Can NOT HAVE both "Use ERROR Patter" and "Use Random Data" checked')
        if useRandom==False and useErrorData==False:
            msgsnd=[d for d in range(nwords16)]
        if useRandom==True  and useErrorData==False:
            msgsnd=[int(RndObj.uniform(0,65536)) for d in range(nwords16)]
        if useRandom==False and useErrorData==True:
            if len(theErrorData)!=528:
                raise Exception('When using Error Data Pattern the length of the pattern must be 528 hex characters, 264 bytes, 132 words16bits, 66 words32bits')
            for i in range(0,528,4):
                msgsnd.append(int(theErrorData[i:i+4],16))
            if theCROCE.includeCRC==False: msgsnd.append(0x0000) #SEE above CAUTION D32 compatibility
            if theCROCE.includeCRC==True: pass                   #SEE above CAUTION D32 compatibility
            nwords16=len(msgsnd)  #overwrite actual parameter nwords16
            nsend=1 #133          #overwrite actual parameter nsend
            #rotate left this pattern 
            msgsnd=msgsnd[itry:]+msgsnd[:itry]
        ##print 'theCROCE.Description()=%s, theCROCE.includeCRC=%s'%(theCROCE.Description(),theCROCE.includeCRC)
        ##print 'itry=%d, nwords16=%s, len(msgsnd)=%s, msgsnd=%s'%(itry,nwords16,len(msgsnd),''.join([hex(w16)[2:].rjust(4,'0') for w16 in msgsnd]))
        if theCROCE.includeCRC==False:
            rcvBlockLengthBytes=10+2*len(msgsnd)
        else:
            rcvBlockLengthBytes=10+2*len(msgsnd)+2
        if rcvBlockLengthBytes%4!=0:
            raise Exception('rcvBlockLengthBytes=%d is NOT a multiple of 4'%rcvBlockLengthBytes)
        #print 'len(theErrorData=%d, theErrorData=%s'%(len(theErrorData),theErrorData)
        #print 'len(msgsnd)=%d, msgsend=%s'%(len(msgsnd),msgsnd)
        #print 'rcvBlockLengthBytes=%d'%rcvBlockLengthBytes
        #This is the loop through all selected ChannelE 
        for iche in theCheckCh:
            theCROCEChannelE=theCROCE.Channels()[iche]
            #1. Set configuration (FIFO mode)
            config=0x0BFF & theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration(config)
            #2. Clear status
            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            #3. Read all registers -> report errors
            #   data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
            data=theCROCEChannelE.ReadAllRegisters()
            if data!=[config,0x0000,0x0000,0x4040,0x2410,0x0000,theREGHeader]:
                #print '3.1'
                errmsg='TRY#%s, TEST#%s.1 TestWSRfrms, %s:%s: Error ReadAllRegisters=%s, should be [%s,0x0000,0x0000,0x4040,0x2410,0x0000,%s]'\
                    %(itry,tn,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),
                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                      hex(config)[2:].rjust(4,'0'),hex(theREGHeader)[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
                if quitFirstError==True: return nfails
            #4. Write the message to SndMem in FIFO mode
            for data in msgsnd: theCROCEChannelE.WriteSendMemory(data)
            #5. Read all registers -> report errors
            #   data=[WRConfig,RRDFECounter,RRcvMemFramesCounter,RStatusFrame,RStatusTXRX,RRcvMemWPointer,WRHeaderData]
            data=theCROCEChannelE.ReadAllRegisters()
            if data!=[config,0x0000,0x0000,0x0040,0x2410,0x0000,theREGHeader]:
                errmsg='TRY#%s, TEST#%s.2 TestWSRfrms, %s:%s: Error ReadAllRegisters=%s, should be [%s,0x0000,0x0000,0x0040,0x2410,0x0000,%s]'\
                    %(itry,tn,theCROCE.Description(),(theCROCE.Channels()[iche]).Description(),
                      ['0x'+hex(d)[2:].rjust(4,'0') for d in data],
                      hex(config)[2:].rjust(4,'0'),hex(theREGHeader)[2:].rjust(4,'0'))
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
                if quitFirstError==True: return nfails
            #6. Send the message, nsend times
            for isend in range(nsend):
                #6.1. Change/update the data[isend] from SndMem, in RAM mode, before sending. Do this only for isend>0 
                if isend>0 and useRAMMode==True:
                    theCROCEChannelE.WriteConfiguration(config | 0x4800)
                    theCROCEChannelE.WriteSendMemory(theRAMData, 2*isend)           #change this word16
                    theCROCEChannelE.WriteSendMemory(msgsnd[isend-1], 2*(isend-1))  #recover previous word
                    theCROCEChannelE.WriteConfiguration(config)
                #6.2. Send the message
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendMessage'])
                #6.3. Wait for message received
                #New code 08.22.2013, check ONLY the StatusFrame register and StatusTXRX if the first one falis
                for i in range(timeout):
                    status=theCROCEChannelE.ReadStatusFrame()
                    if status==0x1010:break
                if status!=0x1010:
                    #print '6.3.1'
                    errmsg='TRY#%s, TEST#%s.3a TestWSRfrms, %s:%s: Error FrameNumber=%s, StatusFrame=0x%s, should be 0x1010'\
                        %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,hex(status)[2:].rjust(4,'0'))
                    nfails=nfails+1
                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
                    else: print errmsg
                    status=theCROCEChannelE.ReadStatusTXRX()
                    if status!=0x2410:
                        #print '6.3.2'
                        errmsg='TRY#%s, TEST#%s.3b TestWSRfrms, %s:%s: Error FrameNumber=%s, StatusTXRX=0x%s, should be 0x2410'\
                            %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,hex(status)[2:].rjust(4,'0'))
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    if quitFirstError==True: return nfails
            # After sending nsend times, Check FramesCounter==nsend
            frmsCounter=theCROCEChannelE.ReadRcvMemFramesCounter()
            if frmsCounter!=nsend:
                #print '6.3.3'
                errmsg='TRY#%s, TEST#%s.3c TestWSRfrms, %s:%s: Error FramesCounter=%d, should be %d'\
                    %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),frmsCounter,nsend)
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
                if quitFirstError==True: return nfails
            # After sending nsend times, Check RcvMemWPointe==nsend*rcvBlockLengthBytes
            rcvMemWPointer=theCROCEChannelE.ReadRcvMemWPointer()
            if rcvMemWPointer!=nsend*rcvBlockLengthBytes:
                #print '6.3.4'
                errmsg='TRY#%s, TEST#%s.3d TestWSRfrms, %s:%s: Error RcvMemWPointer=%d, should be %d'\
                    %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),rcvMemWPointer,nsend*rcvBlockLengthBytes)
                nfails=nfails+1
                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                else: print errmsg
                if quitFirstError==True: return nfails
            #7.n Repeat READ/CHECK loop BEGIN   
            for repeat in range(repeatRead):
                #7. Read all nsend received messages (checking readout from ReceiveMemory)
                ibyte=0
                for isend in range(nsend): #nsend frames
                    #reading frame number "isend"
                    rcvfrmRead=[]
                    #7.1. Case D16 
                    if dw=='D16':
                        rcvfrmDataLengthBytes=theCROCEChannelE.ReadReceiveMemory(ibyte,dw='D16')
                        if rcvfrmDataLengthBytes!=rcvBlockLengthBytes:
                            errmsg='TRY#%s, TEST#%s.3e TestWSRfrms, %s:%s: Error FrameNumber=%s, rcvfrmDataLengthBytes=%d, should be %d'\
                                %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,rcvfrmDataLengthBytes,rcvBlockLengthBytes)
                            nfails=nfails+1
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
                            #FORCING correct value
                            if forceCorrectValues==True: rcvfrmDataLengthBytes=rcvBlockLengthBytes
                            if quitFirstError==True: return nfails
                        if useBLT==False:
                            for i16word in range(ibyte, ibyte+rcvfrmDataLengthBytes, 2):
                                rcvfrmRead.append(theCROCEChannelE.ReadReceiveMemory(i16word,dw='D16'))
                        if useBLT==True:
                            raise Exception('D16 BLT readout mode NOT supported in CROCE')
                        rcvfrmDataLengthBytes =rcvfrmRead[0]
                        rcvfrmStatus          =rcvfrmRead[1]
                        rcvfrmFirmwareDevFunc =rcvfrmRead[2]
                        rcvfrmSourceID        =rcvfrmRead[3]
                        rcvfrmDataLengthBytes2=rcvfrmRead[4]
                        if theCROCE.includeCRC==False:
                            rcvfrmData        =rcvfrmRead[5:]
                            rcvfrmCRCs        =[]
                        else:
                            rcvfrmData        =rcvfrmRead[5:-1]
                            rcvfrmCRCs        =[rcvfrmRead[-1]]
                        #print 'D16 rcvfrmRead=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmRead]))
                        #print 'D16 rcvfrmData=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmData]))
                        #print 'D16 rcvfrmCRCs=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmCRCs]))
                    #7.2. Case D32 
                    if dw=='D32':
                        rcvfrmDataLengthBytes=theCROCEChannelE.ReadReceiveMemory(ibyte,dw='D16')
                        if rcvfrmDataLengthBytes!=rcvBlockLengthBytes:
                            errmsg='TRY#%s, TEST#%s.3f TestWSRfrms, %s:%s: Error FrameNumber=%s, rcvfrmDataLengthBytes=%d, should be %d'\
                                %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,rcvfrmDataLengthBytes,rcvBlockLengthBytes)
                            nfails=nfails+1
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
                            #FORCING correct value
                            if forceCorrectValues==True: rcvfrmDataLengthBytes=rcvBlockLengthBytes
                            if quitFirstError==True: return nfails
                        if useBLT==False:
                            for i32word in range(ibyte, ibyte+rcvfrmDataLengthBytes, 4):
                                data32=theCROCEChannelE.ReadReceiveMemory(i32word,dw='D32')
                                rcvfrmRead.append((data32&0xFFFF0000)>>16)
                                rcvfrmRead.append((data32&0x0000FFFF))
                        if useBLT==True:
                            data32=theCROCEChannelE.controller.ReadCycleBLT(
                                theCROCEChannelE.RRcvMemory|(ibyte),rcvfrmDataLengthBytes,am='A32_U_BLT',dw='D32sw')
                            for i in range(0,len(data32),4):
                                rcvfrmRead.append((data32[i+0]<<8) | data32[i+1])
                                rcvfrmRead.append((data32[i+2]<<8) | data32[i+3])
                        rcvfrmDataLengthBytes =rcvfrmRead[0]
                        rcvfrmStatus          =rcvfrmRead[1]
                        rcvfrmFirmwareDevFunc =rcvfrmRead[2]
                        rcvfrmSourceID        =rcvfrmRead[3]
                        rcvfrmDataLengthBytes2=rcvfrmRead[4]
                        if theCROCE.includeCRC==False:
                            rcvfrmData        =rcvfrmRead[5:]
                            rcvfrmCRCs        =[]
                        else:
                            rcvfrmData        =rcvfrmRead[5:-1]
                            rcvfrmCRCs        =[rcvfrmRead[-1]]
                        #print 'D32 rcvfrmRead=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmRead]))
                        #print 'D32 rcvfrmData=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmData]))
                        #print 'D32 rcvfrmCRCs=%s'%(''.join([hex(x)[2:].rjust(4,'0') for x in rcvfrmCRCs]))
                    # Checking frame number "isend"
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
                    sourceid=((hitnum&0x10)<<15)+(crateid<<14)+((hitnum&0x08)<<15)+(croceid<<9)+(iche<<7)+(febmum<<3)+(hitnum&0x07)
                    #7.3. Checking header bytes of frame number "isend"
                    if rcvfrmDataLengthBytes!=rcvBlockLengthBytes:
                        errmsg='TRY#%s.%s, TEST#%s.4 TestWSRfrms, %s:%s: HeaderError FrameNumber=%s, word0==RcvFrameLengthBytes=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              rcvfrmDataLengthBytes,rcvBlockLengthBytes)
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    if rcvfrmStatus!=0x1010:
                        errmsg='TRY#%s.%s, TEST#%s.5 TestWSRfrms, %s:%s: HeaderError FrameNumber=%s, word1==RcvFrameStatus=%s, should be 0x1010'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              hex(rcvfrmStatus))
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    if rcvfrmFirmwareDevFunc!=((febvers<<8)+(devfunc)):
                        errmsg='TRY#%s.%s, TEST#%s.6 TestWSRfrms, %s:%s: HeaderError FrameNumber=%s, word2==RcvFrameFirmwareDevFunc=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              hex(rcvfrmFirmwareDevFunc),hex((febvers<<8)+(devfunc)))
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
##                    #Can't check rcvfrmSourceID because of random data in msgsnd
##                    #some bits come from random data, some bits come from header register...
##                    if rcvfrmSourceID!=sourceid:
##                        print 'TRY#%s, TEST#%s.7 Write/Send/Receive Frames, %s:%s: HeaderError FrameNumber=%s, word3==RcvFrameSourceID=%s, should be %s'\
##                            %(itry,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
##                              hex(rcvfrmSourceID),hex(sourceid))
##                        print 'crateid=%s, croceid=%s, febvers=%s, febmum=%s, devfunc=%s, hitnum=%s'%\
##                              (crateid,croceid,febvers,hex(febmum),hex(devfunc),hitnum)
##                        nfails=nfails+1
                    if rcvfrmDataLengthBytes2!=rcvBlockLengthBytes:
                        errmsg='TRY#%s.%s, TEST#%s.8 TestWSRfrms, %s:%s: HeaderError FrameNumber=%s, word4==RcvFrameLengthBytes=%s, should be %s'\
                            %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                              rcvfrmDataLengthBytes2,rcvBlockLengthBytes)
                        nfails=nfails+1
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                    #7.4. Checking data bytes of frame number "isend"
                    if isend==0:
                        if rcvfrmData!=msgsnd:
                            errmsg='TRY#%s.%s, TEST#%s.9 TestWSRfrms, %s:%s: Error FrameNumber=%s, \nSndFrameData=%s, \nRcvFrameData=%s, \n%s'\
                                %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                                  [hex(d)[2:].rjust(4,'0') for d in msgsnd],
                                  [hex(d)[2:].rjust(4,'0') for d in rcvfrmData],rcvfrmDataIndex)
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
##                            for i in range(len(rcvfrmData)):
##                                if rcvfrmData[i]!=msgsnd[i]:
##                                    #print '7.4.2'
##                                    errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'\
##                                    %(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
##                                    UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
                            nfails=nfails+1
                    else:                        
                        if (rcvfrmData[:isend]!=msgsnd[:isend] or rcvfrmData[isend+1:]!=msgsnd[isend+1:] or
                            (useRAMMode==True and rcvfrmData[isend]!=theRAMData) or
                            (useRAMMode==False and rcvfrmData[isend]!=msgsnd[isend])):
                            #print '7.4.3'
                            errmsg='TRY#%s.%s, TEST#%s.10 TestWSRfrms, %s:%s: Error FrameNumber=%s, \nSndFrameData=%s, \nRcvFrameData=%s, \n%s'\
                                %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                                  [hex(d)[2:].rjust(4,'0') for d in msgsnd],
                                  [hex(d)[2:].rjust(4,'0') for d in rcvfrmData],rcvfrmDataIndex)
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
##                            for i in range(len(rcvfrmData)):
##                                if i==isend and useRAMMode==True and rcvfrmData[i]!=theRAMData:
##                                    #print '7.4.4'
##                                    errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'\
##                                    %(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(theRAMData)[2:].rjust(4,'0'))
##                                    UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],theRAMData,daqWFile)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
##                                if i==isend and useRAMMode==False and rcvfrmData[i]!=msgsnd[i]:
##                                    #print '7.4.5'
##                                    errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'\
##                                    %(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
##                                    UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
##                                if i!=isend and rcvfrmData[i]!=msgsnd[i]:
##                                    #print '7.4.6'
##                                    errmsg='\tindex=%s, RcvFrameData=0x%s, expected=0x%s'\
##                                    %(i,hex(rcvfrmData[i])[2:].rjust(4,'0'),hex(msgsnd[i])[2:].rjust(4,'0'))
##                                    UpdateBitErrorFrequency(bitErrFreqCHX[iche],rcvfrmData[i],msgsnd[i],daqWFile)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
                            nfails=nfails+1
                    #7.5. Checking CRC bytes of frame number "isend"
                        inputCRCByte=255    #CROCE Firmware defined, all bits set to 1
                        outputCRCByte1=0    #to be calculated here
                        outputCRCByte2=0    #to be calculated here
                        outputCRCByte1=CalculateCRCData16(self,rcvfrmData,inputCRCByte)
                        outputCRCByte2=CalculateCRCData16(self,rcvfrmRead[:5],outputCRCByte1)
                        theCRCs=(outputCRCByte1<<8)+(outputCRCByte2)
                        if rcvfrmCRCs!=[theCRCs]:
                            errmsg='TRY#%s.%s, TEST#%s.11 TestWSRfrms, %s:%s: Error FrameNumber=%s, CRC Error, read=%s, expected=%s'\
                                %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),isend,
                                  [hex(d)[2:].rjust(4,'0') for d in rcvfrmCRCs],
                                  [hex(theCRCs)[2:].rjust(4,'0')])
                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
                            else: print errmsg
                            if quitFirstError==True: return nfails
                    #7.6. Update pointer ibyte for next frame isend+1
                    ibyte=ibyte+rcvBlockLengthBytes
                #8. Read all nsend frame pointers (checking readout from FramePointersMemory)
                #nsend frames, data[2]==RRcvMemFramesCounter
                frmPointersData=[]
                #8.1. Case D16
                if dw=='D16':
                    if useBLT==False:
                        for ifrmPointer in range(nsend):
                            frmPointersData.append(theCROCEChannelE.ReadFramePointersMemory(2*ifrmPointer))
                    if useBLT==True:
                        raise Exception('D16 BLT readout mode NOT supported in CROCE')
                        data16=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RFramePointersMemory,2*nsend,am='A32_U_BLT',dw='D16sw')
                        for i in range(0,len(data16),2):
                            frmPointersData.append((data16[i+0]<<8) | data16[i+1])       
                #8.2. Case D32 
                if dw=='D32':
                    if nsend%2==0: nsendeven=nsend
                    else: nsendeven=nsend+1
                    if useBLT==False:
                        for ifrmPointer in range(0,nsendeven,2):
                            data32=theCROCEChannelE.ReadFramePointersMemory(2*ifrmPointer,dw='D32')
                            frmPointersData.append((data32&0xFFFF0000)>>16)
                            frmPointersData.append((data32&0x0000FFFF))
                    if useBLT==True:
                        data32=theCROCEChannelE.controller.ReadCycleBLT(theCROCEChannelE.RFramePointersMemory,2*nsendeven,am='A32_U_BLT',dw='D32sw')
                        for i in range(0,len(data32),4):
                            frmPointersData.append((data32[i+0]<<8) | data32[i+1])
                            frmPointersData.append((data32[i+2]<<8) | data32[i+3])
                    if nsend%2==1: frmPointersData=frmPointersData[:-1]       
                #8.3. Check FramePointersMemory data
                frmpointeris17bits=False
                for ifrmPointer in range(nsend):
                    if ifrmPointer==0 and frmPointersData[ifrmPointer]!=0x0000:
                        #print '8.3.1'
##                            errmsg='TRY#%s.%s, TEST#%s.13 TestWSRfrms, %s:%s: Error FrameNumber=%s, \nFramePointersMemoryData=%s, \n%s'\
##                                %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
##                                  [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
##                            if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                            else: print errmsg
                        #print '8.3.2'
                        errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                            %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*rcvBlockLengthBytes))
                        if daqWFile!=None: daqWFile.write('\n'+errmsg)
                        else: print errmsg
                        nfails=nfails+1
                        if quitFirstError==True: return nfails
                    else:
                        if frmPointersData[ifrmPointer]>frmPointersData[ifrmPointer-1]:
                            if ((frmpointeris17bits==False and frmPointersData[ifrmPointer]!=ifrmPointer*rcvBlockLengthBytes) or
                                (frmpointeris17bits==True  and frmPointersData[ifrmPointer]!=0xFFFF&(ifrmPointer*rcvBlockLengthBytes))):
                                #print '8.3.3'
##                                    errmsg='TRY#%s.%s, TEST#%s.14 TestWSRfrms, %s:%s: Error FrameNumber=%s, \nFramePointersMemoryData=%s, \n%s'\
##                                        %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
##                                          [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
                                #print '8.3.4'
                                errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                                    %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*rcvBlockLengthBytes))
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                nfails=nfails+1
                                if quitFirstError==True: return nfails
                        else:
                            frmpointeris17bits=True
                            if frmPointersData[ifrmPointer]!=0xFFFF&(ifrmPointer*rcvBlockLengthBytes):
                                #print '8.3.5'
##                                    errmsg='TRY#%s.%s, TEST#%s.15 TestWSRfrms, %s:%s: Error FrameNumber=%s, \nFramePointersMemoryData=%s, \n%s'\
##                                        %(itry,repeat,tn,theCROCE.Description(),theCROCEChannelE.Description(),ifrmPointer,
##                                          [hex(d)[2:].rjust(4,'0') for d in frmPointersData],rcvfrmDataIndex)
##                                    if daqWFile!=None: daqWFile.write('\n'+errmsg)
##                                    else: print errmsg
                                #print '8.3.6'
                                errmsg='\tindex=%s, FramePointersMemoryData=%s, expected=%s'\
                                    %(ifrmPointer,hex(frmPointersData[ifrmPointer]),hex(ifrmPointer*rcvBlockLengthBytes))
                                if daqWFile!=None: daqWFile.write('\n'+errmsg)
                                else: print errmsg
                                nfails=nfails+1
                                if quitFirstError==True: return nfails
            #7.n Repeat READ/CHECK loop END
            #8. Leave all register in default state 
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0BC0&theCROCE.Channels()[iche].ReadConfiguration())            
        return nfails
##    def TestRegWR(self,itry,theCROCE,fails,theREGAddr):
##        RndObj=random.Random()
##        nfails=fails
##        #baseAddr=theCROCE.controller.baseAddr
##        #theAddr=baseAddr+theREGAddr
##        #print 'baseAddr='%('0x'+hex(baseAddr)[2:].rjust(8,'0'))
##        #print 'theAddr='%('0x'+hex(theAddr)[2:].rjust(8,'0'))
##        wdata=int(RndObj.uniform(0,65536))
##        theCROCE.controller.WriteCycle(theREGAddr, wdata, am='A32_U_DATA', dw='D16')
##        rdata=int(theCROCE.controller.ReadCycle(theREGAddr, am='A32_U_DATA', dw='D16'))
##        if wdata!=rdata:
##            print 'TRY#%s, TEST#8: Register D16: REGAddr=%s: Error write=%s, read=%s'\
##            %(itry,'0x'+hex(theREGAddr)[2:].rjust(8,'0'),'0x'+hex(wdata)[2:].rjust(4,'0'),'0x'+hex(rdata)[2:].rjust(4,'0'))
##            nfails=nfails+1
##        return nfails
    def TestRegWR(self,itry,theCROCE,theCheckCh,nfails,theREGTestData,theREGHeader,useRandomData,bitErrFreqCHXTest8):
        if useRandomData==False:
            for iche in theCheckCh:                         
                theCROCE.Channels()[iche].WriteHeaderData(theREGTestData)
                for ix in range(1000):
                    rdata=theCROCE.Channels()[iche].ReadHeaderData()
                    if rdata!=theREGTestData:
                        errmsg='TRY#%s, TEST#8 %s:%s: Test Register D16 Error: write=0x%s, read=0x%s'\
                            %(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
                              hex(theREGTestData)[2:].rjust(4,'0'),hex(rdata)[2:].rjust(4,'0'))
                        UpdateBitErrorFrequency(bitErrFreqCHXTest8[iche],rdata,theREGTestData,self.daqWFile)
                        nfails=nfails+1
                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                        else: print errmsg                                        
        else:
            wRndData=int(random.Random().uniform(0,65536))
            for iche in theCheckCh:                         
                theCROCE.Channels()[iche].WriteHeaderData(wRndData)
                for ix in range(1000):
                    rdata=theCROCE.Channels()[iche].ReadHeaderData()
                    if rdata!=wRndData:
                        errmsg='TRY#%s, TEST#8 %s:%s: Test Register D16 Error: write=0x%s, read=0x%s'\
                            %(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
                              hex(wRndData)[2:].rjust(4,'0'),hex(rdata)[2:].rjust(4,'0'))
                        UpdateBitErrorFrequency(bitErrFreqCHXTest8[iche],rdata,wRndData,self.daqWFile)
                        nfails=nfails+1
                        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                        else: print errmsg
        # Leave this register in default state
        for iche in theCheckCh:
            theCROCE.Channels()[iche].WriteHeaderData(theREGHeader)
        return nfails
    def TestSequencer(self,itry,theCROCE,theCheckCh,fails,theREGHeader=0x1234):
        nfails=fails
        if itry==0:
            for iche in theCheckCh:
                theCROCE.Channels()[iche].WriteCommands(
                    SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
        #custom choice that relates the itry variable with nfebs CROCE parameter
        nfebs=itry%16
        rdfeCounters=[0,0,0,0]
        theCROCE.SendFastCommand(SC_Util.FastCmds['OpenGate'])                          #1OpenGate
        for iche in theCheckCh:
            rdfeCounters[iche]=theCROCE.Channels()[iche].ReadRDFECounter()              #2ReadRDFECounter
            cfg=theCROCE.Channels()[iche].ReadConfiguration()
            theCROCE.Channels()[iche].WriteConfiguration((0x0BC0&cfg)|(0xA000+nfebs))   #3SequencerMode,SingleHitMode
        theCROCE.SendSoftwareRDFE()                                                     #4SendSoftwareRDFE
        for iche in theCheckCh:
            for timeout in range(100):
                if theCROCE.Channels()[iche].ReadRDFECounter()==rdfeCounters[iche]+1:   #5ReadRDFECounter
                    break
            if timeout==100:
                errmsg='TRY#%s, TEST#9.1: Sequencer, %s:%s: ERROR RDFE Counter increment timeout'\
                    %(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description())
                nfails=nfails+1
                if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
                else: print errmsg
            rcvmem=theCROCE.Channels()[iche].ReadFullDPMBLT() # BLT D32, returns a multiple of four bytes
            #print 'itry=%d: %s:%s: len(rcvmem)=%s, rcvmem=%s'%\
            #      (itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
            #       len(rcvmem),''.join([hex(w8)[2:].rjust(2,'0') for w8 in rcvmem]))
            #print 'itry=%d: %s:%s: len(rcvmem)=%s, rcvmem=%s'%\
            #      (itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
            #       len(rcvmem),rcvmem)
            #length correction based on theCROCE.includeCRC==False/True
            #for each feb there are 3 frames = 1discrim+1hit+1fpgaregisters
            if theCROCE.includeCRC==False:
                lenRcvMem=nfebs*3*(10+10)
            else:
                lenRcvMem=nfebs*3*(10+10+2)
            #length correction because reading in BLT D32 (four bytes)
            if lenRcvMem%4==0:
                lenRcvMemRead=lenRcvMem
            else:
                lenRcvMemRead=lenRcvMem+(4-(lenRcvMem%4))
            #NOTE: data content is not checked since there is no 'real' frame data
            #1.checking rcvmem length
            if len(rcvmem)!=lenRcvMemRead:
                nfails=self.TestSequencerReportError1(itry,theCROCE,iche,len(rcvmem),lenRcvMemRead,nfails,\
                    '9.2: Sequencer','ReceiveMemLength')
            #2.checking misc registers content after sequencer done
            #2.1.checking framesCounter
            framesCounter=theCROCE.Channels()[iche].ReadRcvMemFramesCounter()
            if framesCounter!=nfebs*3: #discrim+hit0+fpgaregs
                nfails=self.TestSequencerReportError1(itry,theCROCE,iche,framesCounter,nfebs*3,nfails,\
                    '9.3: Sequencer','RcvMemFramesCounter')
            #2.2.checking statusFrame
            statusFrame=theCROCE.Channels()[iche].ReadStatusFrame()
            ##if ((nfebs==0 and statusFrame!=0x4440 and statusFrame!=0x5450) or
            ##    (nfebs!=0 and statusFrame!=0x5410)):
            #NOTE: June 20th, 2014: cvme_05c_x.bit fails on Ch3 sequencer test ???WHY???
            ##if not((nfebs==0 and (statusFrame==0x4440 or statusFrame==0x5450 or \
            ##                      statusFrame==0x0440 or statusFrame==0x1450)) or
            ##       (nfebs!=0 and (statusFrame==0x5410 or statusFrame==0x1410))):
            # SndMemEmpty bit is 0 instead of 1 => add conditions statusFrame!=0x0440, statusFrame!=0x1450
            #NOTE: Version 2.0.11. Release Date: February 12 2015
            if not((nfebs==0 and (statusFrame==0x4440                       )) or
                   (nfebs!=0 and (statusFrame==0x5010 or statusFrame==0x5410))):
                nfails=self.TestSequencerReportError1(itry,theCROCE,iche,statusFrame,0xFFFF,nfails,\
                    '9.4: Sequencer','StatusFrame')
            #2.3.checking statusTXRX
            statusTXRX=theCROCE.Channels()[iche].ReadStatusTXRX()
            if statusTXRX!=0x2570:
                nfails=self.TestSequencerReportError1(itry,theCROCE,iche,statusTXRX,0x2570,nfails,\
                    '9.5: Sequencer','StatusTXRX')
            #2.4.checking rcvMemWPointer
            rcvMemWPointer=theCROCE.Channels()[iche].ReadRcvMemWPointer()
            if rcvMemWPointer!=lenRcvMem:
                nfails=self.TestSequencerReportError1(itry,theCROCE,iche,rcvMemWPointer,lenRcvMem,nfails,\
                    '9.6: Sequencer','RcvMemWPointer')
            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: length=%s, rcvmem=%s'%(itry,
            #    theCROCE.Description(),theCROCE.Channels()[iche].Description(),
            #    len(rcvmem),''.join([hex(x)[2:].rjust(2,'0') for x in rcvmem]))
            #print 'TRY#%s, TEST#9: Sequencer, %s:%s: framesCounter=%s statusFrame=%s statusTXRX=%s rcvMemWPointer=%s'\
            #      %(itry,theCROCE.Description(),theCROCE.Channels()[iche].Description(),
            #        framesCounter,hex(statusFrame),hex(statusTXRX),rcvMemWPointer)
            #
            #NOTE:Version 2.0.11. Release Date: February 12 2015, Frame content is NOW checked!
            #NOTE:Frames order is:feb1(disc+hit),feb2(disc+hit)...feb15(disc+hit),fpgareg(feb1+feb2+...feb15)
            if nfebs!=0:
                #3.checking MinervaFrameHeader bytes
                #3.1.checking MFH FrameLength1       -> byte#1,2
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22:ifrm*22+2]!=[0x00, 0x16]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.1: Sequencer','MFH FrameLength1')  
                #3.2.checking MFH ChannelStatus      -> byte#3,4
                for ifrm in range(3*nfebs-1):
                    if rcvmem[ifrm*22+2:ifrm*22+4]!=[0x50, 0x10]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.2: Sequencer','MFH ChannelStatus')
                ifrm = 3*nfebs-1
                if rcvmem[ifrm*22+2:ifrm*22+4]!=[0x54, 0x10]:
                    nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                        '9.7.3: Sequencer','MFH ChannelStatus')
                #3.3.checking MFH FEBFirmwareVersion -> byte#5
                crateid =(0x1000&theREGHeader)>>12
                croceid =(0x0F00&theREGHeader)>>8
                febvers =(0x00FF&theREGHeader)
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22+4]!=febvers:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.4: Sequencer','MFH FEBFirmwareVersion')
                #3.4.checking MFH DeviceFunction     -> byte#6
                for ifrm in range(2*nfebs):
                    if (ifrm%2==0 and rcvmem[ifrm*22+5]!=0x37) or \
                       (ifrm%2==1 and rcvmem[ifrm*22+5]!=0x3F):
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.5: Sequencer','MFH DeviceFunction')
                for ifrm in range(2*nfebs,3*nfebs,1):
                    if rcvmem[ifrm*22+5]!=0x23:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.6: Sequencer','MFH DeviceFunction')
                #3.5.checking MFH SourceID           -> byte#7,8
                hitnum=0 #because we are in SingleHitMode
                for ifrm in range(2*nfebs):
                    #NOTE:Frames order is:feb1(disc+hit),feb2(disc+hit)...feb15(disc+hit)
                    current_feb=(ifrm>>1)+1
                    sourceid=(((hitnum&0x10)>>4)<<15)+(crateid<<14)+(((hitnum&0x08)>>3)<<13)+(croceid<<9)+(iche<<7)+(current_feb<<3)+(hitnum&0x07)
                    #print 'crateid=0x%s, croceid=0x%s, sourceid=0x%s'%(hex(crateid),hex(croceid),hex(sourceid))
                    if rcvmem[ifrm*22+6:ifrm*22+8]!=[(0xFF00&sourceid)>>8,0xFF&sourceid]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.7: Sequencer','MFH SourceID')
                for ifrm in range(2*nfebs,3*nfebs,1):
                    #NOTE:Frames order is:fpgareg(feb1+feb2+...feb15)
                    current_feb=ifrm-2*nfebs+1
                    sourceid=(((hitnum&0x10)>>4)<<15)+(crateid<<14)+(((hitnum&0x08)>>3)<<13)+(croceid<<9)+(iche<<7)+(current_feb<<3)+(hitnum&0x07)
                    #print 'crateid=0x%s, croceid=0x%s, sourceid=0x%s'%(hex(crateid),hex(croceid),hex(sourceid))
                    if rcvmem[ifrm*22+6:ifrm*22+8]!=[(0xFF00&sourceid)>>8,0xFF&sourceid]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.8: Sequencer','MFH SourceID')
                #3.6.checking MFH FrameLength2       -> byte#9,10
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22+8:ifrm*22+8+2]!=[0x00, 0x16]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.9: Sequencer','MFH FrameLength2')
                #4.checking Frame bytes
                #4.1.checking FRM FEBNumber          -> byte#10+1StartFrame
                for ifrm in range(2*nfebs):
                    #NOTE:Frames order is:feb1(disc+hit),feb2(disc+hit)...feb15(disc+hit)
                    current_feb=(ifrm>>1)+1
                    if rcvmem[ifrm*22+10]!=current_feb:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.10: Sequencer','FRM FEBNumber')
                for ifrm in range(2*nfebs,3*nfebs,1):
                    #NOTE:Frames order is:fpgareg(feb1+feb2+...feb15)
                    current_feb=ifrm-2*nfebs+1
                    if rcvmem[ifrm*22+10]!=current_feb:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.11: Sequencer','FRM FEBNumber')
                #4.2.checking FRM DeviceFunction     -> byte#10+2
                for ifrm in range(2*nfebs):
                    if (ifrm%2==0 and rcvmem[ifrm*22+10+1]!=0x37) or \
                       (ifrm%2==1 and rcvmem[ifrm*22+10+1]!=0x3F):
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.12: Sequencer','FRM DeviceFunction')
                for ifrm in range(2*nfebs,3*nfebs,1):
                    if rcvmem[ifrm*22+10+1]!=0x23:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.13: Sequencer','FRM DeviceFunction')
                #4.3.checking FRM FrameStatus        -> byte#10+3
                framestatus =0x00 #no FEBs are present in the chain
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22+10+2]!=0x0:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.14: Sequencer','FRM FrameStatus')
                #4.4.checking FRM ChannelNumber(+EventNumber) -> byte#10+4
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22+10+3]!=iche:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,mfails,\
                            '9.7.15: Sequencer','FRM ChannelNumber')
                #4.5.checking FRM EventNumber        -> byte#10+5
                #4.6.checking FRM TimeStamp          -> byte#10+6,7,8,9
                #4.7.checking FRM DummyByte          -> byte#10+10
                for ifrm in range(3*nfebs):
                    if rcvmem[ifrm*22+10+4:ifrm*22+10+10]!=[0,0,0,0,0,0]:
                        nfails=self.TestSequencerReportError2(itry,theCROCE,iche,rcvmem,nfails,\
                            '9.7.16: Sequencer','FRM EventNumber,TimeStamp,DummyByte')
                #5.checking the two CRC bytes
                for ifrm in range(3*nfebs):
                    mfhBytes=rcvmem[ifrm*22   :ifrm*22+10]   #MinervaFrameHeader Bytes
                    frmBytes=rcvmem[ifrm*22+10:ifrm*22+20]   #Frame Bytes
                    crcBytes=rcvmem[ifrm*22+20:ifrm*22+22]   #CRC Bytes
                    inputCRCByte=255    #CROCE Firmware defined, all bits set to 1
                    outputCRCByte1=0    #to be calculated here
                    outputCRCByte2=0    #to be calculated here
                    outputCRCByte1=CalculateCRCData8(self,frmBytes,inputCRCByte)
                    outputCRCByte2=CalculateCRCData8(self,mfhBytes,outputCRCByte1)
                    if crcBytes[0]!=outputCRCByte1:
                        nfails=self.TestSequencerReportError1(itry,theCROCE,iche,crcBytes[0],outputCRCByte1,nfails,\
                            '9.7.17: Sequencer','CRC Byte1 FRM')
                    if crcBytes[1]!=outputCRCByte2:
                        nfails=self.TestSequencerReportError1(itry,theCROCE,iche,crcBytes[1],outputCRCByte2,nfails,\
                            '9.7.18: Sequencer','CRC Byte2 FRM+MFH')                            
        # Leave all register in default state 
        for iche in theCheckCh:
            theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus']+SC_Util.CHECmds['ClearRDFECounter'])
            theCROCE.Channels()[iche].WriteConfiguration(0x0800&theCROCE.Channels()[iche].ReadConfiguration())
        self.frame.SetStatusText('%s: TEST#9: Test Sequencer: Fails=%s'%(theCROCE.Description(),nfails), 1)
        return nfails
    def TestSequencerReportError1(self,itry,theCROCE,iche,val1,val2,nfails,testnumberstring,testerrorstring):
        errmsg='TRY#%s, TEST#%s, %s:%s: ERROR %s=0x%s, should be 0x%s'%\
            (itry,testnumberstring,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
             testerrorstring,hex(val1)[2:].rjust(4,'0'),hex(val2)[2:].rjust(4,'0'))
        nfails=nfails+1
        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
        else: print errmsg
        return nfails
    def TestSequencerReportError2(self,itry,theCROCE,iche,rcvmem,nfails,testnumberstring,testerrorstring):
        errmsg='TRY#%s, TEST#%s, %s:%s: ERROR %s, found %s'%\
            (itry,testnumberstring,theCROCE.Description(),theCROCE.Channels()[iche].Description(),\
             testerrorstring,''.join([hex(w8)[2:].rjust(2,'0') for w8 in rcvmem]))
        nfails=nfails+1
        if self.daqWFile!=None: self.daqWFile.write('\n'+errmsg)
        else: print errmsg
        return nfails

    # CRIM Timing pannel events ##########################################################
    def OnCRIMTimingbtnWriteTimingSetup(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            mode = SC_Util.CRIMTimingModes[self.frame.crim.TimingModule.TimingSetupRegister.choiceMode.GetStringSelection()]
            freq = SC_Util.CRIMTimingFrequencies[self.frame.crim.TimingModule.TimingSetupRegister.choiceFrequency.GetStringSelection()]
            data = mode | freq
            theCRIM.TimingModule.WriteTimingSetup(data)         
        except: ReportException('OnCRIMTimingbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCRIMTimingbtnReadTimingSetup(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
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
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            gateWidth = int(self.frame.crim.TimingModule.GateWidthRegister.txtGateWidthData.GetValue()) & 0x7F
            enableBit = self.frame.crim.TimingModule.GateWidthRegister.chkCNTRSTEnable.IsChecked() << 15               
            theCRIM.TimingModule.WriteGateWidth(gateWidth | enableBit)         
        except: ReportException('OnCRIMTimingbtnWriteGateWidth', self.reportErrorChoice)
    def OnCRIMTimingbtnReadGateWidth(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadGateWidth()
            self.frame.crim.TimingModule.GateWidthRegister.txtGateWidthData.SetValue(str(data & 0x7F))
            self.frame.crim.TimingModule.GateWidthRegister.chkCNTRSTEnable.SetValue((data & 0x8000) >> 15)
        except: ReportException('OnCRIMTimingbtnReadGateWidth', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTCALBDelay(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.TimingModule.TCALBDelayRegister.txtData.GetValue()) & 0x3FF         
            theCRIM.TimingModule.WriteTCALBDelay(data)         
        except: ReportException('OnCRIMTimingbtnWriteTCALBDelay', self.reportErrorChoice)
    def OnCRIMTimingbtnReadTCALBDelay(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadTCALBDelay()
            self.frame.crim.TimingModule.TCALBDelayRegister.txtData.SetValue(str(data & 0x3FF))
        except: ReportException('OnCRIMTimingbtnReadTCALBDelay', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTRIGGERSend(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendTRIGGER()         
        except: ReportException('OnCRIMTimingbtnWriteTRIGGERSend', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteTCALBSend(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendTCALB()         
        except: ReportException('OnCRIMTimingbtnWriteTCALBSend', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteGATEStart(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendGateStart()         
        except: ReportException('OnCRIMTimingbtnWriteGATEStart', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteGATEStop(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendGateStop()         
        except: ReportException('OnCRIMTimingbtnWriteGATEStop', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteSeqCNTRST(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendSequenceCNTRST()         
        except: ReportException('OnCRIMTimingbtnWriteSeqCNTRST', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteSeqCNTRSTSGATETCALB(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.SendSequenceCNTRSTSGATETCALB()         
        except: ReportException('OnCRIMTimingbtnWriteSeqCNTRSTSGATETCALB', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteSequencerReset(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.TimingModule.WriteSequencerReset()         
        except: ReportException('OnCRIMTimingbtnWriteSequencerReset', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteMTMTimingViolationsClear(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.TimingModule.WriteMTMTimingViolationsClear()         
        except: ReportException('OnCRIMTimingbtnWriteMTMTimingViolationsClear', self.reportErrorChoice)
    def OnCRIMTimingbtnReadMTMTimingViolations(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadMTMTimingViolations()
            self.frame.crim.TimingModule.MTMTimingViolationsRegister.txtData.SetValue(hex(data & 0x1FF))
        except: ReportException('OnCRIMTimingbtnReadMTMTimingViolations', self.reportErrorChoice)
    def OnCRIMTimingbtnWriteScrap(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.TimingModule.ScrapRegister.txtData.GetValue())
            theCRIM.TimingModule.WriteScrap(data)         
        except: ReportException('OnCRIMTimingbtnWriteScrap', self.reportErrorChoice)
    def OnCRIMTimingbtnReadScrap(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadScrap()
            self.frame.crim.TimingModule.ScrapRegister.txtData.SetValue(str(data))
        except: ReportException('OnCRIMTimingbtnReadScrap', self.reportErrorChoice)
    def OnCRIMTimingbtnReadGateTimestamp(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.TimingModule.ReadGateTimestamp()
            self.frame.crim.TimingModule.GateTimestampRegisters.txtData.SetValue(str(data))
        except: ReportException('OnCRIMTimingbtnReadGateTimestamp', self.reportErrorChoice)

    # CRIM CH pannel events ##########################################################
    def OnCRIMCHbtnClearStatus(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.ClearStatus()
        except: ReportException('OnCRIMCHbtnClearStatus', self.reportErrorChoice) 
    def OnCRIMCHbtnReadStatus(self, event): 
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadStatus()
            self.frame.crim.ChannelModule.StatusRegister.txtReadStatusData.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.crim.ChannelModule.StatusRegister.RegValues)
        except: ReportException('OnCRIMCHbtnReadStatus', self.reportErrorChoice)        
    def OnCRIMCHbbtnDPMPointerReset(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.DPMPointerReset()
        except: ReportException('OnCRIMCHbbtnDPMPointerReset', self.reportErrorChoice) 
    def OnCRIMCHbtnDPMPointerRead(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.DPMPointerRead()
            self.frame.crim.ChannelModule.DPMPointer.txtData.SetValue(hex(data))
        except: ReportException('OnCRIMCHbtnDPMPointerRead', self.reportErrorChoice)        
    def OnCRIMCHbtnWriteFIFO(self, event):
        try:
            msg=self.frame.crim.ChannelModule.MessageRegisters.txtAppendMessage.GetValue()
            if ((len(msg) % 4) !=0): raise Exception("A CROC/CRIM message string must have a muliple of 4 hex characters")
            nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar 
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            for i in range(nWords):
                data = msg[4*i:4*(i+1)]
                theCRIM.ChannelModule.WriteFIFO(int(data,16))
        except: ReportException('OnCRIMCHbtnWriteFIFO', self.reportErrorChoice)        
    def OnCRIMCHbtnSendFrame(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.SendMessage()
        except: ReportException('OnCRIMCHbtnSendFrame', self.reportErrorChoice)  
    def OnCRIMCHbtnReadDPMWordsN(self, event):
        msg=''
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            nWords=int(self.frame.crim.ChannelModule.MessageRegisters.txtReadDPMWordsN.GetValue())
            for i in range(nWords):
                data=hex(theCRIM.ChannelModule.ReadDPM(2*i)).upper()
                msg += data[2:].rjust(4, '0')            
        except: ReportException('OnCRIMCHbtnReadDPMWordsN', self.reportErrorChoice)
        self.frame.crim.ChannelModule.MessageRegisters.txtReadDPMContent.SetValue(msg)             
    def OnCRIMCHbtnWriteMode(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            chkReTransmit = self.frame.crim.ChannelModule.ModeRegister.chkReTransmit.IsChecked() << 15
            chkSendMessage = self.frame.crim.ChannelModule.ModeRegister.chkSendMessage.IsChecked() << 14
            chkCRCErrorEnabled = self.frame.crim.ChannelModule.ModeRegister.chkCRCErrorEnabled.IsChecked() << 13
            chkFETriggerEnabled = self.frame.crim.ChannelModule.ModeRegister.chkFETriggerEnabled.IsChecked() << 12          
            theCRIM.ChannelModule.WriteMode(chkReTransmit | chkSendMessage | chkCRCErrorEnabled | chkFETriggerEnabled)         
        except: ReportException('OnCRIMCHbtnWriteMode', self.reportErrorChoice)
    def OnCRIMCHbtnReadMode(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadMode()
            chkReTransmit = self.frame.crim.ChannelModule.ModeRegister.chkReTransmit.SetValue((data & 0x8000) >> 15)
            chkSendMessage = self.frame.crim.ChannelModule.ModeRegister.chkSendMessage.SetValue((data & 0x4000) >> 14)
            chkCRCErrorEnabled = self.frame.crim.ChannelModule.ModeRegister.chkCRCErrorEnabled.SetValue((data & 0x2000) >> 13)
            chkFETriggerEnabled = self.frame.crim.ChannelModule.ModeRegister.chkFETriggerEnabled.SetValue((data & 0x1000) >> 12) 
        except: ReportException('OnCRIMCHbtnReadMode', self.reportErrorChoice)        
    def OnCRIMCHbtnFIFOFlagReset(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.ResetFIFO()
        except: ReportException('OnCRIMCHbtnFIFOFlagReset', self.reportErrorChoice)  
    def OnCRIMCHbtnTimingCmdRead(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.ChannelModule.ReadDecodTmgCmd()
            self.frame.crim.ChannelModule.MiscRegisters.txtTimingCmdReadData.SetValue(hex(data))
        except: ReportException('OnCRIMCHbtnTimingCmdRead', self.reportErrorChoice)      
    def OnCRIMCHbtnSendSYNC(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            theCRIM.ChannelModule.SendSYNC()
        except: ReportException('OnCRIMCHbtnSendSYNC', self.reportErrorChoice)  
       
    # CRIM INTERRUPTER pannel events ##########################################################
    def OnCRIMINTbtnWriteMaskRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.InterrupterModule.MaskRegister.txtData.GetValue(), 16)
            theCRIM.InterrupterModule.WriteMask(data)         
        except: ReportException('OnCRIMINTbtnWriteMaskRegister', self.reportErrorChoice)        
    def OnCRIMINTbtnReadMaskRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadMask()
            self.frame.crim.InterrupterModule.MaskRegister.txtData.SetValue(hex(data)[2:])
        except: ReportException('OnCRIMINTbtnReadMaskRegister', self.reportErrorChoice) 
    def OnCRIMINTbtnWriteStatusRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = int(self.frame.crim.InterrupterModule.StatusRegister.txtData.GetValue(), 16)
            theCRIM.InterrupterModule.WriteStatus(data)         
        except: ReportException('OnCRIMINTbtnWriteStatusRegister', self.reportErrorChoice)
    def OnCRIMINTbtnReadStatusRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadStatus()
            self.frame.crim.InterrupterModule.StatusRegister.txtData.SetValue(hex(data)[2:])
        except: ReportException('OnCRIMINTbtnReadStatusRegister', self.reportErrorChoice) 
    def OnCRIMINTbtnWriteIntConfigRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            level = int(self.frame.crim.InterrupterModule.IntConfigRegister.txtVMEIntLevelData.GetValue()) & 0x7
            enableBit = self.frame.crim.InterrupterModule.IntConfigRegister.chkGlobalIntEnable.IsChecked() << 7               
            theCRIM.InterrupterModule.WriteIntConfig(level | enableBit)         
        except: ReportException('OnCRIMINTbtnWriteIntConfigRegister', self.reportErrorChoice)
    def OnCRIMINTbtnReadIntConfigRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadIntConfig()
            self.frame.crim.InterrupterModule.IntConfigRegister.txtVMEIntLevelData.SetValue(str(data & 0x7))
            self.frame.crim.InterrupterModule.IntConfigRegister.chkGlobalIntEnable.SetValue((data & 0x80) >> 7)
        except: ReportException('OnCRIMINTbtnReadIntConfigRegister', self.reportErrorChoice)
    def OnCRIMINTbtnWriteClearInterruptRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)  
            theCRIM.InterrupterModule.SendClearInterrupt()         
        except: ReportException('OnCRIMINTbtnWriteClearInterruptRegister', self.reportErrorChoice)
    def OnCRIMINTbtnWriteVectorTableRegister(self, event): 
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = []
            for txt in self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues:
                data.append(int(txt.GetValue(), 16))
            theCRIM.InterrupterModule.WriteVectorTable(data)         
        except: ReportException('OnCRIMINTbtnWriteVectorTableRegister', self.reportErrorChoice)       
    def OnCRIMINTbtnReadVectorTableRegister(self, event):
        try:
            theCRIM=FindVMEdev(self.scs[self.frame.crim.crateNumber].vmeCRIMs, self.frame.crim.crimNumber<<16)
            data = theCRIM.InterrupterModule.ReadVectorTable()
            for i in range(len(self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues)):
                self.frame.crim.InterrupterModule.VectorTableRegisters.txtVectorValues[i].SetValue(hex(data[i])[2:])
        except: ReportException('OnCRIMINTbtnReadVectorTableRegister', self.reportErrorChoice)   
    
    # CROC pannel events ##########################################################
    def OnCROCbtnWriteTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            data = self.frame.croc.TimingSetup.choiceCLKSource.GetSelection()<<15 | \
                self.frame.croc.TimingSetup.choiceTPDelayEnable.GetSelection()<<12 | \
                int(self.frame.croc.TimingSetup.txtTPDelayValue.GetValue()) & 0x3FF 
            theCROC.WriteTimingSetup(data)
        except: ReportException('OnCROCbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCROCbtnReadTimingSetup(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadTimingSetup()
            self.frame.croc.TimingSetup.choiceCLKSource.SetSelection((data & 0x8000)>>15)
            self.frame.croc.TimingSetup.choiceTPDelayEnable.SetSelection((data & 0x1000)>>12)
            self.frame.croc.TimingSetup.txtTPDelayValue.SetValue(str(data & 0x3FF))
        except: ReportException('OnCROCbtnReadTimingSetup', self.reportErrorChoice)
    def OnCROCbtnSendFastCmd(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            fcmd=self.frame.croc.FastCmd.choiceFastCmd.GetStringSelection()
            if (SC_Util.FastCmds.has_key(fcmd)):                
                theCROC.SendFastCommand(SC_Util.FastCmds[fcmd])
            else: wx.MessageBox('Please select a Fast Command')
        except: ReportException('OnCROCbtnSendFastCmd', self.reportErrorChoice)
    def OnCROCbtnSendFastCmdAll(self, event):
        try:
            fcmd=self.frame.croc.FastCmd.choiceFastCmd.GetStringSelection()
            if (SC_Util.FastCmds.has_key(fcmd)):
                for sc in self.scs:
                    for theCROC in sc.vmeCROCs:
                        theCROC.SendFastCommand(SC_Util.FastCmds[fcmd])
            else: wx.MessageBox('Please select a Fast Command')
        except: ReportException('OnCROCbtnSendFastCmdAll', self.reportErrorChoice)
    def OnCROCbtnWriteRSTTP(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            data=0
            for i in range(4):
                ChXReset=self.frame.croc.ResetAndTestPulse.ChXReset[i].IsChecked()
                ChXTPulse=self.frame.croc.ResetAndTestPulse.ChXTPulse[i].IsChecked()
                data = data | (ChXReset<<(i+8)) | (ChXTPulse<<i)
            theCROC.WriteRSTTP(data)
        except: ReportException('OnCROCbtnWriteRSTTP', self.reportErrorChoice)
    def OnCROCbtnReadRSTTP(self, event): 
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            data=theCROC.ReadRSTTP()
            ParseDataToListCheckBoxs((data & 0x000F), self.frame.croc.ResetAndTestPulse.ChXTPulse)
            ParseDataToListCheckBoxs((data & 0x0F00)>>8, self.frame.croc.ResetAndTestPulse.ChXReset)
        except: ReportException('OnCROCbtnReadRSTTP', self.reportErrorChoice)
    def OnCROCbtnSendRSTOnly(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            theCROC.SendRSTOnly()
        except: ReportException('OnCROCbtnSendRSTOnly', self.reportErrorChoice)        
    def OnCROCbtnSendTPOnly(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            theCROC.SendTPOnly()
        except: ReportException('OnCROCbtnSendTPOnly', self.reportErrorChoice)
    def OnCROCbtnClearLoopDelays(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            for ch in theCROC.Channels():
                ch.ClearStatus()
            self.OnCROCbtnReadLoopDelays(None)
        except: ReportException('OnCROCbtnClearLoopDelays', self.reportErrorChoice)
    def OnCROCbtnReadLoopDelays(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
            for i in range(len(theCROC.Channels())):
                data=theCROC.Channels()[i].ReadLoopDelay()
                self.frame.croc.LoopDelays.txtLoopDelayValues[i].SetValue(str(data))            
        except: ReportException('OnCROCbtnReadLoopDelays', self.reportErrorChoice)
    def OnCROCbtnReportAlignmentsAllCHs(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.croc.crateNumber].vmeCROCs, self.frame.croc.crocNumber<<16)
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
            for theCROC in self.scs[self.frame.croc.crateNumber].vmeCROCs:
                for theCROCChannel in theCROC.Channels():
                    FEB(0).AlignGateDelays(theCROC, theCROCChannel, theNumberOfMeas, theLoadTimerValue, theGateStartValue)
        except: ReportException('OnCROCbtnReportAlignmentsAllCROCs', self.reportErrorChoice)
    def OnCROCbtnReportAlignmentsAllCRATEs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croc.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croc.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croc.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for sc in self.scs:
                for theCROC in sc.vmeCROCs:
                    for theCROCChannel in theCROC.Channels():
                        FEB(0).AlignGateDelays(theCROC, theCROCChannel, theNumberOfMeas, theLoadTimerValue, theGateStartValue)
        except: ReportException('OnCROCbtnReportAlignmentsAllCRATEs', self.reportErrorChoice)

    # CH pannel events ##########################################################
    def OnCHbtnClearStatus(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.ClearStatus()
        except: ReportException('OnCHbtnClearStatus', self.reportErrorChoice)        
    def OnCHbtnReadStatus(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            data=theCROCChannel.ReadStatus()
            self.frame.ch.StatusRegister.txtReadStatusData.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.ch.StatusRegister.RegValues)
        except: ReportException('OnCHbtnReadStatus', self.reportErrorChoice)
    def OnCHbtnDPMPointerReset(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.DPMPointerReset()
        except: ReportException('OnCHbtnDPMPointerReset', self.reportErrorChoice)
    def OnCHbtnDPMPointerRead(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            data=theCROCChannel.DPMPointerRead()
            self.frame.ch.DPMPointer.txtData.SetValue(hex(data))
        except: ReportException('OnCHbtnDPMPointerRead', self.reportErrorChoice)
    def OnCHbtnWriteFIFO(self, event):
        try:
            msg=self.frame.ch.MessageRegisters.txtAppendMessage.GetValue()
            if ((len(msg) % 4) !=0): raise Exception("A CROC/CRIM message string must have a muliple of 4 hex characters")
            nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar 
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]           
            for i in range(nWords):
                data = msg[4*i:4*(i+1)]
                theCROCChannel.WriteFIFO(int(data,16))
        except: ReportException('OnCHbtnWriteFIFO', self.reportErrorChoice)
    def OnCHbtnSendFrame(self, event):
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
            theCROCChannel=theCROC.Channels()[self.frame.ch.chNumber]
            theCROCChannel.SendMessage()
        except: ReportException('OnCHbtnSendFrame', self.reportErrorChoice)
    def OnCHbtnReadDPMWordsN(self, event):
        msg=''
        try:
            theCROC=FindVMEdev(self.scs[self.frame.ch.crateNumber].vmeCROCs, self.frame.ch.crocNumber<<16)
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
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data = self.frame.croce.TimingSetup.choiceCLKSource.GetSelection()<<15 | \
                self.frame.croce.TimingSetup.choiceTPDelayEnable.GetSelection()<<12 | \
                int(self.frame.croce.TimingSetup.txtTPDelayValue.GetValue()) & 0x1FF 
            theCROCE.WriteTimingSetup(data)
        except: ReportException('OnCROCEbtnWriteTimingSetup', self.reportErrorChoice)
    def OnCROCEbtnReadTimingSetup(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadTimingSetup()
            self.frame.croce.TimingSetup.choiceCLKSource.SetSelection((data & 0x8000)>>15)
            self.frame.croce.TimingSetup.choiceTPDelayEnable.SetSelection((data & 0x1000)>>12)
            self.frame.croce.TimingSetup.txtTPDelayValue.SetValue(str(data & 0x1FF))
        except: ReportException('OnCROCEbtnReadTimingSetup', self.reportErrorChoice)
    def OnCROCEbtnSendFastCmd(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            fcmd=self.frame.croce.FastCmd.choiceFastCmd.GetStringSelection()
            theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
        except: ReportException('OnCROCEbtnSendFastCmd', self.reportErrorChoice)
    def OnCROCEbtnSendFastCmdAll(self, event):
        try:
            fcmd=self.frame.croce.FastCmd.choiceFastCmd.GetStringSelection()
            for sc in self.scs:
                for theCROCE in sc.vmeCROCEs:
                    theCROCE.SendFastCommand(SC_Util.FastCmds[fcmd])
        except: ReportException('OnCROCEbtnSendFastCmdAll', self.reportErrorChoice)
    def OnCROCEbtnWriteRSTTP(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            ChXReset=self.frame.croce.ResetAndTestPulse.ChXReset[0].IsChecked()
            ChXTPulse=self.frame.croce.ResetAndTestPulse.ChXTPulse[0].IsChecked()
            data = (ChXReset<<8) | (ChXTPulse<<0)
            theCROCE.WriteRSTTP(data)
        except: ReportException('OnCROCEbtnWriteRSTTP', self.reportErrorChoice)
    def OnCROCEbtnReadRSTTP(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadRSTTP()
            self.frame.croce.ResetAndTestPulse.ChXTPulse[0].SetValue(data & 0x0001)
            self.frame.croce.ResetAndTestPulse.ChXReset[0].SetValue((data & 0x0100) >> 8)
        except: ReportException('OnCROCEbtnReadRSTTP', self.reportErrorChoice)
    def OnCROCEbtnSendRSTOnly(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            theCROCE.SendRSTOnly()
        except: ReportException('OnCROCEbtnSendRSTOnly', self.reportErrorChoice)        
    def OnCROCEbtnSendTPOnly(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            #Enable TP on all four CROCEChannelE
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteConfiguration(theCROCEChannelE.ReadConfiguration()|0x0020)
            theCROCE.SendTPOnly()
            #Disable TP on all four CROCEChannelE
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteConfiguration(theCROCEChannelE.ReadConfiguration()&0xFFDF)
        except: ReportException('OnCROCEbtnSendTPOnly', self.reportErrorChoice)
    def OnCROCEbtnWriteRDFEPulseDelay(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data = self.frame.croce.RDFESetup.choiceRDFEDelayEnable.GetSelection()<<15 | \
                int(self.frame.croce.RDFESetup.txtRDFEPulseDelayValue.GetValue()) & 0x1FF 
            theCROCE.WriteRDFEPulseDelay(data)
        except: ReportException('OnCROCEbtnWriteRDFEPulseDelay', self.reportErrorChoice)
    def OnCROCEbtnReadRDFEPulseDelay(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadRDFEPulseDelay()
            self.frame.croce.RDFESetup.choiceRDFEDelayEnable.SetSelection((data & 0x8000)>>15)
            self.frame.croce.RDFESetup.txtRDFEPulseDelayValue.SetValue(str(data & 0x1FF))
        except: ReportException('OnCROCEbtnReadRDFEPulseDelay', self.reportErrorChoice)
    def OnCROCEbtnSendRDFESoftware(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            theCROCE.SendSoftwareRDFE()
        except: ReportException('OnCROCEbtnSendRDFESoftware', self.reportErrorChoice)
    def OnCROCEbtnClearLoopDelays(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
            self.OnCROCEbtnReadLoopDelays(None)
        except: ReportException('OnCROCEbtnClearLoopDelays', self.reportErrorChoice)
    def OnCROCEbtnReadLoopDelays(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            for i in range(len(theCROCE.Channels())):
                data=theCROCE.Channels()[i].ReadTXRstTpInDelayCounter()
                self.frame.croce.LoopDelays.txtLoopDelayValues[i].SetValue(str(data))            
        except: ReportException('OnCROCEbtnReadLoopDelays', self.reportErrorChoice)
    def OnCROCEbtnReportAlignmentsAllCHEs(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            theNumberOfMeas=int(self.frame.croce.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croce.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croce.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROCEChannelE in theCROCE.Channels():
                FEB(0).AlignGateDelays(theCROCE,theCROCEChannelE,theNumberOfMeas,theLoadTimerValue,theGateStartValue,theType='CROCE')
        except: ReportException('OnCROCEbtnReportAlignmentsAllCHEs', self.reportErrorChoice)
    def OnCROCEbtnReportAlignmentsAllCROCEs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croce.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croce.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croce.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for theCROCE in self.scs[self.frame.croce.crateNumber].vmeCROCEs:
                for theCROCEChannelE in theCROCE.Channels():
                    FEB(0).AlignGateDelays(theCROCE,theCROCEChannelE,theNumberOfMeas,theLoadTimerValue,theGateStartValue,theType='CROCE')
        except: ReportException('OnCROCEbtnReportAlignmentsAllCROCEs', self.reportErrorChoice)
    def OnCROCEbtnReportAlignmentsAllCRATEs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croce.FEBGateDelays.txtNumberOfMeas.GetValue())
            theLoadTimerValue=int(self.frame.croce.FEBGateDelays.txtLoadTimerValue.GetValue())
            theGateStartValue=int(self.frame.croce.FEBGateDelays.txtGateStartValue.GetValue())
            self.frame.nb.ChangeSelection(0)
            for sc in self.scs:
                for theCROCE in sc.vmeCROCEs:
                    for theCROCEChannelE in theCROCE.Channels():
                        FEB(0).AlignGateDelays(theCROCE,theCROCEChannelE,theNumberOfMeas,theLoadTimerValue,theGateStartValue,theType='CROCE')
        except: ReportException('OnCROCEbtnReportAlignmentsAllCRATEs', self.reportErrorChoice)
    def ReportLoopDelaysAndConfigREFE(self, theSC, theCROCE, theNumberOfMeas):
        theCROCE.WriteRSTTP(0x0001)                     #Enable TP on CROCE
        for theCROCEChannelE in theCROCE.Channels():    #Enable TP on all four CROCEChannelE
            theCROCEChannelE.WriteConfiguration(theCROCEChannelE.ReadConfiguration()|0x0020)
        TPMeas=[0.0, 0.0, 0.0, 0.0]
        for imeas in range(theNumberOfMeas):
            theCROCE.SendTPOnly()
            for iche in range(4):
                data=theCROCE.Channels()[iche].ReadTXRstTpInDelayCounter()
                theCROCE.Channels()[iche].WriteCommands(SC_Util.CHECmds['ClearStatus'])
                TPMeas[iche]+=data
            if (imeas+1)%1000==0:
                self.frame.Refresh(); self.frame.Update()
                self.frame.SetStatusText('Loop Delay %s:%s...%s'%(theSC.Description(),theCROCE.Description(),imeas+1), 0)
        theCROCEsConfigREFE=[-1,-1,-1,-1]
        for iche in range(4):
            TPMeas[iche]/=theNumberOfMeas
            self.frame.croce.LoopDelays.txtLoopDelayValues[iche].SetValue(str(TPMeas[iche]))
            theCROCEsConfigREFE[iche]=(theCROCE.Channels()[iche].ReadConfiguration()&0x0800)>>11
        print '%s:%s ConfigREFE=%s  Loop Delays=%s'%(theSC.Description(), theCROCE.Description(), \
            theCROCEsConfigREFE, ['%09.5f'%x for x in TPMeas])            
        theCROCE.WriteRSTTP(0x0000)                     #Disable TP on CROCE
        for theCROCEChannelE in theCROCE.Channels():    #Disable TP on all four CROCEChannelE
            theCROCEChannelE.WriteConfiguration(theCROCEChannelE.ReadConfiguration()&0xFFDF)        
    def OnCROCEbtnReportLoopDelaysStatistic(self, event):
        try:
            theSC=self.scs[self.frame.croce.crateNumber]
            theCROCE=FindVMEdev(theSC.vmeCROCEs, self.frame.croce.croceNumber<<24)
            theNumberOfMeas=int(self.frame.croce.LoopDelaysStatistic.txtData.GetValue())
            if theNumberOfMeas<1:
                raise Exception('Number of Measurements must be greater than one')
            self.ReportLoopDelaysAndConfigREFE(theSC, theCROCE, theNumberOfMeas)
        except: ReportException('OnCROCEbtnReportLoopDelaysStatistic', self.reportErrorChoice)
    def OnCROCEbtnReportLoopDelaysStatisticALLCROCEs(self, event):
        try:
            theNumberOfMeas=int(self.frame.croce.LoopDelaysStatistic.txtData.GetValue())
            if theNumberOfMeas<1:
                raise Exception('Number of Measurements must be greater than one')
            for theSC in self.scs:
                for theCROCE in theSC.vmeCROCEs:
                    self.ReportLoopDelaysAndConfigREFE(theSC, theCROCE, theNumberOfMeas)
            self.frame.nb.ChangeSelection(0)
        except: ReportException('OnCROCEbtnReportLoopDelaysStatisticALLCROCEs', self.reportErrorChoice)
    def OnCROCEbtnWriteStatusAndVersion(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=int(self.frame.croce.StatusAndVersionRegister.txtValueStatusAndVersion.GetValue(),16)
            theCROCE.WriteStatusAndVersion(data)
        except: ReportException('OnCROCEbtnWritedStatusAndVersion', self.reportErrorChoice)
    def OnCROCEbtnReadStatusAndVersion(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            data=theCROCE.ReadStatusAndVersion()
            self.frame.croce.StatusAndVersionRegister.txtValueStatusAndVersion.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.croce.StatusAndVersionRegister.RegValues, reverse=True) 
        except: ReportException('OnCROCEbtnReadStatusAndVersion', self.reportErrorChoice)
    def OnCROCEbtnReadFlashToFile(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            theConfig=theCROCE.ReadStatusAndVersion()
            #1.Send CmdClearStatus(bit#15) and CmdResetWPointer(bit#10)
            theCROCE.WriteStatusAndVersion(0x8400)
            theConfig=(0xFFF0 & theCROCE.ReadStatusAndVersion()) #discard firmware version bits#3-0
            if (0x0000!=theConfig):
                raise Exception('OnCROCEbtnReadFlashToFile Controller: Unable to clear FLASH Control bits %4X'%theConfig)
            #2.Set FlashMem_Enable(bit#12)
            theCROCE.WriteStatusAndVersion(0x1000)
            nbytesperpage=CROCEFlash.NBytesPerPage
            dlg = wx.FileDialog(self.frame, message='SAVE CTRL Flash Configuration', defaultDir='', defaultFile='',
                wildcard='CTRL Flash Config (*.spidata)|*.spidata|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                print 'OnCROCEbtnReadFlashToFile START: %s'%time.ctime()
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH WriteFILE %s'%filename, 1)
                f=open(filename,'w')
                iPage=0
                for iPage in range(CROCEFlash.NPages):
                    #3.ReadFlashToFile one page at a time 
                    msgrcvstr=theCROCE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')                    
                    f.write('%s %s\n'%(str(iPage).rjust(5,'0'),msgrcvstr[8:]))
                    if iPage%500==0: 
                        source='FLASH:CTRL:%d,%d,%d'%(
                            iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%(source),0)
                source='FLASH:CTRL:%d,%d,%d'%(
                    iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                self.frame.SetStatusText('%s...done'%(source), 0)
                f.close()
                print 'OnCROCEbtnReadFlashToFile STOP : %s'%time.ctime()
            dlg.Destroy()
            #4.Set back default values
            theCROCE.WriteStatusAndVersion(0x0000)
        except: ReportException('OnCROCEbtnReadFlashToFile', self.reportErrorChoice)
    def OnCROCEbtnCompareFileToFlash(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            theConfig=theCROCE.ReadStatusAndVersion()
            #1.Send CmdClearStatus(bit#15) and CmdResetWPointer(bit#10)
            theCROCE.WriteStatusAndVersion(0x8400)
            theConfig=(0xFFF0 & theCROCE.ReadStatusAndVersion()) #discard firmware version bits#3-0
            if (0x0000!=theConfig):
                raise Exception('OnCROCEbtnCompareFileToFlash Controller: Unable to clear FLASH Control bits %4X'%theConfig)
            #2.Set FlashMem_Enable(bit#12)
            theCROCE.WriteStatusAndVersion(0x1000)
            nbytesperpage=CROCEFlash.NBytesPerPage
            dlg = wx.FileDialog(self.frame, message='READ CTRL Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='CTRL FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                print 'OnCROCEbtnCompareFileToFlash START: %s'%time.ctime()
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH CompFILE %s'%filename, 1)
                f=open(filename,'r')
                pagesAddrFile, pagesBytesFile = CROCEFlash().ParseFileLinesToMessages(f)
                f.close()
                errPages=''
                iPage=0
                for iPage in range(CROCEFlash.NPages):
                    #3.CompareFileToFlash one page at a time 
                    msgrcvstr=theCROCE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
                    if msgrcvstr[8:]+'\n'!=pagesBytesFile[iPage]:
                        print 'msgrcvstr[8:]     =%s'%msgrcvstr[8:]
                        print 'pagesBytesFile[%s]=%s'%(iPage,pagesBytesFile[iPage])
                        errPages += '%s '%(str(iPage).rjust(5,'0'))
                    if iPage%500==0:
                        source='FLASH:CTRL:%d,%d,%d'%(
                            iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%(source),0)
                source='FLASH:CTRL:%d,%d,%d'%(
                    iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                self.frame.SetStatusText('%s...done'%(source), 0)
                if errPages!='':
                    raise Exception('ReadFLASH CompFILE Error on page %s'%errPages)
                print 'OnCROCEbtnCompareFileToFlash STOP : %s'%time.ctime()
            dlg.Destroy()
            #4.Set back default values
            theCROCE.WriteStatusAndVersion(0x0000)
        except: ReportException('OnCROCEbtnCompareFileToFlash', self.reportErrorChoice)
    def OnCROCEbtnWriteFileToFlash(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.croce.crateNumber].vmeCROCEs, self.frame.croce.croceNumber<<24)
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                self.CROCE_WriteFileToFlash(dlg, theCROCE)
            dlg.Destroy()
        except: ReportException('OnCROCEbtnWriteFileToFlash', self.reportErrorChoice)
    def OnCROCEbtnWriteFileToFlashThisCRATE(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                for theCROCE in self.scs[self.frame.croce.crateNumber].vmeCROCEs:
                    self.CROCE_WriteFileToFlash(dlg, theCROCE)
            dlg.Destroy()
        except: ReportException('OnCROCEbtnWriteFileToFlashThisCRATE', self.reportErrorChoice)
    def OnCROCEbtnWriteFileToFlashALL(self, event):
        try:
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                for sc in self.scs:
                    for theCROCE in sc.vmeCROCEs:
                        self.CROCE_WriteFileToFlash(dlg, theCROCE)
            dlg.Destroy()            
        except: ReportException('OnCROCEbtnWriteFileToFlashALL', self.reportErrorChoice)
    def CROCE_WriteFileToFlash(self, dlg, theCROCE):
        #1.Send CmdClearStatus(bit#15) and CmdResetWPointer(bit#10)
        theCROCE.WriteStatusAndVersion(0x8400)
        theConfig=(0xFFF0 & theCROCE.ReadStatusAndVersion()) #discard firmware version bits#3-0
        if (0x0000!=theConfig):
            raise Exception('OnCROCEbtnWriteFileToFlash FLASH:CTRL:%d,%d Unable to clear FLASH Control bits %4X'%(
                theCROCE.baseAddr>>24,theCROCE.controller.boardNum,theConfig))
        #2.Set FlashMem_Enable(bit#12)
        theCROCE.WriteStatusAndVersion(0x1000)
        #3.WriteFileToFlash all pages from file
        self.CROCE_CHE_WriteFileToFlash(dlg, None, theCROCE)
        #4.Set back default values
        theCROCE.WriteStatusAndVersion(0x0000)
    def CROCE_CHE_WriteFileToFlash(self, dlg, theCROCEChannelE, theCROCE):
        if theCROCEChannelE==None:
            source='FLASH:CTRL:%d,%d'%(theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        else:
            source='FLASH:CHE:%d,%d,%d'%(theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        print 'CROCE_CHE_WriteFileToFlash START: %s %s'%(time.ctime(),source)
        #1. Read the File.
        filename=dlg.GetFilename()
        dirname=dlg.GetDirectory()
        self.frame.SetStatusText('ReadFILE WriteFLASH %s'%filename, 1)
        f=open(filename,'r')
        pagesAddrFile, pagesBytesFile = CROCEFlash().ParseFileLinesToMessages(f)
        f.close()
        #2.Send WriteEnable and check status.
        if theCROCEChannelE==None:
            theCROCE.FlashWREN()
            status=theCROCE.FlashRDSR(5)
        else:
            theCROCEChannelE.FlashWREN()
            status=theCROCEChannelE.FlashRDSR(5)
        if status!="FF0202020202":
            raise Exception('CROCE_CHE_WriteFileToFlash Error1: FlashRDSR(5)=%s, should be 0x0202020202'%status[2:])
        #3.Send ChipErase and wait to finish.
        #  ChipErase cycle time is 50s to 80s (typ to max).
        #  BlockErase cycle time is 0.7s to 2s (typ to max).
        #  SectorErase cycle time is 60ms to 300ms (typ to max).
        if theCROCEChannelE==None:
            theCROCE.FlashCE()         #theCROCE.FlashBE(0).
        else:
            theCROCEChannelE.FlashCE() #theCROCEChannelE.FlashBE(0).  
        start_time=time.time()
        x=0
        while (time.time()-start_time) <= 100:
            self.frame.SetStatusText('FLASH ChipErase...%ss'%(x),0)
            self.frame.Refresh(); self.frame.Update()
            if theCROCEChannelE==None:
                status=theCROCE.FlashRDSR(5)
            else:
                status=theCROCEChannelE.FlashRDSR(5)
            if status=='FF0000000000':
                break
            x=x+1
            time.sleep(1)
        if status!="FF0000000000":
            raise Exception('CROCE_CHE_WriteFileToFlash Error2: FlashRDSR(5)=%s, should be 0x0000000000'%status[2:])
        #print 'ChipErase elapsed_time=%s, status=%s, i=%s'%(time.time()-start_time, status, x)
        self.frame.SetStatusText('FLASH ChipErase...DONE',0)
        #4.Loop for each Page
        errPages=''
        iPage=0
        nbytesperpage=CROCEFlash.NBytesPerPage
        for iPage in range(CROCEFlash.NPages):
            #4.1.Send Write Enable and check status.
            if theCROCEChannelE==None:
                theCROCE.FlashWREN()
                status=theCROCE.FlashRDSR(5)
            else:
                theCROCEChannelE.FlashWREN()
                status=theCROCEChannelE.FlashRDSR(5)
            if status!="FF0202020202":
                raise Exception('CROCE_CHE_WriteFileToFlash Error3: FlashRDSR(5)=%s, should be 0x0202020202'%status[2:])
            #4.2.Create iPage wordsData from File.
            wordsStr=pagesBytesFile[iPage][:-1] #CAUTION:remove the /n from the end of line
            addr24bits=int(pagesAddrFile[iPage])*(len(wordsStr)/2)
            #print 'iPage=%s, pagesAddrFile=%s, pagesBytesFile=%s'%(iPage, pagesAddrFile[iPage], wordsStr)
            wordsData=[]
            for i in range(0,len(wordsStr),4):
                #theword=wordsStr[i+2:i+4]+wordsStr[i:i+2]
                wordsData.append(int(wordsStr[i+2:i+4]+wordsStr[i:i+2],16))
            #4.3.Write iPage wordsData from File to FLASH and wait to finish.
            if theCROCEChannelE==None:
                theCROCE.FlashWRITE(addr24bits,wordsData)
            else:
                theCROCEChannelE.FlashWRITE(addr24bits,wordsData)
            start_time=time.time()
            while (time.time()-start_time) <= 1:
                if theCROCEChannelE==None:
                    status=theCROCE.FlashRDSR(199)
                else:
                    status=theCROCEChannelE.FlashRDSR(199)
                if status[-2:]=='00':
                    break
            if status[-2:]!='00':
                raise Exception('CROCE_CHE_WriteFileToFlash Error4: FlashRDSR(5)=%s, should be 0x00'%status[2:])
            #print '4.3.Write iPage=%s wordsData from File to FLASH and wait to finish: %ss'%(iPage,time.time()-start_time)
##            theCROCEChannelE.FlashWriteGenericSequence([0x0005]) #do FlashRDSR()
##            i=0
##            for i in range(100):
##                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
##                if theCROCEChannelE.ReadStatusFrame()!=0x4040:
##                    raise Exception('FlashWriteGenericSequence Error1: StatusFrame=%s after ClearStatus'%hex(self.ReadStatusFrame()))
##                status=theCROCEChannelE.ReadFlashMemoryBottom(0)
##                print i, hex(status)
##                if status==0xFF00:
##                    break
##            print '4.3. iPage=%s, itry=%s, status=%s, Write wordsData from File to FLASH and wait to finish: %ss'%\
##                (iPage,i,status,time.time()-start_time)
            #4.4.Read back iPage from FLASH and verify with iPage from File
            if theCROCEChannelE==None:
                msgrcvstr=theCROCE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
            else:
                msgrcvstr=theCROCEChannelE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
            if msgrcvstr[8:]!=wordsStr:
                print 'msgrcvstr[8:]     =%s'%msgrcvstr[8:]
                print 'pagesBytesFile[%s]=%s'%(iPage,pagesBytesFile[iPage])
                errPages += '%s '%(str(iPage).rjust(5,'0'))
            if iPage%500==0:
                if theCROCEChannelE==None:
                    source='FLASH:CTRL:%d,%d,%d'%(
                        iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                else:
                    source='FLASH:CHE:%d,%d,%d,%d'%(
                        iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                self.frame.SetStatusText('%s...'%(source),0)
                self.frame.Refresh(); self.frame.Update()
        if theCROCEChannelE==None:
            source='FLASH:CTRL:%d,%d,%d'%(
                iPage,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        else:
            source='FLASH:CHE:%d,%d,%d,%d'%(
                iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        self.frame.SetStatusText('%s...done'%(source), 0)
        if theCROCEChannelE==None:
            source='FLASH:CTRL:%d,%d'%(theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        else:
            source='FLASH:CHE:%d,%d,%d'%(theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
        print 'CROCE_CHE_WriteFileToFlash STOP : %s %s'%(time.ctime(),source)
        
        
    # CHE REGISTERS pannel events ##########################################################
    def OnCHEbtnWriteConfig(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=int(self.frame.che.regs.ConfigurationRegister.txtValueConfig.GetValue(),16) & 0xFFFF
            theCROCEChannelE.WriteConfiguration(data)
        except: ReportException('OnCHEbtnWriteConfig', self.reportErrorChoice)  
    def OnCHEbtnReadConfig(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadConfiguration()
            self.frame.che.regs.ConfigurationRegister.txtValueConfig.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.regs.ConfigurationRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadConfig', self.reportErrorChoice)
    def OnCHEbtnWriteCommands(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            #cmd=0
            cmd=int(self.frame.che.regs.CommandsRegister.chkClearStatus.IsChecked())<<15 | \
                int(self.frame.che.regs.CommandsRegister.chkSendMessage.IsChecked())<<14 | \
                int(self.frame.che.regs.CommandsRegister.chkClearSndMemWPointer.IsChecked())<<13 | \
                int(self.frame.che.regs.CommandsRegister.chkClearRcvMemWPointer.IsChecked())<<12 | \
                int(self.frame.che.regs.CommandsRegister.chkClearRDFECounter.IsChecked())<<11 | \
                int(self.frame.che.regs.CommandsRegister.chkSendFlashMessage.IsChecked())<<10 | \
                int(self.frame.che.regs.CommandsRegister.chkTXSendSyncWords.IsChecked())<<0
            theCROCEChannelE.WriteCommands(cmd)
        except: ReportException('OnCHEbtnWriteCommands', self.reportErrorChoice)
    def OnCHEbtnReadRcvMemWPointerRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRcvMemWPointer()
            self.frame.che.regs.RcvMemWPointerRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRcvMemWPointerRegister', self.reportErrorChoice)
    def OnCHEbtnReadRcvMemFramesCounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRcvMemFramesCounter()
            self.frame.che.regs.RcvMemFramesCounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRcvMemFramesCounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadRDFECounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadRDFECounter()
            self.frame.che.regs.RDFECounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadRDFECounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadTXRstTpInDelayCounterRegister(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadTXRstTpInDelayCounter()
            self.frame.che.regs.TXRstTpInDelayCounterRegister.txtData.SetValue(str(data))
        except: ReportException('OnCHEbtnReadTXRstTpInDelayCounterRegister', self.reportErrorChoice)
    def OnCHEbtnReadStatusFrame(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadStatusFrame()
            self.frame.che.regs.StatusFrameRegister.txtValueStatusFrame.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.regs.StatusFrameRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadStatusFrame', self.reportErrorChoice)
    def OnCHEbtnReadStatusTXRX(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadStatusTXRX()
            self.frame.che.regs.StatusTXRXRegister.txtValueStatusTXRX.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.regs.StatusTXRXRegister.RegValues, reverse=True)
        except: ReportException('OnCHEbtnReadStatusTXRX', self.reportErrorChoice)
    def OnCHEbtnWriteHeaderData(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=int(self.frame.che.regs.HeaderDataRegister.txtValueHeaderData.GetValue(),16) & 0xFFFF
            theCROCEChannelE.WriteHeaderData(data)
        except: ReportException('OnCHEbtnWriteHeaderData', self.reportErrorChoice)  
    def OnCHEbtnReadHeaderData(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            data=theCROCEChannelE.ReadHeaderData()
            self.frame.che.regs.HeaderDataRegister.txtValueHeaderData.SetValue(hex(data))
            ParseDataToListLabels(data, self.frame.che.regs.HeaderDataRegister.RegValues, reverse=True)
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
    def OnCHEbtnResetThisCHE(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theCROCE.WriteRSTTP(0x0100)
            theCROCEChannelE.WriteConfiguration(0x0010 | theCROCEChannelE.ReadConfiguration())
            theCROCE.SendRSTOnly()
            time.sleep(3)
            theCROCE.WriteRSTTP(0x0000)
            theCROCEChannelE.WriteConfiguration(0xFFEF & theCROCEChannelE.ReadConfiguration())
            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
            theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
            if theRXTXStatus!=0x2410:
                print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                    %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnResetThisCHE', self.reportErrorChoice)  
    def OnCHEbtnResetThisCROCE(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCE.WriteRSTTP(0x0100)
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteConfiguration(0x0010 | theCROCEChannelE.ReadConfiguration())
            theCROCE.SendRSTOnly()
            time.sleep(3)
            theCROCE.WriteRSTTP(0x0000)
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteConfiguration(0xFFEF & theCROCEChannelE.ReadConfiguration())
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                if theRXTXStatus!=0x2410:
                    print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                        %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnResetThisCROCE', self.reportErrorChoice)  
    def OnCHEbtnResetThisCRATE(self, event):
        try:
            for theCROCE in self.scs[self.frame.che.crateNumber].vmeCROCEs:
                theCROCE.WriteRSTTP(0x0100)
                for theCROCEChannelE in theCROCE.Channels():
                    theCROCEChannelE.WriteConfiguration(0x0010 | theCROCEChannelE.ReadConfiguration())
                theCROCE.SendRSTOnly()
            time.sleep(3)
            for theCROCE in self.scs[self.frame.che.crateNumber].vmeCROCEs:
                theCROCE.WriteRSTTP(0x0000)
                for theCROCEChannelE in theCROCE.Channels():
                    theCROCEChannelE.WriteConfiguration(0xFFEF & theCROCEChannelE.ReadConfiguration())
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                    theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                    if theRXTXStatus!=0x2410:
                        print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                            %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))            
        except: ReportException('OnCHEbtnResetThisCRATE', self.reportErrorChoice)  
    def OnCHEbtnResetAllCRATEs(self, event):
        try:
            for sc in self.scs:
                for theCROCE in sc.vmeCROCEs:
                    theCROCE.WriteRSTTP(0x0100)
                    for theCROCEChannelE in theCROCE.Channels():
                        theCROCEChannelE.WriteConfiguration(0x0010 | theCROCEChannelE.ReadConfiguration())
                    theCROCE.SendRSTOnly()
            time.sleep(3)
            for sc in self.scs:
                for theCROCE in sc.vmeCROCEs:
                    theCROCE.WriteRSTTP(0x0000)
                    for theCROCEChannelE in theCROCE.Channels():
                        theCROCEChannelE.WriteConfiguration(0xFFEF & theCROCEChannelE.ReadConfiguration())
                        theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                        theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                        if theRXTXStatus!=0x2410:
                            print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                                %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnResetAllCRATEs', self.reportErrorChoice)




    def OnCHEbtnClearStatusThisCHE(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
            theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
            if theRXTXStatus!=0x2410:
                print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                    %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('ClearStatus', self.reportErrorChoice)  
    def OnCHEbtnClearStatusThisCROCE(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            for theCROCEChannelE in theCROCE.Channels():
                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                if theRXTXStatus!=0x2410:
                    print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                        %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnClearStatusThisCROCE', self.reportErrorChoice)  
    def OnCHEbtnClearStatusThisCRATE(self, event):
        try:
            for theCROCE in self.scs[self.frame.che.crateNumber].vmeCROCEs:
                for theCROCEChannelE in theCROCE.Channels():
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                    theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                    if theRXTXStatus!=0x2410:
                        print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                            %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnClearStatusThisCRATE', self.reportErrorChoice)  
    def OnCHEbtnClearStatusAllCRATEs(self, event):
        try:
            for sc in self.scs:
                for theCROCE in sc.vmeCROCEs:
                    for theCROCEChannelE in theCROCE.Channels():
                        theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'])
                        theRXTXStatus=theCROCEChannelE.ReadStatusTXRX()
                        if theRXTXStatus!=0x2410:
                            print '%s:%s: Error TXRXStatusRegisters=%s, should be 0x2410'\
                                %(theCROCE.Description(),theCROCEChannelE.Description(),hex(theRXTXStatus)[2:].rjust(4,'0'))
        except: ReportException('OnCHEbtnClearStatusAllCRATEs', self.reportErrorChoice)

    # CHE MEMORIES pannel events ##########################################################
    def OnCHEbtnWriteSendMemory(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            configBit14=((1<<14) & theCROCEChannelE.ReadConfiguration()) >> 14
            addr=int(self.frame.che.mems.SendMemory.txt3.GetValue(), 10)
            msg=self.frame.che.mems.SendMemory.txt5.GetValue()
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
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            msg=''
            nwords=int(self.frame.che.mems.ReceiveMemory.txt3.GetValue(), 10)
            if (nwords>=32768):raise Exception('ReceiveMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadReceiveMemory(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnReadReceiveMemory', self.reportErrorChoice)
        self.frame.che.mems.ReceiveMemory.txt5.SetValue(msg)
    def OnCHEbtnReadFramePointersMemory(self, event):
        try:
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            msg=''
            nwords=int(self.frame.che.mems.FramePointersMemory.txt3.GetValue(), 10)
            if (nwords>32768):raise Exception('ReceiveMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadFramePointersMemory(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnReadFramePointersMemory', self.reportErrorChoice)
        self.frame.che.mems.FramePointersMemory.txt5.SetValue(msg)
    def OnCHEbtnFlashMemoryWrite(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashMemoryWrite: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            configBit14=((1<<14) & theCROCEChannelE.ReadConfiguration()) >> 14
            addr=int(self.frame.che.mems.FlashMemoryWrite.txt3.GetValue(), 10)
            msg=self.frame.che.mems.FlashMemoryWrite.txt5.GetValue()
            if ((len(msg) % 4) !=0): raise Exception('FlashMemory: Data message string must have a muliple of 4 hex characters')
            if configBit14==0:
                #FlashMemory is in FIFO mode. Write ALL data words (16bits) at address 0
                if addr!=0: ReportException('FlashMemory: Address is ignored in FIFO mode', self.reportErrorChoice)
                nWords=len(msg)/4   # one word == 2 bytes == 4 HexChar
                for i in range(nWords):
                    data = int(msg[4*i:4*(i+1)],16)
                    data = ((data&0x00FF)<<8) + ((data&0xFF00)>>8)
                    theCROCEChannelE.WriteFlashMemory(data)
            else:
                #FlashMemory is in RNDM access mode. Write ONE data word (16bits) at given address
                if ((addr%2)!=0):raise Exception('FlashMemory: Address must be a multiple of 2 in RNDM mode')
                if (addr>1020):raise Exception('FlashMemory: Address must be less than 1K bytes in RNDM mode')
                if (len(msg)!=4):raise Exception('FlashMemory: Data message string must have 4 hex characters in RNDM mode')
                theCROCEChannelE.WriteFlashMemory(int(msg,16), addr)
        except: ReportException('OnCHEbtnFlashMemoryWrite', self.reportErrorChoice)
    def OnCHEbtnFlashMemoryReadTop(self, event):
        try:
            msg=''
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashMemoryReadTop: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            nwords=int(self.frame.che.mems.FlashMemoryReadTop.txt3.GetValue(), 10)
            if (nwords>=32768):raise Exception('FlashMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadFlashMemoryTop(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnFlashMemoryReadTop', self.reportErrorChoice)
        self.frame.che.mems.FlashMemoryReadTop.txt5.SetValue(msg)
    def OnCHEbtnFlashMemoryReadBottom(self, event):
        try:
            msg=''
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashMemoryReadBottom: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            nwords=int(self.frame.che.mems.FlashMemoryReadBottom.txt3.GetValue(), 10)
            if (nwords>32768):raise Exception('ReceiveMemory: #Words (16bits) must be less than 64K bytes (32768 words)')
            for i in range(nwords):
                data=hex(theCROCEChannelE.ReadFlashMemoryBottom(2*i)).upper()
                msg += data[2:].rjust(4, '0')      
        except: ReportException('OnCHEbtnFlashMemoryReadBottom', self.reportErrorChoice)
        self.frame.che.mems.FlashMemoryReadBottom.txt5.SetValue(msg)
    def OnCHEbtnReadFlashToFile(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnReadFlashToFile: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            nbytesperpage=CROCEFlash.NBytesPerPage
            dlg = wx.FileDialog(self.frame, message='SAVE CHE Flash Configuration', defaultDir='', defaultFile='',
                wildcard='CHE FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                print 'OnCHEbtnReadFlashToFile START: %s'%time.ctime()
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH WriteFILE %s'%filename, 1)
                f=open(filename,'w')
                iPage=0
                for iPage in range(CROCEFlash.NPages):
                    msgrcvstr=theCROCEChannelE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
                    f.write('%s %s\n'%(str(iPage).rjust(5,'0'),msgrcvstr[8:]))
                    if iPage%500==0: 
                        source='FLASH:CHE:%d,%d,%d,%d'%(
                            iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%(source),0)
                source='FLASH:CHE:%d,%d,%d,%d'%(
                    iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                self.frame.SetStatusText('%s...done'%(source), 0)
                f.close()
                print 'OnCHEbtnReadFlashToFile STOP : %s'%time.ctime()
            dlg.Destroy()              
        except: ReportException('OnCHEbtnReadFlashToFile', self.reportErrorChoice)
    def OnCHEbtnCompareFileToFlash(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnCompareFileToFlash: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            nbytesperpage=CROCEFlash.NBytesPerPage
            dlg = wx.FileDialog(self.frame, message='READ CHE Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='CHE FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                print 'OnCHEbtnCompareFileToFlash START: %s'%time.ctime()
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH CompFILE %s'%filename, 1)
                f=open(filename,'r')
                pagesAddrFile, pagesBytesFile = CROCEFlash().ParseFileLinesToMessages(f)
                f.close()
                errPages=''
                iPage=0
                for iPage in range(CROCEFlash.NPages):
                    msgrcvstr=theCROCEChannelE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
                    if msgrcvstr[8:]+'\n'!=pagesBytesFile[iPage]:
                        print 'msgrcvstr[8:]     =%s'%msgrcvstr[8:]
                        print 'pagesBytesFile[%s]=%s'%(iPage,pagesBytesFile[iPage])
                        errPages += '%s '%(str(iPage).rjust(5,'0'))
                    if iPage%500==0:
                        source='FLASH:CHE:%d,%d,%d,%d'%(
                            iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%(source),0)
                source='FLASH:CHE:%d,%d,%d,%d'%(
                    iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
                self.frame.SetStatusText('%s...done'%(source), 0)
                if errPages!='':
                    raise Exception('ReadFLASH CompFILE Error on page %s'%errPages)
                print 'OnCHEbtnCompareFileToFlash STOP : %s'%time.ctime()
            dlg.Destroy()              
        except: ReportException('OnCHEbtnCompareFileToFlash', self.reportErrorChoice)        
##    def CHEWriteFileToFlash(self, dlg, theCROCEChannelE, theCROCE):
##        source='FLASH:CHE:%d,%d,%d'%(theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
##        print 'CHEWriteFileToFlash START: %s %s'%(time.ctime(),source)
##        #1. Read the File.
##        filename=dlg.GetFilename()
##        dirname=dlg.GetDirectory()
##        self.frame.SetStatusText('ReadFILE WriteFLASH %s'%filename, 1)
##        f=open(filename,'r')
##        pagesAddrFile, pagesBytesFile = CROCEFlash().ParseFileLinesToMessages(f)
##        f.close()
##        #2.Send WriteEnable and check status.
##        theCROCEChannelE.FlashWREN()
##        status=theCROCEChannelE.FlashRDSR(5)
##        if status!="FF0202020202":
##            raise Exception('CHEWriteFileToFlash Error1: StatusRegister=%s, should be 0x0202020202'%status[2:])
##        #3.Send ChipErase and wait to finish.
##        #  ChipErase cycle time is 50s to 80s (typ to max).
##        #  BlockErase cycle time is 0.7s to 2s (typ to max).
##        #  SectorErase cycle time is 60ms to 300ms (typ to max).
##        theCROCEChannelE.FlashCE() #theCROCEChannelE.FlashBE(0). 
##        start_time=time.time()
##        x=0
##        while (time.time()-start_time) <= 100:
##            self.frame.SetStatusText('FLASH ChipErase...%ss'%(x),0)
##            self.frame.Refresh(); self.frame.Update()
##            status=theCROCEChannelE.FlashRDSR(5)
##            if status=='FF0000000000':
##                break
##            x=x+1
##            time.sleep(1)
##        if status!="FF0000000000":
##            raise Exception('CHEWriteFileToFlash Error2: StatusRegister=%s, should be 0x0000000000'%status[2:])
##        #print 'ChipErase elapsed_time=%s, status=%s, i=%s'%(time.time()-start_time, status, x)
##        self.frame.SetStatusText('FLASH ChipErase...DONE',0)
##        #4.Loop for each Page
##        errPages=''
##        iPage=0
##        nbytesperpage=CROCEFlash.NBytesPerPage
##        for iPage in range(CROCEFlash.NPages):
##            #4.1.Send Write Enable and check status.
##            theCROCEChannelE.FlashWREN()
##            status=theCROCEChannelE.FlashRDSR(5)
##            if status!="FF0202020202":
##                raise Exception('CHEWriteFileToFlash Error3: StatusRegister=%s, should be 0x0202020202'%status[2:])
##            #4.2.Create iPage wordsData from File.
##            wordsStr=pagesBytesFile[iPage][:-1] #CAUTION:remove the /n from the end of line
##            addr24bits=int(pagesAddrFile[iPage])*(len(wordsStr)/2)
##            #print 'iPage=%s, pagesAddrFile=%s, pagesBytesFile=%s'%(iPage, pagesAddrFile[iPage], wordsStr)
##            wordsData=[]
##            for i in range(0,len(wordsStr),4):
##                #theword=wordsStr[i+2:i+4]+wordsStr[i:i+2]
##                wordsData.append(int(wordsStr[i+2:i+4]+wordsStr[i:i+2],16))
##            #4.3.Write iPage wordsData from File to FLASH and wait to finish.
##            theCROCEChannelE.FlashWRITE(addr24bits,wordsData)
##            start_time=time.time()
##            while (time.time()-start_time) <= 1:
##                status=theCROCEChannelE.FlashRDSR(199)
##                if status[-2:]=='00':
##                    break
##            if status[-2:]!='00':
##                raise Exception('CHEWriteFileToFlash Error4: StatusRegister=%s, should be 0x00'%status[2:])
##            #print '4.3.Write iPage=%s wordsData from File to FLASH and wait to finish: %ss'%(iPage,time.time()-start_time)
####            theCROCEChannelE.FlashWriteGenericSequence([0x0005]) #do FlashRDSR()
####            i=0
####            for i in range(100):
####                theCROCEChannelE.WriteCommands(SC_Util.CHECmds['SendFlashMessage'])
####                if theCROCEChannelE.ReadStatusFrame()!=0x4040:
####                    raise Exception('FlashWriteGenericSequence Error1: StatusFrame=%s after ClearStatus'%hex(self.ReadStatusFrame()))
####                status=theCROCEChannelE.ReadFlashMemoryBottom(0)
####                print i, hex(status)
####                if status==0xFF00:
####                    break
####            print '4.3. iPage=%s, itry=%s, status=%s, Write wordsData from File to FLASH and wait to finish: %ss'%\
####                (iPage,i,status,time.time()-start_time)
##            #4.4.Read back iPage from FLASH and verify with iPage from File
##            msgrcvstr=theCROCEChannelE.FlashREAD(iPage*nbytesperpage, nbytesperpage, dw='D32')
##            if msgrcvstr[8:]!=wordsStr:
##                print 'msgrcvstr[8:]     =%s'%msgrcvstr[8:]
##                print 'pagesBytesFile[%s]=%s'%(iPage,pagesBytesFile[iPage])
##                errPages += '%s '%(str(iPage).rjust(5,'0'))
##            if iPage%500==0:
##                source='FLASH:CHE:%d,%d,%d,%d'%(
##                    iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
##                self.frame.SetStatusText('%s...'%(source),0)
##                self.frame.Refresh(); self.frame.Update()
##        source='FLASH:CHE:%d,%d,%d,%d'%(
##            iPage,theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
##        self.frame.SetStatusText('%s...done'%(source), 0)
##        source='FLASH:CHE:%d,%d,%d'%(theCROCEChannelE.cheNumber,theCROCE.baseAddr>>24,theCROCE.controller.boardNum)
##        print 'CHEWriteFileToFlash STOP : %s %s'%(time.ctime(),source)        
    def OnCHEbtnWriteFileToFlash(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnWriteFileToFlash: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                #self.CHEWriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
                self.CROCE_CHE_WriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
            dlg.Destroy()
            theCROCEChannelE.WriteConfiguration(theConfig)
        except: ReportException('OnCHEbtnWriteFileToFlash', self.reportErrorChoice)
    def OnCHEbtnWriteFileToFlashThisCRATE(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnWriteFileToFlashThisCRATE: Only CH3 has FLASH memory capabilities')
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                for theCROCE in self.scs[self.frame.che.crateNumber].vmeCROCEs:
                    theCROCEChannelE=theCROCE.Channels()[3]
                    theConfig=theCROCEChannelE.ReadConfiguration()
                    theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
                    #self.CHEWriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
                    self.CROCE_CHE_WriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
                    theCROCEChannelE.WriteConfiguration(theConfig)
            dlg.Destroy()
        except: ReportException('OnCHEbtnWriteFileToFlashThisCRATE', self.reportErrorChoice)
    def OnCHEbtnWriteFileToFlashALL(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnWriteFileToFlashALL: Only CH3 has FLASH memory capabilities')
            dlg = wx.FileDialog(self.frame, message='READ Flash Configuration from File', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                for sc in self.scs:
                    for theCROCE in sc.vmeCROCEs:
                        theCROCEChannelE=theCROCE.Channels()[3]
                        theConfig=theCROCEChannelE.ReadConfiguration()
                        theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
                        #self.CHEWriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
                        self.CROCE_CHE_WriteFileToFlash(dlg, theCROCEChannelE, theCROCE)
                        theCROCEChannelE.WriteConfiguration(theConfig)
            dlg.Destroy()
        except: ReportException('OnCHEbtnWriteFileToFlashALL', self.reportErrorChoice)
    def OnCHEbtnFlashCmdWriteEnable(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdWriteEnable: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            theCROCEChannelE.FlashWREN()
        except: ReportException('OnCHEbtnFlashCmdWriteEnable', self.reportErrorChoice)
    def OnCHEbtnFlashCmdWriteDisable(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdWriteDisable: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            theCROCEChannelE.FlashWRDI()
        except: ReportException('OnCHEbtnFlashCmdWriteDisable', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReadStatus(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReadStatus: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.TextEntryDialog(self.frame, message='Enter how many times to ReadStatus, in decimal',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                print 'OnCHEbtnFlashCmdReadStatus=%s'%theCROCEChannelE.FlashRDSR(int(dlg.GetValue(),10))
            dlg.Destroy()
        except: ReportException('OnCHEbtnFlashCmdReadStatus', self.reportErrorChoice)
    def OnCHEbtnFlashCmdWriteStatus(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdWriteStatus: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.TextEntryDialog(self.frame, message='Enter StatusRegister Byte, in hex (bit#7 SRWP ignored!)',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                theCROCEChannelE.FlashWRSR(int(dlg.GetValue(),16) & 0x7F)
            dlg.Destroy()
        except: ReportException('OnCHEbtnFlashCmdWriteStatus', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReadData(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReadData: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg1 = wx.TextEntryDialog(self.frame, message='Enter Start Address (23bits), in hex',
                caption=self.frame.GetTitle(), defaultValue='0')
            dlg2 = wx.TextEntryDialog(self.frame, message='Enter Even Number of Bytes to Read, in decimal',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg1.ShowModal()==wx.ID_OK and dlg2.ShowModal()==wx.ID_OK:
                print 'OnCHEbtnFlashCmdReadData=%s'%theCROCEChannelE.FlashREAD(int(dlg1.GetValue(),16),int(dlg2.GetValue(),10))
            dlg1.Destroy()
            dlg2.Destroy()
        except: ReportException('OnCHEbtnFlashCmdReadData', self.reportErrorChoice)
    def OnCHEbtnFlashCmdSectorErase(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdSectorErase: Only CH3 has FLASH memory capabilities')
            #raise Exception('Not implemented, CAUTION!')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.TextEntryDialog(self.frame, message='CAUTION! Enter SectorErase number, dec 0 to 2047',\
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                #1Sector=16pages*256bytes/page=4096Bytes
                addr24bits=(int(dlg.GetValue(),10) & 0x7FF)<<12
                theCROCEChannelE.FlashSE(addr24bits)
            dlg.Destroy()
        except: ReportException('OnCHEbtnFlashCmdSectorErase', self.reportErrorChoice)
    def OnCHEbtnFlashCmdBlockErase(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdBlockErase: Only CH3 has FLASH memory capabilities')
            #raise Exception('Not implemented, CAUTION!')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.TextEntryDialog(self.frame, message='CAUTION! Enter BlockErase number, dec, 0 to 127',\
                caption=self.frame.GetTitle(), defaultValue='0')  
            if dlg.ShowModal()==wx.ID_OK:
                #1Block=16Sectors=65536Bytes
                addr24bits=(int(dlg.GetValue(),10) & 0x7F)<<16
                theCROCEChannelE.FlashBE(addr24bits)
            dlg.Destroy()
        except: ReportException('OnCHEbtnFlashCmdBlockErase', self.reportErrorChoice)
    def OnCHEbtnFlashCmdChipErase(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdChipErase: Only CH3 has FLASH memory capabilities')
            #raise Exception('Not implemented, CAUTION!')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg = wx.TextEntryDialog(self.frame, message='CAUTION! ChipErase',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg.ShowModal()==wx.ID_OK:
                theCROCEChannelE.FlashCE()                                      #1Chip=128Blocks=8388608Bytes
            dlg.Destroy()
        except: ReportException('OnCHEbtnFlashCmdChipErase', self.reportErrorChoice)
    def OnCHEbtnFlashCmdPageProgram(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdPageProgram: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            dlg1 = wx.TextEntryDialog(self.frame, message='Enter Start Address (23bits), in hex',
                caption=self.frame.GetTitle(), defaultValue='0')
            dlg2 = wx.TextEntryDialog(self.frame, message='Enter Values, in hex, for an Even number of Bytes',
                caption=self.frame.GetTitle(), defaultValue='0')
            if dlg1.ShowModal()==wx.ID_OK and dlg2.ShowModal()==wx.ID_OK:
                addr24bits=int(dlg1.GetValue(),16)
                wordsStr=dlg2.GetValue()
                wordsData=[]
                for i in range(0,len(wordsStr),4):
                    theword=wordsStr[i+2:i+4]+wordsStr[i:i+2]
                    wordsData.append(int(theword,16))
                theCROCEChannelE.FlashWRITE(addr24bits,wordsData)
            dlg1.Destroy()
            dlg2.Destroy()
        except: ReportException('OnCHEbtnFlashCmdPageProgram', self.reportErrorChoice)
    def OnCHEbtnFlashCmdDeepPowerDown(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdDeepPowerDown: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            theCROCEChannelE.FlashDP()
        except: ReportException('OnCHEbtnFlashCmdDeepPowerDown', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReleaseDPD(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReleaseDPD: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            theCROCEChannelE.FlashRDP()
        except: ReportException('OnCHEbtnFlashCmdReleaseDPD', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReadID(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReadID: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            print 'OnCHEbtnFlashCmdReadID=%s'%theCROCEChannelE.FlashRDID()
        except: ReportException('OnCHEbtnFlashCmdReadID', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReadEMandID(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReadEMandID: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            print 'OnCHEbtnFlashCmdReadElectronicManufacturerAndID=%s'%theCROCEChannelE.FlashREMS()
        except: ReportException('OnCHEbtnFlashCmdReadEMandID', self.reportErrorChoice)
    def OnCHEbtnFlashCmdReadSecurity(self, event):
        try:
            if self.frame.che.cheNumber!=3: raise Exception(
                'OnCHEbtnFlashCmdReadSecurity: Only CH3 has FLASH memory capabilities')
            theCROCE=FindVMEdev(self.scs[self.frame.che.crateNumber].vmeCROCEs, self.frame.che.croceNumber<<24)
            theCROCEChannelE=theCROCE.Channels()[self.frame.che.cheNumber]
            theConfig=theCROCEChannelE.ReadConfiguration()
            theCROCEChannelE.WriteConfiguration((theConfig&0x0BFF)+0x0400)
            print 'OnCHEbtnFlashCmdReadSecurity=%s'%theCROCEChannelE.FlashRDSCUR()
        except: ReportException('OnCHEbtnFlashCmdReadSecurity', self.reportErrorChoice)
    def OnCHEbtnFlashCmdWriteSecurity(self, event):
        try:raise Exception('Not implemented, CAUTION!')
        except: ReportException('OnCHEbtnFlashCmdWriteSecurity', self.reportErrorChoice)

    # FE FPGA pannel events ##########################################################
    def OnFEFPGAbtnRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGARead(theCROCXChannelX, theType, theIncludeCRC) 
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnRead', self.reportErrorChoice)
    def OnFEFPGAbtnDumpRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGADumpRead(theCROCXChannelX, theType, theIncludeCRC)
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnDumpRead', self.reportErrorChoice)  
    def OnFEFPGAbtnWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            sentMessageData=theFEB.ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            rcvMessageData,rcvMFH_10bytes=theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType, theIncludeCRC)
            theFEB.ParseMessageToFPGAtxtRegs(rcvMessageData, self.frame.fe.fpga.Registers.txtRegs)            
        except: ReportException('OnFEFPGAbtnWrite', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALLThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for febAddress in theCROCXChannelX.FEBs:
                theFEB=FEB(febAddress)
                rcvMessageData,rcvMFH_10bytes=theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType, theIncludeCRC)
                self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALLThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType, theIncludeCRC)
                    self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALLThisCRATE(self, event):
        try:
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType, theIncludeCRC)
                        self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALLThisCRATE', self.reportErrorChoice)
    def OnFEFPGAbtnWriteALL(self, event):
        try:
            sentMessageData=FEB(self.frame.fe.febNumber).ParseFPGARegsToMessage(self.frame.fe.fpga.Registers.txtRegs)
            vmeCROCXs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCEs)
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.FPGAWrite(theCROCXChannelX, sentMessageData, theType, theIncludeCRC)
                        self.frame.SetStatusText('%s...done'%theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFEFPGAbtnWriteALL', self.reportErrorChoice)

    # FE TRIP pannel events ##########################################################
    def OnFETRIPbtnRead(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            rcvMessageData,rcvMFH_10bytes=theFEB.TRIPRead(theCROCXChannelX, theTRIPIndex, theType, theIncludeCRC)
            theFEB.ParseMessageToTRIPtxtRegs(rcvMessageData, theTRIPIndex, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead', self.reportErrorChoice)
    def OnFETRIPbtnRead6(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            rcvMessageData,rcvMFH_10bytes=theFEB.TRIPRead(theCROCXChannelX, None, theType, theIncludeCRC)
            theFEB.ParseMessageToTRIPtxtRegs6(rcvMessageData, self.frame.fe.trip.Registers.txtRegs) 
        except: ReportException('OnFETRIPbtnRead6', self.reportErrorChoice)
    def OnFETRIPbtnWrite(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theTRIPIndex=self.frame.fe.trip.Registers.chkTrip.GetSelection()
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCXChannelX, theRegs, theTRIPIndex, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnWrite', self.reportErrorChoice)
    def OnFETRIPbtnWrite6(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theRegs=self.frame.fe.trip.Registers.txtRegs
            theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnWrite6', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for febAddress in theCROCXChannelX.FEBs:
                theFEB=FEB(febAddress)
                theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType, theIncludeCRC)
                self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCH', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    theFEB=FEB(febAddress)
                    theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType, theIncludeCRC)
                    self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCROC', self.reportErrorChoice)
    def OnFETRIPbtnWriteALLThisCRATE(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType, theIncludeCRC)
                        self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALLThisCRATE', self.reportErrorChoice)
    def OnFETRIPbtnWriteALL(self, event):
        try:
            vmeCROCXs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCEs)
            theRegs=self.frame.fe.trip.Registers.txtRegs
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        theFEB=FEB(febAddress)
                        theFEB.TRIPWrite(theCROCXChannelX, theRegs, None, theType, theIncludeCRC)
                        self.frame.SetStatusText('%s...done'%theFEB.TRIPDescription('X', theCROCXChannelX, theCROCX, theType), 0)
        except: ReportException('OnFETRIPbtnWriteALL', self.reportErrorChoice)
    def OnFETRIPbtnPRGRST(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.TRIPProgramRST(theCROCXChannelX, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnPRGRST', self.reportErrorChoice)

    def OnFETRIPbtnPRGRSTALLThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            for febAddress in theCROCXChannelX.FEBs:
                FEB(febAddress).TRIPProgramRST(theCROCXChannelX, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnPRGRSTALLThisC', self.reportErrorChoice)
    def OnFETRIPbtnPRGRSTALLThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC
            for theCROCXChannelX in theCROCX.Channels():
                for febAddress in theCROCXChannelX.FEBs:
                    FEB(febAddress).TRIPProgramRST(theCROCXChannelX, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnPRGRSTALLThisCROC', self.reportErrorChoice)
    def OnFETRIPbtnPRGRSTALLThisCRATE(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        FEB(febAddress).TRIPProgramRST(theCROCXChannelX, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnPRGRSTALLThisCRATE', self.reportErrorChoice)
    def OnFETRIPbtnPRGRSTALL(self, event):
        try:
            vmeCROCXs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCEs)
            for theCROCX in vmeCROCXs:
                if theType=='CROC': theIncludeCRC='Unknown'
                if theType=='CROCE': theIncludeCRC=theCROCX.includeCRC
                for theCROCXChannelX in theCROCX.Channels():
                    for febAddress in theCROCXChannelX.FEBs:
                        FEB(febAddress).TRIPProgramRST(theCROCXChannelX, theType, theIncludeCRC)
        except: ReportException('OnFETRIPbtnPRGRSTALL', self.reportErrorChoice)

    # FE FLASH pannel events ##########################################################
    def OnFEFLASHbtnReadFlashToFile(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC; dw='D32'; useBLT=True
            theFEB=FEB(self.frame.fe.febNumber)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            dlg = wx.FileDialog(self.frame, message='SAVE Flash Configuration', defaultDir='', defaultFile='',
                wildcard='FLASH Config (*.spidata)|*.spidata|All files (*)|*', style=wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                filename=dlg.GetFilename()
                dirname=dlg.GetDirectory()
                self.frame.SetStatusText('ReadFLASH WriteFILE %s'%filename, 1)
                f=open(filename,'w')
                print 'OnFEFLASHbtnReadFlashToFile START: %s'%time.ctime()
                for iPage in range(Flash.NPages):
                    pageBytes=theFEB.FLASHMainMemPageRead(theCROCXChannelX, iPage, theType, theIncludeCRC, dw, useBLT)
                    for iread in range(10):
                        pageBytesIRead=theFEB.FLASHMainMemPageRead(theCROCXChannelX, iPage, theType, theIncludeCRC, dw, useBLT)
                        if pageBytes!=pageBytesIRead:
                            print 'OnFEFLASHbtnReadFlashToFile ERROR: iPage=%d, iread=%d'%(iPage,iread)
                            print 'CORRECT: %s'%(''.join([hex(b)[2:].rjust(2,'0') for b in pageBytes]))
                            print 'ERROR  : %s'%(''.join([hex(b)[2:].rjust(2,'0') for b in pageBytesIRead]))
                            for index in range(len(pageBytes)):
                                if pageBytes[index]!=pageBytesIRead[index]:
                                    print'@ index=0x%d, read1=%s, read%s=0x%s'%(
                                        index,hex(pageBytes[index])[2:].rjust(2,'0'),iread,hex(pageBytesIRead[index])[2:].rjust(2,'0'))
                    f.write('%s '%str(iPage).rjust(4,'0').upper())
                    for iByte in pageBytes:
                        f.write('%s'%hex(iByte)[2:].rjust(2,'0').upper())
                    f.write('\n')
                    if iPage%100==0:
                        self.frame.Refresh(); self.frame.Update()
                        self.frame.SetStatusText('%s...'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                print 'OnFEFLASHbtnReadFlashToFile STOP : %s'%time.ctime()
                self.frame.SetStatusText('%s...done'%theFEB.FLASHDescription(iPage, theCROCXChannelX, theCROCX, theType), 0)
                f.close()
            dlg.Destroy()              
        except: ReportException('OnFEFLASHbtnReadFlashToFile', self.reportErrorChoice)
    def OnFEFLASHbtnCompareFileToFlash(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; theIncludeCRC='Unknown'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; theIncludeCRC=theCROCX.includeCRC; dw='D32'; useBLT=True
            theFEB=FEB(self.frame.fe.febNumber)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
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
                    pageBytesRead=theFEB.FLASHMainMemPageRead(theCROCXChannelX, pagesAddrFile[iPage], theType, theIncludeCRC, dw, useBLT)
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
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; dw='D32'; useBLT=True
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=theCROCXChannelX, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=True, toThisCHX=False, toThisCROCX=False, toAllCROCXs=False,
                theFrame=self.frame, theType=theType, dw=dw, useBLT=useBLT)
        except: ReportException('OnFEFLASHbtnWriteFileToFlash', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCH(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; dw='D32'; useBLT=True
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=theCROCXChannelX, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=False, toThisCHX=True, toThisCROCX=False, toAllCROCXs=False,
                theFrame=self.frame, theType=theType, dw=dw, useBLT=useBLT)
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCH', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCROC(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                theType='CROC'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theType='CROCE'; dw='D32'; useBLT=True
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=None, theCROCX=theCROCX, theVMECROCXs=None,
                toThisFEB=False, toThisCHX=False, toThisCROCX=True, toAllCROCXs=False,
                theFrame=self.frame, theType=theType, dw=dw, useBLT=useBLT)
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCROC', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashThisCRATE(self, event):
        try:
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'; dw='D16'; useBLT=True
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'; dw='D32'; useBLT=True
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=None, theCROCX=None, theVMECROCXs=vmeCROCXs,
                toThisFEB=False, toThisCHX=False, toThisCROCX=False, toAllCROCXs=True,
                theFrame=self.frame, theType=theType, dw=dw, useBLT=useBLT)
        except: ReportException('OnFEFLASHbtnWriteFileToFlashThisCRATE', self.reportErrorChoice)
    def OnFEFLASHbtnWriteFileToFlashALL(self, event):
        try:
            vmeCROCXs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theType='CROC'; dw='D16'; useBLT=True
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'; dw='D32'; useBLT=True
                for sc in self.scs:
                    vmeCROCXs.extend(sc.vmeCROCEs)
            theFEB=FEB(self.frame.fe.febNumber)
            theFEB.WriteFileToFlash(theCROCXChannelX=None, theCROCX=None, theVMECROCXs=vmeCROCXs,
                toThisFEB=False, toThisCHX=False, toThisCROCX=False, toAllCROCXs=True,
                theFrame=self.frame, theType=theType, dw=dw, useBLT=useBLT)
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
            raise Exception('not updated for SlowControl version %s'%self.version)
            vmeCROCXsAllCRATEs=[]
            #get configuration parameters from GUI
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnAcqCtrlStart - START Acquisition is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                if len(self.threads)==1:
                    self.LogMessage('A thread is running on CROCE, wait to finish or press "STOP Thread" button')
                    return
                theType='CROCE'
                theCROCE=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theCROCEChannelE=theCROCE.Channels()[self.frame.fe.chNumber]
                vmeCROCEs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
                theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                self.theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
                nEvents=int(self.frame.fe.daq.txtAcqCtrlNEvents.GetValue())                
                #1. Setup Channels for RDFE based acquisition: execute 'ClearStatus' and 'ClearRDFECounter'
                #   commands in WriteCommands register and enable RDFE mode (set bit15) in Configuration Register
                if theReadType==0 or theReadType==1:    # RO one FEB | RO one CHE
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                    if theDataType23Hits==False:
                        theCROCEChannelE.WriteConfiguration(0x8000|theCROCEChannelE.ReadConfiguration())
                    if theDataType23Hits==True:
                        theCROCEChannelE.WriteConfiguration(0x9000|theCROCEChannelE.ReadConfiguration())                    
                elif theReadType==2:                    # RO one CROCE
                    for ich in range(4):
                        theCROCE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                        if theDataType23Hits==False:
                            theCROCE.Channels()[ich].WriteConfiguration(0x8000|theCROCE.Channels()[ich].ReadConfiguration())
                        if theDataType23Hits==True:
                            theCROCE.Channels()[ich].WriteConfiguration(0x9000|theCROCE.Channels()[ich].ReadConfiguration())
                elif theReadType==3:                    # RO all CROCEs this CRATE 
                    for theCTRLE in vmeCROCEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            if theDataType23Hits==False:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==True:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x9000|theCTRLE.Channels()[ich].ReadConfiguration())
                elif theReadType==4:                    # RO all CROCEs all CRATEs 
                    for theCTRLE in vmeCROCXsAllCRATEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==False:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==True:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x9000|theCTRLE.Channels()[ich].ReadConfiguration())
                #2. Create and star acquisition thread
                threadNumber=len(self.threads)+1
                thread=WorkerThreadCROCE(threadNumber, self, nEvents,
                    theCROCE, theCROCEChannelE, vmeCROCEs, vmeCROCXsAllCRATEs, theReadType, theDataType23Hits)
                self.threads.append(thread)
                #self.UpdateThreadCount()
                thread.start()
        except: ReportException('OnFEDAQbtnAcqCtrlStartThread', self.reportErrorChoice)
    def OnFEDAQbtnAcqCtrlStopThread(self, event):
        try:
            raise Exception('not updated for SlowControl version %s'%self.version)
            self.StopThreads()
            #self.UpdateThreadCount()
        except: ReportException('OnFEDAQbtnAcqCtrlStopThread', self.reportErrorChoice)
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
        if thread in self.threads:
            self.threads.remove(thread)
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
            raise Exception('not updated for SlowControl version %s'%self.version)
            vmeCROCXsAllCRATEs=[]
            #get configuration parameters from GUI
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnAcqCtrlStart - START Acquisition is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'
                theCROCE=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theCROCEChannelE=theCROCE.Channels()[self.frame.fe.chNumber]
                vmeCROCEs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
                theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
                nEvents=int(self.frame.fe.daq.txtAcqCtrlNEvents.GetValue())
                # This is an RDFE based acquisition:
                #1. Execute 'ClearStatus' and 'ClearRDFECounter' commands in WriteCommands register
                #   and enable RDFE mode (set bit15) in Configuration Register
                if theReadType==0 or theReadType==1:    # RO one FEB | RO one CHE
                    theCROCEChannelE.WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                    if theDataType23Hits==False:
                        theCROCEChannelE.WriteConfiguration(0x8000|theCROCEChannelE.ReadConfiguration())
                    if theDataType23Hits==True:
                        theCROCEChannelE.WriteConfiguration(0x9000|theCROCEChannelE.ReadConfiguration())                    
                elif theReadType==2:                    # RO one CROCE
                    for ich in range(4):
                        theCROCE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                        if theDataType23Hits==False:
                            theCROCE.Channels()[ich].WriteConfiguration(0x8000|theCROCE.Channels()[ich].ReadConfiguration())
                        if theDataType23Hits==True:
                            theCROCE.Channels()[ich].WriteConfiguration(0x9000|theCROCE.Channels()[ich].ReadConfiguration())
                elif theReadType==3:                    # RO all CROCEs this CRATE 
                    for theCTRLE in vmeCROCEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            if theDataType23Hits==False:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==True:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x9000|theCTRLE.Channels()[ich].ReadConfiguration())
                elif theReadType==4:                    # RO all CROCEs all CRATEs 
                    for theCTRLE in vmeCROCXsAllCRATEs:
                        for ich in range(4):
                            theCTRLE.Channels()[ich].WriteCommands(SC_Util.CHECmds['ClearStatus'] | SC_Util.CHECmds['ClearRDFECounter'])
                            theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==False:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x8000|theCTRLE.Channels()[ich].ReadConfiguration())
                            if theDataType23Hits==True:
                                theCTRLE.Channels()[ich].WriteConfiguration(0x9000|theCTRLE.Channels()[ich].ReadConfiguration())
                SC_MainMethods.workerDAQSimple(nEvents, self.DAQLock, self.DAQStopEvent, theCROCEChannelE, theCROCE, vmeCROCEs, vmeCROCXsAllCRATEs,
                    self.frame, theReadType, theWriteType, self.daqWFile, theType, theDataType23Hits)
##                self.thrd=threading.Thread(
##                    target=SC_MainMethods.workerDAQSimple,
##                    name='workerDAQSimple',
##                    args=(nEvents, self.DAQLock, self.DAQStopEvent, theCROCEChannelE, theCROCE, self.vmeCROCEs,
##                          self.frame, theReadType, theWriteType, self.daqWFile))
##                self.thrd.start()
        except: ReportException('OnFEDAQbtnAcqCtrlStart', self.reportErrorChoice)
    def OnFEDAQbtnOpenGateWrite(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16);
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24);
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            if theReadType==0 or theReadType==1 or theReadType==2:      # RO one FEB or one CH or one CTRL
                theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif theReadType==3:                                        # RO all CTRLs in this CRATE
                for theCROCX in vmeCROCXs:
                    theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            elif theReadType==4:                                        # RO all CRATEs
                for theCROCX in vmeCROCXsAllCRATEs:
                    theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])
            #SC_MainMethods.OpenGate(theCROCX, theReadType, vmeCROCXs)
        except: ReportException('OnFEDAQbtnOpenGateWrite', self.reportErrorChoice)
    def FEDAQWaitDigitizerDoneBit(self, theDataType23Hits, theFEB, theCROCXChannelX, theCROCX, theType):
        if theDataType23Hits==False:
            time.sleep(0.002)
        if theDataType23Hits==True:
            for itimeout in range(100):
                rcvMessageData,rcvMFH_10bytes=theFEB.FPGADumpRead(theCROCXChannelX, theType, theCROCX.includeCRC)
                if ((rcvMessageData[27]>>7)&0x01)==1: #message word 27-bit 7: R  Digitization Done, 1 bit
                    return 
                if itimeout==99:
                    raise Exception('FEDAQWaitDigitizerDoneBit ERROR: timeout=%s %s'%\
                        (itimeout,theFEB.FPGADescription(theCROCXChannelX, theCROCX, theType)))
    def FEDAQWaitRDFECounterIncremented(self, theCROCXChannelX, oldRDFECounter):
        for itimeout in range(100):
            nrdfe=theCROCXChannelX.ReadRDFECounter()
            if nrdfe==oldRDFECounter+1:
                return
            if itimeout==99:
                raise Exception('FEDAQWaitRDFECounterIncremented ERROR: timeout=%s %s'%(itimeout,theCROCXChannelX.Description()))
    def OnFEDAQbtnSoftRDFEWrite(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                ReportException('OnFEDAQbtnSoftRDFEWrite - RDFE is valid only on CROCEs', self.reportErrorChoice)
                return
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theType='CROCE'
                theFEB=FEB(self.frame.fe.febNumber)
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
                theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
                theReadType=self.frame.fe.daq.radioReadType.GetSelection()
                theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            #1. Send OpenGate to simulate a new event
            #2. Read the current RDFE trigger counter value
            #3. Enable RDFE bit in Channel's Configuration Register
            #4. Send the RDFE trigger signal
            #5. Check the current RDFE trigger counter value is incremented
            #6. Read the RcvMemory Content
            #7. Disable RDFE bit in Channel's Configuration Register
            if theReadType==0 or theReadType==1:
                # RO one FEB | RO one CH
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])
                # Wait for serial adc digitization to finish BEFORE enabling sequencer and sending RDFE.
                # Puling one FEB is enough if gate is aligned, wait for 'Digitization Done'. Do it HERE because
                # if you do it after enabling the sequencer bit the CROCE Channel FPGA will not respond to any
                # frames comming from Control FPGA and thus you can't do it!
                self.FEDAQWaitDigitizerDoneBit(theDataType23Hits, theFEB, theCROCXChannelX, theCROCX, theType)
                theConfigs=[]
                rdfeCounters=[]
                theConfigs.append(theCROCXChannelX.ReadConfiguration())                                             #2
                rdfeCounters.append(theCROCXChannelX.ReadRDFECounter())
                if theDataType23Hits==False:
                    theCROCXChannelX.WriteConfiguration(0x8000|theConfigs[0])                                       #3
                if theDataType23Hits==True:
                    theCROCXChannelX.WriteConfiguration(0x9000|theConfigs[0])                                       #3
                theCROCX.SendSoftwareRDFE()                                                                         #4
                #wait for RDFE sequencer to finish (increment RDFECounter) BEFORE starting the readout
                self.FEDAQWaitRDFECounterIncremented(theCROCXChannelX, rdfeCounters[0])                             #5
                SC_MainMethods.DAQReadRcvMemory(rdfeCounters[0]+1, theCROCX, theCROCXChannelX, theType, vmeCROCXs,             
                    vmeCROCXsAllCRATEs, theReadType, theWriteType, self.daqWFile, self.frame, theDataType23Hits)    #6
                theCROCXChannelX.WriteConfiguration(0x0BFF&theConfigs[0])                                           #7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            elif theReadType==2:
                # RO one CTRL
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                theCROCX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                                              #1
                # Wait for serial adc digitization to finish BEFORE enabling sequencer and sending RDFE.
                # Puling one FEB is enough if gate is aligned, wait for 'Digitization Done'. Do it HERE because
                # if you do it after enabling the sequencer bit the CROCE Channel FPGA will not respond to any
                # frames comming from Control FPGA and thus you can't do it!
                self.FEDAQWaitDigitizerDoneBit(theDataType23Hits, theFEB, theCROCXChannelX, theCROCX, theType)
                theConfigs=[]
                rdfeCounters=[]
                for ich in range(4):
                    theConfigs.append(theCROCX.Channels()[ich].ReadConfiguration())
                    rdfeCounters.append(theCROCX.Channels()[ich].ReadRDFECounter())                                 #2
                    if theDataType23Hits==False:
                        theCROCX.Channels()[ich].WriteConfiguration(0x8000|theConfigs[ich])                         #3
                    if theDataType23Hits==True:
                        theCROCX.Channels()[ich].WriteConfiguration(0x9000|theConfigs[ich])                         #3
                theCROCX.SendSoftwareRDFE()                                                                         #4
                for ich in range(4):
                    #wait for RDFE sequencer to finish (increment RDFECounter) BEFORE starting the readout
                    self.FEDAQWaitRDFECounterIncremented(theCROCX.Channels()[ich], rdfeCounters[ich])               #5
                    SC_MainMethods.DAQReadRcvMemory(rdfeCounters[ich]+1, theCROCX, theCROCX.Channels()[ich], theType, vmeCROCXs, 
                        vmeCROCXsAllCRATEs, 1, theWriteType, self.daqWFile, self.frame, theDataType23Hits)          #6
                    theCROCX.Channels()[ich].WriteConfiguration(0x0BFF&theConfigs[ich])                             #7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            elif theReadType==3:
                # RO all CTRLs this CRATE
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                for theCTRLX in self.scs[self.frame.fe.crateNumber].vmeCROCEs:
                    theCTRLX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                                          #1
                # Wait for serial adc digitization to finish BEFORE enabling sequencer and sending RDFE.
                # Puling one FEB is enough if gate is aligned, wait for 'Digitization Done'. Do it HERE because
                # if you do it after enabling the sequencer bit the CROCE Channel FPGA will not respond to any
                # frames comming from Control FPGA and thus you can't do it!
                self.FEDAQWaitDigitizerDoneBit(theDataType23Hits, theFEB, theCROCXChannelX, theCROCX, theType)
                for theCTRLX in self.scs[self.frame.fe.crateNumber].vmeCROCEs:
                    theConfigs=[]
                    rdfeCounters=[]
                    for ich in range(4):
                        theConfigs.append(theCTRLX.Channels()[ich].ReadConfiguration())
                        rdfeCounters.append(theCTRLX.Channels()[ich].ReadRDFECounter())                             #2
                        if theDataType23Hits==False:
                            theCTRLX.Channels()[ich].WriteConfiguration(0x8000|theConfigs[ich])                     #3
                        if theDataType23Hits==True:
                            theCTRLX.Channels()[ich].WriteConfiguration(0x9000|theConfigs[ich])                     #3
                    theCTRLX.SendSoftwareRDFE()                                                                     #4
                    for ich in range(4):
                        #wait for RDFE sequencer to finish (increment RDFECounter) BEFORE starting the readout
                        self.FEDAQWaitRDFECounterIncremented(theCTRLX.Channels()[ich], rdfeCounters[ich])          #5
                        SC_MainMethods.DAQReadRcvMemory(rdfeCounters[ich]+1, theCTRLX, theCTRLX.Channels()[ich], theType, vmeCROCXs,
                            vmeCROCXsAllCRATEs, 1, theWriteType, self.daqWFile, self.frame, theDataType23Hits)      #6
                        theCTRLX.Channels()[ich].WriteConfiguration(0x0BFF&theConfigs[ich])                         #7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            elif theReadType==4:
                # RO all CTRLs all CRATEs
                print 'OnFEDAQbtnSoftRDFEWrite START: %s'%time.ctime()
                for theCTRLX in vmeCROCXsAllCRATEs:
                    theCTRLX.SendFastCommand(SC_Util.FastCmds['OpenGate'])                                          #1
                # Wait for serial adc digitization to finish BEFORE enabling sequencer and sending RDFE.
                # Puling one FEB is enough if gate is aligned, wait for 'Digitization Done'. Do it HERE because
                # if you do it after enabling the sequencer bit the CROCE Channel FPGA will not respond to any
                # frames comming from Control FPGA and thus you can't do it!
                self.FEDAQWaitDigitizerDoneBit(theDataType23Hits, theFEB, theCROCXChannelX, theCROCX, theType)
                for theCTRLX in vmeCROCXsAllCRATEs:
                    theConfigs=[]
                    rdfeCounters=[]
                    for ich in range(4):
                        theConfigs.append(theCTRLX.Channels()[ich].ReadConfiguration())
                        rdfeCounters.append(theCTRLX.Channels()[ich].ReadRDFECounter())                             #2
                        if theDataType23Hits==False:
                            theCTRLX.Channels()[ich].WriteConfiguration(0x8000|theConfigs[ich])                     #3
                        if theDataType23Hits==True:
                            theCTRLX.Channels()[ich].WriteConfiguration(0x9000|theConfigs[ich])                     #3
                    #wait for serial adc digitization to finish BEFORE sending RDFE sequencer trigger
                    time.sleep(0.002) 
                    theCTRLX.SendSoftwareRDFE()                                                                     #4
                    for ich in range(4):
                        #wait for RDFE sequencer to finish (increment RDFECounter) BEFORE starting the readout
                        self.FEDAQWaitRDFECounterIncremented(theCTRLX.Channels()[ich], rdfeCounters[ich])          #5
                        SC_MainMethods.DAQReadRcvMemory(rdfeCounters[ich]+1, theCTRLX, theCTRLX.Channels()[ich], theType, vmeCROCXs, 
                            vmeCROCXsAllCRATEs, 1, theWriteType, self.daqWFile, self.frame, theDataType23Hits)      #6
                        theCTRLX.Channels()[ich].WriteConfiguration(0x0BFF&theConfigs[ich])                         #7
                print 'OnFEDAQbtnSoftRDFEWrite END  : %s'%time.ctime()
            if self.daqWFile!=None: self.daqWFile.flush() 
        except: ReportException('OnFEDAQbtnSoftRDFEWrite', self.reportErrorChoice)
    def OnFEDAQbtnDiscrimBRAMRead(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            SC_MainMethods.DAQBRAMReadDiscrim(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, 0,
                vmeCROCXs, vmeCROCXsAllCRATEs, theReadType, theWriteType, self.daqWFile, self.frame, theDataType23Hits)
            if self.daqWFile!=None: self.daqWFile.flush() 
        except: ReportException('OnFEDAQbtnDiscrimBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnTripBRAMRead(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            theTripNumber=int(self.frame.fe.daq.txtDataTypeTripNumber.GetValue())
            if not(theTripNumber in range(len(Frame.FuncBRAMReadTripx))) and theTripNumber!=-1:
                raise Exception('Trip number %d is out of range. Select %s or -1 to read all'% \
                    (theTripNumber, range(len(Frame.FuncBRAMReadTripx))))
            SC_MainMethods.DAQBRAMReadTrip(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, theTripNumber,
                vmeCROCXs, vmeCROCXsAllCRATEs, theReadType, theWriteType, self.daqWFile, self.frame, theDataType23Hits)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnTripBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnHitBRAMRead(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            theHitNumber=int(self.frame.fe.daq.txtDataTypeHitNumber.GetValue())
            if theDataType23Hits==False:
                if not(theHitNumber in range(len(Frame.FuncBRAMReadHitx))) and theHitNumber!=-1:
                    raise Exception('Hit number %d is out of range. Select %s or -1 to read all'% \
                        (theHitNumber, range(len(Frame.FuncBRAMReadHitx))))
            if theDataType23Hits==True:
                if not(theHitNumber in range(len(Frame.FuncBRAM2ReadHitx))) and theHitNumber!=-1:
                    raise Exception('Hit number %d is out of range. Select %s or -1 to read all'% \
                        (theHitNumber, range(len(Frame.FuncBRAM2ReadHitx))))
            SC_MainMethods.DAQBRAMReadHit(0, theCROCX, theCROCXChannelX, theType, self.frame.fe.febNumber, theHitNumber,
                vmeCROCXs, vmeCROCXsAllCRATEs, theReadType, theWriteType, self.daqWFile, self.frame, theDataType23Hits)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnHitBRAMRead', self.reportErrorChoice)
    def OnFEDAQbtnReadRcvMem(self, event):
        try:
            vmeCROCXsAllCRATEs=[]
            if self.frame.fe.TopLabels[2].GetValue()=='CH' and self.frame.fe.TopLabels[4].GetValue()=='CROC':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCs, self.frame.fe.crocNumber<<16)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCs
                theType='CROC'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCs)
            if self.frame.fe.TopLabels[2].GetValue()=='CHE' and self.frame.fe.TopLabels[4].GetValue()=='CROCE':
                theCROCX=FindVMEdev(self.scs[self.frame.fe.crateNumber].vmeCROCEs, self.frame.fe.crocNumber<<24)
                vmeCROCXs=self.scs[self.frame.fe.crateNumber].vmeCROCEs
                theType='CROCE'
                for sc in self.scs:
                    vmeCROCXsAllCRATEs.extend(sc.vmeCROCEs)
            theCROCXChannelX=theCROCX.Channels()[self.frame.fe.chNumber]
            theDataType23Hits=self.frame.fe.daq.chkDataTypeDiscrim23Hits.IsChecked()
            theReadType=self.frame.fe.daq.radioReadType.GetSelection()
            theWriteType=self.frame.fe.daq.radioWriteType.GetSelection()
            SC_MainMethods.DAQReadRcvMemory(0, theCROCX, theCROCXChannelX, theType,
                vmeCROCXs, vmeCROCXsAllCRATEs, theReadType, theWriteType, self.daqWFile, self.frame, theDataType23Hits)
            if self.daqWFile!=None: self.daqWFile.flush()
        except: ReportException('OnFEDAQbtnReadRcvMem', self.reportErrorChoice)

    # DIG pannel events ##########################################################
    def OnDIGbtnLoadConfigFile(self, event):
        try:            
            thisDIG=FindVMEdev(self.scs[self.frame.dig.crateNumber].vmeDIGs, self.frame.dig.digNumber<<16)
            dlg = wx.FileDialog(self.frame, message='READ V1720 Configuration', defaultDir='', defaultFile='',
                wildcard='DIG Config (*.digcfg)|*.digcfg|All files (*)|*', style=wx.OPEN|wx.CHANGE_DIR)
            if dlg.ShowModal()==wx.ID_OK:
                flags, lines = self.scs[self.frame.dig.crateNumber].DIGcfgFileLoad(wx.FileDialog.GetPath(dlg), thisDIG)
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
            self.scs[self.frame.dig.crateNumber].controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD16
            ReportException('OnDIGbtnLoadConfigFile', self.reportErrorChoice)  
    def OnDIGbtnReadAllRegs(self, event):
        try:
            theDIG=FindVMEdev(self.scs[self.frame.dig.crateNumber].vmeDIGs, self.frame.dig.digNumber<<16)
            if self.frame.dig.digchNumber in range(8):
                dReadAll=theDIG.Channels()[self.frame.dig.digchNumber].ReadAll()
            else : dReadAll=theDIG.ReadAll()                
            for line in DIGDictOfRegsToString(dReadAll): self.frame.dig.display.WriteText(line+'\n')
        except:
            self.scs[self.frame.dig.crateNumber].controller.dataWidth=CAENVMEwrapper.CAENVMETypes.CVDataWidth.cvD16
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
            theDIG=FindVMEdev(self.scs[self.frame.dig.crateNumber].vmeDIGs, self.frame.dig.digNumber<<16)
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
            theDIG=FindVMEdev(self.scs[self.frame.dig.crateNumber].vmeDIGs, self.frame.dig.digNumber<<16) 
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
            theDIG=FindVMEdev(self.scs[self.frame.dig.crateNumber].vmeDIGs, self.frame.dig.digNumber<<16)
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
    errmsg='bitErrorFrequency=%s, word1=0x%s, word2=0x%s'%(bitErrorFrequency,hex(word1)[2:].rjust(4,'0'),hex(word2)[2:].rjust(4,'0'))
    if daqWFile!=None: daqWFile.write('\n'+errmsg)
    else: print errmsg

def newCRC(newDataByte,oldCRCbits):
    newDataBits=[0,0,0,0,0,0,0,0]
    newCRCBits=[0,0,0,0,0,0,0,0]
    for i in range(8):
        newDataBits[i]=((1<<i)&newDataByte)>>i
    newCRCBits[0]=newDataBits[7]^newDataBits[6]^newDataBits[0]^oldCRCbits[0]^oldCRCbits[6]^oldCRCbits[7]
    newCRCBits[1]=newDataBits[6]^newDataBits[1]^newDataBits[0]^oldCRCbits[0]^oldCRCbits[1]^oldCRCbits[6]
    newCRCBits[2]=newDataBits[6]^newDataBits[2]^newDataBits[1]^newDataBits[0]^oldCRCbits[0]^oldCRCbits[1]^oldCRCbits[2]^oldCRCbits[6]
    newCRCBits[3]=newDataBits[7]^newDataBits[3]^newDataBits[2]^newDataBits[1]^oldCRCbits[1]^oldCRCbits[2]^oldCRCbits[3]^oldCRCbits[7]
    newCRCBits[4]=newDataBits[4]^newDataBits[3]^newDataBits[2]^oldCRCbits[2]^oldCRCbits[3]^oldCRCbits[4]
    newCRCBits[5]=newDataBits[5]^newDataBits[4]^newDataBits[3]^oldCRCbits[3]^oldCRCbits[4]^oldCRCbits[5]
    newCRCBits[6]=newDataBits[6]^newDataBits[5]^newDataBits[4]^oldCRCbits[4]^oldCRCbits[5]^oldCRCbits[6]
    newCRCBits[7]=newDataBits[7]^newDataBits[6]^newDataBits[5]^oldCRCbits[5]^oldCRCbits[6]^oldCRCbits[7]
    newCRCByte=0
    return newCRCBits
def CalculateCRCData8(self,frameData8,inputCRCByte):
    #print 'CalculateCRCData8: inputCRCByte=0x%s'%(hex(inputCRCByte)[2:].rjust(2,'0'))
    theCRCbits=[(inputCRCByte&0x01)>>0,(inputCRCByte&0x02)>>1,(inputCRCByte&0x04)>>2,(inputCRCByte&0x08)>>3,\
                (inputCRCByte&0x10)>>4,(inputCRCByte&0x20)>>5,(inputCRCByte&0x40)>>6,(inputCRCByte&0x80)>>7]
    for w in frameData8:
        theCRCbits=newCRC(w,theCRCbits)
    #    print 'CalculateCRCData8: w=0x%s, theCRCbits=%s'%(hex(w)[2:].rjust(2,'0'),theCRCbits)
    theCRCByte=0
    for i in range(8):
        theCRCByte=theCRCByte+theCRCbits[i]*(2**i)
    #print 'CalculateCRCData8: outputCRCByte=0x%s'%(hex(theCRCByte)[2:].rjust(2,'0'))
    return theCRCByte 
def CalculateCRCData16(self,frameData16,inputCRCByte):
    theCRCbits=[(inputCRCByte&0x01)>>0,(inputCRCByte&0x02)>>1,(inputCRCByte&0x04)>>2,(inputCRCByte&0x08)>>3,\
                (inputCRCByte&0x10)>>4,(inputCRCByte&0x20)>>5,(inputCRCByte&0x40)>>6,(inputCRCByte&0x80)>>7]
    for w in frameData16:
        theCRCbits=newCRC((0xFF00&w)>>8,theCRCbits)
        theCRCbits=newCRC(0x00FF&w,theCRCbits)
    theCRCByte=0
    for i in range(8):
        theCRCByte=theCRCByte+theCRCbits[i]*(2**i)
    return theCRCByte
    
def main():
    """Instantiates the Slow Control GUI."""
    try:
        theArgs = sys.argv[1:]
        #print sys.argv
        app = SCApp(theArgs) 
        app.MainLoop()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]

if __name__ == "__main__":
    main()
