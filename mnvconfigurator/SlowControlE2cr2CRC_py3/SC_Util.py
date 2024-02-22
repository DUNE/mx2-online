"""
MINERvA DAQ Slow Control GUI
Contains misc utilities
Started November 2009
"""

import wx
import sys
import random
from .CAENVMEwrapper import CAENVMETypes

colorButton='coral'     #wx.Color(255,0,0)      #'red'
colorLabel='coral'      #wx.Color(0,255,0)      #'green'
colorText='white'       #wx.Color(255,255,255)  #'white'
colorForeground='blue'  #wx.Color(0,0,255)      #'blue'  #wx.Color.Blue
fontSizeLabel=8
fontSizeButton=8
fontSizeTextCtrl=8
fontSizeCheckBox=8
fontSizeRadioBox=8
fontSizeStaticBox=8
fontSizeChoice=8
def myFont(size, family=wx.DEFAULT, style=wx.NORMAL, weight=wx.NORMAL):
    return wx.Font(size, family, style, weight)

class VMEdevTypes():
    CRIM='CRIM'
    CROC='CROC'
    CH='CH'
    CROCE='CROCE'
    CHE='CHE'
    FE='FE'
    FPGA='FPGA'
    TRIP='TRIP'
    FLASH='FLASH'
    DIG='DIG'
    DIGCH='DIGCH'

##class DIGRegs():
##    //ROEventReadoutBuffer          = 0x0000-0x0FFC    //R
##    WRChannelConfiguration          = 0x8000
##    WOChannelConfigurationBitSet    = 0x8004
##    WOChannelConfigurationBitClear  = 0x8008
##    WRBufferOrganization            = 0x800C
##    WRBufferFree                    = 0x8010
##    WRCustomSize                    = 0x8020
##    WRAcquisitionControl            = 0x8100
##    ROAcquisitionStatus             = 0x8104
##    WOSWTrigger                     = 0x8108
##    WRTriggerSourceEnableMask       = 0x810C
##    WRFrontPanelTriggerOutEnableMask= 0x8110
##    WRPostTriggerSetting            = 0x8114
##    WRFrontPanelIOData              = 0x8118
##    WRFrontPanelIOControl           = 0x811C
##    WRChannelEnableMask             = 0x8120
##    ROCFPGAFirmwareRevision         = 0x8124
##    ROEventStored                   = 0x812C
##    WRSetMonitorDAC                 = 0x8138
##    ROBoardInfo                     = 0x8140
##    //WRMonitorMode = 0x8144,//RW  CAEN Note : To be implemented
##    ROEventSize                     = 0x814C
##    WRVMEControl                    = 0xEF00
##    ROVMEStatus                     = 0xEF04
##    WRBoardId                       = 0xEF08
##    WRMulticastBaseAddrAndCtrl      = 0xEF0C
##    WRRelocationAddress             = 0xEF10
##    WRInterruptStatusId             = 0xEF14
##    WRInterruptEventNumber          = 0xEF18
##    WRBLTEventNumber                = 0xEF1C
##    WRVMEScratch                    = 0xEF20
##    WOSWReset                       = 0xEF24
##    WOSWClear                       = 0xEF28
##    WRFlashEnable                   = 0xEF2C
##    WRFlashData                     = 0xEF30
##    WOConfigurationReload           = 0xEF34
##    //ROConfigurationROM = 0xF000-0xF3FC //R
##    
##class DIGCHRegs():
##    WRZSThres           = 0x1024
##    WRZSNSamp           = 0x1028
##    WRThresholdValue    = 0x1080
##    WRThresholdOverUnder= 0x1084
##    ROStatus            = 0x1088
##    ROAMCFPGAFirmware   = 0x108C
##    ROBufferOccupancy   = 0x1094
##    WRDACOffset         = 0x1098
##    WRADCConfiguration  = 0x109C

class CROCRegs():
    RegWRTimingSetup        = 0xF000
    RegWRResetAndTestMask   = 0xF010
    RegWChannelReset        = 0xF020
    RegWFastCommand         = 0xF030
    RegWTestPulse           = 0xF040
class CROCERegs():
    RegWRTimingSetup        = 0x0FF000
    RegWRResetAndTestMask   = 0x0FF010
    RegWChannelReset        = 0x0FF020
    RegWFastCommand         = 0x0FF030
    RegWTestPulse           = 0x0FF040
    RegWRRDFEPulseDelay     = 0x0FF050
    RegWSoftwareRDFE        = 0x0FF060
    RegRStatusAndVersion    = 0x0FF070
    WRFlashMemory           = 0x0FF800

class CROCCHRegs():
    RegRMemory      = 0x0000
    RegWInput       = 0x2000
    RegWSendMessage = 0x2010
    RegRStatus      = 0x2020
    RegWClearStatus = 0x2030
    RegRLoopDelay   = 0x2040
    RegRDPMPointer  = 0x2050
class CROCCHStatusBits():
    MessageSent     = 0x0001
    MessageReceived = 0x0002
    CRCError        = 0x0004
    TimeoutError    = 0x0008
    FIFONotEmpty    = 0x0010
    FIFOFull        = 0x0020
    DPMFull         = 0x0040
    UnusedBit7      = 0x0080
    RFPresent       = 0x0100
    SerializerSynch = 0x0200
    DeserializerLock= 0x0400
    UnusedBit11     = 0x0800
    PLL0Locked      = 0x1000
    PLL1Locked      = 0x2000
    UnusedBit14     = 0x4000
    UnusedBit14     = 0x8000

class CROCECHERegs():
    RRcvMemory                  = 0x000000
    WSendMemory                 = 0x022000
    RFramePointersMemory        = 0x024000
    RegWRConfig                 = 0x028002
    RegWCommand                 = 0x028004
    RegRRDFECounter             = 0x028008
    RegRTXRstTpInDelayCounter   = 0x028010
    RegRRcvMemFramesCounter     = 0x028010
    RegRStatusFrame             = 0x028020
    RegRStatusTXRX              = 0x028040
    RegRRcvMemWPointer          = 0x028080
    RegWRHeaderData             = 0x028100
    WRFlashMemory               = 0x030000
    
class CRIMTimingModuleRegs():
    RegWRTimingSetup = 0xC010
    RegWRGateWidth   = 0xC020
    RegWRTCALBDelay  = 0xC030
    RegWTRIGGERSend  = 0xC040
    RegWTCALBSend    = 0xC050
    RegWGATE         = 0xC060
    RegWSequencerReset      = 0xC070
    RegWCNTRST              = 0xC080
    RegRMTMTimingViolations = 0xC090
    RegWRScrapRegister      = 0xC0A0
    RegRGateTimestampLower  = 0xC0B0
    RegRGateTimestampUpper  = 0xC0C0

class CRIMCHModuleRegs(CROCCHRegs):
    RegWResetFIFO   = 0x2008
    RegRDecodTmgCmd = 0x2060
    RegWRMode       = 0x2070
class CRIMCHStatusBits():
    MessageSent     = 0x0001
    MessageReceived = 0x0002
    CRCError        = 0x0004
    TimeoutError    = 0x0008
    FIFONotEmpty    = 0x0010
    FIFOFull        = 0x0020
    DPMFull         = 0x0040
    UnusedBit7      = 0x0080
    RFPresent       = 0x0100
    SerializerSynch = 0x0200
    DeserializerLock= 0x0400
    UnusedBit11     = 0x0800
    PLLLocked       = 0x1000
    TestPulseRcv    = 0x2000
    FERebootRcv     = 0x4000
    EncodedCmdRcv   = 0x8000
    
class CRIMInterrupterModuleRegs(): 
    RegWRMask           = 0xF000
    RegWRStatus         = 0xF010
    RegWClearInterrupt  = 0xF020
    RegWRIntConfig      = 0xF040
    RegWRVectorTable    = \
    [0xF810, 0xF812, 0xF814, 0xF816, \
     0xF818, 0xF81A, 0xF81C, 0xF81E]

FastCmds={
    'ResetFPGA':0x8D,
    'OpenGate':0xB1,
    'ResetTimer':0xC9,
    'LoadTimer':0xC5,
    'TriggerFound':0x89,
    'TriggerRearm':0x85,
    'QueryFPGA':0x91}

CHECmds={
    'ClearStatus':0x8000,
    'SendMessage':0x4000,
    'ClearSndMemWPointer':0x2000,
    'ClearRcvMemWPointer':0x1000,
    'ClearRDFECounter':0x0800,
    'SendFlashMessage':0x0400,
    'SendTxSyncWords':0x0001}
    
CRIMTimingModes={
    '1 DAQ':0x1000,
    '2 EXT':0x2000,
    '4 INT':0x4000,
    '8 MTM':0x8000}

CRIMTimingFrequencies={
    '0 None':0x0000,
    'F00':0x0001,
    'F01':0x0002,
    'F02':0x0004,
    'F03':0x0008,
    'F04':0x0010,
    'F05':0x0020,
    'F06':0x0040,
    'F07':0x0080,
    'F08':0x0100,
    'F09':0x0200,
    'F10':0x0400,
    'F11':0x0800}
    
def CRIMCHModeChkBoxData():
    pos=(0,0)
    size=(125, 16)
    color=colorLabel
    leftLabels=(
        (' re-transmit', pos, size, '', color),
        (' send message', pos, size, '', color),
        (' CRC error enabled', pos, size, '', color),
        (' FE trigger enabled', pos, size, '', color))
    return leftLabels

