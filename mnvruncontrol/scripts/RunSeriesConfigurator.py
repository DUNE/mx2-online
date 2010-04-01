import wx
import sys
import os
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
        self.mainPage = wx.Panel(self)

        #runSeriesNameLabel = wx.StaticText(self.mainPage, -1, "Run Series Name")
        #self.runSeriesNameEntry = wx.TextCtrl(self.mainPage, -1, "Enter Run Series Name", size=(200, -1))

        runModeLabel = wx.StaticText(self.mainPage, -1, "Run Mode")
        self.runModeEntry = wx.Choice(self.mainPage, -1, choices=MetaData.RunningModes.descriptions)

	gatesLabel = wx.StaticText(self.mainPage, -1, "Gates")
        self.gatesEntry = wx.SpinCtrl(self.mainPage, -1, "0", size=(125, -1), min=0, max=10000)

	ledLevelLabel = wx.StaticText(self.mainPage, -1, "LED Level")
        self.ledLevelEntry = wx.Choice(self.mainPage, -1, choices=MetaData.LILevels.descriptions)

        ledGroupLabel = wx.StaticText(self.mainPage, -1, "LED Group")
        self.ledGroupEntry = wx.Choice(self.mainPage, -1, choices=MetaData.LEDGroups.descriptions)

        self.b_clearRunSeries = wx.Button(self.mainPage, -1, "Clear Series")
        self.Bind(wx.EVT_BUTTON, self.ClearRunSeries, self.b_clearRunSeries)

        self.b_writeRunSeries = wx.Button(self.mainPage, -1, "Write Series")
        self.Bind(wx.EVT_BUTTON, self.WriteRunSeries, self.b_writeRunSeries)

        self.b_openRunSeries = wx.Button(self.mainPage, -1, "Open Series")
        self.Bind(wx.EVT_BUTTON, self.OpenRunSeries, self.b_openRunSeries)

	self.b_showRunSeries = wx.Button(self.mainPage, -1, "Print Series")
        self.Bind(wx.EVT_BUTTON, self.ShowRunSeries, self.b_showRunSeries)

        self.b_appendRunToSeries = wx.Button(self.mainPage, -1, "Append Run")
        self.Bind(wx.EVT_BUTTON, self.AppendRunToSeries, self.b_appendRunToSeries)

	self.b_updateRun = wx.Button(self.mainPage, -1, "Update Run")
        self.Bind(wx.EVT_BUTTON, self.UpdateRun, self.b_updateRun)
	self.b_updateRun.Disable()	

	self.b_insertRun = wx.Button(self.mainPage, -1, "Insert Run")
	self.Bind(wx.EVT_BUTTON, self.InsertRun, self.b_insertRun)
        self.b_insertRun.Disable()

        self.b_editSelectedRun = wx.Button(self.mainPage, -1, "Edit Selected Run")
        self.Bind(wx.EVT_BUTTON, self.EditSelectedRun, self.b_editSelectedRun)
	self.b_editSelectedRun.Disable()
	
        self.b_deleteSelectedRun = wx.Button(self.mainPage, -1, "Delete Selected Run")
        self.Bind(wx.EVT_BUTTON, self.DeleteSelectedRun, self.b_deleteSelectedRun)
	self.b_deleteSelectedRun.Disable()

        self.runList = wx.ListCtrl(self.mainPage, -1, style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_SINGLE_SEL)
        self.runList.InsertColumn(0, "Seq. No.", wx.LIST_FORMAT_CENTER)
        self.runList.InsertColumn(1, "Run Mode", wx.LIST_FORMAT_CENTER)
        self.runList.InsertColumn(2, "Gates", wx.LIST_FORMAT_CENTER)
        self.runList.InsertColumn(3, "LED Level", wx.LIST_FORMAT_CENTER)
        self.runList.InsertColumn(4, "LED Group", wx.LIST_FORMAT_CENTER)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.runList)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.DisableEditDeleteInsert, self.runList)
        self.Bind(wx.EVT_LIST_DELETE_ITEM, self.DisableEditDeleteInsert, self.runList)
        self.Bind(wx.EVT_LIST_DELETE_ALL_ITEMS, self.DisableEditDeleteInsert, self.runList)

        self.runList.SetColumnWidth(0, 75)
        self.runList.SetColumnWidth(1, 200)
        self.runList.SetColumnWidth(2, 75)
        self.runList.SetColumnWidth(3, 100)
        self.runList.SetColumnWidth(4, 100)

        seriesButtonSizer = wx.GridSizer(4, 1, 10, 10)
        seriesButtonSizer.AddMany([     (self.b_openRunSeries, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),
                                        (self.b_writeRunSeries, 0,  wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),
                                        (self.b_clearRunSeries, 0,  wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),
                                        (self.b_showRunSeries, 0,  wx.EXPAND | wx.ALIGN_CENTER_VERTICAL) ])

	seriesBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run Series"), wx.VERTICAL)
        seriesBoxSizer.Add(seriesButtonSizer, 1, flag=wx.EXPAND)

        runParameterSizer = wx.GridSizer(2, 2, 10, 10)
        runParameterSizer.AddMany([     (runModeLabel, 0, wx.ALIGN_CENTER_VERTICAL),             (self.runModeEntry, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),
					(gatesLabel, 0, wx.ALIGN_CENTER_VERTICAL),		 (self.gatesEntry, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),
                                        (ledLevelLabel, 0, wx.ALIGN_CENTER_VERTICAL),            (self.ledLevelEntry, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL),  
                                        (ledGroupLabel, 0, wx.ALIGN_CENTER_VERTICAL),          	 (self.ledGroupEntry, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL) ])

	runButtonSizer = wx.GridSizer(1, 3, 10, 10)
	runButtonSizer.AddMany([(self.b_appendRunToSeries, 1,  wx.EXPAND), (self.b_updateRun, 1, wx.EXPAND), (self.b_insertRun, 1, wx.EXPAND)])

        runBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run"), wx.VERTICAL)
	runBoxSizer.Add(runParameterSizer, 1, flag=wx.EXPAND)
	runBoxSizer.Add(runButtonSizer, flag=wx.EXPAND)
	runBoxSizer.InsertSpacer(1,10)

        configureSizer = wx.BoxSizer(wx.HORIZONTAL)
        configureSizer.Add(seriesBoxSizer, proportion=1, flag=wx.EXPAND)
        configureSizer.Add(runBoxSizer, proportion=2, flag=wx.EXPAND)

        runSelectGridSizer = wx.GridSizer(cols=2, vgap=10, hgap=10)
        runSelectGridSizer.AddMany([ (self.b_editSelectedRun, 1, wx.EXPAND | wx.ALIGN_CENTER), (self.b_deleteSelectedRun, 1, wx.EXPAND | wx.ALIGN_CENTER) ])

    	runListBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run List"), orient=wx.VERTICAL)
	runListBoxSizer.Add(self.runList, 1, flag=wx.EXPAND)
	runListBoxSizer.Add(runSelectGridSizer, flag=wx.EXPAND)
	runListBoxSizer.InsertSpacer(1,10)

	globalSizer = wx.BoxSizer(wx.VERTICAL)
	globalSizer.Add(configureSizer, flag=wx.EXPAND)
	globalSizer.Add(runListBoxSizer, 1, flag=wx.EXPAND)

 	self.mainPage.SetSizer(globalSizer)
        self.mainPage.SetAutoLayout(True)

	# Run Series Instance
	self.runSeries = RunSeries.RunSeries()

    def OnTimeToClose(self, evt):
        self.Close()

    def OpenRunSeries(self,evt):
        dlg = wx.FileDialog(    self,
                                message="Open Run Series",
                                defaultDir=os.getcwd(),
                                defaultFile="",
                                wildcard="*.db",
                                style=wx.OPEN | wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:

                path = dlg.GetPaths()

                try:
		        d = shelve.open(path[0], 'r')
			self.runSeries = d['series']
			self.UpdateRunList()
                except:
                        message  = "Could not retrieve run series from "+path[0]+"\n"
			message += "Possible reasons are:\n"
			message += "1) The selected file is not a python database\n"
			message += "2) The database does not contain the key \"series\"\n"
			message += "3) The keyed value is not a RunSeries object\n"
			print message

        dlg.Destroy()

    def WriteRunSeries(self,evt):

        dlg = wx.FileDialog(    self, 
				message="Save Run Series as ...",
				defaultDir=os.getcwd(), 
				defaultFile="",
				wildcard="*.db",
				style=wx.SAVE)

	if dlg.ShowModal() == wx.ID_OK:
		
		path = dlg.GetPath()
		d = shelve.open(path+".db", 'c')
		d['series'] = self.runSeries
		d.close()
		
	dlg.Destroy()
	
    def ShowRunSeries(self,evt):

        print "Printing contents of RunSeries container"+":\n"
        print self.runSeries.Show()

    def ClearRunSeries(self,evt):
        
	self.runSeries.ClearRunList()
	self.runList.DeleteAllItems()

    def AppendRunToSeries(self,evt):

        run = self.GetRunFromGUI()
        self.runSeries.AppendRun(run)
        num_items = self.runList.GetItemCount()
        self.AppendRunToList(num_items,run)

    def UpdateRun(self,evt):

        run = self.GetRunFromGUI()
        index = self.runList.GetFirstSelected()
        self.runSeries.SetRun(index,run)

        self.runList.SetStringItem(index, 1, self.runModeEntry.GetStringSelection())
        self.runList.SetStringItem(index, 2, str(self.gatesEntry.GetValue()))
        self.runList.SetStringItem(index, 3, self.ledLevelEntry.GetStringSelection())
        self.runList.SetStringItem(index, 4, self.ledGroupEntry.GetStringSelection())

	self.b_openRunSeries.Enable()
	self.b_writeRunSeries.Enable()
        self.b_clearRunSeries.Enable()
        self.runList.Enable()
        self.b_editSelectedRun.Enable()
        self.b_deleteSelectedRun.Enable()
        self.b_appendRunToSeries.Enable()
	self.b_insertRun.Enable()
        self.b_updateRun.Disable()

    def InsertRun(self,evt):

	run = self.GetRunFromGUI()
        index = self.runList.GetFirstSelected()
	self.runSeries.Runs.insert(index,run)
	self.UpdateRunList()

    def EditSelectedRun(self,evt):

        self.b_openRunSeries.Disable()
        self.b_writeRunSeries.Disable()
        self.b_clearRunSeries.Disable()
        self.runList.Disable()
        self.b_editSelectedRun.Disable()
        self.b_deleteSelectedRun.Disable()
        self.b_appendRunToSeries.Disable()
	self.b_insertRun.Disable()

        index = self.runList.GetFirstSelected()
        run = self.runSeries.GetRun(index)
        self.UpdateGUIFromRun(run)

        self.b_updateRun.Enable()

    def DeleteSelectedRun(self,evt):
        
	index = self.runList.GetFirstSelected()
	del self.runSeries.Runs[index]
	self.UpdateRunList()

    def OnItemSelected(self,evt):

	self.b_editSelectedRun.Enable()
        self.b_deleteSelectedRun.Enable()
	self.b_insertRun.Enable()	

    def DisableEditDeleteInsert(self,evt):

        self.b_editSelectedRun.Disable()
        self.b_deleteSelectedRun.Disable()
	self.b_insertRun.Disable()

    def UpdateRunList(self):
	
	self.runList.DeleteAllItems() 
	for run in self.runSeries.Runs:
	        num_items = self.runList.GetItemCount()
		self.AppendRunToList(num_items,run)

    def AppendRunToList(self,index,run):

	self.runList.InsertStringItem(index, str(index))
	self.runList.SetStringItem(index, 1, MetaData.RunningModes[run.runMode,MetaData.DESCRIPTION])
	self.runList.SetStringItem(index, 2, str(run.gates))
	self.runList.SetStringItem(index, 3, MetaData.LILevels[run.ledLevel,MetaData.DESCRIPTION])
	self.runList.SetStringItem(index, 4, MetaData.LEDGroups[run.ledGroup,MetaData.DESCRIPTION])

    def GetRunFromGUI(self):

        return RunSeries.RunInfo(       gates      = self.gatesEntry.GetValue(),
					runMode    = MetaData.RunningModes[self.runModeEntry.GetStringSelection(),MetaData.HASH],
                                	ledLevel   = MetaData.LILevels[self.ledLevelEntry.GetStringSelection(),MetaData.HASH],
                                	ledGroup   = MetaData.LEDGroups[self.ledGroupEntry.GetStringSelection(),MetaData.HASH])

    def UpdateGUIFromRun(self,run):

        self.gatesEntry.SetValue(run.gates)
        self.runModeEntry.SetSelection(self.runModeEntry.FindString(MetaData.RunningModes[run.runMode,MetaData.DESCRIPTION]))
        self.ledLevelEntry.SetSelection(self.ledLevelEntry.FindString(MetaData.LILevels[run.ledLevel,MetaData.DESCRIPTION]))
        self.ledGroupEntry.SetSelection(self.ledGroupEntry.FindString(MetaData.LEDGroups[run.ledGroup,MetaData.DESCRIPTION]))

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None, "Run Series Configurator")
        self.SetTopWindow(frame)

        frame.Show(True)
        return True
        
app = MyApp(redirect=True)
app.MainLoop()

