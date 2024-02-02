"""
MINERvA DAQ Slow Control GUI
Contains Frames (Layout) classes
Started October 21 2009
"""

import wx
import sys
import SC_Util
import V1720Config
from wx.py.shell import ShellFrame
from wx.py.filling import FillingFrame

class SCMainFrame(wx.Frame):
    '''SlowControl main frame '''
    def __init__(self, parent=None, id=-1, title='Slow Control Main Frame'):
        wx.Frame.__init__(self, parent, id, title, size=(1000, 600))
        self.SetIcon(wx.Icon('minerva.jpg', wx.BITMAP_TYPE_JPEG))
        
        self.Bind(wx.EVT_CLOSE, self.OnSCMainFrameClose)

        # Creating the top menu
        menuFile = wx.Menu()
        self.menuFileLoadHardware   = menuFile.Append(wx.NewId(), text="Find &Hardware", help=" Finds the VME crate hardware")
        self.menuFileLoadFromFile   = menuFile.Append(wx.NewId(), "&Load from File", " Open a file with hardware settings")
        self.menuFileSaveToFile     = menuFile.Append(wx.NewId(), "&Save to File", " Save a file with hardware settings")
        menuFile.AppendSeparator()
        self.menuFileReset          = menuFile.Append(wx.NewId(), "System &Reset", " V2718/VME System Reset")
        self.menuFileQuit           = menuFile.Append(wx.NewId(), "&Quit", " Quit the application")
        menuShow = wx.Menu()
        self.menuShowExpandAll      = menuShow.Append(wx.NewId(), "&Expand All", "Expand Hardware Tree")
        self.menuShowCollapseAll    = menuShow.Append(wx.NewId(), "&Collapse All", "Collapse Hardware Tree")
        menuActions = wx.Menu()
        self.menuActionsReadAllHV   = menuActions.Append(wx.NewId(), "&Read All HVs") 
        self.menuActionsSetAllHV    = menuActions.Append(wx.NewId(), "&Set All HVs") 
        self.menuActionsSTARTMonitorAllHV   = menuActions.Append(wx.NewId(), "START Monitor All HVs\tCTRL+H")
        self.menuActionsSTOPMonitor         = menuActions.Append(wx.NewId(), "STOP Monitor\tCTRL+K")
        menuActions.AppendSeparator()
        self.menuActionsClearDescription    = menuActions.Append(wx.NewId(), "&Clear Description")
        menuDebug = wx.Menu()
        self.menuDebugShell     = menuDebug.Append(wx.NewId(), "&Python Shell", "Open wxPython shell frame")
        self.menuDebugNamespace = menuDebug.Append(wx.NewId(), "&Namespace Viewer", "Open namespace viewer frame")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuShow, "&Show")
        menuBar.Append(menuActions, "&Actions")
        ###menuBar.Append(menuDebug, "&Debug")
        self.SetMenuBar(menuBar)
        # Binding top menu events
        self.Bind(wx.EVT_MENU, self.OnMenuDebugShell, self.menuDebugShell)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugNamespace, self.menuDebugNamespace)
        self.Bind(wx.EVT_MENU, self.OnMenuActionsClearDescription, self.menuActionsClearDescription)
        
        # Creating the bottom status bar
        self.CreateStatusBar(number=3)
        self.SetStatusText('*** Welcome to Minerva ! ***', 0)
        self.SetStatusText('*** Welcome to Minerva ! ***', 1)
        self.SetStatusText('*** Welcome to Minerva ! ***', 2)
        
        # Creating the Splitter window
        self.sp = wx.SplitterWindow(self, style=wx.SP_3D|wx.SP_3D)
        self.sp.SetMinimumPaneSize(50)
        # Creating the Tree and Notebook
        self.tree = wx.TreeCtrl(self.sp, style=wx.TR_DEFAULT_STYLE)
        self.nb = wx.Notebook(self.sp)        
        # Notebook page objects.
        self.description = Description(self.nb)
        self.nb.AddPage(self.description, "Description")
        self.vme = VME(self.nb)
        self.nb.AddPage(self.vme, "VME")
        self.crim = CRIM(self.nb)
        self.nb.AddPage(self.crim, SC_Util.VMEdevTypes.CRIM)
        self.croc = CROC(self.nb)
        self.nb.AddPage(self.croc, SC_Util.VMEdevTypes.CROC)
        self.ch = CH(self.nb)
        self.nb.AddPage(self.ch, SC_Util.VMEdevTypes.CH)
        self.croce = CROCE(self.nb)
        self.nb.AddPage(self.croce, SC_Util.VMEdevTypes.CROCE)
        self.che = CHE(self.nb)
        self.nb.AddPage(self.che, SC_Util.VMEdevTypes.CHE)
        self.fe = FE(self.nb)
        self.nb.AddPage(self.fe, SC_Util.VMEdevTypes.FE)
        self.dig = DIG(self.nb)
        self.nb.AddPage(self.dig, SC_Util.VMEdevTypes.DIG)
        # Adding Tree and Notebook instances to Splitter
        self.sp.SplitVertically(self.tree, self.nb, sashPosition=150)
        # Binding tree events
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged, self.tree)

    # MENU events ##########################################################
    def OnMenuDebugShell(self, event):
        frame = ShellFrame(parent=self)
        frame.Show()
    def OnMenuDebugNamespace(self, event):
        frame = FillingFrame(parent=self)
        frame.Show()
    def OnMenuActionsClearDescription(self, event):
        self.description.text.SetValue('')
        
    # Tree events ##########################################################
    def OnTreeSelChanged(self, event):
        items = self.tree.GetItemText(event.GetItem()).split(':')
        if items[0]==self.tree.GetItemText(self.tree.GetRootItem()):
            self.nb.ChangeSelection(1)    
        if items[0]==SC_Util.VMEdevTypes.CRIM:
            self.nb.ChangeSelection(2)
            self.crim.SetAddress(items[1])
            self.crim.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.CROC:
            self.nb.ChangeSelection(3)
            self.croc.SetAddress(items[1])
            self.croc.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.CH:
            self.nb.ChangeSelection(4)
            parent=self.tree.GetItemParent(event.GetItem())
            self.ch.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1])
            self.ch.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.CROCE:
            self.nb.ChangeSelection(5)
            self.croce.SetAddress(items[1])
            self.croce.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.CHE:
            self.nb.ChangeSelection(6)
            parent=self.tree.GetItemParent(event.GetItem())
            self.che.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1])
            self.che.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.FE:
            self.nb.ChangeSelection(7)
            parent=self.tree.GetItemParent(event.GetItem())
            grandparent=self.tree.GetItemParent(parent)
            self.fe.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1],
                self.tree.GetItemText(grandparent).split(':')[1],
                self.tree.GetItemText(parent).split(':')[0],
                self.tree.GetItemText(grandparent).split(':')[0])
            self.fe.ResetControls()
        if items[0]==SC_Util.VMEdevTypes.DIG:
            self.nb.ChangeSelection(8)
            self.dig.SetAddress('-1', items[1])
        if items[0]==SC_Util.VMEdevTypes.DIGCH:
            self.nb.ChangeSelection(8)
            parent=self.tree.GetItemParent(event.GetItem())
            self.dig.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1])
    
    def OnSCMainFrameClose(self, event):
        #self.Close(True)
        self.Destroy()


