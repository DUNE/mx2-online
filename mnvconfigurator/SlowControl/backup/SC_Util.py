"""
MINERvA DAQ Slow Control GUI
Contains misc utilities
Started November 2009
"""

import wx
import sys
import random

class VMDdevTypes():
    CRIM='CRIM'
    CROC='CROC'
    CH='CH'
    FE='FE'

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

class CRIMCHRegs():
    RegRMemory      = 0x0000
    RegWInput       = 0x2000
    RegWResetFIFO   = 0x2008
    RegWSendMessage = 0x2010
    RegRStatus      = 0x2020
    RegWClearStatus = 0x2030
    RegRLoopDelay   = 0x2040
    RegRDPMPointer  = 0x2050
    RegRDecodTmgCmd = 0x2060
    RegRWControl    = 0x2070

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

class FastCommands():
    ResetFPGA   = 0x8D
    OpenGate    = 0xB1
    ResetTimer  = 0xC9
    LoadTimer   = 0xC5
    TriggerFound= 0x89
    TriggerRearm= 0x85
    QueryFPGA   = 0x91
FastCmds={
    'ResetFPGA':0x8D,
    'OpenGate':0xB1,
    'ResetTimer':0xC9,
    'LoadTimer':0xC5,
    'TriggerFound':0x89,
    'TriggerRearm':0x85,
    'QueryFPGA':0x91}

def CROCResetAndTestPulseChkBoxData():
    pos=(0,0)
    size=(58, 16)
    color='coral'
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
    color='coral'
    leftLabels=(
        (' N of Meas', pos, size, '', color),
        (' Load Timer Value', pos, size, '', color),
        (' Gate Start Value', pos, size, '', color))
    return leftLabels

def CROCFEBGateDelaysTextData():
    pos=(0,0)
    size=(50, 20)
    color='white'
    rightText=(
        ('5', pos, size, 'NofMeasurements', color),
        ('15', pos, size, 'LoadTimerValue', color),
        ('63500', pos, size, 'GateStartValue', color))
    return rightText

def CROCLoopDelayRegLabelsData():
    pos=(0,0)
    size=(90, 16)
    color='coral'
    leftLabels=(
        (' Channel 1', pos, size, '', color),
        (' Channel 2', pos, size, '', color),
        (' Channel 3', pos, size, '', color),
        (' Channel 4', pos, size, '', color))
    rightLabels=(('X', pos, (30, 16), '', 'white'),)
    rightLabels=(len(leftLabels))*rightLabels
    return (leftLabels, rightLabels) 

def CROCCHStatusRegLabelsData():
    pos=(0,0)
    size=(100, 16)
    color='coral'
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
    color='coral'
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
    color='coral'
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
        (' INJB0', pos, size, '', color),
        (' INJB1', pos, size, '', color),
        (' INJB2', pos, size, '', color),
        (' INJB3', pos, size, '', color),
        (' INJEX33', pos, size, '', color))
    return leftRegLabels

def TRIPRegTextData():
    pos=(0,0)
    size=(30, 20)
    color='white'
    rightRegText=(
        ('', pos, size, 'IBP', color),
        ('', pos, size, 'IBBNFALL', color),
        ('', pos, size, 'IFF', color),
        ('', pos, size, 'IBPIFF1REF', color),
        ('', pos, size, 'IBOPAMP', color),
        ('', pos, size, 'IB_T', color),
        ('', pos, size, 'IFFP2', color),
        ('', pos, size, 'IBCOMP', color),
        ('', pos, size, 'VREF', color),
        ('', pos, size, 'VTH', color),
        ('', pos, size, 'GAIN', color),
        ('', pos, size, 'PIPEDEL', color),
        ('', pos, size, 'IRSEL', color),
        ('', pos, size, 'IWSEL', color),
        ('', pos, size, 'INJEX0', color),
        ('', pos, size, 'INJB0', color),
        ('', pos, size, 'INJB1', color),
        ('', pos, size, 'INJB2', color),
        ('', pos, size, 'INJB3', color),
        ('', pos, size, 'INJEX33', color))
    return rightRegText