def CRIMIntVectorTableIDLabelsData():
    pos=(0,0)
    size=(80, 16)
    color=colorLabel
    leftLabels=(
        (' Vect Inp 0', pos, size, '', color),
        (' Vect Inp 1', pos, size, '', color),
        (' Vect Inp 2', pos, size, '', color),
        (' Vect Inp 3', pos, size, '', color),
        (' Vect Inp 4', pos, size, '', color),
        (' Vect Inp 5', pos, size, '', color),
        (' Vect Inp 6', pos, size, '', color),
        (' Vect Inp 7', pos, size, '', color))
    rightLabels=(('X', pos, (40, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CROCResetAndTestPulseChkBoxData():
    pos=(0,0)
    size=(70, 16)
    color=colorLabel
    leftLabels=(
        ('RST Ch0', pos, size, '', color),
        ('RST Ch1', pos, size, '', color),
        ('RST Ch2', pos, size, '', color),
        ('RST Ch3', pos, size, '', color))
    rightLabels=(
        ('TP Ch0', pos, size, '', color),
        ('TP Ch1', pos, size, '', color),
        ('TP Ch2', pos, size, '', color),
        ('TP Ch3', pos, size, '', color))
    return leftLabels, rightLabels
def CROCEResetAndTestPulseChkBoxData():
    pos=(0,0)
    size=(70, 16)
    color=colorLabel
    leftLabels=(('RST EN', pos, size, '', color),)
    rightLabels=(('TP EN', pos, size, '', color),)
    return leftLabels, rightLabels

def CROCFEBGateDelaysLabelsData():
    pos=(0,0)
    size=(70, 16)
    color=colorLabel
    leftLabels=(
        (' N of Meas', pos, size, '', color),
        (' Load Timer', pos, size, '', color),
        (' Gate Start', pos, size, '', color))
    size=(60, 16)
    color=colorText
    rightLabels=(
        ('5', pos, size, 'NofMeasurements', color),
        ('15', pos, size, 'LoadTimerValue', color),
        ('63500', pos, size, 'GateStartValue', color))
    return leftLabels, rightLabels

def CROCLoopDelaysLabelsData():
    pos=(0,0)
    size=(70, 16)
    color=colorLabel
    leftLabels=(
        (' Channel 0', pos, size, '', color),
        (' Channel 1', pos, size, '', color),
        (' Channel 2', pos, size, '', color),
        (' Channel 3', pos, size, '', color))
    rightLabels=(('X', pos, (60, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CROCCHStatusRegLabelsData():
    pos=(0,0)
    size=(110, 16)
    color=colorLabel
    leftLabels=(
        (' Msg Sent', pos, size, '', color),
        (' Msg Received', pos, size, '', color),
        (' CRC Error', pos, size, '', color),
        (' Timeout Error', pos, size, '', color),
        (' FIFO Not Empty', pos, size, '', color),
        (' FIFO Full', pos, size, '', color),
        (' DPM Full', pos, size, '', color),
        (' Unused', pos, size, '', color),
        (' RF Present', pos, size, '', color),
        (' Serializer SYNC', pos, size, '', color),
        (' Deserializer LOCK', pos, size, '', color),
        (' Unused', pos, size, '', color),
        (' PLL0 LOCK', pos, size, '', color),
        (' PLL1 LOCK', pos, size, '', color),
        (' Unused', pos, size, '', color),
        (' Unused', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CROCEStatusAndVersionRegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftLabels=(
        (' WO CMD Clear Status', pos, size, '', color),
        (' WO CMD Send Message', pos, size, '', color),
        (' RO STATUS Flash Error', pos, size, '', color),
        (' WR ENABLE Memory', pos, size, '', color),
        (' WR ENABLE WRand', pos, size, '', color),
        (' WO CMD Clear WPointer', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Unused', pos, size, '', color),
        (' RO Frmw_Version_3', pos, size, '', color),
        (' RO Frmw_Version_2', pos, size, '', color),
        (' RO Frmw_Version_1', pos, size, '', color),
        (' RO Frmw_Version_0', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def CROCECHEConfigurationRegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftLabels=(
        (' WR RDFEModeEn (MSB)', pos, size, '', color),
        (' WR SndMemWRandEn', pos, size, '', color),
        (' WR SingleHitModeEn', pos, size, '', color),
        (' WR FiveBitsHitEncodEn', pos, size, '', color),
        (' WR EncClkMonitorFEEn', pos, size, '', color),
        (' WR FlashMemEn', pos, size, '', color),
        (' RO Frmw_Version_3', pos, size, '', color),
        (' RO Frmw_Version_2', pos, size, '', color),
        (' RO Frmw_Version_1', pos, size, '', color),
        (' RO Frmw_Version_0', pos, size, '', color),
        (' WR TestPulseEn', pos, size, '', color),
        (' WR ChannelResetEn', pos, size, '', color),
        (' WR NumberOfFEBs_3', pos, size, '', color),
        (' WR NumberOfFEBs_2', pos, size, '', color),
        (' WR NumberOfFEBs_1', pos, size, '', color),
        (' WR NumberOfFEBs_0', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def CROCECHEStatusFrameRegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftLabels=(
        (' SndMem_Full (MSB)', pos, size, '', color),
        (' SndMem_Empty', pos, size, '', color),
        (' SndMem_FrmSending', pos, size, '', color),
        (' SndMem_FrmSent', pos, size, '', color),
        (' SndMem_RDFEUpdating', pos, size, '', color),
        (' SndMem_RDFEDone', pos, size, '', color),
        (' SndMem_RDFEError', pos, size, '', color),
        (' FlashMem_Error', pos, size, '', color),
        (' RcvMem_Full', pos, size, '', color),
        (' RcvMem_Empty', pos, size, '', color),
        (' RcvMem_FrmCntFull', pos, size, '', color),
        (' RcvMem_FrmReceived', pos, size, '', color),
        (' RcvMem_FrmTimeout', pos, size, '', color),
        (' RcvMem_FrmCRCError', pos, size, '', color),
        (' RcvMem_FrmHdrError', pos, size, '', color),
        (' RcvMem_WSMError', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def CROCECHEStatusTXRXRegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftLabels=(
        (' RX_Lock (MSB)', pos, size, '', color),
        (' RX_LockError', pos, size, '', color),
        (' RX_LockStable', pos, size, '', color),
        (' TX_Sync1', pos, size, '', color),
        (' TX_LockError', pos, size, '', color),
        (' TX_LockStable', pos, size, '', color),
        (' TX_Sync2', pos, size, '', color),
        (' TX_EncOutCmdSent', pos, size, '', color),
        (' RX_EncInCmdTimeout', pos, size, '', color),
        (' RX_EncInCmdFound', pos, size, '', color),
        (' RX_EncInCmdMatch', pos, size, '', color),
        (' RX_EncInRFOK', pos, size, '', color),
        (' RX_RstTpOutCmdSent', pos, size, '', color),
        (' TX_RstTpInCmdTimeout', pos, size, '', color),
        (' TX_RstTpInCmdFound', pos, size, '', color),
        (' Unused', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def CROCECHEHeaderRegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftLabels=(
        (' WR Unused', pos, size, '', color),
        (' WR Unused', pos, size, '', color),
        (' WR Unused', pos, size, '', color),
        (' WR Crate_ID_0', pos, size, '', color),
        (' WR CROC_ID_3', pos, size, '', color),
        (' WR CROC_ID_2', pos, size, '', color),
        (' WR CROC_ID_1', pos, size, '', color),
        (' WR CROC_ID_0', pos, size, '', color),
        (' WR FEB_Version_7', pos, size, '', color),
        (' WR FEB_Version_6', pos, size, '', color),
        (' WR FEB_Version_5', pos, size, '', color),
        (' WR FEB_Version_4', pos, size, '', color),
        (' WR FEB_Version_3', pos, size, '', color),
        (' WR FEB_Version_2', pos, size, '', color),
        (' WR FEB_Version_1', pos, size, '', color),
        (' WR FEB_Version_0', pos, size, '', color))
    rightLabels=(('X', pos, (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def CRIMCHStatusRegLabelsData():
    pos=(0,0)
    size=(110, 16)
    color=colorLabel
    leftLabels=(
        (' Msg Sent', pos, size, '', color),
        (' Msg Received', pos, size, '', color),
        (' CRC Error', pos, size, '', color),
        (' Timeout Error', pos, size, '', color),
        (' FIFO Not Empty', pos, size, '', color),
        (' FIFO Full', pos, size, '', color),
        (' DPM Full', pos, size, '', color),
        (' Unused', pos, size, '', color),
        (' RF Present', pos, size, '', color),
        (' Serializer SYNC', pos, size, '', color),
        (' Deserializer LOCK', pos, size, '', color),
        (' Unused', pos, size, '', color),
        (' PLL0 LOCK', pos, size, '', color),
        (' PLL1 LOCK', pos, size, '', color),
        (' FE Reboot Rcv', pos, size, '', color),
        (' Encoded Cmd Rcv', pos, size, '', color))        
    rightLabels=(('X', (0, 0), (10, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels)

def TRIPRegLabelsData():
    pos=(0,0)
    size=(80, 16)
    color=colorLabel
    leftRegLabels=(
        (' IBP', pos, size, '', color),
        (' IBBNFALL', pos, size, '', color),
        (' IFF', pos, size, '', color),
        (' IBPIFF1REF', pos, size, '', color),
        (' IBOPAMP', pos, size, '', color),
        (' IB_T', pos, size, '', color),
        (' IFFP2', pos, size, '', color),
        (' IBCOMP', pos, size, '', color),
        (' VREF', pos, size, '', color),
        (' VTH', pos, size, '', color),
        (' GAIN', pos, size, '', color),
        (' PIPEDEL', pos, size, '', color),
        (' IRSEL', pos, size, '', color),
        (' IWSEL', pos, size, '', color),
        (' INJEX0', pos, size, '', color),
        (' INJB0 (0x)', pos, size, '', color),
        (' INJB1 (0x)', pos, size, '', color),
        (' INJB2 (0x)', pos, size, '', color),
        (' INJB3 (0x)', pos, size, '', color),
        (' INJEX33', pos, size, '', color))
    return leftRegLabels

def TRIPRegTextData():
    pos=(0,0)
    size=(180, 20)
    color=colorText
    rightRegText=(
        ('1', pos, size, 'IBP', color),
        ('2', pos, size, 'IBBNFALL', color),
        ('3', pos, size, 'IFF', color),
        ('4', pos, size, 'IBPIFF1REF', color),
        ('5', pos, size, 'IBOPAMP', color),
        ('6', pos, size, 'IB_T', color),
        ('7', pos, size, 'IFFP2', color),
        ('8', pos, size, 'IBCOMP', color),
        ('9', pos, size, 'VREF', color),
        ('10', pos, size, 'VTH', color),
        ('11', pos, size, 'GAIN', color),
        ('12', pos, size, 'PIPEDEL', color),
        ('13', pos, size, 'IRSEL', color),
        ('14', pos, size, 'IWSEL', color),
        ('1', pos, size, 'INJEX0', color),
        ('F', pos, size, 'INJB0', color),
        ('F0', pos, size, 'INJB1', color),
        ('F', pos, size, 'INJB2', color),
        ('F0', pos, size, 'INJB3', color),
        ('1', pos, size, 'INJEX33', color))
    return rightRegText

def FPGARegLabelsData():
    pos=(0,0)
    size=(140, 16)
    color=colorLabel
    leftRegLabels=(
        #these are the default GUI
        (' WR Trip PowOFF', pos, size, '', color),
        (' WR Gate Start', pos, size, '', color),
        (' WR Gate Length', pos, size, '', color),
        (' WR HV Enable(1)', pos, size, '', color),
        (' WR HV Target', pos, size, '', color),
        (' R  HV Actual', pos, size, '', color),
        (' WR HV Auto(0)Man(1)', pos, size, '', color),
        (' WR HV NumAvg', pos, size, '', color),
        (' WR HV PeriodMan', pos, size, '', color),
        (' R  HV PeriodAuto', pos, size, '', color),
        (' WR HV PulseWidth', pos, size, '', color),
        (' R  Temperature', pos, size, '', color),
        (' R  Firmware Version', pos, size, '', color),
        (' R  FE Board ID', pos, size, '', color),
        #these are the advanced GUI
        (' WR Timer (0x)', pos, size, '', color),
        (' WR Trip0 En+Inj', pos, size, '', color),
        (' WR Trip1 En+Inj', pos, size, '', color),
        (' WR Trip2 En+Inj', pos, size, '', color),
        (' WR Trip3 En+Inj', pos, size, '', color),
        (' WR Trip4 En+Inj', pos, size, '', color),
        (' WR Trip5 En+Inj', pos, size, '', color),
        (' WR TripX InjRange', pos, size, '', color),
        (' WR TripX InjPhase', pos, size, '', color),
        (' WR InjDAC Value', pos, size, '', color),
        (' WR InjDAC Mode(0)', pos, size, '', color),
        (' WR InjDAC R(0)S(1)', pos, size, '', color),   
        (' R  InjDAC Done(1)', pos, size, '', color),
        (' WR Phase R(0)S(1)', pos, size, '', color),
        (' WR Phase -(0)+(1)', pos, size, '', color),
        (' WR Phase Ticks', pos, size, '', color),
        (' R  DCM1 Lock(0)', pos, size, '', color),
        (' R  DCM2 Lock(0)', pos, size, '', color),
        (' R  DCM1 NoCLK(0)', pos, size, '', color),
        (' R  DCM2 NoCLK(0)', pos, size, '', color),
        (' R  DCM2 PhaseDone', pos, size, '', color),
        (' R  DCM2 PhaseTotal', pos, size, '', color),
        (' R  TP Count2b', pos, size, '', color),
        (' R  TP Count (0x)', pos, size, '', color),
        (' WR TripX Threshold', pos, size, '', color),
        (' R  TripX Comparators', pos, size, '', color),
        (' R  ExtTriggFound', pos, size, '', color),
        (' WR ExtTriggRearm', pos, size, '', color),
        (' WR DiscMaskT0 (0x)', pos, size, '', color),
        (' WR DiscMaskT1 (0x)', pos, size, '', color),
        (' WR DiscMaskT2 (0x)', pos, size, '', color),
        (' WR DiscMaskT3 (0x)', pos, size, '', color),
        (' R  GateTimeStamp (0x)', pos, size, '', color),        
        (' R  SCmdErr(1)', pos, size, '', color),
        (' R  FCmdErr(1)', pos, size, '', color),
        (' R  RXLockErr(1)', pos, size, '', color),
        (' R  TXSyncErr(1)', pos, size, '', color),
        (' WR Enable Preview', pos, size, '', color),
        (' WR After Pulse Ticks', pos, size, '', color),
        (' WR TripX ACQ Mode', pos, size, '', color),
        (' R  Digitization Done', pos, size, '', color),
        (' WR Spare 3b', pos, size, '', color),
        (' WR Spare 8b v95 (0x)', pos, size, '', color))
##            #these are the default GUI
##        (' WR Trip PowOFF 00', pos, size, '', color),
##        (' WR Gate Start 01', pos, size, '', color),
##        (' WR Gate Length 02', pos, size, '', color),
##        (' WR HV Enable(1) 03', pos, size, '', color),
##        (' WR HV Target 04', pos, size, '', color),
##        (' R  HV Actual 05', pos, size, '', color),
##        (' WR HV Auto(0)Man(1) 06', pos, size, '', color),
##        (' WR HV NumAvg 07', pos, size, '', color),
##        (' WR HV PeriodMan 08', pos, size, '', color),
##        (' R  HV PeriodAuto 09', pos, size, '', color),
##        (' WR HV PulseWidth 10', pos, size, '', color),
##        (' R  Temperature 11', pos, size, '', color),
##        (' R  Firmware Version 12', pos, size, '', color),
##        (' R  FE Board ID 13', pos, size, '', color),
##        #these are the advanced GUI
##        (' WR Timer (0x) 14', pos, size, '', color),
##        (' WR Trip0 En+Inj 15', pos, size, '', color),
##        (' WR Trip1 En+Inj 16', pos, size, '', color),
##        (' WR Trip2 En+Inj 17', pos, size, '', color),
##        (' WR Trip3 En+Inj 18', pos, size, '', color),
##        (' WR Trip4 En+Inj 19', pos, size, '', color),
##        (' WR Trip5 En+Inj 20', pos, size, '', color),
##        (' WR TripX InjRange 21', pos, size, '', color),
##        (' WR TripX InjPhase 22', pos, size, '', color),
##        (' WR InjDAC Value 23', pos, size, '', color),
##        (' WR InjDAC Mode(0) 24', pos, size, '', color),
##        (' WR InjDAC R(0)S(1) 25', pos, size, '', color),   
##        (' R  InjDAC Done(1) 26', pos, size, '', color),
##        (' WR Phase R(0)S(1) 27', pos, size, '', color),
##        (' WR Phase -(0)+(1) 28', pos, size, '', color),
##        (' WR Phase Ticks 29', pos, size, '', color),
##        (' R  DCM1 Lock(0) 30', pos, size, '', color),
##        (' R  DCM2 Lock(0) 31', pos, size, '', color),
##        (' R  DCM1 NoCLK(0) 32', pos, size, '', color),
##        (' R  DCM2 NoCLK(0) 33', pos, size, '', color),
##        (' R  DCM2 PhaseDone 34', pos, size, '', color),
##        (' R  DCM2 PhaseTotal 35', pos, size, '', color),
##        (' R  TP Count2b 36', pos, size, '', color),
##        (' R  TP Count (0x) 37', pos, size, '', color),
##        (' WR TripX Threshold 38', pos, size, '', color),
##        (' R  TripX Comparators 39', pos, size, '', color),
##        (' R  ExtTriggFound 40', pos, size, '', color),
##        (' WR ExtTriggRearm 41', pos, size, '', color),
##        (' WR DiscMaskT0 (0x) 42', pos, size, '', color),
##        (' WR DiscMaskT1 (0x) 43', pos, size, '', color),
##        (' WR DiscMaskT2 (0x) 44', pos, size, '', color),
##        (' WR DiscMaskT3 (0x) 45', pos, size, '', color),
##        (' R  GateTimeStamp (0x) 46', pos, size, '', color),        
##        (' R  SCmdErr(1) 47', pos, size, '', color),
##        (' R  FCmdErr(1) 48', pos, size, '', color),
##        (' R  RXLockErr(1) 49', pos, size, '', color),
##        (' R  TXSyncErr(1) 50', pos, size, '', color),
##        (' WR Enable Preview 51', pos, size, '', color),
##        (' WR After Pulse Ticks 52', pos, size, '', color),
##        (' WR TripX ACQ Mode 53', pos, size, '', color),
##        (' R  Digitization Done 54', pos, size, '', color),
##        (' WR Spare 55', pos, size, '', color))
    return leftRegLabels

def FPGARegTextData():
    pos=(0,0)
    size=(70, 20)
    color=colorText
    rightRegText=(
        #these are the default GUI
        ('', pos, size, ' WR Trip PowOFF', color),
        ('', pos, size, ' WR Gate Start', color),
        ('', pos, size, ' WR Gate Length', color),
        ('', pos, size, ' WR HV Enable(1)', color),
        ('', pos, size, ' WR HV Target', color),
        ('', pos, size, ' R  HV Actual', color),
        ('', pos, size, ' WR HV Auto(0)Man(1)', color),
        ('', pos, size, ' WR HV NumAvg', color),
        ('', pos, size, ' WR HV PeriodMan', color),
        ('', pos, size, ' R  HV PeriodAuto', color),
        ('', pos, size, ' WR HV PulseWidth', color),
        ('', pos, size, ' R  Temperature', color),
        ('', pos, size, ' R  Version', color),
        ('', pos, size, ' R  FEB ID', color),
        #these are the advanced GUI
        ('', pos, size, ' WR Timer', color),
        ('', pos, size, ' WR Trip0 En+Inj', color),
        ('', pos, size, ' WR Trip1 En+Inj', color),
        ('', pos, size, ' WR Trip2 En+Inj', color),
        ('', pos, size, ' WR Trip3 En+Inj', color),
        ('', pos, size, ' WR Trip4 En+Inj', color),
        ('', pos, size, ' WR Trip5 En+Inj', color),
        ('', pos, size, ' WR TripX InjRange', color),
        ('', pos, size, ' WR TripX InjPhase', color),
        ('', pos, size, ' WR InjDAC Value', color),
        ('', pos, size, ' WR InjDAC Mode(0)', color),
        ('', pos, size, ' WR InjDAC R(0)S(1)', color),   
        ('', pos, size, ' R  InjDAC Done(1)', color),
        ('', pos, size, ' WR Phase R(0)S(1)', color),
        ('', pos, size, ' WR Phase -(0)+(1)', color),
        ('', pos, size, ' WR Phase Ticks', color),
        ('', pos, size, ' R  DCM1 Lock(0)', color),
        ('', pos, size, ' R  DCM2 Lock(0)', color),
        ('', pos, size, ' R  DCM1 NoCLK(0)', color),
        ('', pos, size, ' R  DCM2 NoCLK(0)', color),
        ('', pos, size, ' R  DCM2 PhaseDone', color),
        ('', pos, size, ' R  DCM2 PhaseTotal', color),
        ('', pos, size, ' R  TP Count2b', color),
        ('', pos, size, ' R  TP Count (0x)', color),
        ('', pos, size, ' WR TripX Threshold', color),
        ('', pos, size, ' R  TripX Comparators', color),
        ('', pos, size, ' R  ExtTriggFound', color),
        ('', pos, size, ' WR ExtTriggRearm', color),
        ('', pos, size, ' WR DiscrimTrip0 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip1 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip2 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip3 (0x)', color),
        ('', pos, size, ' R  GateTimeStamp (0x)', color),        
        ('', pos, size, ' R  SCmdErr(1)', color),
        ('', pos, size, ' R  FCmdErr(1)', color),
        ('', pos, size, ' R  RXLockErr(1)', color),
        ('', pos, size, ' R  TXSyncErr(1)', color),
        ('', pos, size, ' WR Enable Hit Preview', color),
        ('', pos, size, ' WR After Pulse Ticks', color),
        ('', pos, size, ' WR TripX ACQ Mode', color),
        ('', pos, size, ' R  Digitization Done', color),
        ('', pos, size, ' WR Spare 3b', color),
        ('', pos, size, ' WR Spare 8b v95', color))
    return rightRegText

def CreateLabels(panel, data, style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE, offset=(0,0)):
    '''Returns a list of wx.StaticText objects, as specified by Data'''
    top = [] 
    for label, pos, size, name, color in data:
        newpos = (pos[0]+offset[0], pos[1]+offset[1])
        top.append(CreateLabel(panel, label, newpos, size, name, color, style))
    return top

def CreateButtons(panel, data, offset=(0,0)):
    '''Returns a list of wx.Button objects, as specified by Data'''
    top = []
    for label, pos, size, name, color in data:
        newpos = (pos[0]+offset[0], pos[1]+offset[1])
        top.append(CreateButton(panel, label, newpos, size, name, color))
    return top

def CreateTextCtrls(panel, data, offset=(0,0)):
    '''Returns a list of wx.TextCtrl objects, as specified by Data'''
    top = []
    for label, pos, size, name, color in data:
        newpos = (pos[0]+offset[0], pos[1]+offset[1])
        top.append(CreateTextCtrl(panel, label, newpos, size, name, color))
    return top

def CreateCheckBoxs(panel, data, offset=(0,0)):
    '''Returns a list of wx.CheckBox objects, as specified by Data'''
    top = []
    for label, pos, size, name, color in data:
        newpos = (pos[0]+offset[0], pos[1]+offset[1])
        top.append(CreateCheckBox(panel, label, newpos, size, name, color))
    return top

def CreateLabel(panel, label, pos, size, name, color, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE):
    '''Returns a wx.StaticText object'''
    theLabel = wx.StaticText(panel, label=label, pos=pos, size=size, style=style, name=name)
    theLabel.SetBackgroundColour(color)
    theLabel.SetFont(myFont(fontSizeLabel))
    return theLabel

def CreateButton(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.Button object'''
    theButton = wx.Button(panel, label=label, pos=pos, size=size)#, 
        #style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
    theButton.SetBackgroundColour(bckcolor)
    theButton.SetFont(myFont(fontSizeButton))
    return theButton

def CreateTextCtrl(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.TextCtrl object'''
    theTextCtrl = wx.TextCtrl(panel, value=label, pos=pos, size=size, name=name)
    theTextCtrl.SetBackgroundColour(bckcolor)
    theTextCtrl.SetFont(myFont(fontSizeTextCtrl))
    return theTextCtrl

def CreateCheckBox(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.CheckBox object'''
    theCheckBox = wx.CheckBox(panel, label=label, pos=pos, size=size, name=name)
    theCheckBox.SetBackgroundColour(bckcolor)
    theCheckBox.SetFont(myFont(fontSizeCheckBox))
    return theCheckBox

def ShowControls(btnShow, boolShow=True, *paramctrls):
    '''Hide/Show a list of control objects (StaticText, TextCtrl etc.'''
    for ctrls in paramctrls:
        for control in ctrls:
            control.Show(boolShow)
    boolShow=not(boolShow)
    if boolShow==True: btnShow.Label="Show Advanced GUI"
    else: btnShow.Label="Show Default GUI"
    return boolShow

def AddTreeNodes(tree, parentItem, items):
    '''Add the 'items' list of nodes to a given parentItem node'''
    for item in items:
        if type(item) == str:
            tree.AppendItem(parentItem, item)
        else:
            newParentItem=tree.AppendItem(parentItem, item[0])
            AddTreeNodes(tree, newParentItem, item[1])

def GetChildren(tree, parent):
    '''Returns a list of the text for each child of a given tree item'''
    result=[]
    item, cookie = tree.GetFirstChild(parent)
    while item:
        result.append(tree.GetItemText(item))
        item, cookie = tree.GetNextChild(parent, cookie)
    return result

def SizerTop(btnShowAdvancedGUI, TopLabels):       
    szTopLabels=wx.FlexGridSizer(rows=1, cols=8, hgap=0, vgap=0)
    for lbl in TopLabels:
        szTopLabels.Add(lbl,0,wx.ALL,0)
    szTop=wx.FlexGridSizer(rows=1, cols=2, hgap=0, vgap=0)
    szTop.Add(btnShowAdvancedGUI,0,wx.ALL,5)
    szTop.Add(szTopLabels,0,wx.ALL,7)
    return szTop

class BoardTest():
 def __init__(self, panel, caption=' CROCE Board Test',testcaptions=['RUN BOARD TEST','T1','T2','T3','T4','T5','T6','T7','T8','T9'],
              optioncaptions=['Opt 0','Opt 1']):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.btnRunBoardTest=CreateButton(panel, testcaptions[0], pos=(0,0), size=(160, 20), name='', bckcolor=colorButton)
        lblNtimes=CreateLabel(panel, 'N times', pos=(0,0), size=(65, 20), name='', color=colorLabel)
        self.txtNtimes=CreateTextCtrl(panel, label='1', pos=(0,0), size=(65, 20), name='', bckcolor=colorText)
        self.chkCh=[0,0,0,0]
        for i in range(4):
            self.chkCh[i]=CreateCheckBox(panel, 'Ch%d'%i, pos=(0,0), size=(78,20), name='', bckcolor=colorButton)
            self.chkCh[i].SetValue(True)
        self.chkTest1=CreateCheckBox(panel, testcaptions[1], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest2=CreateCheckBox(panel, testcaptions[2], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest3=CreateCheckBox(panel, testcaptions[3], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest4=CreateCheckBox(panel, testcaptions[4], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest5=CreateCheckBox(panel, testcaptions[5], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest6=CreateCheckBox(panel, testcaptions[6], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest7=CreateCheckBox(panel, testcaptions[7], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest8=CreateCheckBox(panel, testcaptions[8], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkTest9=CreateCheckBox(panel, testcaptions[9], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkUseErrorData=CreateCheckBox(panel, optioncaptions[2], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkUseRandomData=CreateCheckBox(panel, optioncaptions[1], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkIncludeRAMMode=CreateCheckBox(panel, optioncaptions[0], pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkIncludeRAMMode.SetValue(True)
        lblRAMData=CreateLabel(panel, 'RAM data', pos=(0,0), size=(75, 20), name='', color=colorLabel)
        self.txtRAMData=CreateTextCtrl(panel, label='FFFF', pos=(0,0), size=(65, 20), name='', bckcolor=colorText)
        lblRegHeader=CreateLabel(panel, 'Header data', pos=(0,0), size=(75, 20), name='', color=colorLabel)
        self.txtREGHeader=CreateTextCtrl(panel, label='0000', pos=(0,0), size=(65, 20), name='', bckcolor=colorText)
        lblRegTest=CreateLabel(panel, 'Test Reg data', pos=(0,0), size=(75, 20), name='', color=colorLabel)
        self.txtREGTestData=CreateTextCtrl(panel, label='FFFF', pos=(0,0), size=(65, 20), name='', bckcolor=colorText)
        self.chkWriteToFile=CreateCheckBox(panel, 'Write To File', pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        self.chkIncludeCRCCheck=CreateCheckBox(panel, 'Include CRC Check', pos=(0,0), size=(160,20), name='', bckcolor=colorButton)
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(self.btnRunBoardTest, 0, wx.ALL, 2)
        szH1.Add(lblNtimes, 0, wx.ALL, 6)
        szH1.Add(self.txtNtimes, 0, wx.ALL, 2)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(lblRAMData, 0, wx.ALL, 2)
        szH2.Add(self.txtRAMData, 0, wx.ALL, 0)
        szH3=wx.BoxSizer(wx.HORIZONTAL)
        szH3.Add(lblRegHeader, 0, wx.ALL, 2)
        szH3.Add(self.txtREGHeader, 0, wx.ALL, 0)
        szH4=wx.BoxSizer(wx.HORIZONTAL)
        szH4.Add(lblRegTest, 0, wx.ALL, 2)
        szH4.Add(self.txtREGTestData, 0, wx.ALL, 0)
        szH5=wx.BoxSizer(wx.HORIZONTAL)
        for ich in self.chkCh: szH5.Add(ich, 0, wx.ALL, 2)
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.chkTest1, 0, wx.ALL, 0)
        szV1.Add(self.chkTest2, 0, wx.ALL, 0)
        szV1.Add(self.chkTest3, 0, wx.ALL, 0)
        szV1.Add(self.chkTest4, 0, wx.ALL, 0)
        szV1.Add(self.chkTest5, 0, wx.ALL, 0)
        szV1.Add(self.chkTest6, 0, wx.ALL, 0)
        szV1.Add(self.chkTest7, 0, wx.ALL, 0)
        szV1.Add(self.chkTest8, 0, wx.ALL, 0)
        szV1.Add(self.chkTest9, 0, wx.ALL, 0)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.chkUseErrorData, 0, wx.ALL, 0)
        szV2.Add(self.chkUseRandomData, 0, wx.ALL, 0)
        szV2.Add(self.chkIncludeRAMMode, 0, wx.ALL, 0)
        szV2.Add(szH2, 0, wx.ALL, 0)
        szV2.Add(szH3, 0, wx.ALL, 0)
        szV2.Add(szH4, 0, wx.ALL, 0)
        szV2.Add(self.chkWriteToFile, 0, wx.ALL, 0)
        szV2.Add(self.chkIncludeCRCCheck, 0, wx.ALL, 0)
        szH6=wx.BoxSizer(wx.HORIZONTAL)
        szH6.Add(szV1, 0, wx.ALL, 2)
        szH6.Add(szV2, 0, wx.ALL, 2)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(szH1, 0, wx.ALL, 2)
        self.BoxSizer.Add(szH5, 0, wx.ALL, 2)
        self.BoxSizer.Add(szH6, 0, wx.ALL, 2)
        self.controls=[StaticBox,self.BoxSizer,self.btnRunBoardTest,lblNtimes,
            self.txtNtimes,self.chkCh[0],self.chkCh[1],self.chkCh[2],self.chkCh[3],
            self.chkTest1,self.chkTest2,self.chkTest3,self.chkTest4,self.chkTest5,
            self.chkTest6,self.chkTest7,self.chkTest8,self.chkTest9,
            self.chkUseErrorData,self.chkUseRandomData,self.chkIncludeRAMMode,
            lblRAMData,self.txtRAMData,lblRegHeader,self.txtREGHeader,lblRegTest,
            self.txtREGTestData,self.chkWriteToFile,self.chkIncludeCRCCheck]

class VMEReadWrite():
    def __init__(self, panel, caption=' VME Read/Write (hex)'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        lblEmpty=CreateLabel(panel, '',
            pos=(0,0), size=(100, 16), name='', color=colorLabel)
        lblAddr=CreateLabel(panel, 'Address',
            pos=(0,0), size=(100, 16), name='', color=colorLabel)
        lblData=CreateLabel(panel, 'Data/Size',
            pos=(0,0), size=(100, 16), name='', color=colorLabel)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorButton)
        self.txtReadAddr = CreateTextCtrl(panel, label='addr',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorText)
        self.txtReadData = CreateTextCtrl(panel, label='data',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorText)
        self.txtReadData.Enable(False)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorButton)
        self.txtWriteAddr = CreateTextCtrl(panel, label='addr',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorText)
        self.txtWriteData = CreateTextCtrl(panel, label='data',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorText)
        AM=list(CAENVMETypes.cvAMDict.keys()); AM.sort()
        DW=list(CAENVMETypes.cvDWDict.keys()); DW.sort()
        self.choiceAddressModifier=wx.Choice(panel, size=(100,20), choices=AM)
        self.choiceAddressModifier.SetFont(myFont(fontSizeChoice))
        self.choiceDataWidth=wx.Choice(panel, size=(100,20), choices=DW)
        self.choiceDataWidth.SetFont(myFont(fontSizeChoice))
        self.txtBLTSize = CreateTextCtrl(panel, label='size',
            pos=(0,0), size=(100, 20), name='', bckcolor=colorText)
        szFGS = wx.FlexGridSizer(rows=4, cols=3, hgap=5, vgap=5)
        szFGS.Add(lblEmpty, 0, 0, 0)
        szFGS.Add(lblAddr, 0, 0, 0)
        szFGS.Add(lblData, 0, 0, 0)
        szFGS.Add(self.btnRead, 0, 0, 0)
        szFGS.Add(self.txtReadAddr, 0, 0, 0)
        szFGS.Add(self.txtReadData, 0, 0, 0)
        szFGS.Add(self.btnWrite, 0, 0, 0)
        szFGS.Add(self.txtWriteAddr, 0, 0, 0)
        szFGS.Add(self.txtWriteData, 0, 0, 0)
        szFGS.Add(self.choiceAddressModifier, 0, 0, 0)
        szFGS.Add(self.choiceDataWidth, 0, 0, 0)
        szFGS.Add(self.txtBLTSize, 0, 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(szFGS, 0, 0, 0)
        self.controls=[StaticBox,self.BoxSizer,lblEmpty,lblAddr,lblData,
            self.btnRead,self.txtReadAddr,self.txtReadData,
            self.btnWrite,self.txtWriteAddr,self.txtWriteData,
            self.choiceAddressModifier,self.choiceDataWidth,self.txtBLTSize]
    
class CRIMTimingTimingSetupRegister():
    def __init__(self, panel, caption=' Timing Setup Register'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        Modes=list(CRIMTimingModes.keys()); Modes.sort()
        Frequencies=list(CRIMTimingFrequencies.keys()); Frequencies.sort()
        self.choiceMode=wx.Choice(panel, size=(125,20), choices=Modes)
        self.choiceFrequency=wx.Choice(panel, size=(125,20), choices=Frequencies)
        self.choiceMode.SetFont(myFont(fontSizeChoice))
        self.choiceFrequency.SetFont(myFont(fontSizeChoice))
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceMode, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.choiceFrequency, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)        
        self.controls=[StaticBox, self.choiceMode, self.choiceFrequency,
            self.btnWrite, self.btnRead]
    def ResetControls(self):
        self.choiceMode.SetSelection(0)
        self.choiceFrequency.SetSelection(0)
    
class FlashButtons():
    def __init__(self, panel):
        FlashBox=wx.StaticBox(panel, -1, 'Flash Commands')
        FlashBox.SetFont(myFont(fontSizeStaticBox))
        FlashBox.SetForegroundColour(colorForeground)
        self.btnReadFlashToFile=CreateButton(panel, 'Read Flash To File',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnCompareFileToFlash=CreateButton(panel, 'Compare File To Flash',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlash=CreateButton(panel, 'Write File To Flash',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCH=CreateButton(panel, 'Write File To Flash This CH',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCROC=CreateButton(panel, 'Write File To Flash This CROC',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCRATE=CreateButton(panel, 'Write File To Flash This CRATE',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashALL=CreateButton(panel, 'Write File To Flash ALL',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)        
        self.FlashBoxSizer=wx.StaticBoxSizer(FlashBox, wx.VERTICAL)
        self.FlashBoxSizer.Add(self.btnReadFlashToFile, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnCompareFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCH, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCROC, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCRATE, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashALL, 0, wx.ALL|wx.EXPAND, 2)
        self.controls=[FlashBox, self.btnReadFlashToFile, self.btnCompareFileToFlash,
            self.btnWriteFileToFlash, self.btnWriteFileToFlashThisCH,
            self.btnWriteFileToFlashThisCROC, self.btnWriteFileToFlashThisCRATE,
            self.btnWriteFileToFlashALL]
class FlashEButtons():
    def __init__(self, panel):
        FlashBox=wx.StaticBox(panel, -1, 'Flash Commands')
        FlashBox.SetFont(myFont(fontSizeStaticBox))
        FlashBox.SetForegroundColour(colorForeground)
        self.btnReadFlashToFile=CreateButton(panel, 'Read Flash To File',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnCompareFileToFlash=CreateButton(panel, 'Compare File To Flash',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlash=CreateButton(panel, 'Write File To Flash',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCRATE=CreateButton(panel, 'Write File To Flash This CRATE',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashALL=CreateButton(panel, 'Write File To Flash ALL',
            pos=(0,0), size=(225,20), name='', bckcolor=colorButton)        
        self.FlashBoxSizer=wx.StaticBoxSizer(FlashBox, wx.VERTICAL)
        self.FlashBoxSizer.Add(self.btnReadFlashToFile, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnCompareFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCRATE, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashALL, 0, wx.ALL|wx.EXPAND, 2)
        self.controls=[FlashBox, self.btnReadFlashToFile, self.btnCompareFileToFlash,
            self.btnWriteFileToFlash, self.btnWriteFileToFlashThisCRATE,
            self.btnWriteFileToFlashALL]
class FlashEBasicCommands():
    def __init__(self, panel):
        FlashBox=wx.StaticBox(panel, -1, 'Flash Basic Commands')
        FlashBox.SetFont(myFont(fontSizeStaticBox))
        FlashBox.SetForegroundColour(colorForeground)
        self.btnFlashCmdWriteEnable=CreateButton(panel, 'Write Enable',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdWriteDisable=CreateButton(panel, 'Write Disable',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReadStatus=CreateButton(panel, 'Read Status',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdWriteStatus=CreateButton(panel, 'Write Status',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReadData=CreateButton(panel, 'Read Data',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdSectorErase=CreateButton(panel, 'Sector Erase',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdBlockErase=CreateButton(panel, 'Block Erase',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdChipErase=CreateButton(panel, 'Chip Erase',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdPageProgram=CreateButton(panel, 'Page Program',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdDeepPowerDown=CreateButton(panel, 'Deep Power Down',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReleaseDPD=CreateButton(panel, 'Release DPD',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReadID=CreateButton(panel, 'Read ID',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReadEMandID=CreateButton(panel, 'Read EM & ID',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdReadSecurity=CreateButton(panel, 'Read Security',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnFlashCmdWriteSecurity=CreateButton(panel, 'Write Security',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        fgs=wx.FlexGridSizer(rows=5, cols=3, hgap=5, vgap=5)
        fgs.Add(self.btnFlashCmdWriteEnable, 0, 0)
        fgs.Add(self.btnFlashCmdWriteDisable, 0, 0)
        fgs.Add(self.btnFlashCmdReadStatus, 0, 0)
        fgs.Add(self.btnFlashCmdWriteStatus, 0, 0)
        fgs.Add(self.btnFlashCmdReadData, 0, 0)
        fgs.Add(self.btnFlashCmdSectorErase, 0, 0)
        fgs.Add(self.btnFlashCmdBlockErase, 0, 0)
        fgs.Add(self.btnFlashCmdChipErase, 0, 0)
        fgs.Add(self.btnFlashCmdPageProgram, 0, 0)
        fgs.Add(self.btnFlashCmdDeepPowerDown, 0, 0)
        fgs.Add(self.btnFlashCmdReleaseDPD, 0, 0)
        fgs.Add(self.btnFlashCmdReadID, 0, 0)
        fgs.Add(self.btnFlashCmdReadEMandID, 0, 0)
        fgs.Add(self.btnFlashCmdReadSecurity, 0, 0)
        fgs.Add(self.btnFlashCmdWriteSecurity, 0, 0)
        self.FlashBoxSizer=wx.StaticBoxSizer(FlashBox, wx.VERTICAL)
        self.FlashBoxSizer.Add(fgs, 0, wx.ALL, 2)
        self.controls=[FlashBox,
            self.btnFlashCmdWriteEnable, self.btnFlashCmdWriteDisable, self.btnFlashCmdReadStatus,
            self.btnFlashCmdWriteStatus, self.btnFlashCmdReadData, self.btnFlashCmdSectorErase,
            self.btnFlashCmdBlockErase, self.btnFlashCmdChipErase, self.btnFlashCmdPageProgram,
            self.btnFlashCmdDeepPowerDown, self.btnFlashCmdReleaseDPD, self.btnFlashCmdReadID,
            self.btnFlashCmdReadEMandID, self.btnFlashCmdReadSecurity, self.btnFlashCmdWriteSecurity]
        
class StatusRegister():
    def __init__(self, panel, caption='CROC CH'):
        if caption=='CROC CH':
            leftLabelsData, rightLabelData = CROCCHStatusRegLabelsData()
        if caption=='CRIM CH':
            leftLabelsData, rightLabelData = CRIMCHStatusRegLabelsData()
        StaticBox=wx.StaticBox(panel, -1, caption+' Status Reg')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnClearStatus=CreateButton(panel, 'Clear Status',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnReadStatus=CreateButton(panel, 'Read Status',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.txtReadStatusData = CreateTextCtrl(panel, label='status value',
            pos=(0,0), size=(125, 20), name='', bckcolor=colorText)
        self.txtReadStatusData.Enable(False) 
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnClearStatus, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadStatus, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtReadStatusData, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnClearStatus, self.btnReadStatus, self.txtReadStatusData]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtReadStatusData.SetValue('')
        for txt in self.RegValues: txt.Label=''

class GenericRegister():
    def __init__(self, panel, caption='Generic Register (hex)', 
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=False, btnReadCaption='Read',
            txtDataVisible=False, txtDataCaption='value', WEnable=True, size=(125,20)):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.controls=[StaticBox]
        if btnWriteVisible==True:
            self.btnWrite=CreateButton(panel, btnWriteCaption,
                pos=(0,0), size=size, name='', bckcolor=colorButton)
            self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
            self.controls.append(self.btnWrite)
        if btnReadVisible==True:
            self.btnRead=CreateButton(panel, btnReadCaption,
                pos=(0,0), size=size, name='', bckcolor=colorButton)
            self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)
            self.controls.append(self.btnRead)
        if txtDataVisible==True:
            self.txtData = CreateTextCtrl(panel, label=txtDataCaption,
                pos=(0,0), size=size, name='', bckcolor=colorText)
            self.txtData.Enable(WEnable)
            self.BoxSizer.Add(self.txtData, 0, wx.ALL, 2)
            self.controls.append(self.txtData)
        self.txtDataVisible=txtDataVisible
    def ResetControls(self):
        if self.txtDataVisible==True: self.txtData.SetValue('')
 
class MessageRegisters():
    def __init__(self, panel):
        StaticBox=wx.StaticBox(panel, -1, 'Message Registers (hex)')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.txtAppendMessage=CreateTextCtrl(panel, 'message string',
            pos=(0,0), size=(125,16), name='', bckcolor=colorText)
        self.btnWriteFIFO=CreateButton(panel, 'Write FIFO',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnSendFrame=CreateButton(panel, 'Send Frame',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnReadDPMWordsN=CreateButton(panel, 'Read DPM Words#',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.txtReadDPMWordsN=CreateTextCtrl(panel, '#words',
            pos=(0,0), size=(125,20), name='', bckcolor=colorText)
        self.txtReadDPMContent=wx.TextCtrl(panel, -1, size=(125,100),
            style = wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)
        self.txtReadDPMContent.SetFont(myFont(fontSizeTextCtrl))
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.txtAppendMessage, 0, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.btnWriteFIFO, 0, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.btnSendFrame, 0, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.btnReadDPMWordsN, 0, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.txtReadDPMWordsN, 0, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.txtReadDPMContent, 1, wx.ALL|wx.EXPAND, 2)       
        self.controls=[StaticBox, self.txtAppendMessage,
            self.btnWriteFIFO, self.btnSendFrame, self.btnReadDPMWordsN,
            self.txtReadDPMWordsN, self.txtReadDPMContent]
    def ResetControls(self):
        self.txtAppendMessage.SetValue('')
        self.txtReadDPMWordsN.SetValue('')
        self.txtReadDPMContent.SetValue('')

class CRIMTimingTimingSetupRegister():
    def __init__(self, panel, caption=' Timing Setup Register'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        Modes=list(CRIMTimingModes.keys()); Modes.sort()
        Frequencies=list(CRIMTimingFrequencies.keys()); Frequencies.sort()
        self.choiceMode=wx.Choice(panel, size=(125,20), choices=Modes)
        self.choiceFrequency=wx.Choice(panel, size=(125,20), choices=Frequencies)
        self.choiceMode.SetFont(myFont(fontSizeChoice))
        self.choiceFrequency.SetFont(myFont(fontSizeChoice))
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceMode, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.choiceFrequency, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)        
        self.controls=[StaticBox, self.choiceMode, self.choiceFrequency,
            self.btnWrite, self.btnRead]
    def ResetControls(self):
        self.choiceMode.SetSelection(0)
        self.choiceFrequency.SetSelection(0)


class CRIMTimingGateWidthRegister():
    def __init__(self, panel, caption='Gate Width Register'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.chkCNTRSTEnable=CreateCheckBox(panel, 'TCALB Enable',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.txtGateWidthData = CreateTextCtrl(panel, label='150.6ns per bit',
            pos=(0,0), size=(125, 20), name='', bckcolor=colorText)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.chkCNTRSTEnable, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtGateWidthData, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.chkCNTRSTEnable,
            self.txtGateWidthData, self.btnWrite, self.btnRead]
    def ResetControls(self):
        self.chkCNTRSTEnable.SetValue(False)
        self.txtGateWidthData.SetValue('')

class CRIMCHMiscRegisters():
    def __init__(self, panel):
        StaticBox=wx.StaticBox(panel, -1, 'Misc Registers')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.btnFIFOFlagReset=CreateButton(panel, 'Reset FIFO Flag',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnTimingCmdRead=CreateButton(panel, 'Read Timing Cmd',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.txtTimingCmdReadData = CreateTextCtrl(panel, label='timing cmd data',
            pos=(0,0), size=(125, 20), name='', bckcolor=colorText)
        self.txtTimingCmdReadData.Enable(False)
        self.btnSendSYNC=CreateButton(panel, 'Send SYNC',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnFIFOFlagReset, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnTimingCmdRead, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtTimingCmdReadData, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendSYNC, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnFIFOFlagReset,
            self.btnTimingCmdRead, self.txtTimingCmdReadData, self.btnSendSYNC]
    def ResetControls(self):
        self.txtTimingCmdReadData.SetValue('')

class CRIMCHModeRegister():
    def __init__(self, panel):
        StaticBox=wx.StaticBox(panel, -1, 'Mode Register')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.chkReTransmit=CreateCheckBox(panel, 'Re-Transmit',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.chkSendMessage=CreateCheckBox(panel, 'Send Message',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.chkCRCErrorEnabled=CreateCheckBox(panel, 'CRC Error Enabled',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.chkFETriggerEnabled=CreateCheckBox(panel, 'FE Trigger Enabled',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.chkReTransmit, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkSendMessage, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkCRCErrorEnabled, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkFETriggerEnabled, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)       
        self.controls=[StaticBox, self.chkReTransmit, self.chkSendMessage,
            self.chkCRCErrorEnabled, self.chkFETriggerEnabled,
            self.btnWrite, self.btnRead]
    def ResetControls(self):
        self.chkReTransmit.SetValue(False)
        self.chkSendMessage.SetValue(False)
        self.chkCRCErrorEnabled.SetValue(False)
        self.chkFETriggerEnabled.SetValue(False)

class CRIMIntVectorTableID():
    def __init__(self, panel, caption=' Vector Table IDs (hex)'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        leftLabelsData, rightTextsData = CRIMIntVectorTableIDLabelsData()      
        rows=len(leftLabelsData)
        lblVectorLabels=CreateLabels(panel, leftLabelsData)
        self.txtVectorValues=CreateTextCtrls(panel, rightTextsData)
        VectorSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            VectorSizer.Add(lblVectorLabels[i], 0, 0)
            VectorSizer.Add(self.txtVectorValues[i], 0, 0)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)
        self.BoxSizer.Add(VectorSizer, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnWrite, self.btnRead]
        for lbl in lblVectorLabels: self.controls.append(lbl)
        for txt in self.txtVectorValues: self.controls.append(txt)
    def ResetControls(self):
        for txt in self.txtVectorValues: txt.SetValue('')

class CRIMIntConfigRegister():
    def __init__(self, panel, caption='Int Config Register'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.chkGlobalIntEnable=CreateCheckBox(panel, 'Global Int Enable',
            pos=(0,0), size=(125,16), name='', bckcolor=colorButton)
        self.txtVMEIntLevelData = CreateTextCtrl(panel, label='VME Int Level',
            pos=(0,0), size=(125, 20), name='', bckcolor=colorText)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.chkGlobalIntEnable, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtVMEIntLevelData, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.chkGlobalIntEnable,
            self.txtVMEIntLevelData, self.btnWrite, self.btnRead]
    def ResetControls(self):
        self.chkGlobalIntEnable.SetValue(False)
        self.txtVMEIntLevelData.SetValue('')

class CROCTimingSetup():
    def __init__(self, panel, caption=' Timing Setup'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.choiceCLKSource=wx.Choice(panel, size=(145,20),
            choices=['0 CLK Internal', '1 CLK External'])
        self.choiceTPDelayEnable=wx.Choice(panel, size=(145,20),
            choices=['0 TPDel Disabled', '1 TPDel Enabled'])
        self.choiceCLKSource.SetFont(myFont(fontSizeChoice))
        self.choiceTPDelayEnable.SetFont(myFont(fontSizeChoice))
        lblTPDelayValue=CreateLabel(panel, 'Delay Val',
            pos=(0,0), size=(70, 16), name='', color=colorLabel)
        self.txtTPDelayValue=CreateTextCtrl(panel, label='TP Delay',
            pos=(0,0), size=(70, 20), name='', bckcolor=colorText)
        self.btnWriteTimingSetup=CreateButton(panel, 'Write',
            pos=(0,0), size=(70,20), name='', bckcolor=colorButton)
        self.btnReadTimingSetup=CreateButton(panel, 'Read',
            pos=(0,0), size=(70,20), name='', bckcolor=colorButton)
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(lblTPDelayValue, 0, wx.ALL, 2)
        szH1.Add(self.txtTPDelayValue, 0, wx.ALL, 0)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(self.btnWriteTimingSetup, 0, wx.ALL, 1)
        szH2.Add(self.btnReadTimingSetup, 0, wx.ALL, 1)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceCLKSource, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.choiceTPDelayEnable, 0, wx.ALL, 2)
        self.BoxSizer.Add(szH1, 0, wx.ALL, 2)
        self.BoxSizer.Add(szH2, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.choiceCLKSource,
            self.choiceTPDelayEnable, lblTPDelayValue, self.txtTPDelayValue,
            self.btnWriteTimingSetup, self.btnReadTimingSetup]
    def ResetControls(self):
        self.choiceCLKSource.SetSelection(0)
        self.choiceTPDelayEnable.SetSelection(0)
        self.txtTPDelayValue.SetValue('')

class CROCFastCmd():
    def __init__(self, panel, caption=' Fast Commands'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        FCmds=list(FastCmds.keys()); FCmds.sort()
        self.choiceFastCmd=wx.Choice(panel, size=(145,20), choices=FCmds)
        self.choiceFastCmd.SetFont(myFont(fontSizeChoice))
        self.btnSendFastCmd=CreateButton(panel, 'Send Fast Cmd',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnSendFastCmdAll=CreateButton(panel, 'Send Fast Cmd All',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceFastCmd, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendFastCmd, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendFastCmdAll, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.choiceFastCmd, self.btnSendFastCmd, self.btnSendFastCmdAll]
    def ResetControls(self):
        self.choiceFastCmd.SetSelection(0)

class CROCLoopDelays():
    def __init__(self, panel, caption=' LoopDelays'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        leftLabelsData, rightLabelsData = CROCLoopDelaysLabelsData()
        rows=len(leftLabelsData)
        LoopDelayLabels=CreateLabels(panel, leftLabelsData)
        self.txtLoopDelayValues=CreateTextCtrls(panel, rightLabelsData)
        for txt in self.txtLoopDelayValues: txt.Enable(False)
        loopDelaySizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            loopDelaySizer.Add(LoopDelayLabels[i], 0, 0)
            loopDelaySizer.Add(self.txtLoopDelayValues[i], 0, 0)
        self.btnClearLoopDelays=CreateButton(panel, 'Clear Loop Delays',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnReadLoopDelays=CreateButton(panel, 'Read Loop Delays',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnClearLoopDelays, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadLoopDelays, 0, wx.ALL, 2)
        self.BoxSizer.Add(loopDelaySizer, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnClearLoopDelays, self.btnReadLoopDelays]
        for lbl in LoopDelayLabels: self.controls.append(lbl)
        for txt in self.txtLoopDelayValues: self.controls.append(txt)
    def ResetControls(self):
        for txt in self.txtLoopDelayValues: txt.SetValue('')

class CROCResetAndTestPulse():
    def __init__(self, panel, caption=' Reset And Test Pulse', nrows=0):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        if nrows==1:
            leftChkBoxData, rightChkBoxData = CROCEResetAndTestPulseChkBoxData()
        else:
            leftChkBoxData, rightChkBoxData = CROCResetAndTestPulseChkBoxData()
        rows=len(leftChkBoxData)
        self.ChXReset=CreateCheckBoxs(panel, leftChkBoxData, offset=(0,0))
        self.ChXTPulse=CreateCheckBoxs(panel, rightChkBoxData, offset=(0,0))
        CheckBoxsSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            CheckBoxsSizer.Add(self.ChXReset[i], 0, 0, 0)
            CheckBoxsSizer.Add(self.ChXTPulse[i], 0, 0, 0)
        self.btnWriteRSTTP=CreateButton(panel, 'Write',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnReadRSTTP=CreateButton(panel, 'Read',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnSendRSTOnly=CreateButton(panel, 'Send Reset',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnSendTPOnly=CreateButton(panel, 'Send Test Pulse',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(CheckBoxsSizer, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWriteRSTTP, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadRSTTP, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendRSTOnly, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendTPOnly, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnWriteRSTTP,
            self.btnReadRSTTP, self.btnSendRSTOnly, self.btnSendTPOnly]
        for chk in self.ChXReset: self.controls.append(chk)
        for chk in self.ChXTPulse: self.controls.append(chk)
    def ResetControls(self):
        for chk in self.ChXReset: chk.SetValue(False)
        for chk in self.ChXTPulse: chk.SetValue(False)

class CROCFEBGateDelays():
    def __init__(self, panel, caption=' FEB Gate Delays'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        leftLabelsData, rightTextData = CROCFEBGateDelaysLabelsData()
        rows=len(leftLabelsData)
        FEBGateDelaysLabels=CreateLabels(panel, leftLabelsData)
        FEBGateDelaysValues=CreateTextCtrls(panel, rightTextData)
        self.txtNumberOfMeas=FEBGateDelaysValues[0]
        self.txtLoadTimerValue=FEBGateDelaysValues[1]
        self.txtGateStartValue=FEBGateDelaysValues[2]
        FEBGateDelaysSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            FEBGateDelaysSizer.Add(FEBGateDelaysLabels[i], 0, wx.ALL, 0)
            FEBGateDelaysSizer.Add(FEBGateDelaysValues[i], 0, wx.ALL, 0)
        self.btnReportAlignmentsAllCHs=CreateButton(panel, 'Report Align All CHs',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnReportAlignmentsAllCROCs=CreateButton(panel, 'Report Align All CROCs',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnReportAlignmentsAllCRATEs=CreateButton(panel, 'Report Align All CRATEs',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnReportAlignmentsAllCHs, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReportAlignmentsAllCROCs, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReportAlignmentsAllCRATEs, 0, wx.ALL, 2)
        self.BoxSizer.Add(FEBGateDelaysSizer, 1, wx.ALL|wx.EXPAND, 2)
        self.controls=[StaticBox, self.btnReportAlignmentsAllCHs,
            self.btnReportAlignmentsAllCROCs, self.btnReportAlignmentsAllCRATEs]
        for lbl in FEBGateDelaysLabels: self.controls.append(lbl)
        for txt in FEBGateDelaysValues: self.controls.append(txt)
    def ResetControls(self):
        self.txtNumberOfMeas.SetValue('')
        self.txtLoadTimerValue.SetValue('')
        self.txtGateStartValue.SetValue('')

class CROCERDFESetup():
    def __init__(self, panel, caption=' RDFE Setup'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.choiceRDFEDelayEnable=wx.Choice(panel, size=(1,20),
            choices=['0 RDFE Del Disabled', '1 RDFE Del Enabled'])
        self.choiceRDFEDelayEnable.SetFont(myFont(fontSizeChoice))
        lblRDFEPulseDelayValue=CreateLabel(panel, 'Delay Val',
            pos=(0,0), size=(6, 16), name='', color=colorLabel)
        self.txtRDFEPulseDelayValue=CreateTextCtrl(panel, label='RDFE Delay',
            pos=(0,0), size=(6, 20), name='', bckcolor=colorText)
        self.btnWriteRDFEPulseDelay=CreateButton(panel, 'Write',
            pos=(0,0), size=(6,20), name='', bckcolor=colorButton)
        self.btnReadRDFEPulseDelay=CreateButton(panel, 'Read',
            pos=(0,0), size=(6,20), name='', bckcolor=colorButton)
        self.btnSendRDFESoftware=CreateButton(panel, 'Send Software RDFE',
            pos=(0,0), size=(1,20), name='', bckcolor=colorButton)
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(lblRDFEPulseDelayValue, 1, wx.ALL|wx.EXPAND, 1)
        szH1.Add(self.txtRDFEPulseDelayValue, 1, wx.ALL|wx.EXPAND, 1)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(self.btnWriteRDFEPulseDelay, 1, wx.ALL|wx.EXPAND, 1)
        szH2.Add(self.btnReadRDFEPulseDelay, 1, wx.ALL|wx.EXPAND, 1)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceRDFEDelayEnable, 1, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(szH1, 1, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(szH2, 1, wx.ALL|wx.EXPAND, 2)
        self.BoxSizer.Add(self.btnSendRDFESoftware, 1, wx.ALL|wx.EXPAND, 2)
        self.controls=[StaticBox, self.choiceRDFEDelayEnable,
            lblRDFEPulseDelayValue, self.txtRDFEPulseDelayValue,
            self.btnWriteRDFEPulseDelay, self.btnReadRDFEPulseDelay,
            self.btnSendRDFESoftware]
    def ResetControls(self):
        self.choiceRDFEDelayEnable.SetSelection(0)
        self.txtRDFEPulseDelayValue.SetValue('')


class CROCEStatusAndVersionRegister():
    def __init__(self, panel, caption=''):
        leftLabelsData, rightLabelData = CROCEStatusAndVersionRegLabelsData()  
        StaticBox=wx.StaticBox(panel, -1, caption+'')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnWriteStatusAndVersion=CreateButton(panel, 'Write FLASH Control',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.btnReadStatusAndVersion=CreateButton(panel, 'Read FLASH Control',
            pos=(0,0), size=(145,20), name='', bckcolor=colorButton)
        self.txtValueStatusAndVersion = CreateTextCtrl(panel, label='register value',
            pos=(0,0), size=(145, 20), name='', bckcolor=colorText)
        self.txtValueStatusAndVersion.Enable(True)
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnWriteStatusAndVersion, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadStatusAndVersion, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtValueStatusAndVersion, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnWriteStatusAndVersion,
            self.btnReadStatusAndVersion, self.txtValueStatusAndVersion]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtValueStatusAndVersion.SetValue('')
        for txt in self.RegValues: txt.Label=''


class CHECommandsRegister():
    def __init__(self, panel, caption=' Commands'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.chkClearStatus=CreateCheckBox(panel, 'Clear Status', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkSendMessage=CreateCheckBox(panel, 'Send Message', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkClearSndMemWPointer=CreateCheckBox(panel, 'Clear SndMemWPointer', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkClearRcvMemWPointer=CreateCheckBox(panel, 'Clear RcvMemWPointer', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkClearRDFECounter=CreateCheckBox(panel, 'Clear RDFECounter', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkSendFlashMessage=CreateCheckBox(panel, 'Send Flash Message', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.chkTXSendSyncWords=CreateCheckBox(panel, 'TX SendSyncWords', pos=(0,0), size=(155,16), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write Commands', pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.chkClearStatus, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkSendMessage, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkClearSndMemWPointer, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkClearRcvMemWPointer, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkClearRDFECounter, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkSendFlashMessage, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.chkTXSendSyncWords, 0, wx.ALL, 0)
        self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnWrite, 
            self.chkClearStatus, self.chkSendMessage, self.chkClearSndMemWPointer,
            self.chkClearRcvMemWPointer, self.chkClearRDFECounter,
            self.chkSendFlashMessage, self.chkTXSendSyncWords]
    def ResetControls(self):
        self.chkClearStatus.SetValue(False)
        self.chkSendMessage.SetValue(False)
        self.chkClearSndMemWPointer.SetValue(False)
        self.chkClearRcvMemWPointer.SetValue(False)
        self.chkClearRDFECounter.SetValue(False)
        self.chkSendFlashMessage.SetValue(False)
        self.chkTXSendSyncWords.SetValue(False)

class CHEConfigurationRegister():
    def __init__(self, panel, caption=''):
        leftLabelsData, rightLabelData = CROCECHEConfigurationRegLabelsData()  
        StaticBox=wx.StaticBox(panel, -1, caption+' Configuration (hex)')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnWriteConfig=CreateButton(panel, 'Write Config',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.btnReadConfig=CreateButton(panel, 'Read Config',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.txtValueConfig = CreateTextCtrl(panel, label='status value',
            pos=(0,0), size=(155, 20), name='', bckcolor=colorText)
        self.txtValueConfig.Enable(True) 
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnWriteConfig, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadConfig, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtValueConfig, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnWriteConfig, self.btnReadConfig, self.txtValueConfig]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtValueConfig.SetValue('')
        for txt in self.RegValues: txt.Label=''

class CHEStatusFrameRegister():
    def __init__(self, panel, caption=''):
        leftLabelsData, rightLabelData = CROCECHEStatusFrameRegLabelsData()  
        StaticBox=wx.StaticBox(panel, -1, caption+' Frame Status')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnReadStatusFrame=CreateButton(panel, 'Read Status',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.txtValueStatusFrame = CreateTextCtrl(panel, label='status value',
            pos=(0,0), size=(155, 20), name='', bckcolor=colorText)
        self.txtValueStatusFrame.Enable(False) 
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnReadStatusFrame, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtValueStatusFrame, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnReadStatusFrame, self.txtValueStatusFrame]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtValueStatusFrame.SetValue('')
        for txt in self.RegValues: txt.Label=''

class CHEStatusTXRXRegister():
    def __init__(self, panel, caption=''):
        leftLabelsData, rightLabelData = CROCECHEStatusTXRXRegLabelsData()  
        StaticBox=wx.StaticBox(panel, -1, caption+' TXRX Status')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnReadStatusTXRX=CreateButton(panel, 'Read Status',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.txtValueStatusTXRX = CreateTextCtrl(panel, label='status value',
            pos=(0,0), size=(155, 20), name='', bckcolor=colorText)
        self.txtValueStatusTXRX.Enable(False) 
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnReadStatusTXRX, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtValueStatusTXRX, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 1, wx.ALL|wx.EXPAND, 2)
        self.controls=[StaticBox, self.btnReadStatusTXRX, self.txtValueStatusTXRX]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtValueStatusTXRX.SetValue('')
        for txt in self.RegValues: txt.Label=''

class CHEHeaderDataRegister():
    def __init__(self, panel, caption=''):
        leftLabelsData, rightLabelData = CROCECHEHeaderRegLabelsData()  
        StaticBox=wx.StaticBox(panel, -1, caption+' Header Data')
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        rows=len(leftLabelsData)
        self.btnWriteHeaderData=CreateButton(panel, 'Write Header',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.btnReadHeaderData=CreateButton(panel, 'Read Header',
            pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.txtValueHeaderData = CreateTextCtrl(panel, label='header value',
            pos=(0,0), size=(155, 20), name='', bckcolor=colorText)
        self.txtValueHeaderData.Enable(True) 
        RegLabels=CreateLabels(panel, leftLabelsData)
        self.RegValues=CreateLabels(panel, rightLabelData)
        statSizer1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        statSizer4=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(4):
            statSizer1.Add(RegLabels[i], 0, 0)
            statSizer1.Add(self.RegValues[i], 0, 0)
            statSizer2.Add(RegLabels[i+4], 0, 0)
            statSizer2.Add(self.RegValues[i+4], 0, 0)
            statSizer3.Add(RegLabels[i+8], 0, 0)
            statSizer3.Add(self.RegValues[i+8], 0, 0)
            statSizer4.Add(RegLabels[i+12], 0, 0)
            statSizer4.Add(self.RegValues[i+12], 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnWriteHeaderData, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadHeaderData, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txtValueHeaderData, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.BoxSizer.Add(statSizer4, 1, wx.ALL|wx.EXPAND, 2)
        self.controls=[StaticBox, self.btnWriteHeaderData,
            self.btnReadHeaderData, self.txtValueHeaderData]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)
    def ResetControls(self):
        self.txtValueHeaderData.SetValue('')
        for txt in self.RegValues: txt.Label=''

class CHEMemories():
    def __init__(self, panel, captions=['Send Memory', 'Write', 'Addr(hex)', 'addr', 'Data', 'data'],
            txtenables=[False, True]): 
        StaticBox=wx.StaticBox(panel, -1, captions[0])
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.btn1=CreateButton(panel, captions[1], pos=(0,0), size=(60,20), name='', bckcolor=colorButton)
        self.lbl2=CreateLabel(panel, captions[2], pos=(0,0), size=(60,16), name='', color=colorLabel)
        self.txt3=CreateTextCtrl(panel, captions[3], pos=(0,0), size=(50, 20), name='', bckcolor=colorText)
        self.lbl4=CreateLabel(panel, captions[4], pos=(0,0), size=(60,16), name='', color=colorLabel)
        self.txt5=CreateTextCtrl(panel, captions[5], pos=(0,0), size=(50, 20), name='', bckcolor=colorText)
        self.txt3.Enable(txtenables[0])
        self.txt5.Enable(txtenables[1])
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.HORIZONTAL)
        self.BoxSizer.Add(self.btn1, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.lbl2, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txt3, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.lbl4, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.txt5, 1, wx.ALL, 2)
        self.controls=[StaticBox, self.btn1, self.lbl2, self.txt3, self.lbl4, self.txt5]
    def ResetControls(self):
        #self.txt3.SetValue('')
        self.txt5.SetValue('')

class CHEResets():
    def __init__(self, panel, captions=['Reset options','Reset this CHE','Reset this CROCE','Reset this CRATE','Reset all CRATES']): 
        StaticBox=wx.StaticBox(panel, -1, captions[0])
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.btnResetThisCHE=CreateButton(panel, captions[1], pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.btnResetThisCROCE=CreateButton(panel, captions[2], pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.btnResetThisCRATE=CreateButton(panel, captions[3], pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.btnResetAllCRATEs=CreateButton(panel, captions[4], pos=(0,0), size=(155,20), name='', bckcolor=colorButton)
        self.fdsz=wx.FlexGridSizer(rows=1, cols=4, hgap=16, vgap=2)
        self.fdsz.Add(self.btnResetThisCHE, 0, 0, 0)
        self.fdsz.Add(self.btnResetThisCROCE, 0, 0, 0)
        self.fdsz.Add(self.btnResetThisCRATE, 0, 0, 0)
        self.fdsz.Add(self.btnResetAllCRATEs, 0, 0, 0)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.HORIZONTAL)
        self.BoxSizer.Add(self.fdsz, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnResetThisCHE, self.btnResetThisCROCE,
            self.btnResetThisCRATE, self.btnResetAllCRATEs]

class FPGARegisters():
    def __init__(self, panel):
        leftLabelsData = FPGARegLabelsData()
        rightTextData = FPGARegTextData()
        lblRegs=CreateLabels(panel, leftLabelsData)
        self.txtRegs=CreateTextCtrls(panel, rightTextData)
        #self.txtRegs[0].SetValidator(myValidator(self.txtRegs[0], 0,15))
        rows=len(leftLabelsData)
        szRegs1=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=0)
        szRegs2=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=0)
        szRegs3=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=0)
        for i in range(20):
            szRegs1.Add(lblRegs[i], 0, 0, 0)
            szRegs1.Add(self.txtRegs[i], 0, 0, 0)
            if i+20<rows:
                szRegs2.Add(lblRegs[i+20], 0, 0, 0)
                szRegs2.Add(self.txtRegs[i+20], 0, 0, 0)
            if i+40<rows:
                szRegs3.Add(lblRegs[i+40], 0, 0, 0)
                szRegs3.Add(self.txtRegs[i+40], 0, 0, 0)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnDumpRead=CreateButton(panel, 'Dump Read',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCH=CreateButton(panel, 'Write ALL This CH',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCROC=CreateButton(panel, 'Write ALL This CROC',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCRATE=CreateButton(panel, 'Write ALL This CRATE',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALL=CreateButton(panel, 'Write ALL FEs',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnDumpRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCH, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCROC, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCRATE, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALL, 0, wx.ALL, 2)
        self.FPGABoxSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.FPGABoxSizer.Add(szBtns, 0, wx.ALL, 2)
        self.FPGABoxSizer.Add(szRegs1, 0, wx.ALL, 2)
        self.FPGABoxSizer.Add(szRegs2, 0, wx.ALL, 2)
        self.FPGABoxSizer.Add(szRegs3, 0, wx.ALL, 2)
        self.controlsAdvanced=[]
        for i in range(14, len(lblRegs)):
            self.controlsAdvanced.append(lblRegs[i])
            self.controlsAdvanced.append(self.txtRegs[i])
    def ResetControls(self):
        for txt in self.txtRegs: txt.SetValue('')

class TRIPRegisters():
    def __init__(self, panel):
        leftLabelsData = TRIPRegLabelsData()
        rightTextData = TRIPRegTextData()
        lblRegs=CreateLabels(panel, leftLabelsData)
        self.txtRegs=CreateTextCtrls(panel, rightTextData)
        rows=len(leftLabelsData)
        szRegs=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=0)
        for i in range(rows):
            szRegs.Add(lblRegs[i], 0, 0, 0)
            szRegs.Add(self.txtRegs[i], 0, 0, 0)
        self.chkTrip=wx.RadioBox(panel, -1, 'Trip choices', (5,5), wx.DefaultSize,
            ['Trip 0','Trip 1','Trip 2','Trip 3','Trip 4','Trip 5'], 2, wx.RA_SPECIFY_COLS)
        self.chkTrip.SetFont(myFont(fontSizeRadioBox))
        self.btnRead=CreateButton(panel, 'Read', 
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnRead6=CreateButton(panel, 'Read ALL 6',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWrite6=CreateButton(panel, 'Write ALL 6',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCH=CreateButton(panel, 'Write ALL This CH',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCROC=CreateButton(panel, 'Write ALL This CROC',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCRATE=CreateButton(panel, 'Write ALL This CRATE',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnWriteALL=CreateButton(panel, 'Write ALL TRIPs',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnPRGRST=CreateButton(panel, 'RESET All 6',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnPRGRSTALLThisCH=CreateButton(panel, 'RESET All This CH',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnPRGRSTALLThisCROC=CreateButton(panel, 'RESET All This CROC',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnPRGRSTALLThisCRATE=CreateButton(panel, 'RESET All This CRATE',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        self.btnPRGRSTALL=CreateButton(panel, 'RESET ALL TRIPs',
            pos=(0,0), size=(135,20), name='', bckcolor=colorButton)
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.chkTrip, 0, wx.ALL|wx.EXPAND, 2)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnRead6, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite6, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCH, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCROC, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCRATE, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALL, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRST, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRSTALLThisCH, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRSTALLThisCROC, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRSTALLThisCRATE, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRSTALL, 0, wx.ALL, 2)
        self.TripBoxSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.TripBoxSizer.Add(szBtns, 0, wx.ALL, 2)
        self.TripBoxSizer.Add(szRegs, 0, wx.ALL, 2)
    def ResetControls(self):
        for txt in self.txtRegs: txt.SetValue('')

##class myValidator(wx.PyValidator):
##    def __init__(self, txtCtrl, minValue, maxValue):
##        wx.PyValidator.__init__(self)
##        self.txtCtrl=txtCtrl
##        self.min=minValue
##        self.max=maxValue 
##        #self.Bind(wx.EVT_LEAVE_WINDOW, self.Validate)
##        #self.Bind(wx.EVT_SET_FOCUS, self.Validate)
##        #self.Bind(wx.EVT_TEXT, self.Validate)
##        #self.Bind(wx.EVT_TEXT_ENTER, self.Validate)
##    def Clone(self): return myValidator(self.txtCtrl, self.min, self.max)
##    def Validate(self, evt):
##        if self.txtCtrl.GetValue()=='':self.txtCtrl.SetValue('0')
##        try:
##            data = int(self.txtCtrl.GetValue()) 
##            if data<self.min or data>self.max:
##                wx.MessageBox('data must be %d to %d' % (self.min, self.max))  
##                self.txtCtrl.SetValue('0')
##                evt.Skip()
##        except:
##            evt.Skip()
##            self.txtCtrl.SetValue('')
            
        



        