class Description(wx.Panel):
    def __init__(self, parent):
        """Creates the Description tab in the Notebook.
        All 'print' statements are redirected here by the supporting
        RedirectText class. It is impossible to print to the terminal
        in this program, but trivial to send a message to be displayed
        in the Description."""
        wx.Panel.__init__(self, parent)
        self.text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.VSCROLL | wx.HSCROLL)
        self.text.SetFont(wx.Font(SC_Util.fontSizeTextCtrl, family=wx.MODERN, style=wx.NORMAL, weight=wx.NORMAL))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.text, proportion=1, flag=wx.EXPAND|wx.ALL, border=0)
        self.SetSizer(sizer)
        sys.stdout = RedirectText(self.text)


class RedirectText:
    def __init__(self, description):
        """Supports the Description class, so that all 'print' statements
        will print to the Description page rather than to the terminal.
        This facilitates simple, easy coding of writing to the description tab."""
        self.out = description
    def write(self, string):
        self.out.WriteText(string)


class VME(wx.Panel):
    def __init__(self, parent):
        """Creates the VME tab in the Notebook."""
        p=wx.Panel.__init__(self, parent)
        self.VMEReadWrite = SC_Util.VMEReadWrite(self, caption=' Read/Write (hex)')
        self.BoardTest = SC_Util.BoardTest(self, caption=' CROCE Board Test',
            testcaptions=['RUN BOARD TEST','T1  Fast Commands','T2  Test Pulse','T3  Reset Pulse',
                          'T4  Memories D16','T5  Memories D32',
                          'T6  Memories D16 BLT','T7  Memories D32 BLT'],
            optioncaptions=['Opt1 Include RAM Mode','Opt2 Use Random Data'])
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(self.VMEReadWrite.BoxSizer, proportion=0, flag=wx.ALL, border=5)
        sizerALL.Add(self.BoardTest.BoxSizer, proportion=0, flag=wx.ALL, border=5)
        self.SetSizer(sizerALL)
        self.Fit()


class CRIM(wx.Panel):
    def __init__(self, parent):
        """Creates the CRIM tab in the Notebook."""
        self.Panel=wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CRIM', (0, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'crimID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        #Creates the CRIM 'modules' Notebook
        self.modules = wx.Notebook(self)
        self.TimingModule = CRIMTimingModule(self.modules)
        self.modules.AddPage(self.TimingModule, "TimingModule")
        self.ChannelModule = CRIMChannelModule(self.modules)
        self.modules.AddPage(self.ChannelModule, "CHModule")
        self.InterrupterModule = CRIMInterrupterModule(self.modules)
        self.modules.AddPage(self.InterrupterModule, "InterrupterModule")
        szBottom = wx.BoxSizer(wx.HORIZONTAL)
        szBottom.Add(self.modules, proportion=1, flag=wx.EXPAND|wx.ALL, border=0)
        self.sizerALL=wx.BoxSizer(wx.VERTICAL)
        self.sizerALL.Add(szTop,0,wx.ALL,5)
        self.sizerALL.Add(szBottom, 1, wx.EXPAND|wx.ALL, 0)  
        self.SetSizer(self.sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)
    def SetAddress(self, crimNumber):
        '''Sets crimNumber variables and GUI labels'''
        self.crimNumber=int(crimNumber)
        self.FindWindowByName('crimID').SetValue(crimNumber)
    def ResetControls(self):
        self.TimingModule.ResetControls()
        self.ChannelModule.ResetControls()
        self.InterrupterModule.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.TimingModule.TimingSetupRegister.controls, self.TimingModule.GateWidthRegister.controls,
            self.TimingModule.TCALBDelayRegister.controls, self.TimingModule.TRIGGERSendRegister.controls,
            self.TimingModule.TCALBSendRegister.controls, self.TimingModule.GATERegister.controls,
            self.TimingModule.CNTRSTRegister.controls, self.TimingModule.ScrapRegister.controls,
            self.TimingModule.GateTimestampRegisters.controls,                                              
            self.ChannelModule.StatusRegister.controls, self.ChannelModule.MiscRegisters.controls,
            self.ChannelModule.ModeRegister.controls, self.ChannelModule.DPMPointer.controls,
            self.ChannelModule.MessageRegisters.controls,
            self.InterrupterModule.MaskRegister.controls, self.InterrupterModule.StatusRegister.controls,
            self.InterrupterModule.IntConfigRegister.controls, self.InterrupterModule.ClearInterruptRegister.controls,
            self.InterrupterModule.VectorTableRegisters.controls)
        self.TimingModule.Fit()
        self.ChannelModule.Fit()
        self.InterrupterModule.Fit()


