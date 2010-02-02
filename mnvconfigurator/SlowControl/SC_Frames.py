"""
MINERvA DAQ Slow Control GUI
Contains Frames (Layout) classes
Started October 21 2009
"""

import wx
import sys
import SC_Util
from wx.py.shell import ShellFrame
from wx.py.filling import FillingFrame

class SCMainFrame(wx.Frame):
    '''SlowControl main frame '''
    def __init__(self, logoPhoto=None, parent=None, id=-1, title='Slow Control Main Frame'):
        wx.Frame.__init__(self, parent, id, title, size=(850, 600)
            , style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
            ###, style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER))
        #self.bmp = wx.StaticBitmap(parent=self, bitmap=logoPhoto.ConvertToBitmap())
        #self.SetIcon(logoPhoto)
        #self.SetIcon(images.getPyIcon())
        self.Bind(wx.EVT_CLOSE, self.OnSCMainFrameClose)

        # Creating the top menu
        menuFile = wx.Menu()
        self.menuFileLoadHardware = menuFile.Append(wx.NewId(), text="Load &Hardware", help=" Loads the VME crate hardware")
        self.menuFileLoadFromFile =menuFile.Append(wx.NewId(), "&Load from File", " Open a file with hardware settings")
        self.menuFileSaveToFile = menuFile.Append(wx.NewId(), "&Save to File", " Save a file with hardware settings")
        menuShow = wx.Menu()
        self.menuShowExpandAll = menuShow.Append(wx.NewId(), "&Expand All")
        self.menuShowCollapseAll = menuShow.Append(wx.NewId(), "&Collapse All")
        menuActions = wx.Menu()
        self.menuActionsReadVoltages = menuActions.Append(wx.NewId(), "&Read Voltages")
        self.menuActionsZeroHVAll = menuActions.Append(wx.NewId(), "&Zero HV All")
        self.menuActionsMonitorVoltages = menuActions.Append(wx.NewId(), "&Monitor Voltages")
        menuDebug = wx.Menu()
        self.menuDebugShell = menuDebug.Append(wx.NewId(), "&Python Shell", "Open wxPython shell frame")
        self.menuDebugNamespace = menuDebug.Append(wx.NewId(), "&Namespace Viewer", "Open namespace viewer frame")
        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, "&File")
        menuBar.Append(menuShow, "&Show")
        menuBar.Append(menuActions, "&Actions")
        menuBar.Append(menuDebug, "&Debug")
        self.SetMenuBar(menuBar)
        # Binding top menu events
        self.Bind(wx.EVT_MENU, self.OnMenuDebugShell, self.menuDebugShell)
        self.Bind(wx.EVT_MENU, self.OnMenuDebugNamespace, self.menuDebugNamespace)
        
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
        self.descrip = Description(self.nb)
        self.nb.AddPage(self.descrip, "Description")
        self.vme = VME(self.nb)
        self.nb.AddPage(self.vme, "VME")
        self.crim = CRIM(self.nb)
        self.nb.AddPage(self.crim, "CRIM")
        self.croc = CROC(self.nb)
        self.nb.AddPage(self.croc, "CROC")
        self.ch = CH(self.nb)
        self.nb.AddPage(self.ch, "CH")
        self.fe = FE(self.nb)
        self.nb.AddPage(self.fe, "FE")
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
    # Tree events ##########################################################
    def OnTreeSelChanged(self, event):
        items = self.tree.GetItemText(event.GetItem()).split(':')
        if items[0]==self.tree.GetItemText(self.tree.GetRootItem()):
            self.nb.ChangeSelection(1)    
        if items[0]==CRIM.__name__:
            self.nb.ChangeSelection(2)
            self.crim.SetAddress(items[1])
            self.crim.ResetControls()
        if items[0]==CROC.__name__:
            self.nb.ChangeSelection(3)
            self.croc.SetAddress(items[1])
            self.croc.ResetControls()
        if items[0]==CH.__name__:
            self.nb.ChangeSelection(4)
            parent=self.tree.GetItemParent(event.GetItem())
            self.ch.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1])
            self.ch.ResetControls()
        if items[0]==FE.__name__: 
            self.nb.ChangeSelection(5)
            parent=self.tree.GetItemParent(event.GetItem())
            grandparent=self.tree.GetItemParent(parent)
            self.fe.SetAddress(items[1],
                self.tree.GetItemText(parent).split(':')[1],
                self.tree.GetItemText(grandparent).split(':')[1])
            self.fe.ResetControls()
    
    def OnSCMainFrameClose(self, event):
        self.Close(True)
        self.Destroy()