def FPGARegLabelsData():
    pos=(0,0)
    size=(120, 16)
    color='coral'
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
        (' R  Version', pos, size, '', color),
        (' R  FEB ID', pos, size, '', color),
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
        (' WR InjDAC Mode', pos, size, '', color),
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
        (' R  Temperature', pos, size, '', color),
        (' WR TripX Threshold', pos, size, '', color),
        (' R  TripX Comparators', pos, size, '', color),
        (' R  ExtTriggFound', pos, size, '', color),
        (' WR ExtTriggRearm', pos, size, '', color),
        (' WR DiscrimTrip0 (0x)', pos, size, '', color),
        (' WR DiscrimTrip1 (0x)', pos, size, '', color),
        (' WR DiscrimTrip2 (0x)', pos, size, '', color),
        (' WR DiscrimTrip3 (0x)', pos, size, '', color),
        (' R  GateTimeStamp', pos, size, '', color),        
        (' R  SCmdErr(1)', pos, size, '', color),
        (' R  FCmdErr(1)', pos, size, '', color),
        (' R  RXSyncErr(1)', pos, size, '', color),
        (' R  TXSyncErr(1)', pos, size, '', color))
    return leftRegLabels

def FPGARegTextData():
    pos=(0,0)
    size=(30, 20)
    color='white'
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
        ('', pos, size, ' WR InjDAC Mode', color),
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
        ('', pos, size, ' R  Temperature', color),
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

def CreateLabels(panel, data, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE, offset=(0,0)):
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

def CreateLabel(panel, label, pos, size, name,
    color, style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE):
    '''Returns a wx.StaticText object'''
    theLabel = wx.StaticText(panel, label=label, pos=pos, size=size, style=style, name=name)
    theLabel.SetBackgroundColour(color)
    return theLabel

