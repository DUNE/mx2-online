import wx
import sys
import RunSeries
import shelve

import MetaData

class MyFrame(wx.Frame):
    """
    This is MyFrame.  It just shows a few controls on a wxPanel,
    and has a simple menu.
    """
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title,
                          pos=(0, 0), size=(800, 600))

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
        self.mainPage = wx.Panel(self)

        runSeriesNameLabel = wx.StaticText(self.mainPage, -1, "Run Series Name")
        self.runSeriesNameEntry = wx.TextCtrl(self.mainPage, -1, "Enter Run Series Name", size=(200, -1))

        runModeLabel = wx.StaticText(self.mainPage, -1, "Run Mode")
        self.runModeEntry = wx.Choice(self.mainPage, -1, choices=MetaData.RunningModes.descriptions)

	gatesLabel = wx.StaticText(self.mainPage, -1, "Gates")
        self.gatesEntry = wx.SpinCtrl(self.mainPage, -1, "0", size=(125, -1), min=0, max=10000)

	ledLevelLabel = wx.StaticText(self.mainPage, -1, "LED Level")
        self.ledLevelEntry = wx.Choice(self.mainPage, -1, choices=MetaData.LILevels.descriptions)

        ledGroupLabel = wx.StaticText(self.mainPage, -1, "LED Group")
        self.ledGroupEntry = wx.Choice(self.mainPage, -1, choices=MetaData.LEDGroups.descriptions)

        b_clearRunSeries = wx.Button(self.mainPage, -1, "Clear Run Series")
        self.Bind(wx.EVT_BUTTON, self.ClearRunSeries, b_clearRunSeries)

        b_appendRunToSeries = wx.Button(self.mainPage, -1, "Append Run To Series")
        self.Bind(wx.EVT_BUTTON, self.AppendRunToSeries, b_appendRunToSeries)

        b_writeRunSeries = wx.Button(self.mainPage, -1, "Write Run Series")
        self.Bind(wx.EVT_BUTTON, self.WriteRunSeries, b_writeRunSeries)

	b_showRunSeries = wx.Button(self.mainPage, -1, "Show Run Series")
        self.Bind(wx.EVT_BUTTON, self.ShowRunSeries, b_showRunSeries)

        seriesGridSizer = wx.GridSizer(2, 2, 10, 10)
       	seriesGridSizer.AddMany([       (runSeriesNameLabel, 0, wx.ALIGN_CENTER_VERTICAL),       (self.runSeriesNameEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
        				(b_writeRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),         (0,0),
                               		(b_showRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),          (0,0),
                               		(b_clearRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),      	 (0,0) ])
	seriesBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run Series"), wx.VERTICAL)
        seriesBoxSizer.Add(seriesGridSizer, flag=wx.EXPAND)

        runGridSizer = wx.GridSizer(2, 2, 10, 10)
        runGridSizer.AddMany([          (runModeLabel, 0, wx.ALIGN_CENTER_VERTICAL),             (self.runModeEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
					(gatesLabel, 0, wx.ALIGN_CENTER_VERTICAL),		 (self.gatesEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
                                        (ledLevelLabel, 0, wx.ALIGN_CENTER_VERTICAL),            (self.ledLevelEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),  
                                        (ledGroupLabel, 0, wx.ALIGN_CENTER_VERTICAL),          	 (self.ledGroupEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
                                        (b_appendRunToSeries, 0, wx.ALIGN_CENTER_VERTICAL),         (0,0) ])
        runBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run"), wx.VERTICAL)
        runBoxSizer.Add(runGridSizer, flag=wx.EXPAND)

        configureSizer = wx.BoxSizer(wx.HORIZONTAL)
        configureSizer.Add(seriesBoxSizer, proportion=1, flag=wx.EXPAND)
        configureSizer.Add(runBoxSizer, proportion=1, flag=wx.EXPAND)

	self.runList = wx.ListCtrl(self.mainPage, -1, style=wx.LC_REPORT | wx.LC_VRULES)
	self.runList.InsertColumn(0, "Sequence No.", wx.EXPAND)
      	self.runList.InsertColumn(1, "Run Mode")
       	self.runList.InsertColumn(2, "Gates")
     	self.runList.InsertColumn(3, "LED Level")
      	self.runList.InsertColumn(4, "LED Group")

	#runList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        #runList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        #runList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        #runList.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        #runList.SetColumnWidth(4, wx.LIST_AUTOSIZE)

    	runListBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run List"), orient=wx.VERTICAL)
	runListBoxSizer.Add(self.runList, flag=wx.EXPAND)

	globalSizer = wx.BoxSizer(wx.VERTICAL)
	globalSizer.Add(configureSizer, flag=wx.EXPAND)
	globalSizer.Add(runListBoxSizer, flag=wx.EXPAND)

 	self.mainPage.SetSizer(globalSizer)
        self.mainPage.SetAutoLayout(True)
		

	# Run Series Instance
	self.runSeries = RunSeries.RunSeries()

    def OnTimeToClose(self, evt):
        self.Close()

    def ClearRunSeries(self,evt):
        self.runSeries.ClearRunList()

    def AppendRunToSeries(self,evt):
        run = RunSeries.RunInfo(gates      = self.gatesEntry.GetValue(),
                        	runMode    = self.runModeEntry.GetStringSelection(),
                                ledLevel   = self.ledLevelEntry.GetStringSelection(),
                                ledGroup   = self.ledGroupEntry.GetStringSelection())

        self.runSeries.AppendToRunList(run)

	num_items = self.runList.GetItemCount()
 	self.runList.InsertStringItem(num_items, str(num_items))
        self.runList.SetStringItem(num_items, 1, run.runMode)
  	self.runList.SetStringItem(num_items, 2, str(run.gates))
        self.runList.SetStringItem(num_items, 3, run.ledLevel)
        self.runList.SetStringItem(num_items, 4, run.ledGroup)

    def WriteRunSeries(self,evt):
        d = shelve.open(str(self.runSeriesNameEntry.GetValue())+".db", 'c')
        d['series'] = self.runSeries
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