class CRIMTimingModule(wx.Panel):
    def __init__(self, parent):
        """Creates the TimingModule tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.TimingSetupRegister=SC_Util.CRIMTimingTimingSetupRegister(
            self, caption='Timing Setup Register')
        self.GateWidthRegister=SC_Util.CRIMTimingGateWidthRegister(
            self, caption='Gate Width Register')
        self.TCALBDelayRegister=SC_Util.GenericRegister(self, caption='TCALB Delay Register',
            btnWriteVisible=True, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='18.9ns per bit', WEnable=True)
        self.TRIGGERSendRegister=SC_Util.GenericRegister(self, caption='TRIGGER Send Register',
            btnWriteVisible=True, btnWriteCaption='Send TRIGGER',
            btnReadVisible=False, txtDataVisible=False)
        self.TCALBSendRegister=SC_Util.GenericRegister(self, caption='TCALB Send Register',
            btnWriteVisible=True, btnWriteCaption='Send TCALB',
            btnReadVisible=False, txtDataVisible=False)
        self.GATERegister=SC_Util.GenericRegister(self, caption='GATE Register',
            btnWriteVisible=True, btnWriteCaption='Start GATE',
            btnReadVisible=True, btnReadCaption='Stop GATE', txtDataVisible=False)
        self.CNTRSTRegister=SC_Util.GenericRegister(self, caption='SEQUENCE Register',
            btnWriteVisible=True, btnWriteCaption='CNTRST',
            btnReadVisible=True, btnReadCaption='CNTRSTSGATETCALB', txtDataVisible=False)
        self.ScrapRegister=SC_Util.GenericRegister(self, caption='Scrap Register',
            btnWriteVisible=True, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='any value', WEnable=True)
        self.GateTimestampRegisters=SC_Util.GenericRegister(self, caption='Gate Time Register',
            btnWriteVisible=False, btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='timestamp 28bits', WEnable=False)
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.TimingSetupRegister.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.GateWidthRegister.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.TCALBDelayRegister.BoxSizer, 0, wx.ALL, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.TRIGGERSendRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.TCALBSendRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.GATERegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.CNTRSTRegister.BoxSizer, 0, wx.ALL, 2)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.ScrapRegister.BoxSizer, 0, wx.ALL, 2)
        szV3.Add(self.GateTimestampRegisters.BoxSizer, 0, wx.ALL, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV2, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV3, 1, wx.ALL|wx.EXPAND, 0)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szH, 0, wx.ALL, 5)       
        self.SetSizer(sizerALL)
        self.Fit()
    def ResetControls(self):
        self.TimingSetupRegister.ResetControls()
        self.GateWidthRegister.ResetControls()
        self.TCALBDelayRegister.ResetControls()
        self.TRIGGERSendRegister.ResetControls()
        self.TCALBSendRegister.ResetControls()
        self.GATERegister.ResetControls()
        self.CNTRSTRegister.ResetControls()
        self.ScrapRegister.ResetControls()
        self.GateTimestampRegisters.ResetControls()


class CRIMChannelModule(wx.Panel):
    def __init__(self, parent):
        """Creates the DAQModule tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.StatusRegister=SC_Util.StatusRegister(self, 'CRIM CH')
        self.DPMPointer=SC_Util.GenericRegister(self, caption='DPM Pointer',
            btnWriteVisible=True, btnWriteCaption='Reset DPM Pointer',
            btnReadVisible=True, btnReadCaption='Read DPM Pointer',
            txtDataVisible=True, txtDataCaption='dpm pointer value', WEnable=False)
        self.MessageRegisters=SC_Util.MessageRegisters(self)
        self.ModeRegister=SC_Util.CRIMCHModeRegister(self)
        self.MiscRegisters=SC_Util.CRIMCHMiscRegisters(self)
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.StatusRegister.BoxSizer, 1, wx.ALL, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.DPMPointer.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.MessageRegisters.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.ModeRegister.BoxSizer, 0, wx.ALL, 2)
        szV3.Add(self.MiscRegisters.BoxSizer, 0, wx.ALL, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV2, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV3, 1, wx.ALL|wx.EXPAND, 0)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szH, 0, wx.ALL, 5)       
        self.SetSizer(sizerALL)
        self.Fit()
    def ResetControls(self):
        self.StatusRegister.ResetControls()
        self.DPMPointer.ResetControls()
        self.MessageRegisters.ResetControls()
        self.ModeRegister.ResetControls()
        self.MiscRegisters.ResetControls()

       
class CRIMInterrupterModule(wx.Panel):
    def __init__(self, parent):
        """Creates the InterrupterModule tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.MaskRegister=SC_Util.GenericRegister(
            self, caption='Mask Register (hex)',
            btnWriteVisible=True, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='mask value', WEnable=True)
        self.StatusRegister=SC_Util.GenericRegister(
            self, caption='Status Register (hex)',
            btnWriteVisible=True, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='interrupt value', WEnable=True)
        self.IntConfigRegister = SC_Util.CRIMIntConfigRegister(
            self, caption='Int Config Register')
        self.ClearInterruptRegister=SC_Util.GenericRegister(
            self, caption='Interrupt Clear Register',
            btnWriteVisible=True, btnWriteCaption='Clear ALL Pending Int',
            btnReadVisible=False, txtDataVisible=False)
        self.VectorTableRegisters=SC_Util.CRIMIntVectorTableID(
            self, caption='Vector Table IDs (hex)')
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.MaskRegister.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.StatusRegister.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szV2.Add(self.IntConfigRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.ClearInterruptRegister.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szV3.Add(self.VectorTableRegisters.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 0, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV2, 0, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV3, 0, wx.ALL|wx.EXPAND, 0)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szH, 0, wx.ALL, 5)       
        self.SetSizer(sizerALL)
        self.Fit()
    def ResetControls(self):
        self.MaskRegister.ResetControls()
        self.StatusRegister.ResetControls()
        self.IntConfigRegister.ResetControls()
        self.ClearInterruptRegister.ResetControls()
        self.VectorTableRegisters.ResetControls()

        
class CROC(wx.Panel):
    def __init__(self, parent):
        """Creates the CROC tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CROC', (0, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'crocID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.TimingSetup=SC_Util.CROCTimingSetup(self, caption=' Timing Setup')
        self.FastCmd=SC_Util.CROCFastCmd(self, caption=' Fast Commands')
        self.ResetAndTestPulse=SC_Util.CROCResetAndTestPulse(
            self, caption=' Reset And Test Pulse')
        self.LoopDelays=SC_Util.CROCLoopDelays(self, caption=' Loop Delays')
        self.FEBGateDelays=SC_Util.CROCFEBGateDelays(
            self, caption=' FEB Gate Delays')        
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.TimingSetup.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.FastCmd.BoxSizer, 0, wx.ALL, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.ResetAndTestPulse.BoxSizer, 0, wx.ALL, 2)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.LoopDelays.BoxSizer, 0, wx.ALL, 2)
        szV3.Add(self.FEBGateDelays.BoxSizer, 0, wx.ALL, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 0, wx.ALL, 0)
        szH.Add(szV2, 0, wx.ALL, 0)
        szH.Add(szV3, 0, wx.ALL, 0)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5) 
        sizerALL.Add(szH, 0, wx.ALL, 5)
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)   
    def SetAddress(self, crocNumber):
        '''Sets crocNumber variables and GUI labels'''
        self.crocNumber=int(crocNumber)
        self.FindWindowByName('crocID').SetValue(crocNumber)
    def ResetControls(self):
        self.TimingSetup.ResetControls()
        self.FastCmd.ResetControls()
        self.LoopDelays.ResetControls()
        self.ResetAndTestPulse.ResetControls()
        #self.FEBGateDelays.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.TimingSetup.controls, self.FastCmd.controls, 
            self.ResetAndTestPulse.controls,
            self.LoopDelays.controls, self.FEBGateDelays.controls)
        self.Fit()