def CreateButton(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.Button object'''
    theButton = wx.Button(panel, label=label, pos=pos, size=size, 
        style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE)
    theButton.SetBackgroundColour(bckcolor)
    return theButton

def CreateTextCtrl(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.TextCtrl object'''
    theTextCtrl = wx.TextCtrl(panel, value=label, pos=pos, size=size, name=name)
    theTextCtrl.SetBackgroundColour(bckcolor)
    return theTextCtrl

def CreateCheckBox(panel, label, pos, size, name, bckcolor):
    '''Returns a wx.CheckBox object'''
    theCheckBox = wx.CheckBox(panel, label=label, pos=pos, size=size, name=name)
    theCheckBox.SetBackgroundColour(bckcolor)
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
        
class FlashButtons():
    def __init__(self, panel, lblFirst, lblSecond):
        FlashBox=wx.StaticBox(panel, -1, 'Flash Commands')
        self.btnFlashFirst=CreateButton(panel, lblFirst,
            pos=(0,0), size=(270,20), name=lblFirst, bckcolor='coral')
        self.btnFlashSecond=CreateButton(panel, lblSecond,
            pos=(0,0), size=(270,20), name=lblSecond, bckcolor='coral')
        self.FlashBoxSizer=wx.StaticBoxSizer(FlashBox, wx.VERTICAL)
        self.FlashBoxSizer.Add(self.btnFlashFirst, 0, wx.ALL|wx.EXPAND, 2)
        self.FlashBoxSizer.Add(self.btnFlashSecond, 0, wx.ALL|wx.EXPAND, 2)
        self.controls=[FlashBox, self.btnFlashFirst, self.btnFlashSecond]
        
class StatusRegister():
    def __init__(self, panel, caption='CROC CH'):
        if caption=='CROC CH':
            leftLabelsData, rightLabelData = CROCCHStatusRegLabelsData()
        if caption=='CRIM CH':
            leftLabelsData, rightLabelData = CRIMCHStatusRegLabelsData()
        StatusBox=wx.StaticBox(panel, -1, caption+' Status Register')
        rows=len(leftLabelsData)
        self.btnClearStatus=CreateButton(panel, 'Clear Status',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnReadStatus=CreateButton(panel, 'Read Status',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.lblStatus=CreateLabel(panel, 'status value',
            pos=(0,0), size=(125,16), name='', color='white')
        RegLabels=CreateLabels(panel, leftLabelsData,
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.RegValues=CreateLabels(panel, rightLabelData,
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
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
        self.StatusBoxSizer=wx.StaticBoxSizer(StatusBox, wx.VERTICAL)
        self.StatusBoxSizer.Add(self.btnClearStatus, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(self.btnReadStatus, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(self.lblStatus, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(statSizer1, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(statSizer2, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(statSizer3, 0, wx.ALL, 2)
        self.StatusBoxSizer.Add(statSizer4, 0, wx.ALL, 2)

        self.controls=[StatusBox, self.btnClearStatus, self.btnReadStatus, self.lblStatus]
        for lbl in RegLabels: self.controls.append(lbl)
        for lbl in self.RegValues: self.controls.append(lbl)

class DPMPointer():
    def __init__(self, panel):
        DPMRegisterBox=wx.StaticBox(panel, -1, 'DPM Pointer')
        self.btnDPMPointerReset=CreateButton(panel, 'Reset DPM Pointer',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnDPMPointerRead=CreateButton(panel, 'Read DPM Pointer',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.lblDPMPointerValue=CreateLabel(panel, 'pointer value',
            pos=(0,0), size=(125,16), name='', color='white',
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.DPMBoxSizer=wx.StaticBoxSizer(DPMRegisterBox, wx.VERTICAL)
        self.DPMBoxSizer.Add(self.btnDPMPointerReset, 0, wx.ALL, 2)
        self.DPMBoxSizer.Add(self.btnDPMPointerRead, 0, wx.ALL, 2)
        self.DPMBoxSizer.Add(self.lblDPMPointerValue, 0, wx.ALL, 2)

        self.controls=[DPMRegisterBox, self.btnDPMPointerReset,
            self.btnDPMPointerRead, self.lblDPMPointerValue]

class MessageRegisters():
    def __init__(self, panel):
        MessageRegisterBox=wx.StaticBox(panel, -1, 'Message Registers')
        self.btnAppendMessage=CreateButton(panel, 'Append Message',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.txtAppendMessage=CreateTextCtrl(panel, 'message string',
            pos=(0,0), size=(125,16), name='', bckcolor='white')
        self.btnWriteFIFO=CreateButton(panel, 'Write FIFO',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnSendFrame=CreateButton(panel, 'Send Frame',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnReadDPMBytesN=CreateButton(panel, 'Read DPM Bytes#',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.txtReadDPMBytesN=CreateTextCtrl(panel, '#bytes',
            pos=(0,0), size=(125,20), name='', bckcolor='white')
        self.txtReadDPMContent=wx.TextCtrl(panel, -1, size=(125,100),
            style = wx.TE_READONLY | wx.TE_MULTILINE | wx.VSCROLL)
        
        self.MessageBoxSizer=wx.StaticBoxSizer(MessageRegisterBox, wx.VERTICAL)
        self.MessageBoxSizer.Add(self.btnAppendMessage, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.txtAppendMessage, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.btnWriteFIFO, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.btnSendFrame, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.btnReadDPMBytesN, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.txtReadDPMBytesN, 0, wx.ALL|wx.EXPAND, 2)
        self.MessageBoxSizer.Add(self.txtReadDPMContent, 1, wx.ALL|wx.EXPAND, 2)
    
        self.controls=[MessageRegisterBox, self.btnAppendMessage, self.txtAppendMessage,
            self.btnWriteFIFO, self.btnSendFrame, self.btnReadDPMBytesN,
            self.txtReadDPMBytesN, self.txtReadDPMContent]

class TRIPRegisters():
    def __init__(self, panel):
        leftLabelsData = TRIPRegLabelsData()
        rightTextData = TRIPRegTextData()
        lblRegs=CreateLabels(panel, leftLabelsData, style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.txtRegs=CreateTextCtrls(panel, rightTextData, offset=(0,0))     
        rows=len(leftLabelsData)
        szRegs=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=0)
        for i in range(rows):
            szRegs.Add(lblRegs[i], 0, 0, 0)
            szRegs.Add(self.txtRegs[i], 0, 0, 0)

        self.chkTrip=wx.RadioBox(panel, -1, 'Trip choices', (5,5), wx.DefaultSize,
            ['Trip 0','Trip 1','Trip 2','Trip 3','Trip 4','Trip 5'], 2, wx.RA_SPECIFY_COLS)        
        self.btnRead=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnWriteALL=CreateButton(panel, 'Write ALL FEs',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.chkTrip, 0, wx.ALL|wx.EXPAND, 2)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
        szBtns.Add(self.btnWriteALL, 0, wx.ALL, 2)

        self.TripBoxSizer=wx.BoxSizer(wx.HORIZONTAL)
        self.TripBoxSizer.Add(szBtns, 0, wx.ALL, 2)
        self.TripBoxSizer.Add(szRegs, 0, wx.ALL, 2)
        
        self.controls=[self.chkTrip, self.btnRead, self.btnWrite, self.btnWriteALL]
        for lbl in lblRegs: self.controls.append(lbl)
        for txt in self.txtRegs: self.controls.append(txt)

class FPGARegisters():
    def __init__(self, panel):
        leftLabelsData = FPGARegLabelsData()
        rightTextData = FPGARegTextData()
        lblRegs=CreateLabels(panel, leftLabelsData, style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.txtRegs=CreateTextCtrls(panel, rightTextData, offset=(0,0))     
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
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnWrite=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnWriteALL=CreateButton(panel, 'Write ALL FEs',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        szBtns=wx.BoxSizer(wx.VERTICAL)
        szBtns.Add(self.btnRead, 0, wx.ALL, 2)
        szBtns.Add(self.btnWrite, 0, wx.ALL, 2)
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

class CROCFastCmd():
    def __init__(self, panel, caption=' Fast Commands'):
        CROCFastCommandBox=wx.StaticBox(panel, -1, caption)
        FCmds=FastCmds.keys(); FCmds.sort()
        self.choiceFastCmd=wx.Choice(panel, size=(125,20), choices=FCmds)
        self.btnSendFastCmd=CreateButton(panel, 'Send Fast Cmd',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.BoxSizer=wx.StaticBoxSizer(CROCFastCommandBox, wx.VERTICAL)
        self.BoxSizer.Add(self.choiceFastCmd, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendFastCmd, 0, wx.ALL, 2)
        self.controls=[CROCFastCommandBox, self.choiceFastCmd, self.btnSendFastCmd]

class LoopDelays():
    def __init__(self, panel, caption=' LoopDelays'):
        LoopDelayBox=wx.StaticBox(panel, -1, caption)
        leftLabelsData, rightsLabelData = CROCLoopDelayRegLabelsData()
        rows=len(leftLabelsData)
        LoopDelayLabels=CreateLabels(panel, leftLabelsData,
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        self.LoopDelayValues=CreateLabels(panel, rightsLabelData,
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        loopDelaySizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            loopDelaySizer.Add(LoopDelayLabels[i], 0, 0)
            loopDelaySizer.Add(self.LoopDelayValues[i], 0, 0)
        self.btnClearLoopDelays=CreateButton(panel, 'Clear Loop Delays',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnReadLoopDelays=CreateButton(panel, 'Read Loop Delays',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.BoxSizer=wx.StaticBoxSizer(LoopDelayBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnClearLoopDelays, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadLoopDelays, 0, wx.ALL, 2)
        self.BoxSizer.Add(loopDelaySizer, 0, wx.ALL, 2)

        self.controls=[LoopDelayBox, self.btnClearLoopDelays, self.btnReadLoopDelays]
        for lbl in LoopDelayLabels: self.controls.append(lbl)
        for lbl in self.LoopDelayValues: self.controls.append(lbl)

class CROCResetAndTestPulse():
    def __init__(self, panel, caption=' Reset And Test Pulse'):
        CROCResetAndTestPulseBox=wx.StaticBox(panel, -1, caption)
        leftChkBoxData, rightChkBoxData = CROCResetAndTestPulseChkBoxData()
        rows=len(leftChkBoxData)
        self.ChXReset=CreateCheckBoxs(panel, leftChkBoxData, offset=(0,0))
        self.ChXTPulse=CreateCheckBoxs(panel, rightChkBoxData, offset=(0,0))
        CheckBoxsSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            CheckBoxsSizer.Add(self.ChXReset[i], 0, 0, 0)
            CheckBoxsSizer.Add(self.ChXTPulse[i], 0, 0, 0)
        self.btnWriteRSTTP=CreateButton(panel, 'Write',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnReadRSTTP=CreateButton(panel, 'Read',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnSendRSTOnly=CreateButton(panel, 'Send Reset',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        self.btnSendTPOnly=CreateButton(panel, 'Send Test Pulse',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')

        self.BoxSizer=wx.StaticBoxSizer(CROCResetAndTestPulseBox, wx.VERTICAL)
        self.BoxSizer.Add(CheckBoxsSizer, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnWriteRSTTP, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnReadRSTTP, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendRSTOnly, 0, wx.ALL, 2)
        self.BoxSizer.Add(self.btnSendTPOnly, 0, wx.ALL, 2)

        self.controls=[CROCResetAndTestPulseBox, self.btnWriteRSTTP,
            self.btnReadRSTTP, self.btnSendRSTOnly, self.btnSendTPOnly]
        for lbl in self.ChXReset: self.controls.append(lbl)
        for txt in self.ChXTPulse: self.controls.append(txt)

class FEBGateDelays():
    def __init__(self, panel, caption=' FEB Gate Delays'):
        FEBGateDelaysBox=wx.StaticBox(panel, -1, caption)
        leftLabelsData = CROCFEBGateDelaysLabelsData()
        rightTextData = CROCFEBGateDelaysTextData()
        rows=len(leftLabelsData)
        FEBGateDelaysLabels=CreateLabels(panel, leftLabelsData,
            style=wx.ALIGN_LEFT | wx.ST_NO_AUTORESIZE)
        FEBGateDelaysValues=CreateTextCtrls(panel, rightTextData, offset=(0,0))
        self.txtNumberOfMeas=FEBGateDelaysValues[0]
        self.txtLoadTimerValue=FEBGateDelaysValues[1]
        self.txtGateStartValue=FEBGateDelaysValues[2]
        FEBGateDelaysSizer=wx.FlexGridSizer(rows=rows, cols=2, hgap=5, vgap=1)
        for i in range(rows):
            FEBGateDelaysSizer.Add(FEBGateDelaysLabels[i], 0, 0, 0)
            FEBGateDelaysSizer.Add(FEBGateDelaysValues[i], 0, 0, 0)
        self.btnReportAlignmentsAllChains=CreateButton(panel, 'Report Align All CHs',
            pos=(0,0), size=(125,20), name='', bckcolor='coral')
        
        self.BoxSizer=wx.StaticBoxSizer(FEBGateDelaysBox, wx.VERTICAL)
        self.BoxSizer.Add(self.btnReportAlignmentsAllChains, 0, wx.ALL, 2)
        self.BoxSizer.Add(FEBGateDelaysSizer, 0, wx.ALL, 2)

        self.controls=[FEBGateDelaysBox, self.btnReportAlignmentsAllChains]
        for lbl in FEBGateDelaysLabels: self.controls.append(lbl)
        for txt in FEBGateDelaysValues: self.controls.append(txt)






        
        
