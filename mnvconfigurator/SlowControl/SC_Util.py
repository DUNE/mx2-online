"""
MINERvA DAQ Slow Control GUI
Contains misc utilities
Started November 2009
"""

import wx
import sys
import random

colorButton='coral'     #wx.Color(255,0,0)      #'red'
colorLabel='coral'      #wx.Color(0,255,0)      #'green'
colorText='white'       #wx.Color(255,255,255)  #'white'
colorForeground='blue'  #wx.Color(0,0,255)      #'blue'  #wx.Color.Blue
fontSizeLabel=8
fontSizeButton=8
fontSizeTextCtrl=8
fontSizeCheckBox=6
fontSizeRadioBox=8
fontSizeStaticBox=8
fontSizeChoice=8
def myFont(size, family=wx.DEFAULT, style=wx.NORMAL, weight=wx.NORMAL):
    return wx.Font(size, family, style, weight)

class VMEdevTypes():
    CRIM='CRIM'
    CROC='CROC'
    CH='CH'
    FE='FE'
    FPGA='FPGA'
    TRIP='TRIP'
    FLASH='FLASH'
    DIG='DIG'
    
class CROCRegs():
    RegWRTimingSetup        = 0xF000
    RegWRResetAndTestMask   = 0xF010
    RegWChannelReset        = 0xF020
    RegWFastCommand         = 0xF030
    RegWTestPulse           = 0xF040

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
    
class CRIMTimingModuleRegs():
    RegWRTimingSetup = 0xC010
    RegWRGateWidth   = 0xC020
    RegWRTCALBDelay  = 0xC030
    RegWTRIGGERSend  = 0xC040
    RegWTCALBSend    = 0xC050
    RegWGATE         = 0xC060
    #RegWR___         = 0xC070
    RegWCNTRST       = 0xC080
    #RegWR___         = 0xC090
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
    size=(58, 16)
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

def CROCFEBGateDelaysLabelsData():
    pos=(0,0)
    size=(70, 16)
    color=colorLabel
    leftLabels=(
        (' N of Meas', pos, size, '', color),
        (' Load Timer', pos, size, '', color),
        (' Gate Start', pos, size, '', color))
    size=(50, 16)
    color=colorText
    rightLabels=(
        ('5', pos, size, 'NofMeasurements', color),
        ('15', pos, size, 'LoadTimerValue', color),
        ('63500', pos, size, 'GateStartValue', color))
    return leftLabels, rightLabels

