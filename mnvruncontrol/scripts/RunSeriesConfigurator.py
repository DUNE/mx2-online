
import wx
import sys
import RunSeries
import shelve

class MainFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(0, 0), size=(600, 600))

        # Create the menubar
        menuBar = wx.MenuBar()

        # and a menu 
        menu = wx.Menu()

        # add an item to the menu, using \tKeyName automatically
        # creates an accelerator, the third param is some help text
        # that will show up in the statusbar
        menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

        # bind the menu event to an event handler
        self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

        # and put the menu on the menubar
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)

        self.CreateStatusBar()
        

        # Now create the Panel to put the other controls on.
        mainPage = wx.Panel(self)

	runSeriesNameEntryLabel = wx.StaticText(mainPage, -1, "Run Series Name")
	self.runSeriesNameEntry = wx.TextCtrl(mainPage, -1, "RunSeries_1", size=(125, -1))

        runEntryLabel = wx.StaticText(mainPage, -1, "Run")
       	self.runEntry = wx.SpinCtrl(mainPage, -1, '1', size=(125, -1), min=1, max=100000)
        #self.Bind(wx.EVT_SPINCTRL, self.CheckRunNumber, self.runEntry)
        #self.runEntry.Disable()

        subrunEntryLabel = wx.StaticText(mainPage, -1, "Subrun")
        self.subrunEntry = wx.SpinCtrl(mainPage, -1, '1', size=(125, -1), min=1, max=100000)
        self.subrunEntry.Disable()

        detectorEntryLabel = wx.StaticText(mainPage, -1, "Detector")
        self.detectorChoices = ["Unknown", "PMT test stand", "Tracking prototype", "Test beam", "Frozen", "Upstream", "Full MINERvA"]
        self.detectorCodes = ["UN", "FT", "TP", "TB", "MN", "US", "MV"]
        self.detectorEntry = wx.Choice(mainPage, -1, choices=self.detectorChoices)
        self.detectorEntry.SetSelection(5)

        runTypeEntryLabel = wx.StaticText(mainPage, -1, "Run Mode")
        self.runTypeChoices = ["Pedestal", "Light injection", "Charge injection", "Cosmics", "NuMI beam", "Mixed beam/pedestal", "Mixed beam/light injection", "Unknown trigger"]
        self.runTypeCodes = ["pdstl", "linjc", "chinj", "cosmc", "numib", "numip", "numil", "unkwn"]
        self.runTypeEntry =  wx.Choice(mainPage, -1, choices=self.runTypeChoices)

        detConfigEntryLabel = wx.StaticText(mainPage, -1, "Det. Config")
        self.detConfigEntry = wx.SpinCtrl(mainPage, -1, '0', size=(125, -1), min=0, max=10)

        runLengthEntryLabel = wx.StaticText(mainPage, -1, "Run Length (s)")
        self.runLengthEntry = wx.SpinCtrl(mainPage, -1, '0', size=(125, -1), min=0, max=100000)

        gatesEntryLabel = wx.StaticText(mainPage, -1, "Gates")
        self.gatesEntry = wx.SpinCtrl(mainPage, -1, "10", size=(125, -1), min=1, max=10000)

	hwInitLevelEntryLabel = wx.StaticText(mainPage, -1, "HW Init. Level")
	self.hwInitLevelChoices = ["FullHWInit","NoHWInit"]
	self.hwInitLevelEntry = wx.Choice(mainPage, -1, choices = self.hwInitLevelChoices)

        operatingModeEntryLabel = wx.StaticText(mainPage, -1, "Operating Mode")
        self.operatingModeChoices = ["OneShot","Cosmic","MixedModePedLI","MTM","MixedModeMTMLI","MixedModePedMTM"]
        self.operatingModeEntry = wx.Choice(mainPage, -1, choices = self.operatingModeChoices)

	liLevelEntryLabel = wx.StaticText(mainPage, -1, "LI Level")
        self.liLevelChoices = ["ZeroPE","OnePE","MaxPE"]
        self.liLevelEntry = wx.Choice(mainPage, -1, choices = self.liLevelEntry)

	liPulseHeightEntryLabel = wx.StaticText(mainPage, -1, "LI Pulse Height")
	self.liPulseHeightEntry = wx.TextCtrl(mainPage, -1, "4.05", size=(125, -1))

        liEventPeriodEntryLabel = wx.StaticText(mainPage, -1, "LI Event Period")
        self.liEventPeriodEntry = wx.SpinCtrl(mainPage, -1, "1", size=(125, -1), min=1, max=10000)

        febsEntryLabel = wx.StaticText(mainPage, -1, "FEBs")
        self.febsEntry = wx.SpinCtrl(mainPage, -1, "1", size=(125, -1), min=1, max=10000)

        b_createNewRunSeries = wx.Button(panel, -1, "Create New Run Series")
        self.Bind(wx.EVT_BUTTON, self.CreateNewRunSeries, b_createNewRunSeries)

	b_addRunToSeries = wx.Button(panel, -1, "Add Run To Series")
        self.Bind(wx.EVT_BUTTON, self.AddToRunSeries, b_addRunToSeries)

	b_writeRunSeries = wx.Button(panel, -1, "Write Run Series")
        self.Bind(wx.EVT_BUTTON, self.WriteRunSeries, b_addRunToSeries)

        space = 6
        #bsizer = wx.BoxSizer(wx.VERTICAL)
        #bsizer.Add(b, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b2, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b3, 0, wx.GROW|wx.ALL, space)

        sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
        sizer.AddMany([runSeriesNameEntryLabel,self.runSeriesNameEntry,
		       runEntryLabel,self.runEntry,
                       subrunEntryLabel,self.subrunEntry,
		       detectorEntryLabel,self.detectorEntry,
		       runTypeEntryLabel,self.runTypeEntry,
		       detConfigEntryLabel,self.detConfigEntry,
		       runLengthEntryLabel,self.runLengthEntry,
                       gatesEntryLabel,self.gatesEntry,
		       hwInitLevelEntryLabel,self.hwInitLevelEntry,
		       operatingModeEntryLabel,self.operatingModeEntry,
		       liLevelEntryLabel,self.liLevelEntry,
		       liPulseHeightEntryLabel,self.liPulseHeightEntry,
		       liEventPeriodEntryLabel,self.liEventPeriodEntry,
		       febsEntryLabel,self.febsEntry,
		       b, (0,0)])
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        panel.SetSizer(border)
        panel.SetAutoLayout(True)


    def OnTimeToClose(self, evt):
        self.Close()

    def CreateNewRunSeries(self,evt):
	self.runSeries = RunSeries.RunSeries()
	self.runEntry.SetValue(1)
        self.subrunEntry.SetValue(1)

    def AddToRunSeries(self,evt):
	run = RunSeries.RunInfo(detector          = self.detectorEntry.GetStringSelection(),
				sequenceNumber    = 0,
				runType           = self.runTypeEntry.GetStringSelection(),
				runNumber         = self.runEntry.GetValue(),
				subRunNumber      = self.subrunEntry.GetValue(),
				daqConfigFile     = 'daqConfig', # No reasonable default? -> SlowControl xml
				liConfigFile      = 'liConfig', # No reasonable default? -> LI Box config
				runTimeLength     = self.runLengthEntry.GetValue(), # seconds
				numberOfEvents    = self.gatesEntry.GetValue(), # events
				fileBase          = 'Run0',
				hwInitLevel       = self.hwInitLevelEntry.GetStringSelection(),
				operatingMode     = self.operatingModeEntry.GetStringSelection(), # default mode right now is oneShot
				version           = 1,
				liLevel           = self.liLevelEntry.GetStringSelection(),
				liEnabled         = False,
				detectorConfig    = self.detConfigEntry.GetValue(),
				pulserEventPeriod = self.liEventPeriodEntry.GetValue(),
				pulserHeight      = self.liPulseHeightEntry.GetValue(),
				ledtoprow         = 1,
				ledbotrow         = 0,
				crocList          = 0)

	self.runSeries.AppendToRunList(run)
        self.subrunEntry.SetValue(self.subrunEntry.GetValue()+1)

    def WriteRunSeries(self,evt):
	d = shelve.open('run_series_test.db', 'c')
	d[self.runSeriesNameEntry.GetValue()] = self.runSeries
	d.close()

class MainApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, "Run Series Configurator")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MainApp(redirect=True)
app.MainLoop()

