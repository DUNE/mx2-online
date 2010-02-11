import wx
import sys
import RunSeries
import shelve

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(0, 0), size=(600, 800))

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

        subrunEntryLabel = wx.StaticText(mainPage, -1, "Subrun")
        self.subrunEntry = wx.SpinCtrl(mainPage, -1, '1', size=(125, -1), min=1, max=100000)
        self.subrunEntry.Disable()

        gatesEntryLabel = wx.StaticText(mainPage, -1, "Gates")
        self.gatesEntry = wx.SpinCtrl(mainPage, -1, "0", size=(125, -1), min=0, max=10000)

        runLengthEntryLabel = wx.StaticText(mainPage, -1, "Run Length (s)")
        self.runLengthEntry = wx.SpinCtrl(mainPage, -1, '0', size=(125, -1), min=0, max=100000)

        runModeEntryLabel = wx.StaticText(mainPage, -1, "Run Mode")
        self.runModeChoices = ["Null","OneShot","NumiBeam","Cosmics","PureLightInjection","MixedBeamPedestal","MixedBeamLightInjection"]
        self.runModeEntry = wx.Choice(mainPage, -1, choices = self.runModeChoices)

        detectorEntryLabel = wx.StaticText(mainPage, -1, "Detector")
        self.detectorChoices = ["Null","PMTTestStand","TrackingPrototype","TestBeam","FrozenDetector","UpstreamDetector","FullMinerva","DTReserved7","DTReserved8"]
        self.detectorEntry = wx.Choice(mainPage, -1, choices=self.detectorChoices)

        configFileLabel = wx.StaticText(mainPage, -1, "Config. File")
        self.configFileEntry = wx.TextCtrl(mainPage, -1, "", size=(125, -1))
	
        febsEntryLabel = wx.StaticText(mainPage, -1, "FEBs")
        self.febsEntry = wx.SpinCtrl(mainPage, -1, "1", size=(125, -1), min=1, max=10000)

	ledLevelLabel = wx.StaticText(mainPage, -1, "LED Level")
        self.ledLevelChoices = ["Off","ZeroPE","OnePE","MaxPE"]
        self.ledLevelEntry = wx.Choice(mainPage, -1, choices=self.ledLevelChoices)

        ledGroupLabel = wx.StaticText(mainPage, -1, "LED Group")
        self.ledGroupChoices = ["None","LEDALL","LEDA","LEDB","LEDC","LEDD","LEDE","LEDF","LEDG","LEDI","LEDJ","LEDK","LEDL","LEDM","LEDN","LEDO","LEDQ","LEDR","LEDS","LEDT","LEDU","LEDV"]
        self.ledGroupEntry = wx.Choice(mainPage, -1, choices=self.ledGroupChoices)

        b_clearRunSeries = wx.Button(mainPage, -1, "Clear Run Series")
        self.Bind(wx.EVT_BUTTON, self.ClearRunSeries, b_clearRunSeries)

        b_addRunToSeries = wx.Button(mainPage, -1, "Add Run To Series")
        self.Bind(wx.EVT_BUTTON, self.AddToRunSeries, b_addRunToSeries)

        b_writeRunSeries = wx.Button(mainPage, -1, "Write Run Series")
        self.Bind(wx.EVT_BUTTON, self.WriteRunSeries, b_writeRunSeries)

	b_showRunSeries = wx.Button(mainPage, -1, "Show Run Series")
        self.Bind(wx.EVT_BUTTON, self.ShowRunSeries, b_showRunSeries)

        space = 6
        #bsizer = wx.BoxSizer(wx.VERTICAL)
        #bsizer.Add(b, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b2, 0, wx.GROW|wx.ALL, space)
        #bsizer.Add(b3, 0, wx.GROW|wx.ALL, space)

        sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
        sizer.AddMany([ runSeriesNameEntryLabel,self.runSeriesNameEntry,
			runEntryLabel,self.runEntry,
                        subrunEntryLabel,self.subrunEntry,
                        gatesEntryLabel,self.gatesEntry,
                        runLengthEntryLabel,self.runLengthEntry,
                        runModeEntryLabel,self.runModeEntry,
			detectorEntryLabel,self.detectorEntry,
			configFileLabel,self.configFileEntry,
			febsEntryLabel,self.febsEntry,
			ledLevelLabel,self.ledLevelEntry,
			ledGroupLabel,self.ledGroupEntry,
                        b_addRunToSeries, (0,0),
			b_writeRunSeries, (0,0),
			b_showRunSeries, (0,0),
                        b_clearRunSeries, (0,0),
                        ])
        border = wx.BoxSizer(wx.VERTICAL)
        border.Add(sizer, 0, wx.ALL, 25)
        mainPage.SetSizer(border)
        mainPage.SetAutoLayout(True)

	# Run Series Instance
	self.runSeries = RunSeries.RunSeries()

    def OnTimeToClose(self, evt):
        self.Close()

    def ClearRunSeries(self,evt):
        self.runSeries.ClearRunList()
        self.runEntry.SetValue(1)
        self.subrunEntry.SetValue(1)

    
    def AddToRunSeries(self,evt):
        run = RunSeries.RunInfo(run        = self.runEntry.GetValue(),
                        	subrun     = self.subrunEntry.GetValue(),
                        	gates      = self.gatesEntry.GetValue(),
                        	runLength  = self.runLengthEntry.GetValue(),
                        	runMode    = self.runModeEntry.GetStringSelection(),
                        	detector   = self.detectorEntry.GetStringSelection(),
                                configFile = self.configFileEntry.GetValue(),
                                febs       = self.febsEntry.GetValue(),
                                ledLevel   = self.ledLevelEntry.GetStringSelection(),
                                ledGroup   = self.ledGroupEntry.GetStringSelection())

        self.runSeries.AppendToRunList(run)
        self.subrunEntry.SetValue(self.subrunEntry.GetValue()+1)

    def WriteRunSeries(self,evt):
        d = shelve.open('run_series_test.db', 'c')
        d[str(self.runSeriesNameEntry.GetValue())] = self.runSeries
        d.close()

    def ShowRunSeries(self,evt):
	print str(self.runSeriesNameEntry.GetValue())+":\n"
	print self.runSeries.Show()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Run Series Configurator")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