def CROCLoopDelaysLabelsData():
    pos=(0,0)
    size=(80, 16)
    color=colorLabel
    leftLabels=(
        (' Channel 1', pos, size, '', color),
        (' Channel 2', pos, size, '', color),
        (' Channel 3', pos, size, '', color),
        (' Channel 4', pos, size, '', color))
    rightLabels=(('X', pos, (40, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CROCCHStatusRegLabelsData():
    pos=(0,0)
    size=(100, 16)
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
    rightLabels=(('X', pos, (20, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CRIMCHStatusRegLabelsData():
    pos=(0,0)
    size=(100, 16)
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
    rightLabels=(('X', (0, 0), (20, 16), '', 'white'),)
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
    size=(120, 16)
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
        (' WR Timer', pos, size, '', color),
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
        (' R  HV Control', pos, size, '', color),
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
        (' R  TP Count', pos, size, '', color),
        (' WR TripX Threshold', pos, size, '', color),
        (' R  TripX Comparators', pos, size, '', color),
        (' R  ExtTriggFound', pos, size, '', color),
        (' WR ExtTriggRearm', pos, size, '', color),
        (' WR DiscMaskT0 (0x)', pos, size, '', color),
        (' WR DiscMaskT1 (0x)', pos, size, '', color),
        (' WR DiscMaskT2 (0x)', pos, size, '', color),
        (' WR DiscMaskT3 (0x)', pos, size, '', color),
        (' R  GateTimeStamp', pos, size, '', color),        
        (' R  SCmdErr(1)', pos, size, '', color),
        (' R  FCmdErr(1)', pos, size, '', color),
        (' R  RXSyncErr(1)', pos, size, '', color),
        (' R  TXSyncErr(1)', pos, size, '', color))
    return leftRegLabels

def FPGARegTextData():
    pos=(0,0)
    size=(40, 20)
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
        ('', pos, size, ' R  HV Control', color),
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
        ('', pos, size, ' R  TP Count', color),
        ('', pos, size, ' WR TripX Threshold', color),
        ('', pos, size, ' R  TripX Comparators', color),
        ('', pos, size, ' R  ExtTriggFound', color),
        ('', pos, size, ' WR ExtTriggRearm', color),
        ('', pos, size, ' WR DiscrimTrip0 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip1 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip2 (0x)', color),
        ('', pos, size, ' WR DiscrimTrip3 (0x)', color),
        ('', pos, size, ' R  GateTimeStamp', color),        
        ('', pos, size, ' R  SCmdErr(1)', color),
        ('', pos, size, ' R  FCmdErr(1)', color),
        ('', pos, size, ' R  RXSyncErr(1)', color),
        ('', pos, size, ' R  TXSyncErr(1)', color))
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

def CreateLabel(panel, label, pos, size, name, color,
        style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE):
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

class VMEReadWrite():
    def __init__(self, panel, caption=' VME Read/Write (hex)'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        lblEmpty=CreateLabel(panel, '',
            pos=(0,0), size=(60, 16), name='', color=colorLabel)
        lblAddr=CreateLabel(panel, 'Address',
            pos=(0,0), size=(60, 16), name='', color=colorLabel)
        lblData=CreateLabel(panel, 'Data',
            pos=(0,0), size=(60, 16), name='', color=colorLabel)
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorButton)
        self.txtReadAddr = CreateTextCtrl(panel, label='addr',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorText)
        self.txtReadData = CreateTextCtrl(panel, label='data',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorText)
        self.txtReadData.Enable(False)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorButton)
        self.txtWriteAddr = CreateTextCtrl(panel, label='addr',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorText)
        self.txtWriteData = CreateTextCtrl(panel, label='data',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorText)        
        sz = wx.FlexGridSizer(rows=3, cols=3, hgap=5, vgap=5)
        sz.Add(lblEmpty, 0, 0, 0)
        sz.Add(lblAddr, 0, 0, 0)
        sz.Add(lblData, 0, 0, 0)
        sz.Add(self.btnRead, 0, 0, 0)
        sz.Add(self.txtReadAddr, 0, 0, 0)
        sz.Add(self.txtReadData, 0, 0, 0)
        sz.Add(self.btnWrite, 0, 0, 0)
        sz.Add(self.txtWriteAddr, 0, 0, 0)
        sz.Add(self.txtWriteData, 0, 0, 0) 
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(sz, 0, wx.ALL, 2)    
      
class FlashButtons():
    def __init__(self, panel, lblFirst, lblSecond):
        FlashBox=wx.StaticBox(panel, -1, 'Flash Commands')
        FlashBox.SetFont(myFont(fontSizeStaticBox))
        FlashBox.SetForegroundColour(colorForeground)
        self.btnReadFlashToFile=CreateButton(panel, 'Read Flash To File',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)
        self.btnCompareFileToFlash=CreateButton(panel, 'Compare File To Flash',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlash=CreateButton(panel, 'Write File To Flash',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCH=CreateButton(panel, 'Write File To Flash This CH',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashThisCROC=CreateButton(panel, 'Write File To Flash This CROC',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)
        self.btnWriteFileToFlashALL=CreateButton(panel, 'Write File To Flash ALL',
            pos=(0,0), size=(270,20), name='', bckcolor=colorButton)        
        self.FlashBoxSizer=wx.StaticBoxSizer(FlashBox, wx.VERTICAL)
        self.FlashBoxSizer.Add(self.btnReadFlashToFile, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnCompareFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlash, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCH, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashThisCROC, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnWriteFileToFlashALL, 0, wx.ALL|wx.EXPAND, 2)
        self.controls=[FlashBox, self.btnReadFlashToFile, self.btnCompareFileToFlash,
            self.btnWriteFileToFlash, self.btnWriteFileToFlashThisCH,
            self.btnWriteFileToFlashThisCROC, self.btnWriteFileToFlashALL]
      
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
            txtDataVisible=False, txtDataCaption='value', WEnable=True):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.controls=[StaticBox]
        if btnWriteVisible==True:
            self.btnWrite=CreateButton(panel, btnWriteCaption,
                pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
            self.BoxSizer.Add(self.btnWrite, 0, wx.ALL, 2)
            self.controls.append(self.btnWrite)
        if btnReadVisible==True:
            self.btnRead=CreateButton(panel, btnReadCaption,
                pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
            self.BoxSizer.Add(self.btnRead, 0, wx.ALL, 2)
            self.controls.append(self.btnRead)
        if txtDataVisible==True:
            self.txtData = CreateTextCtrl(panel, label=txtDataCaption,
                pos=(0,0), size=(125, 20), name='', bckcolor=colorText)
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
        Modes=CRIMTimingModes.keys(); Modes.sort()
        Frequencies=CRIMTimingFrequencies.keys(); Frequencies.sort()
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
        self.chkCNTRSTEnable=CreateCheckBox(panel, 'CNTRST Enable',
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
        self.choiceCLKSource=wx.Choice(panel, size=(125,20),
            choices=['0 CLK Internal', '1 CLK External'])
        self.choiceTPDelayEnable=wx.Choice(panel, size=(125,20),
            choices=['0 TPDel Disabled', '1 TPDel Enabled'])
        self.choiceCLKSource.SetFont(myFont(fontSizeChoice))
        self.choiceTPDelayEnable.SetFont(myFont(fontSizeChoice))
        lblTPDelayValue=CreateLabel(panel, 'Delay Val',
            pos=(0,0), size=(60, 16), name='', color=colorLabel)
        self.txtTPDelayValue=CreateTextCtrl(panel, label='TP Delay',
            pos=(0,0), size=(60, 20), name='', bckcolor=colorText)
        self.btnWriteTimingSetup=CreateButton(panel, 'Write',
            pos=(0,0), size=(60,20), name='', bckcolor=colorButton)
        self.btnReadTimingSetup=CreateButton(panel, 'Read',
            pos=(0,0), size=(60,20), name='', bckcolor=colorButton)
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
        FCmds=FastCmds.keys(); FCmds.sort()
        self.choiceFastCmd=wx.Choice(panel, size=(125,20), choices=FCmds)
        self.choiceFastCmd.SetFont(myFont(fontSizeChoice))
        self.btnSendFastCmd=CreateButton(panel, 'Send Fast Cmd',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceFastCmd, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendFastCmd, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.choiceFastCmd, self.btnSendFastCmd]
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
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnReadLoopDelays=CreateButton(panel, 'Read Loop Delays',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
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
    def __init__(self, panel, caption=' Reset And Test Pulse'):
        StaticBox=wx.StaticBox(panel, -1, caption)
        StaticBox.SetFont(myFont(fontSizeStaticBox))
        StaticBox.SetForegroundColour(colorForeground)
        leftChkBoxData, rightChkBoxData = CROCResetAndTestPulseChkBoxData()
        rows=len(leftChkBoxData)
        self.ChXReset=CreateCheckBoxs(panel, leftChkBoxData, offset=(0,0))
        self.ChXTPulse=CreateCheckBoxs(panel, rightChkBoxData, offset=(0,0))
        CheckBoxsSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            CheckBoxsSizer.Add(self.ChXReset[i], 0, 0, 0)
            CheckBoxsSizer.Add(self.ChXTPulse[i], 0, 0, 0)
        self.btnWriteRSTTP=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnReadRSTTP=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnSendRSTOnly=CreateButton(panel, 'Send Reset',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnSendTPOnly=CreateButton(panel, 'Send Test Pulse',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
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
            FEBGateDelaysSizer.Add(FEBGateDelaysLabels[i], 0, 0, 0)
            FEBGateDelaysSizer.Add(FEBGateDelaysValues[i], 0, 0, 0)
        self.btnReportAlignmentsAllCHs=CreateButton(panel, 'Report Align All CHs',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnReportAlignmentsAllCROCs=CreateButton(panel, 'Report Align All CROCs',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.BoxSizer=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnReportAlignmentsAllCHs, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReportAlignmentsAllCROCs, 0, wx.ALL, 2)
        self.BoxSizer.Add(FEBGateDelaysSizer, 0, wx.ALL, 2)
        self.controls=[StaticBox, self.btnReportAlignmentsAllCHs, self.btnReportAlignmentsAllCROCs]
        for lbl in FEBGateDelaysLabels: self.controls.append(lbl)
        for txt in FEBGateDelaysValues: self.controls.append(txt)
    def ResetControls(self):
        self.txtNumberOfMeas.SetValue('')
        self.txtLoadTimerValue.SetValue('')
        self.txtGateStartValue.SetValue('')

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
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCH=CreateButton(panel, 'Write ALL This CH',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCROC=CreateButton(panel, 'Write ALL This CROC',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALL=CreateButton(panel, 'Write ALL FEs',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCH, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCROC, 0, wx.ALL, 2)
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
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnRead6=CreateButton(panel, 'Read ALL 6',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWrite6=CreateButton(panel, 'Write ALL 6',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCH=CreateButton(panel, 'Write ALL This CH',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALLThisCROC=CreateButton(panel, 'Write ALL This CROC',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnWriteALL=CreateButton(panel, 'Write ALL TRIPs',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnPRGRST=CreateButton(panel, 'RESET All 6',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        self.btnPRGRSTALL=CreateButton(panel, 'RESET ALL TRIPs',
            pos=(0,0), size=(125,20), name='', bckcolor=colorButton)
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.chkTrip, 0, wx.ALL|wx.EXPAND, 2)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnRead6, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite6, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCH, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALLThisCROC, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALL, 0, wx.ALL, 2)
        szBtns.Add(self.btnPRGRST, 0, wx.ALL, 2)
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
            
        



        
