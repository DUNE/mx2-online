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

        self.b_createNewSeries = wx.Button(self.mainPage, -1, "Create New Series")
        self.Bind(wx.EVT_BUTTON, self.CreateNewSeries, self.b_createNewSeries)

        self.b_writeRunSeries = wx.Button(self.mainPage, -1, "Write Series")
        self.Bind(wx.EVT_BUTTON, self.WriteRunSeries, self.b_writeRunSeries)

        self.b_openRunSeries = wx.Button(self.mainPage, -1, "Open Series")
        self.Bind(wx.EVT_BUTTON, self.OpenRunSeries, self.b_openRunSeries)

	self.b_showRunSeries = wx.Button(self.mainPage, -1, "Show Run Series")
        self.Bind(wx.EVT_BUTTON, self.ShowRunSeries, self.b_showRunSeries)

        self.b_appendRunToSeries = wx.Button(self.mainPage, -1, "Append Run To Series")
        self.Bind(wx.EVT_BUTTON, self.AppendRunToSeries, self.b_appendRunToSeries)

	self.b_updateRun = wx.Button(self.mainPage, -1, "Update Run")
        self.Bind(wx.EVT_BUTTON, self.UpdateRun, self.b_updateRun)
	self.b_updateRun.Disable()	

        self.b_editSelectedRun = wx.Button(self.mainPage, -1, "Edit Selected Run")
        self.Bind(wx.EVT_BUTTON, self.EditSelectedRun, self.b_editSelectedRun)

        self.b_deleteSelectedRun = wx.Button(self.mainPage, -1, "Delete Selected Run")
        self.Bind(wx.EVT_BUTTON, self.DeleteSelectedRun, self.b_deleteSelectedRun)
	self.b_deleteSelectedRun.Disable()

        seriesGridSizer = wx.GridSizer(2, 2, 10, 10)
       	seriesGridSizer.AddMany([       (runSeriesNameLabel, 0, wx.ALIGN_CENTER_VERTICAL),       (self.runSeriesNameEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
        				(self.b_createNewSeries, 0, wx.ALIGN_CENTER_VERTICAL),         (0,0),
                               		(self.b_openRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),          (0,0),
                                        (self.b_writeRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),          (0,0),
                               		(self.b_showRunSeries, 0, wx.ALIGN_CENTER_VERTICAL),      	 (0,0) ])
	seriesBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run Series"), wx.VERTICAL)
        seriesBoxSizer.Add(seriesGridSizer, flag=wx.EXPAND)

        runGridSizer = wx.GridSizer(2, 2, 10, 10)
        runGridSizer.AddMany([          (runModeLabel, 0, wx.ALIGN_CENTER_VERTICAL),             (self.runModeEntry, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
					(gatesLabel, 0, wx.ALIGN_CENTER_VERTICAL),		 (self.gatesEntry, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
                                        (ledLevelLabel, 0, wx.ALIGN_CENTER_VERTICAL),            (self.ledLevelEntry, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),  
                                        (ledGroupLabel, 0, wx.ALIGN_CENTER_VERTICAL),          	 (self.ledGroupEntry, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL),
                                        (self.b_appendRunToSeries, 0, wx.ALIGN_CENTER_VERTICAL), (self.b_updateRun, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL) ])
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

        runSelectGridSizer = wx.GridSizer(cols=2, vgap=10, hgap=10)
        runSelectGridSizer.AddMany([ (self.b_editSelectedRun, 0, wx.ALIGN_RIGHT), (self.b_deleteSelectedRun, 0, wx.ALIGN_LEFT) ])

    	runListBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run List"), orient=wx.VERTICAL)
	runListBoxSizer.Add(self.runList, 1, flag=wx.EXPAND)
	runListBoxSizer.Add(runSelectGridSizer, flag=wx.EXPAND)

	globalSizer = wx.BoxSizer(wx.VERTICAL)
	globalSizer.Add(configureSizer, flag=wx.EXPAND)
	globalSizer.Add(runListBoxSizer, 1, flag=wx.EXPAND)

 	self.mainPage.SetSizer(globalSizer)
        self.mainPage.SetAutoLayout(True)

	# Run Series Instance
	self.runSeries = RunSeries.RunSeries()

	# Run Info Instance
	#self.runSeries = RunSeries.RunInfo()

    def OnTimeToClose(self, evt):
        self.Close()

    def CreateNewSeries(self,evt):
        self.runSeries.ClearRunList()

    def OpenRunSeries(self,evt):
	pass

    def WriteRunSeries(self,evt):
        d = shelve.open(str(self.runSeriesNameEntry.GetValue())+".db", 'c')
        d['series'] = self.runSeries
        d.close()

    def ShowRunSeries(self,evt):
	print str(self.runSeriesNameEntry.GetValue())+":\n"
	print self.runSeries.Show()

    def AppendRunToSeries(self,evt):
        run = RunSeries.RunInfo(gates      = self.gatesEntry.GetValue(),
                                runMode    = MetaData.RunningModes[self.runModeEntry.GetStringSelection(),MetaData.HASH],
                                ledLevel   = MetaData.LILevels[self.ledLevelEntry.GetStringSelection(),MetaData.HASH],
                                ledGroup   = MetaData.LEDGroups[self.ledGroupEntry.GetStringSelection(),MetaData.HASH])

        self.runSeries.AppendToRunList(run)

        num_items = self.runList.GetItemCount()
        self.runList.InsertStringItem(num_items, str(num_items))
        self.runList.SetStringItem(num_items, 1, self.runModeEntry.GetStringSelection())
        self.runList.SetStringItem(num_items, 2, str(self.gatesEntry.GetValue()))
        self.runList.SetStringItem(num_items, 3, self.ledLevelEntry.GetStringSelection())
        self.runList.SetStringItem(num_items, 4, self.ledGroupEntry.GetStringSelection())

    def UpdateRun(self,evt):

        run = RunSeries.RunInfo(gates      = self.gatesEntry.GetValue(),
                                runMode    = MetaData.RunningModes[self.runModeEntry.GetStringSelection(),MetaData.HASH],
                                ledLevel   = MetaData.LILevels[self.ledLevelEntry.GetStringSelection(),MetaData.HASH],
                                ledGroup   = MetaData.LEDGroups[self.ledGroupEntry.GetStringSelection(),MetaData.HASH])

        index = self.runList.GetFirstSelected()
	self.runSeries.SetRun(index,run)

        self.runList.SetStringItem(index, 1, self.runModeEntry.GetStringSelection())
        self.runList.SetStringItem(index, 2, str(self.gatesEntry.GetValue()))
        self.runList.SetStringItem(index, 3, self.ledLevelEntry.GetStringSelection())
        self.runList.SetStringItem(index, 4, self.ledGroupEntry.GetStringSelection())
	
	self.runList.Enable()
	self.b_editSelectedRun.Enable()
        #self.b_deleteSelectedRun.Enable()
        self.b_appendRunToSeries.Enable()
        self.b_updateRun.Disable()

    def EditSelectedRun(self,evt):
	
	self.runList.Disable()
	self.b_editSelectedRun.Disable()
	#self.b_deleteSelectedRun.Disable()
	self.b_appendRunToSeries.Disable()

	index = self.runList.GetFirstSelected()
	run = self.runSeries.GetRun(index)

        self.gatesEntry.SetValue(run.gates)
	self.runModeEntry.SetSelection(self.runModeEntry.FindString(MetaData.RunningModes[run.runMode,MetaData.DESCRIPTION]))
	self.ledLevelEntry.SetSelection(self.ledLevelEntry.FindString(MetaData.LILevels[run.ledLevel,MetaData.DESCRIPTION]))
	self.ledGroupEntry.SetSelection(self.ledGroupEntry.FindString(MetaData.LEDGroups[run.ledGroup,MetaData.DESCRIPTION]))

	self.b_updateRun.Enable()

    def DeleteSelectedRun(self,evt):
        pass

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Run Series Configurator")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