class CH(wx.Panel):
    def __init__(self, parent):
        """Creates the CH tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CH', (0, 0), (50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'chID', SC_Util.colorText),
            ('CROC', (100, 0), (50, 16), 'lbl', SC_Util.colorLabel),
            ('', (150, 0), (50, 16), 'crocID', SC_Util.colorText))
        self.TopLabels=SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.StatusRegister=SC_Util.StatusRegister(self, 'CROC CH')
        self.DPMPointer=SC_Util.GenericRegister(self, caption='DPM Pointer',
            btnWriteVisible=True, btnWriteCaption='Reset DPM Pointer',
            btnReadVisible=True, btnReadCaption='Read DPM Pointer',
            txtDataVisible=True, txtDataCaption='dpm pointer value', WEnable=False)
        self.MessageRegisters=SC_Util.MessageRegisters(self)        
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)  
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.StatusRegister.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.DPMPointer.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.MessageRegisters.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV2, 1, wx.ALL|wx.EXPAND, 0)
        sizerALL.Add(szH, 0, wx.ALL, 5)
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)
    def SetAddress(self, chNumber, crocNumber):
        '''Sets chNumber and crocNumber variables and GUI labels'''
        self.chNumber=int(chNumber)
        self.crocNumber=int(crocNumber)
        self.FindWindowByName('chID').SetValue(chNumber)
        self.FindWindowByName('crocID').SetValue(crocNumber)
    def ResetControls(self):
        self.StatusRegister.ResetControls()
        self.DPMPointer.ResetControls()
        self.MessageRegisters.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.StatusRegister.controls, self.DPMPointer.controls, self.MessageRegisters.controls)
        self.Fit()


class CROCE(wx.Panel):
    def __init__(self, parent):
        """Creates the CROC tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CROCE', (0, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'croceID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.TimingSetup=SC_Util.CROCTimingSetup(self, caption=' Timing Setup')
        self.FastCmd=SC_Util.CROCFastCmd(self, caption=' Fast Commands')
        self.ResetAndTestPulse=SC_Util.CROCResetAndTestPulse(self, caption=' Reset And Test Pulse', nrows=1)
        self.RDFESetup=SC_Util.CROCERDFESetup(self, caption=' RDFE Setup')
        self.LoopDelays=SC_Util.CROCLoopDelays(self, caption=' Loop Delays')
        self.FEBGateDelays=SC_Util.CROCFEBGateDelays(self, caption=' FEB Gate Delays')
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.TimingSetup.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.FastCmd.BoxSizer, 0, wx.ALL, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.ResetAndTestPulse.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.RDFESetup.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.LoopDelays.BoxSizer, 0, wx.ALL, 2)
        szV3.Add(self.FEBGateDelays.BoxSizer, 0, wx.ALL, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 0, wx.ALL, 0)
        szH.Add(szV2, 0, wx.ALL, 0)
        szH.Add(szV3, 0, wx.ALL, 0)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)
        sizerALL.Add(szH, 0, wx.ALL, 5)
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)
    def SetAddress(self, croceNumber):
        '''Sets croceNumber variables and GUI labels'''
        self.croceNumber=int(croceNumber)
        self.FindWindowByName('croceID').SetValue(croceNumber)
    def ResetControls(self):
        self.TimingSetup.ResetControls()
        self.FastCmd.ResetControls()
        self.LoopDelays.ResetControls()
        self.ResetAndTestPulse.ResetControls()
        self.RDFESetup.ResetControls()
        #self.FEBGateDelays.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.TimingSetup.controls, self.FastCmd.controls, 
            self.ResetAndTestPulse.controls, self.RDFESetup.controls,
            self.LoopDelays.controls, self.FEBGateDelays.controls)
        self.Fit()