class Description(wx.Panel):
    def __init__(self, parent):
        """Creates the Description tab in the Notebook.
        All 'print' statements are redirected here by the supporting
        RedirectText class. It is impossible to print to the terminal
        in this program, but trivial to send a message to be displayed
        in the Description."""
        wx.Panel.__init__(self, parent)
        self.text = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.VSCROLL)
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
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(self.VMEReadWrite.BoxSizer, 0, wx.ALL, 5)
        self.SetSizer(sizerALL)
        self.Fit()     


class CRIM(wx.Panel):
    def __init__(self, parent):
        """Creates the CRIM tab in the Notebook."""
        self.Panel=wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CRIM', (0, 0),(40, 16), 'lbl', SC_Util.colorLabel),
            ('', (40, 0), (40, 16), 'crimID', SC_Util.colorText))
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
        self.ScrapRegister=SC_Util.GenericRegister(self, caption='ID Register',
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
        TopLabelsData=(('CROC', (0, 0),(40, 16), 'lbl', SC_Util.colorLabel),
            ('', (40, 0), (40, 16), 'crocID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.FlashButtons=SC_Util.FlashButtons(self,
            'Write File to FLASH Memory', 'Reboot FEs (reload FLASH content)')
        self.TimingSetup=SC_Util.CROCTimingSetup(self, caption=' Timing Setup')
        self.FastCmd=SC_Util.CROCFastCmd(self, caption=' Fast Commands')
        self.LoopDelays=SC_Util.CROCLoopDelays(self, caption=' Loop Delays')
        self.ResetAndTestPulse=SC_Util.CROCResetAndTestPulse(
            self, caption=' Reset And Test Pulse')
        self.FEBGateDelays=SC_Util.CROCFEBGateDelays(
            self, caption=' FEB Gate Delays')
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)
        sizerALL.Add(self.FlashButtons.FlashBoxSizer, 0, wx.ALL, 5)  
        szV1=wx.BoxSizer(wx.VERTICAL)
        szV1.Add(self.TimingSetup.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.FastCmd.BoxSizer, 0, wx.ALL, 2)
        szV1.Add(self.LoopDelays.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szV2=wx.BoxSizer(wx.VERTICAL)
        szV2.Add(self.ResetAndTestPulse.BoxSizer, 0, wx.ALL, 2)
        szV2.Add(self.FEBGateDelays.BoxSizer, 0, wx.ALL|wx.EXPAND, 2)
        szH=wx.BoxSizer(wx.HORIZONTAL)
        szH.Add(szV1, 1, wx.ALL|wx.EXPAND, 0)
        szH.Add(szV2, 1, wx.ALL|wx.EXPAND, 0)
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
        self.FEBGateDelays.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
        self.showAdvanced=SC_Util.ShowControls(self.btnShowAdvancedGUI, self.showAdvanced,
            self.FlashButtons.controls, self.TimingSetup.controls,
            self.FastCmd.controls, self.LoopDelays.controls,
            self.ResetAndTestPulse.controls, self.FEBGateDelays.controls)
        self.Fit()


class CH(wx.Panel):
    def __init__(self, parent):
        """Creates the CH tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('CH', (0, 0), (40, 16), 'lbl', SC_Util.colorLabel),
            ('', (40, 0), (40, 16), 'chID', SC_Util.colorText),
            ('CROC', (80, 0), (40, 16), 'lbl', SC_Util.colorLabel),
            ('', (120, 0), (40, 16), 'crocID', SC_Util.colorText))
        self.TopLabels=SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        self.FlashButtons=SC_Util.FlashButtons(self,
            'Write File to FLASH Memory', 'Reboot FEs (reload FLASH content)')
        self.StatusRegister=SC_Util.StatusRegister(self, 'CROC CH')
        self.DPMPointer=SC_Util.GenericRegister(self, caption='DPM Pointer',
            btnWriteVisible=True, btnWriteCaption='Reset DPM Pointer',
            btnReadVisible=True, btnReadCaption='Read DPM Pointer',
            txtDataVisible=True, txtDataCaption='dpm pointer value', WEnable=False)
        self.MessageRegisters=SC_Util.MessageRegisters(self)        
        sizerALL=wx.BoxSizer(wx.VERTICAL)
        sizerALL.Add(szTop, 0, wx.ALL, 5)
        sizerALL.Add(self.FlashButtons.FlashBoxSizer, 0, wx.ALL, 5)  
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
            self.FlashButtons.controls, self.StatusRegister.controls,
            self.DPMPointer.controls, self.MessageRegisters.controls)


class FE(wx.Panel):
    def __init__(self, parent):
        """Creates the FE tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.btnShowAdvancedGUI=SC_Util.CreateButton(self, "Show Advanced GUI",
            (5,5), (120, 20), 'AdvancedGUI', SC_Util.colorButton)
        TopLabelsData=(('FEB', (0, 0),(40, 16), 'lbl', SC_Util.colorLabel),
            ('', (40, 0), (40, 16), 'febID', SC_Util.colorText),
            ('CH', (80, 0), (40, 16), 'lbl', SC_Util.colorLabel),
            ('', (120, 0), (40, 16), 'chID', SC_Util.colorText),
            ('CROC', (160, 0), (40, 16), 'lbl', SC_Util.colorLabel),
            ('', (200, 0), (40, 16), 'crocID', SC_Util.colorText))
        self.TopLabels = SC_Util.CreateTextCtrls(self, TopLabelsData, offset=(130, 7))
        for txt in self.TopLabels: txt.Enable(False)
        szTop=SC_Util.SizerTop(self.btnShowAdvancedGUI, self.TopLabels)
        #Creates the FE 'devices' Notebook
        self.devices = wx.Notebook(self)
        self.fpga = FPGA(self.devices)
        self.devices.AddPage(self.fpga, "FPGA")
        self.trip = TRIP(self.devices)
        self.devices.AddPage(self.trip, "TRIP")
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
    def SetAddress(self, febNumber, chNumber, crocNumber):
        '''Sets febNumber, chNumber and crocNumber variables and GUI labels'''
        self.febNumber=int(febNumber)
        self.chNumber=int(chNumber)
        self.crocNumber=int(crocNumber)
        self.FindWindowByName('febID').SetValue(febNumber)
        self.FindWindowByName('chID').SetValue(chNumber)
        self.FindWindowByName('crocID').SetValue(crocNumber)
    def ResetControls(self):
        self.fpga.ResetControls()
        self.trip.ResetControls()
    def OnbtnShowAdvancedGUI(self, event):
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
    def ResetControls(self): self.Registers.ResetControls()


class TRIP(wx.Panel):
    def __init__(self, parent):
        """Creates the TRIP tab in the Notebook."""
        wx.Panel.__init__(self, parent)
        self.Registers=SC_Util.TRIPRegisters(self)
        sizerALL=wx.BoxSizer(wx.HORIZONTAL)
        sizerALL.Add(self.Registers.TripBoxSizer, proportion=0, flag=wx.ALL, border=5)  
        self.SetSizer(sizerALL)
        self.Fit()
    def ResetControls(self): self.Registers.ResetControls()


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


if __name__=='__main__':
    app=wx.PySimpleApp()
    frame=SCMainFrame()
    frame.Show()
    app.MainLoop()