class CHE(wx.Panel):
    def __init__(self, parent):
        """Creates the CHE tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CHE', (0, 0), (50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'cheID', SC_Util.colorText),
            ('CROCE', (100, 0), (50, 16), 'lbl', SC_Util.colorLabel),
            ('', (150, 0), (50, 16), 'croceID', SC_Util.colorText))
        self.TopLabels=SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.ConfigurationRegister=SC_Util.CHEConfigurationRegister(self, '')
        self.ReadAllRegisters=SC_Util.GenericRegister(self, caption='Read All Regs',
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read All Regs',
            txtDataVisible=False, txtDataCaption='value', WEnable=False)
        self.CommandsRegister=SC_Util.CHECommandsRegister(self, ' Commands')
        self.RcvMemWPointerRegister=SC_Util.GenericRegister(self, caption='RcvMem WPointer (bytes)',
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='value', WEnable=False, size=(155,20))
        self.RcvMemFramesCounterRegister=SC_Util.GenericRegister(self, caption='RcvMem FrmCounter',
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='value', WEnable=False, size=(155,20))
        self.RDFECounterRegister=SC_Util.GenericRegister(self, caption='RDFE Counter',
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='value', WEnable=False, size=(155,20))
        self.TXRstTpInDelayCounterRegister=SC_Util.GenericRegister(self, caption='RST/TP Delay Counter',
            btnWriteVisible=False, btnWriteCaption='Write',
            btnReadVisible=True, btnReadCaption='Read',
            txtDataVisible=True, txtDataCaption='value', WEnable=False, size=(155,20))
        self.StatusFrameRegister=SC_Util.CHEStatusFrameRegister(self, '')
        self.StatusTXRXRegister=SC_Util.CHEStatusTXRXRegister(self, '')
        self.SendMemory=SC_Util.CHEMemories(self,
            captions=['Send Memory', 'Write', 'Addr', 'addr', 'Data(hex)', 'data'],
            txtenables=[True, True])
        self.ReceiveMemory=SC_Util.CHEMemories(self,
            captions=['Receive Memory', 'Read', '#Words', '#words', 'Data(hex)', 'data'],
            txtenables=[True, True])
        self.FramePointersMemory=SC_Util.CHEMemories(self,
            captions=['Frame Pointers Memory', 'Read', '#Words', '#words', 'Data(hex)', 'data'],
            txtenables=[True, True])
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.ConfigurationRegister.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.ReadAllRegisters.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.CommandsRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.RcvMemWPointerRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.RcvMemFramesCounterRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.RDFECounterRegister.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.TXRstTpInDelayCounterRegister.BoxSizer, 0, wx.ALL, 2)
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.StatusFrameRegister.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szV4=wx.BoxSizer(wx.VERTICAL)
        szV4.Add(self.StatusTXRXRegister.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(szV1, 0, wx.ALL, 0)
        szH1.Add(szV2, 0, wx.ALL, 0)
        szH1.Add(szV3, 0, wx.ALL, 0)
        szH1.Add(szV4, 0, wx.ALL, 0)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(self.SendMemory.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szH3=wx.BoxSizer(wx.HORIZONTAL)
        szH3.Add(self.ReceiveMemory.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        szH4=wx.BoxSizer(wx.HORIZONTAL)
        szH4.Add(self.FramePointersMemory.BoxSizer, 1, wx.ALL|wx.EXPAND, 2)
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)
        sizerALL.Add(szH1, 0, wx.ALL, 2)
        sizerALL.Add(szH2, 0, wx.ALL|wx.EXPAND, 2)
        sizerALL.Add(szH3, 0, wx.ALL|wx.EXPAND, 2)
        sizerALL.Add(szH4, 0, wx.ALL|wx.EXPAND, 2)
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)
    def SetAddress(self, cheNumber, croceNumber):
        '''Sets cheNumber and croceNumber variables and GUI labels'''
        self.cheNumber=int(cheNumber)
        self.croceNumber=int(croceNumber)
        self.FindWindowByName('cheID').SetValue(cheNumber)
        self.FindWindowByName('croceID').SetValue(croceNumber)
    def ResetControls(self):
        self.ConfigurationRegister.ResetControls()
        self.ReadAllRegisters.ResetControls()
        self.StatusFrameRegister.ResetControls()
        self.StatusTXRXRegister.ResetControls()
        self.CommandsRegister.ResetControls()
        self.RcvMemWPointerRegister.ResetControls()
        self.RcvMemFramesCounterRegister.ResetControls()
        self.RDFECounterRegister.ResetControls()
        self.TXRstTpInDelayCounterRegister.ResetControls()
        self.SendMemory.ResetControls()
        self.ReceiveMemory.ResetControls()
        self.FramePointersMemory.ResetControls()  
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.ConfigurationRegister.controls, self.StatusFrameRegister.controls,
            self.StatusTXRXRegister.controls, self.CommandsRegister.controls,
            self.RcvMemWPointerRegister.controls, self.RcvMemFramesCounterRegister.controls,
            self.RDFECounterRegister.controls, self.TXRstTpInDelayCounterRegister.controls,
            self.SendMemory.controls, self.ReceiveMemory.controls, self.FramePointersMemory.controls, 
            self.ReadAllRegisters.controls)
        self.Fit()


class FE(wx.Panel):
    def __init__(self, parent):
        """Creates the FE tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('FEB', (0, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'febID', SC_Util.colorText),
            ('CH', (100, 0), (50, 16), 'chType', SC_Util.colorLabel),
            ('', (150, 0), (50, 16), 'chID', SC_Util.colorText),
            ('CROC', (200, 0), (50, 16), 'crocType', SC_Util.colorLabel),
            ('', (250, 0), (50, 16), 'crocID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        #Creates the FE 'devices' Notebook
        self.devices = wx.Notebook(self)
        self.fpga = FPGA(self.devices)
        self.devices.AddPage(self.fpga, "FPGA")
        self.trip = TRIP(self.devices)
        self.devices.AddPage(self.trip, "TRIP")
        self.daq = DAQ(self.devices)
        self.devices.AddPage(self.daq, "DAQ")
        self.flash = FLASH(self.devices)
        self.devices.AddPage(self.flash, "FLASH")
        szBottom = wx.BoxSizer(wx.HORIZONTAL)
        szBottom.Add(self.devices, proportion=1, flag=wx.EXPAND|wx.ALL, border=0)
        self.sizerALL=wx.BoxSizer(wx.VERTICAL)
        self.sizerALL.Add(szTop,0,wx.ALL,5)
        self.sizerALL.Add(szBottom, 1, wx.EXPAND|wx.ALL, 0)  
        self.SetSizer(self.sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        self.OnbtnShowAdvancedGUI(None)
    def SetAddress(self, febNumber, chNumber, crocNumber, chLabel, crocLabel):
        '''Sets febNumber, chNumber and crocNumber variables and GUI labels'''
        self.febNumber=int(febNumber)
        self.chNumber=int(chNumber)
        self.crocNumber=int(crocNumber)
        self.FindWindowByName('febID').SetValue(febNumber)
        self.FindWindowByName('chID').SetValue(chNumber)
        self.FindWindowByName('crocID').SetValue(crocNumber)
        self.FindWindowByName('chType').SetValue(chLabel)
        self.FindWindowByName('crocType').SetValue(crocLabel)
    def ResetControls(self):
        self.fpga.ResetControls()
        self.trip.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.daq.sizerALL.ShowItems(self.showAdvanced)
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.flash.FlashButtons.controls, self.fpga.Registers.controlsAdvanced)
        self.fpga.Fit()
        self.trip.Fit()
        self.flash.Fit()


class FPGA(wx.Panel):
    def __init__(self, parent):
        """Creates the FPGA tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.Registers=SC_Util.FPGARegisters(self)
        for wrReg in self.Registers.txtRegs:
            if wrReg.GetName()[1]=='R': wrReg.Enable(False)
        sizerALL=wx.BoxSizer(wx.HORIZONTAL)
        sizerALL.Add(self.Registers.FPGABoxSizer, proportion=0, flag=wx.ALL, border=5)  
        self.SetSizer(sizerALL)
        self.Fit()
    def ResetControls(self):
        self.Registers.ResetControls()


class TRIP(wx.Panel):
    def __init__(self, parent):
        """Creates the TRIP tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.Registers=SC_Util.TRIPRegisters(self)
        sizerALL=wx.BoxSizer(wx.HORIZONTAL)
        sizerALL.Add(self.Registers.TripBoxSizer, proportion=0, flag=wx.ALL, border=5)  
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_RADIOBOX, self.ResetControls, self.Registers.chkTrip)
    def ResetControls(self, event=None):
        #if event!=None: print self, event, event.GetInt()#, wx.CommandEvent.GetInt()
        self.Registers.ResetControls()


class FLASH(wx.Panel):
    def __init__(self, parent):
        """Creates the FLASH tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.FlashButtons=SC_Util.FlashButtons(self,
            'Read FLASH to File', 'Write File to FLASH')
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(self.FlashButtons.FlashBoxSizer, proportion=0, flag=wx.ALL, border=5)  
        #self.text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE|wx.VSCROLL)
        #sizerALL.Add(self.text, proportion=1, flag=wx.EXPAND|wx.ALL, border=0)
        self.SetSizer(sizerALL)
        self.Fit()


class DIG(wx.Panel):
    def __init__(self, parent):
        """Creates the CROC tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('DIG', (0, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (50, 0), (50, 16), 'digID', SC_Util.colorText),
            ('DIGCH', (100, 0),(50, 16), 'lbl', SC_Util.colorLabel),
            ('', (150, 0), (50, 16), 'digchID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.btnLoadConfigFile=SC_Util.CreateButton(self, 'Load Config File',
            pos=(0,0), size=(120,20), name='', bckcolor=SC_Util.colorButton)
        self.btnReadAllRegs=SC_Util.CreateButton(self, 'Read All Regs',
            pos=(0,0), size=(120,20), name='', bckcolor=SC_Util.colorButton)
        self.btnTakeNEvents=SC_Util.CreateButton(self, 'Take N Events',
            pos=(0,0), size=(80,20), name='', bckcolor=SC_Util.colorButton)
        self.txtNEvents=SC_Util.CreateTextCtrl(self, label='N',
            pos=(0,0), size=(30, 20), name='', bckcolor=SC_Util.colorText)
        self.btncontrols=[self.btnLoadConfigFile, self.btnReadAllRegs,
            self.btnTakeNEvents, self.btnTakeNEvents, self.txtNEvents]
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(self.btnTakeNEvents, 0, wx.ALL, 1)
        szH1.Add(self.txtNEvents, 1, wx.ALL, 1)
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.btnLoadConfigFile, 0, wx.ALL, 2)
        szV1.Add(self.btnReadAllRegs, 0, wx.ALL, 2)
        szV1.Add(szH1, 0, wx.ALL|wx.EXPAND, 2)
##        lblChoicesData=(
##            ('Write To File', (0, 0),(80, 16), 'lbl', SC_Util.colorLabel),
##            #('Append Mode', (0, 0), (80, 16), 'lbl', SC_Util.colorText),
##            ('Readout Mode', (0, 0),(80, 16), 'lbl', SC_Util.colorLabel))
##        self.lblChoices = SC_Util.CreateLabels(self, lblChoicesData, offset=(0, 0))
##        szV2=wx.BoxSizer(wx.VERTICAL)
##        szV2.Add(self.lblChoices[0], 0, wx.ALL, 4)
##        szV2.Add(self.lblChoices[1], 0, wx.ALL, 4)
##        szV2.Add(self.lblChoices[2], 0, wx.ALL, 4)
        WriteToFileStr=V1720Config.WriteToFile.values(); WriteToFileStr.sort()
        self.choiceWriteToFile=wx.Choice(self, size=(120,20), choices=WriteToFileStr)
        self.choiceWriteToFile.SetFont(SC_Util.myFont(SC_Util.fontSizeChoice))
##        AppendModeStr=V1720Config.AppendMode.values(); AppendModeStr.sort()
##        self.choiceAppendMode=wx.Choice(self, size=(120,20), choices=AppendModeStr)
##        self.choiceAppendMode.SetFont(SC_Util.myFont(SC_Util.fontSizeChoice))
        ReadoutModeStr=V1720Config.ReadoutMode.values(); ReadoutModeStr.sort()
        self.choiceReadoutMode=wx.Choice(self, size=(120,20), choices=ReadoutModeStr)
        self.choiceReadoutMode.SetFont(SC_Util.myFont(SC_Util.fontSizeChoice))
##        self.choicecontrols=[self.choiceWriteToFile, self.choiceAppendMode, self.choiceReadoutMode]
        self.choicecontrols=[self.choiceWriteToFile, self.choiceReadoutMode]
        szV3=wx.BoxSizer(wx.VERTICAL)
        szV3.Add(self.choiceWriteToFile, 0, wx.ALL, 2)
##        szV3.Add(self.choiceAppendMode, 0, wx.ALL, 2)
        szV3.Add(self.choiceReadoutMode, 0, wx.ALL, 2)
        StaticBox=wx.StaticBox(self, -1, 'Output Format')
        StaticBox.SetFont(SC_Util.myFont(SC_Util.fontSizeStaticBox))
        StaticBox.SetForegroundColour(SC_Util.colorForeground)
        self.chkOutputData=SC_Util.CreateCheckBox(self, V1720Config.FormatData,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkOutputOneLineCH=SC_Util.CreateCheckBox(self, V1720Config.FormatOneLineCH,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkOutputHeader=SC_Util.CreateCheckBox(self, V1720Config.FormatHeader,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkOutputEventData=SC_Util.CreateCheckBox(self, V1720Config.FormatEventData,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkOutputConfigInfo=SC_Util.CreateCheckBox(self, V1720Config.FormatConfigInfo,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkOutputEventStat=SC_Util.CreateCheckBox(self, V1720Config.FormatEventStat,
            pos=(0,0), size=(80,16), name='', bckcolor=SC_Util.colorButton)
        self.chkcontrols=[self.chkOutputData, self.chkOutputOneLineCH,
            self.chkOutputHeader, self.chkOutputEventData,
            self.chkOutputConfigInfo, self.chkOutputEventStat, StaticBox]
        szGrid=wx.FlexGridSizer(rows=3, cols=2, hgap=2, vgap=1)
        szGrid.Add(self.chkOutputData, 0, 0, 0)
        szGrid.Add(self.chkOutputHeader, 0, 0, 0)
        szGrid.Add(self.chkOutputConfigInfo, 0, 0, 0)
        szGrid.Add(self.chkOutputOneLineCH, 0, 0, 0)
        szGrid.Add(self.chkOutputEventData, 0, 0, 0)
        szGrid.Add(self.chkOutputEventStat, 0, 0, 0)
        szV4=wx.StaticBoxSizer(StaticBox, wx.VERTICAL)
        szV4.Add(szGrid, 0, wx.ALL, 2)
        self.VMEReadWrite = SC_Util.VMEReadWrite(self, caption=' Read/Write (hex)')
        szV5=wx.BoxSizer(wx.VERTICAL)
        szV5.Add(self.VMEReadWrite.BoxSizer, 0, wx.ALL, 0)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(szV1, 0, wx.ALL, 2)
##        szH2.Add(szV2, 0, wx.ALL, 2)
        szH2.Add(szV3, 0, wx.ALL, 2)
        szH2.Add(szV4, 0, wx.ALL, 2)
        szH2.Add(szV5, 0, wx.ALL, 2)
        self.display = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.VSCROLL | wx.HSCROLL)
        self.display.SetFont(wx.Font(SC_Util.fontSizeTextCtrl, family=wx.MODERN, style=wx.NORMAL, weight=wx.NORMAL))        
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)
        sizerALL.Add(szH2, 0, wx.ALL, 5)
        sizerALL.Add(self.display, 1, wx.ALL|wx.EXPAND, 7)
        self.SetSizer(sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnShowAdvancedGUI, self.btnShowAdvancedGUI)
        self.showAdvanced=False
        #self.OnbtnShowAdvancedGUI(None)
        #self.VMEReadWrite = SC_Util.VMEReadWrite(self, caption=' Read/Write (hex)')
    def SetAddress(self, digchNumber, digNumber):
        '''Sets crocNumber variables and GUI labels'''
        self.digchNumber=int(digchNumber)
        self.digNumber=int(digNumber)
        self.FindWindowByName('digchID').SetValue(digchNumber)
        self.FindWindowByName('digID').SetValue(digNumber)
    def OnbtnShowAdvancedGUI(self, event): 
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.btncontrols, self.choicecontrols, self.chkcontrols, [self.display])
        self.Fit()


class DAQ(wx.Panel):
    def __init__(self, parent):
        """Creates the DAQ tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.display = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.VSCROLL | wx.HSCROLL, size=(100, 100))
        self.display.SetFont(wx.Font(SC_Util.fontSizeTextCtrl, family=wx.MODERN, style=wx.NORMAL, weight=wx.NORMAL))     
        self.radioReadType=wx.RadioBox(self, -1, 'Read from', (5,5), wx.DefaultSize, ['FE','CH','CTRL','ALL'], 2, wx.RA_SPECIFY_COLS)
        self.radioReadType.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        self.radioWriteType=wx.RadioBox(self, -1, 'Write to', (5,5), wx.DefaultSize, ['disp','file','both'], 1, wx.RA_SPECIFY_COLS)
        self.radioWriteType.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        size=(50,18)
        self.chkDataTypeDiscrim=SC_Util.CreateCheckBox(self, label='Disc', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.chkDataTypeTrip=SC_Util.CreateCheckBox(self, label='Trip#', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.chkDataTypeHit=SC_Util.CreateCheckBox(self, label='Hit#', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        size=(20,18)
        self.txtDataTypeTripNumber=wx.TextCtrl(self, size=size, name='Trip#')
        self.txtDataTypeHitNumber=wx.TextCtrl(self, size=size, name='Hit#')
        fgsDataType=wx.FlexGridSizer(rows=3, cols=2, hgap=2, vgap=1)
        fgsDataType.Add(self.chkDataTypeDiscrim, 0, wx.ALL|wx.EXPAND, 1)
        fgsDataType.Add(size, 0, wx.ALL|wx.EXPAND, 1)
        fgsDataType.Add(self.chkDataTypeTrip, 0, wx.ALL|wx.EXPAND, 1)
        fgsDataType.Add(self.txtDataTypeTripNumber, 0, wx.ALL|wx.EXPAND, 1)
        fgsDataType.Add(self.chkDataTypeHit, 0, wx.ALL|wx.EXPAND, 1)
        fgsDataType.Add(self.txtDataTypeHitNumber, 0, wx.ALL|wx.EXPAND, 1)
        sbDataType=wx.StaticBox(self, -1, "Data Type")
        sbDataType.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        szDataType=wx.StaticBoxSizer(sbDataType, wx.VERTICAL)
        szDataType.Add(fgsDataType, 1, wx.ALL|wx.EXPAND, 2)
        size=(100,20)
        self.lblAcqCtrlNEvents=SC_Util.CreateLabel(self, label='N Events', pos=(0,0), size=size, name='', color=SC_Util.colorLabel)
        self.txtAcqCtrlNEvents=SC_Util.CreateTextCtrl(self, label='', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorText)
        self.btnAcqCtrlStart=SC_Util.CreateButton(self, label='START', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
##        self.btnAcqCtrlStop=SC_Util.CreateButton(self, label='STOP', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnAcqCtrlStartThread=SC_Util.CreateButton(self, label='START Thread', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnAcqCtrlStopThread=SC_Util.CreateButton(self, label='STOP Thread', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        fgsAcqCtrl=wx.FlexGridSizer(rows=3, cols=2, hgap=2, vgap=1)
        fgsAcqCtrl.Add(self.lblAcqCtrlNEvents, 0, 0, 0)
        fgsAcqCtrl.Add(self.txtAcqCtrlNEvents, 0, 0, 0)
        fgsAcqCtrl.Add(self.btnAcqCtrlStart, 0, 0, 0)
        fgsAcqCtrl.Add(size, 0, 0, 0)
        fgsAcqCtrl.Add(self.btnAcqCtrlStartThread, 0, 0, 0)
        fgsAcqCtrl.Add(self.btnAcqCtrlStopThread, 0, 0, 0)
        sbAcqCtrl=wx.StaticBox(self, -1, "Acquisition Control CROCE")
        sbAcqCtrl.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        szAcqCtrl=wx.StaticBoxSizer(sbAcqCtrl, wx.VERTICAL)
        szAcqCtrl.Add(fgsAcqCtrl, 0, wx.ALL, 2)
        size=(90,20)
        self.btnActionsClearDisplay=SC_Util.CreateButton(self, label='CLEAR display', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnBRAMCtrlOpenGate=SC_Util.CreateButton(self, label='Open Gate', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnBRAMCtrlSoftRDFE=SC_Util.CreateButton(self, label='Soft RDFE', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        fgsActions=wx.FlexGridSizer(rows=3, cols=1, hgap=2, vgap=1)
        fgsActions.Add(self.btnActionsClearDisplay, 0, 0, 0)
        fgsActions.Add(self.btnBRAMCtrlOpenGate, 0, 0, 0)
        fgsActions.Add(self.btnBRAMCtrlSoftRDFE, 0, 0, 0)
        sbActions=wx.StaticBox(self, -1, "Actions")
        sbActions.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        szActions=wx.StaticBoxSizer(sbActions, wx.VERTICAL)
        szActions.Add(fgsActions, 0, wx.ALL, 2)
        size=(100,20)
        self.btnBRAMCtrlReadDiscrimBRAM=SC_Util.CreateButton(self, label='Read Disc BRAM', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnBRAMCtrlReadTripBRAM=SC_Util.CreateButton(self, label='Read Trip BRAM', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        self.btnBRAMCtrlReadHitBRAM=SC_Util.CreateButton(self, label='Read Hit BRAM', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        fgsBRAMCtrl=wx.FlexGridSizer(rows=3, cols=1, hgap=2, vgap=1)
        fgsBRAMCtrl.Add(self.btnBRAMCtrlReadDiscrimBRAM, 0, 0, 0)
        fgsBRAMCtrl.Add(self.btnBRAMCtrlReadTripBRAM, 0, 0, 0)
        fgsBRAMCtrl.Add(self.btnBRAMCtrlReadHitBRAM, 0, 0, 0)
        sbBRAMCtrl=wx.StaticBox(self, -1, "BRAMs")
        sbBRAMCtrl.SetFont(SC_Util.myFont(SC_Util.fontSizeRadioBox))
        szBRAMCtrl=wx.StaticBoxSizer(sbBRAMCtrl, wx.VERTICAL)
        szBRAMCtrl.Add(fgsBRAMCtrl, 0, wx.ALL, 2)
        szH1=wx.BoxSizer(wx.HORIZONTAL)
        szH1.Add(szActions, 0, wx.ALL, 2)
        szH1.Add(szBRAMCtrl, 0, wx.ALL, 2)
        szH1.Add(szDataType, 0, wx.ALL, 2)
        self.btnReadRcvMem=SC_Util.CreateButton(self, label='Read Rcv MEM', pos=(0,0), size=size, name='', bckcolor=SC_Util.colorButton)
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.radioReadType, 0, wx.ALL, 0)
        szV1.Add(self.btnReadRcvMem, 0, wx.ALL, 2)
        szH1.Add(szV1, 0, wx.ALL, 2)
        szH1.Add(self.radioWriteType, 0, wx.ALL, 2)
        szH1.Add(szAcqCtrl, 1, wx.ALL|wx.EXPAND, 2)
        szH2=wx.BoxSizer(wx.HORIZONTAL)
        szH2.Add(self.display, 1, wx.ALL|wx.EXPAND, 2)
        szV=wx.BoxSizer(wx.VERTICAL)
        szV.Add(szH1, 0, wx.ALL, 0)
        szV.Add(szH2, 1, wx.ALL|wx.EXPAND, 0)
        self.sizerALL=wx.BoxSizer(wx.VERTICAL)
        self.sizerALL.Add(szV, 1, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(self.sizerALL)
        self.Fit()
        self.Bind(wx.EVT_BUTTON, self.OnbtnActionsClearDisplay, self.btnActionsClearDisplay)
        self.chkDataTypeDiscrim.SetValue(False)
        self.txtDataTypeTripNumber.SetValue(str(-1))
        self.txtDataTypeHitNumber.SetValue(str(-1))
        self.txtAcqCtrlNEvents.SetValue(str(3))
    def ResetControls(self): pass
    def OnbtnActionsClearDisplay(self, event):
        self.display.SetValue('')


if __name__=='__main__':
    app=wx.PySimpleApp()
    frame=SCMainFrame()
    frame.Show()
    app.MainLoop()
