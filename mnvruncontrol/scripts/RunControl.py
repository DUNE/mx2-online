#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ListRowHighlighter
import subprocess
import os
import sys
import signal
import threading
import time
import shelve
import anydbm		# if a shelve database doesn't exist, this module contains the error raised
import re			# regular expressions

# other run control modules
import MetaData
import RunSeries
import DataAcquisitionManager

## some constants for configuration
CONFIG_DB_LOCATION = "/work/conditions/run_control_config.db"
#CONFIG_DB_LOCATION = "/home/jeremy/run_control_config.db"

RUN_SUBRUN_DB_LOCATION_DEFAULT = "/work/conditions/next_run_subrun.db"
LOGFILE_LOCATION_DEFAULT = "/work/data/logs"

ET_SYSTEM_LOCATION_DEFAULT = "/work/data/etsys"
RAW_DATA_LOCATION_DEFAULT = "/work/data/rawdata"

LI_CONTROL_LOCATION_DEFAULT = "/work/software/LIBox"

#########################################################
#    MainFrame
#########################################################
ID_START = wx.NewId()
ID_PICKFILE = wx.NewId()
ID_MOREINFO = wx.NewId()
ID_OPTIONS = wx.NewId()
class MainFrame(wx.Frame):
	""" The main control window. """
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title,
				      pos=(0, 0), size=(600, 600) ) 
		self.runmanager = DataAcquisitionManager.DataAcquisitionManager(self)

		self.GetConfig()		# load up the configuration entries from the file.
		self.BuildGraphics()	# build and draw the GUI panel.

		# now initialize some member variables we'll need:
		self.logfileNames = None

		# finally, make sure the display is current
		self.GetNextRunSubrun()
		self.UpdateLogFiles()

	def BuildGraphics(self):
		menuBar = wx.MenuBar()

		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit the run control")
		self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
		menuBar.Append(fileMenu, "&File")

		optionsMenu = wx.Menu()
		optionsMenu.Append(ID_OPTIONS, "Configuration settings...", "Various configuration settings.")
		self.Bind(wx.EVT_MENU, self.Configure, id=ID_OPTIONS)
		menuBar.Append(optionsMenu, "&Options")

		self.SetMenuBar(menuBar)

		self.statusbar = self.CreateStatusBar(2)
		self.SetStatusWidths([-6, -1])
		self.SetStatusText("STOPPED", 1)

#		panel = wx.Panel(self)

		nb = wx.Notebook(self)

		# the main page (main config / run controls)
		self.mainPage = wx.Panel(nb)
		self.singleRunConfigPanel = wx.Panel(self.mainPage)
		self.runSeriesConfigPanel = wx.Panel(self.mainPage)
		self.runSeriesConfigPanel.Show(False)

		# first, the 'global' configuration: run #, subrun #, which detector this is, # of FEBs, whether this is a single run or a series
		runEntryLabel = wx.StaticText(self.mainPage, -1, "Run")
		self.runEntry = wx.SpinCtrl(self.mainPage, -1, '0', size=(125, -1), min=0, max=100000)
		self.Bind(wx.EVT_SPINCTRL, self.CheckRunNumber, self.runEntry)
		self.runEntry.Disable()

		subrunEntryLabel = wx.StaticText(self.mainPage, -1, "Subrun")
		self.subrunEntry = wx.SpinCtrl(self.mainPage, -1, '0', size=(125, -1), min=0, max=100000)
		self.subrunEntry.Disable()

		HWinitEntryLabel = wx.StaticText(self.mainPage, -1, "HW init level")
		self.HWinitEntry =  wx.Choice(self.mainPage, -1, choices=MetaData.HardwareInitLevels.descriptions)

		detConfigEntryLabel = wx.StaticText(self.mainPage, -1, "Detector")
		self.detConfigEntry = wx.Choice(self.mainPage, -1, choices=MetaData.DetectorTypes.descriptions)
		self.detConfigEntry.SetSelection(MetaData.DetectorTypes.index("Upstream"))

		febsEntryLabel = wx.StaticText(self.mainPage, -1, "FEBs")
		self.febsEntry = wx.SpinCtrl(self.mainPage, -1, "4", size=(125, -1), min=1, max=10000)

		self.singleRunButton = wx.RadioButton(self.mainPage, -1, "Single run", style=wx.RB_GROUP)
		self.Bind(wx.EVT_RADIOBUTTON, self.UpdateRunConfig, self.singleRunButton)

		self.runSeriesButton = wx.RadioButton(self.mainPage, -1, "Run series")
		self.Bind(wx.EVT_RADIOBUTTON, self.UpdateRunConfig, self.runSeriesButton)

		runSelectionSizer = wx.BoxSizer(wx.HORIZONTAL)
		runSelectionSizer.Add(self.singleRunButton)
		runSelectionSizer.Add(self.runSeriesButton)
		
		globalConfigSizer = wx.GridSizer(2, 2, 10, 10)
		globalConfigSizer.AddMany([ (runEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                            (self.runEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                            (subrunEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                            (self.subrunEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                            (HWinitEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                            (self.HWinitEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                            (detConfigEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                            (self.detConfigEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                            (febsEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                            (self.febsEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL) ])
		globalConfigBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Global run configuration"), wx.VERTICAL)
		globalConfigBoxSizer.Add(globalConfigSizer, flag=wx.EXPAND)
		globalConfigBoxSizer.Add(runSelectionSizer, flag=wx.ALIGN_CENTER_HORIZONTAL)

		# now the single-run-specific config: # gates, the run mode, LI box config
		gatesEntryLabel = wx.StaticText(self.singleRunConfigPanel, -1, "Gates")
		self.gatesEntry = wx.SpinCtrl(self.singleRunConfigPanel, -1, "10", size=(125, -1), min=1, max=10000)

		runModeEntryLabel = wx.StaticText(self.singleRunConfigPanel, -1, "Run Mode")
		self.runModeEntry =  wx.Choice(self.singleRunConfigPanel, -1, choices=MetaData.RunningModes.descriptions)
		self.Bind(wx.EVT_CHOICE, self.UpdateLEDgroups, self.runModeEntry)

		LEDgroupLabel = wx.StaticText(self.singleRunConfigPanel, -1, "LED groups used in LI")
		LEDgroupSizer = wx.GridSizer(2, 2)
		self.LEDgroups = []
		for letter in ('A', 'B', 'C', 'D'):
			cb = wx.CheckBox(self.singleRunConfigPanel, -1, letter)
			cb.SetValue(True)
			cb.Disable()		# will be enabled when necessary
			self.LEDgroups.append(cb)
			LEDgroupSizer.Add(cb)

		LILevelEntryLabel = wx.StaticText(self.singleRunConfigPanel, -1, "LI light level")
		self.LILevelEntry = wx.Choice(self.singleRunConfigPanel, -1, choices=MetaData.LILevels.descriptions)
		self.LILevelEntry.SetSelection(MetaData.LILevels.index("Max PE"))
		self.LILevelEntry.Disable()		# will be enabled when necessary

		singleRunConfigSizer = wx.GridSizer(3, 2, 10, 10)
		singleRunConfigSizer.AddMany([ (gatesEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.gatesEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (runModeEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.runModeEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (LEDgroupLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (LEDgroupSizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (LILevelEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.LILevelEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL) ])
		singleRunConfigBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.singleRunConfigPanel, -1, "Single run Configuration"), wx.VERTICAL)
		singleRunConfigBoxSizer.Add(singleRunConfigSizer, 1, wx.EXPAND)

		self.singleRunConfigPanel.SetSizer(singleRunConfigBoxSizer)

		# run series config: allows user to select a predefined run series file and see what's in it.
		
		seriesFileLabel = wx.StaticText(self.runSeriesConfigPanel, -1, "Run series file:")
		self.seriesFile = wx.TextCtrl(self.runSeriesConfigPanel, -1, "", style=wx.TE_READONLY)

		self.seriesFileButton = wx.Button(self.runSeriesConfigPanel, ID_PICKFILE, "Load...")
		self.Bind(wx.EVT_BUTTON, self.LoadRunSeriesFile, self.seriesFileButton)
		
		seriesFileSizer = wx.BoxSizer(wx.HORIZONTAL)
		seriesFileSizer.Add(self.seriesFile, 1, flag=wx.RIGHT | wx.LEFT, border=5)
		seriesFileSizer.Add(self.seriesFileButton, 0, flag=wx.LEFT, border=5)
		
		self.seriesDescription = AutoSizingListCtrl(self.runSeriesConfigPanel, -1, style=wx.LC_REPORT | wx.LC_VRULES)
		self.seriesDescription.setResizeColumn(2)
		self.seriesDescription.InsertColumn(0, "", width=20)		# which subrun is currently being executed
		self.seriesDescription.InsertColumn(1, "Run mode")#, width=150)
		self.seriesDescription.InsertColumn(2, "Number of gates", width=125)
		
		self.moreInfoButton = wx.Button(self.runSeriesConfigPanel, ID_MOREINFO, "More details...")
		self.Bind(wx.EVT_BUTTON, self.SeriesMoreInfo, self.moreInfoButton)
		self.moreInfoButton.Disable()		# will be enabled when a file is loaded.
		
		runSeriesConfigSizer = wx.StaticBoxSizer(wx.StaticBox(self.runSeriesConfigPanel, -1, "Run series configuration"), wx.VERTICAL)
		runSeriesConfigSizer.Add(seriesFileLabel, 0, flag=wx.RIGHT, border=5)
		runSeriesConfigSizer.Add(seriesFileSizer, flag=wx.EXPAND)
		runSeriesConfigSizer.Add(self.seriesDescription, 1, flag=wx.EXPAND)
		runSeriesConfigSizer.Add(self.moreInfoButton, flag=wx.ALIGN_CENTER_HORIZONTAL)
		
		self.runSeriesConfigPanel.SetSizer(runSeriesConfigSizer)
		

		# put the configuration stuff together in one sizer.
		runConfigSizer = wx.BoxSizer(wx.VERTICAL)
		runConfigSizer.Add(self.singleRunConfigPanel, proportion=1, flag=wx.EXPAND)
		runConfigSizer.Add(self.runSeriesConfigPanel, proportion=1, flag=wx.EXPAND)
		
		configSizer = wx.BoxSizer(wx.VERTICAL)
		configSizer.Add(globalConfigBoxSizer, flag=wx.EXPAND | wx.BOTTOM, border=5)
		configSizer.Add(runConfigSizer, proportion=1, flag=wx.EXPAND)

		# run control: start, stop, close windows
		self.startButton = wx.Button(self.mainPage, ID_START, "Start")
		self.Bind(wx.EVT_BUTTON, self.StartRunning, self.startButton)
		self.startButton.Disable()
		
		self.stopButton = wx.Button(self.mainPage, wx.ID_STOP)
		self.Bind(wx.EVT_BUTTON, self.StopRunning, self.stopButton)
		self.stopButton.Disable()		# disabled until the 'start' button is pressed

		self.closeAllButton = wx.Button(self.mainPage, wx.ID_CLOSE, "Close ET/DAQ windows")
		self.Bind(wx.EVT_BUTTON, self.CloseAllWindows, self.closeAllButton)
		self.closeAllButton.Disable()
		
		controlBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run Control"), wx.VERTICAL)
		controlBoxSizer.AddMany( [ (self.startButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.stopButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.closeAllButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ] )
		
		
		# a sizer for all the run control stuff (as separate from the status indicator)
		topSizer = wx.BoxSizer(wx.HORIZONTAL)
		topSizer.AddMany( [(configSizer, 1, wx.EXPAND | wx.RIGHT, 5), (controlBoxSizer, 1, wx.EXPAND | wx.LEFT, 5)] )
		
		# now the 'status' area
		self.onImage = wx.Bitmap("LED_on.png", type=wx.BITMAP_TYPE_PNG)
		self.offImage = wx.Bitmap("LED_off.png", type=wx.BITMAP_TYPE_PNG)
		self.runningIndicator = wx.StaticBitmap(self.mainPage, -1)
		self.runningIndicator.SetBitmap(self.offImage)

		runningIndicatorText = wx.StaticText(self.mainPage, -1, "Running?")
		
		runningIndicatorSizer = wx.BoxSizer(wx.VERTICAL)
		runningIndicatorSizer.Add(self.runningIndicator, 0, wx.ALIGN_CENTER_HORIZONTAL)
		runningIndicatorSizer.Add(runningIndicatorText, 0, wx.ALIGN_CENTER_HORIZONTAL)

		statusSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Status"), wx.HORIZONTAL)
		statusSizer.Add(runningIndicatorSizer, 1, wx.ALIGN_CENTER_HORIZONTAL)

		# one sizer to rule them all, one sizer to bind them...
		globalSizer = wx.BoxSizer(wx.VERTICAL)
		globalSizer.Add(topSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP | wx.ALL, border=10)
		globalSizer.Add(statusSizer, 0, wx.EXPAND | wx.ALIGN_TOP | wx.ALL, border=10)

		self.mainPage.SetSizer(globalSizer)

		# now the log page panel.
		logPage = wx.Panel(nb)

		logfileText = wx.StaticText( logPage, -1, wordwrap("Select log files you want to view (ctrl+click for multiple selections) and click the \"View log file(s)\" button below...", 400, wx.ClientDC(self)) )
		self.logfileList = AutoSizingListCtrl(logPage, -1, style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_SORT_DESCENDING)
		self.logfileList.setResizeColumn(6)
		self.logfileList.InsertColumn(0, "Run")
		self.logfileList.InsertColumn(1, "Subrun")
		self.logfileList.InsertColumn(2, "Date")
		self.logfileList.InsertColumn(3, "Time (GMT)")
		self.logfileList.InsertColumn(4, "Run type")
		self.logfileList.InsertColumn(5, "Detector")
		
		self.logFileButton = wx.Button(logPage, -1, "View selected log files")
		self.Bind(wx.EVT_BUTTON, self.ShowLogFiles, self.logFileButton)
		
		logBoxSizer = wx.StaticBoxSizer(wx.StaticBox(logPage, -1, "Logs"), orient=wx.VERTICAL)
		logBoxSizer.AddMany( [ (logfileText, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 10),
		                       (self.logfileList, 1, wx.EXPAND),
		                       (self.logFileButton, 0, wx.ALIGN_CENTER_HORIZONTAL) ] )
		                       
		logPage.SetSizer(logBoxSizer)
		
		# add the pages into the notebook.
		nb.AddPage(self.mainPage, "Run control")
		nb.AddPage(logPage, "Log files")
		
		self.Layout()

		self.Connect(-1, -1, EVT_CONFIGUPDATED_ID, self.UpdateLogFiles)

	def parseLogfileName(self, filename):
		matches = re.match("^(?P<detector>\w\w)_(?P<run>\d{8})_(?P<subrun>\d{4})_(?P<type>\w+)_v\d+_(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hour>\d{2})(?P<minute>\d{2}).txt$", filename)
		
		if matches is None:
			return None
		
		fileinfo = []

		fileinfo.append(matches.group("run").lstrip('0'))
		fileinfo.append(matches.group("subrun").lstrip('0'))
		fileinfo.append(matches.group("month") + "/" + matches.group("day") + "/20" + matches.group("year"))
		fileinfo.append( matches.group("hour") + ":" + matches.group("minute") )

		if matches.group("type") in MetaData.RunningModes:
			fileinfo.append( MetaData.RunningModes[matches.group("type")] )
		else:
			return None
	
		if matches.group("detector") in MetaData.DetectorTypes:
			fileinfo.append( MetaData.DetectorTypes[matches.group("detector")] )	
		else:
			return None

		return fileinfo

	def Configure(self, evt):
		wnd = OptionsFrame(self)
		wnd.Show()

	def GetConfig(self):
		try:
			db = shelve.open(CONFIG_DB_LOCATION)
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The configuration file does not exist.  Default values are being used.", "Config file inaccessible", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()

			self.runinfoFile = RUN_SUBRUN_DB_LOCATION_DEFAULT
			self.logfileLocation = LOGFILE_LOCATION_DEFAULT
			self.runmanager.etSystemFileLocation = ET_SYSTEM_LOCATION_DEFAULT
			self.runmanager.rawdataLocation = RAW_DATA_LOCATION_DEFAULT
			self.runmanager.LIBoxControlLocation = LI_CONTROL_LOCATION_DEFAULT
			
		else:
			try:	self.runinfoFile = db["runinfoFile"]
			except KeyError: self.runinfoFile = RUN_SUBRUN_DB_LOCATION_DEFAULT
			
			try:	self.logfileLocation = db["logfileLocation"]
			except KeyError: self.logfileLocation = LOGFILE_LOCATION_DEFAULT
			
			try:	self.runmanager.etSystemFileLocation = db["etSystemFileLocation"]
			except KeyError: self.runmanager.etSystemFileLocation = ET_SYSTEM_LOCATION_DEFAULT
			
			try:	self.runmanager.rawdataLocation = db["rawdataLocation"]
			except KeyError: self.runmanager.rawdataLocation = RAW_DATA_LOCATION_DEFAULT

			try:	self.runmanager.LIBoxControlLocation = db["LIBoxControlLocation"]
			except KeyError: self.runmanager.LIBoxControlLocation = LI_CONTROL_LOCATION_DEFAULT
		
		
		
	def GetNextRunSubrun(self, evt=None):
		if not os.path.exists(self.runinfoFile):
			errordlg = wx.MessageDialog( None, "The database storing the run/subrun data appears to be missing.  Run/subrun will be set to 1...", "Run/subrun database missing", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()

			self.runEntry.SetRange(1, 100000)
			self.runEntry.SetValue(1)
			self.subrunEntry.SetValue(1)
		else:
			d = shelve.open(self.runinfoFile, 'r')

			if d.has_key('run') and d.has_key('subrun'):
				self.runEntry.SetRange(int(d['run']),100000)
				self.runEntry.SetValue(int(d['run']))
				self.subrunEntry.SetValue(int(d['subrun']))

			else:
				errordlg = wx.MessageDialog( None, "The database storing the run/subrun data appears to be corrupted.  Run/subrun will be set to 1...", "Run/subrun database corrupted", wx.OK | wx.ICON_WARNING )
				errordlg.ShowModal()

				self.runEntry.SetRange(1, 100000)
				self.runEntry.SetValue(1)
				self.subrunEntry.SetValue(1)

			d.close()

		# the minimum subrun allowed for the lowest run.  
		# if the user raises the run number, the subrun will be returned to 1,
		# so if s/he subsequently lowers it again, we need to know what to set the the minimum
		# back to.
		self.minRunSubrun = self.subrunEntry.GetValue()		

		self.runEntry.Enable()
		self.startButton.Enable()
	
	def StoreNextRunSubrun(self):
		try:
			db = shelve.open(self.runinfoFile)
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The database storing the run/subrun data cannot be accessed.  Run/subrun will not be retained...", "Run/subrun database inaccessible", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
		else:
			db["run"] = self.runEntry.GetValue()
			db["subrun"] = self.subrunEntry.GetValue()
			db.close()
			
	def PostSubrun(self, evt=None):
		self.subrunEntry.SetValue(self.subrunEntry.GetValue() + 1)
		self.minRunSubrun = self.subrunEntry.GetValue()
		self.runEntry.SetRange(self.runEntry.GetValue(), 100000)
		self.StoreNextRunSubrun()
		
		self.UpdateLogFiles()
			
	def CheckRunNumber(self, evt=None):
		if self.runEntry.GetValue() < self.runEntry.GetMin():
			self.runEntry.SetValue(self.runEntry.GetMin())
		
		if self.runEntry.GetValue() > self.runEntry.GetMax():
			self.runEntry.SetValue(self.runEntry.GetMax())
		
		if self.runEntry.GetValue() == self.runEntry.GetMin():
			self.subrunEntry.SetValue(self.minRunSubrun)
		else:
			self.subrunEntry.SetValue(1)
			
	def LoadRunSeriesFile(self, evt=None):
		fileSelector = wx.FileDialog(self, "Select a run series file", wildcard="*", style=wx.FD_OPEN)
		fileSelector.ShowModal()
		
		filename = fileSelector.GetFilename()
		path = fileSelector.GetPath()
		if filename != "":
			
			badfile = False
			try:
				db = shelve.open(path)
				self.runmanager.runseries = db["series"]
				db.close()
			except (anydbm.error, KeyError):
				errordlg = wx.MessageDialog( None, "The file you selected is not a valid run series file.  Select another.", "Invalid file", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()
				return
			
			self.seriesFile.SetValue(filename)
			self.seriesFilename = filename
			self.seriesPath = path
			
			self.seriesDescription.DeleteAllItems()
			for runinfo in self.runmanager.runseries.Runs:
				index = self.seriesDescription.InsertStringItem(sys.maxint, "")		# first column is which subrun is currently being executed
				self.seriesDescription.SetStringItem(index, 1, MetaData.RunningModes[runinfo.runMode])
				self.seriesDescription.SetStringItem(index, 2, str(runinfo.gates))
				
			self.moreInfoButton.Enable()
			self.UpdateStatus()
		
	def SeriesMoreInfo(self, evt=None):
		infowindow = RunSeriesInfoFrame(self, self.seriesFilename, self.runmanager.runseries)
		infowindow.Show()

	def UpdateRunConfig(self, evt=None):
		if self.singleRunButton.GetValue() == True:
			self.runSeriesConfigPanel.Show(False)
			self.singleRunConfigPanel.Show(True)
		else:
			self.runSeriesConfigPanel.Show(True)
			self.singleRunConfigPanel.Show(False)
		
		self.mainPage.Layout()
		self.mainPage.Refresh()
		self.mainPage.Update()
		
	def UpdateLEDgroups(self, evt=None):
		runMode = self.runModeEntry.GetSelection()
		if runMode == MetaData.RunningModes.index("Light injection") or runMode == MetaData.RunningModes.index("Mixed beam/LI"):
			for cb in self.LEDgroups:
				cb.Enable()
			self.LILevelEntry.Enable()
		else:
			for cb in self.LEDgroups:
				cb.Disable()
			self.LILevelEntry.Disable()
			
	def UpdateCloseWindows(self, windowsOpen):
		if windowsOpen:
			self.closeAllButton.Enable()
		else:
			self.closeAllButton.Disable()
	
	def UpdateStatus(self):
		symbol = ""
		if self.runmanager.running:
			symbol = u"\u25b7"		# a right-facing triangle: like a "play" symbol
		else:
			symbol = u"\u25a1"		# a square: like a "stop" symbol

		if self.runSeriesButton.GetValue() == True:		# if this is a run SERIES
			index = -1
			while True:
				index = self.seriesDescription.GetNextItem(index)
			
				if index == -1:
					break
			
				if index == self.runmanager.subrun:
					self.seriesDescription.SetStringItem(index, 0, symbol)
					self.seriesDescription.Select(index)
				else:
					self.seriesDescription.SetStringItem(index, 0, "")
					self.seriesDescription.Select(index, False)

	def OnTimeToClose(self, evt):
		self.runmanager.StopDataAcquisition()

		self.CloseAllWindows()

		self.Close()
		

	def UpdateLogFiles(self, evt=None):
		self.GetConfig()

		self.logfileList.DeleteAllItems()
		self.logfileNames = []
		self.logfileInfo = []
		
		try:
			for filename in os.listdir(self.logfileLocation):
				if os.path.isdir(filename):
					continue
				fileinfo = self.parseLogfileName(filename)
				if fileinfo is not None:
					self.logfileNames.append(filename)
					self.logfileInfo.append(fileinfo)
		except OSError:
			self.logfileNames = None
			self.logfileInfo = None
		else:
			self.logfileNames.sort()
			self.logfileInfo.sort(self.SortLogData)
			
			self.logfileNames.reverse()
			self.logfileInfo.reverse()

		if self.logfileNames is not None and len(self.logfileNames) > 0:
			for fileinfo in self.logfileInfo:
				index = self.logfileList.InsertStringItem(sys.maxint, fileinfo[0])
				for i in range(1,len(fileinfo)):
					self.logfileList.SetStringItem(index, i, fileinfo[i])
		else:
			self.logfileList.InsertStringItem(0, "Log directory is empty or inaccessible.")
		
			
	def ShowLogFiles(self, evt=None):
		filenames = []

		index = -1
		while True:
			index = self.logfileList.GetNextSelected(index)
			
			if index == -1:
				break
			
			filenames.append(self.logfileLocation + "/" + self.logfileNames[index])
	
		logframe = LogFrame(self, filenames)
		logframe.Show()

	def CloseAllWindows(self, evt=None):
		self.runmanager.CloseWindows()
		self.runmanager.UpdateWindowCount()
	
	def StartRunning(self, evt=None):
		if (self.singleRunButton.GetValue() == True):		# if this is a single run
			self.runmanager.runseries = RunSeries.RunSeries()
			
			LEDgroups = ""
			for cb in self.LEDgroups:
				if cb.GetValue == True:
					LEDgroups += cb.GetLabelText()
			LEDcode = MetaData.LEDGroups[MetaData.LEDGroups.LEDgroupsToLIgroupCode(LEDgroups), MetaData.HASH]

			gates    = int(self.gatesEntry.GetValue())
			runMode  = MetaData.RunningModes.item(int(self.runModeEntry.GetSelection()), MetaData.HASH)
			LIlevel  = MetaData.LILevels.item(int(self.LILevelEntry.GetSelection()), MetaData.HASH)
			
			run = RunSeries.RunInfo(gates, runMode, LIlevel, LEDcode)
			self.runmanager.runseries.Runs.append(run)
		else:										# if it's a run series
			if self.runmanager.runseries == None:
				errordlg = wx.MessageDialog( None, "You must load a run series file before beginning the run!", "Must load run series before starting run", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()
				
				return

		self.runmanager.run          = int(self.runEntry.GetValue())
		self.runmanager.first_subrun = int(self.subrunEntry.GetValue())
		self.runmanager.detector     = MetaData.DetectorTypes.item(self.detConfigEntry.GetSelection(), MetaData.HASH)
		self.runmanager.febs         = int(self.febsEntry.GetValue())
				
		self.runmanager.StartDataAcquisition()
		if (self.runmanager.running):
			self.runEntry.Disable()
			self.subrunEntry.Disable()
			self.HWinitEntry.Disable()
			self.gatesEntry.Disable()
			self.detConfigEntry.Disable()
			self.runModeEntry.Disable()
			self.febsEntry.Disable()
			
			self.singleRunButton.Disable()
			self.runSeriesButton.Disable()
			self.seriesFileButton.Disable()

			self.startButton.Disable()
			self.stopButton.Enable()

			self.SetStatusText("RUNNING", 1)
			self.runningIndicator.SetBitmap(self.onImage)
			
	
	def StopRunning(self, evt=None):
		if self.runmanager.running:		
			self.runmanager.StopDataAcquisition()

		self.SetStatusText("STOPPED", 1)
		self.runningIndicator.SetBitmap(self.offImage)

		self.runEntry.Enable()
		self.gatesEntry.Enable()
		self.detConfigEntry.Enable()
		self.runModeEntry.Enable()
		self.febsEntry.Enable()
		self.HWinitEntry.Enable()

		self.singleRunButton.Enable()
		self.runSeriesButton.Enable()
		self.seriesFileButton.Enable()

		self.stopButton.Disable()
		self.startButton.Enable()
		self.UpdateStatus()
		self.UpdateLogFiles()
		
	@staticmethod
	def SortLogData(fileinfo1, fileinfo2):
		f1 = fileinfo1[0]*10000 + fileinfo1[1]		# run * 10000 + subrun
		f2 = fileinfo2[0]*10000 + fileinfo2[1]
		
		if f1 == f2:
			t1 = time.strptime("2010 " + fileinfo1[3], "%Y %H:%M")		# need to include a year because otherwise the 'mktime' below overflows.  which year it is is irrelevant (all we need is a difference anyway).
			t2 = time.strptime("2010 " + fileinfo2[3], "%Y %H:%M")
			
			timediff = time.mktime(t1) - time.mktime(t2)
			if timediff == 0:		# this should never happen.
				return 0
			else:
				return 1 if timediff > 0 else -1
		else:
			return 1 if f1 > f2 else -1


#########################################################
#   LogFrame
#########################################################

class LogFrame(wx.Frame):
	def __init__(self, parent, filenames):
		try:
			for filename in filenames:
				f = open(filename)
				f.close()
		except IOError:
			errordlg = wx.MessageDialog( None, "Couldn't open file '" + filename + "'.  Sorry...", "Log file inaccessible", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			self.ok = False			
			
			return

		self.ok = True
		
		wx.Frame.__init__(self, parent, -1, "DAQ log", size=(800,600))
		panel = wx.Panel(self)
		
		nb = wx.Notebook(panel)
		for filename in filenames:
			textarea = wx.TextCtrl(nb, -1, style = wx.TE_MULTILINE | wx.TE_READONLY)

			f = open(filename)
			for line in f:
				textarea.AppendText(line)
			f.close()
			
			nb.AddPage(textarea, filename)
			
		okButton = wx.Button(panel, wx.ID_OK)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(nb, 1, wx.EXPAND | wx.ALIGN_TOP)
		sizer.Add(okButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)

		panel.SetSizer(sizer)

		self.Bind(wx.EVT_BUTTON, self.CloseOut, okButton)
		
	def CloseOut(self, evt=None):
		self.Close()
		
#########################################################
#   RunSeriesInfoFrame
#########################################################

class RunSeriesInfoFrame(wx.Frame):
	""" A window for configuration of paths, etc. """
	def __init__(self, parent, filename, runseries):
		wx.Frame.__init__(self, parent, -1, "Run series: " + filename, size=(600,400))

		panel = wx.Panel(self)

		infoList = AutoSizingListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_VRULES)
		infoList.setResizeColumn(2)

		infoList.InsertColumn(0, "# gates")
		infoList.InsertColumn(1, "Running mode")
		infoList.InsertColumn(2, "LI level")
		infoList.InsertColumn(3, "LED group")

		for runinfo in runseries.Runs:
			index = infoList.InsertStringItem(sys.maxint, str(runinfo.gates))
			infoList.SetStringItem(index, 1, MetaData.RunningModes[runinfo.runMode])
			infoList.SetStringItem(index, 2, MetaData.LILevels[runinfo.ledLevel])
			infoList.SetStringItem(index, 3, MetaData.LEDGroups[runinfo.ledGroup])
		
		okButton = wx.Button(panel, wx.ID_OK)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(infoList, 1, wx.EXPAND | wx.ALIGN_TOP)
		sizer.Add(okButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)

		panel.SetSizer(sizer)

		self.Bind(wx.EVT_BUTTON, self.CloseOut, okButton)
		
	def CloseOut(self, evt=None):
		self.Close()
		

#########################################################
#   OptionsFrame
#########################################################

class OptionsFrame(wx.Frame):
	""" A window for configuration of paths, etc. """
	def __init__(self, parent):
		wx.Frame.__init__(self, parent, -1, "Configuration", size=(600,400))
		
		self.parent = parent

		try:
			db = shelve.open(CONFIG_DB_LOCATION)
		except anydbm.error:
			# the user has already been informed once (when the main frame was opened)
			# if the DB is not accessible, so we'll just silently go to the defaults here.
			runinfoFile = RUN_SUBRUN_DB_LOCATION_DEFAULT
			logfileLocation = LOGFILE_LOCATION_DEFAULT
			etSystemFileLocation = ET_SYSTEM_LOCATION_DEFAULT
			rawdataLocation = RAW_DATA_LOCATION_DEFAULT
			LIBoxControlLocation = LI_CONTROL_LOCATION_DEFAULT
		else:
			try:	runinfoFile = db["runinfoFile"]
			except KeyError: runinfoFile = RUN_SUBRUN_DB_LOCATION_DEFAULT

			try:	logfileLocation = db["logfileLocation"]
			except KeyError: logfileLocation = LOGFILE_LOCATION_DEFAULT
			
			try:	etSystemFileLocation = db["etSystemFileLocation"]
			except KeyError: etSystemFileLocation = ET_SYSTEM_LOCATION_DEFAULT
			
			try:	rawdataLocation = db["rawdataLocation"]
			except KeyError: rawdataLocation = RAW_DATA_LOCATION_DEFAULT
			
			try:	LIBoxControlLocation = db["LIBoxControlLocation"]
			except KeyError: LIBoxControlLocation = LI_CONTROL_LOCATION_DEFAULT

		panel = wx.Panel(self)
		
		warningText = wx.StaticText(panel, -1, "** PLEASE don't change these values unless you know what you're doing! **")
		
		runInfoDBLabel = wx.StaticText(panel, -1, "Run/subrun info database file")
		self.runInfoDBEntry = wx.TextCtrl(panel, -1, runinfoFile)
		
		logfileLocationLabel = wx.StaticText(panel, -1, "Log file location")
		self.logfileLocationEntry = wx.TextCtrl(panel, -1, logfileLocation)

		etSystemFileLocationLabel = wx.StaticText(panel, -1, "ET system file location")
		self.etSystemFileLocationEntry = wx.TextCtrl(panel, -1, etSystemFileLocation)
		
		rawDataLocationLabel = wx.StaticText(panel, -1, "Raw data location")
		self.rawDataLocationEntry = wx.TextCtrl(panel, -1, rawdataLocation)
		
		LIBoxControlLocationLabel = wx.StaticText(panel, -1, "LI box control location")
		self.LIBoxControlLocationEntry = wx.TextCtrl(panel, -1, LIBoxControlLocation)
		
		pathsGridSizer = wx.GridSizer(6, 2, 10, 10)
		pathsGridSizer.AddMany( ( runInfoDBLabel,            (self.runInfoDBEntry, 1, wx.EXPAND),
		                     logfileLocationLabel,      (self.logfileLocationEntry, 1, wx.EXPAND),
		                     etSystemFileLocationLabel, (self.etSystemFileLocationEntry, 1, wx.EXPAND),
		                     rawDataLocationLabel,      (self.rawDataLocationEntry, 1, wx.EXPAND),
		                     LIBoxControlLocationLabel, (self.LIBoxControlLocationEntry, 1, wx.EXPAND) ) )

		pathsSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Paths"), orient=wx.VERTICAL)
		pathsSizer.Add(pathsGridSizer, 1, wx.EXPAND)
		
		DAQrootLabel = wx.StaticText(panel, -1, "$DAQROOT")
		DAQrootText = wx.TextCtrl(panel, -1, os.environ["DAQROOT"], style=wx.TE_READONLY)
		DAQrootText.Disable()
		
		EThomeLabel = wx.StaticText(panel, -1, "$ET_HOME")
		EThomeText = wx.TextCtrl(panel, -1, os.environ["ET_HOME"], style=wx.TE_READONLY)
		EThomeText.Disable()
		
		environGridSizer = wx.GridSizer(2, 2, 10, 10)
		environGridSizer.AddMany( ( DAQrootLabel, (DAQrootText, 1, wx.EXPAND),
		                            EThomeLabel,  (EThomeText, 1, wx.EXPAND) ) )
		
		environSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Environment"), orient=wx.VERTICAL)
		environSizer.Add(environGridSizer, flag = wx.EXPAND)
		
		saveButton = wx.Button(panel, wx.ID_SAVE)
		self.Bind(wx.EVT_BUTTON, self.SaveAll, saveButton)

		cancelButton = wx.Button(panel, wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.Cancel, cancelButton)

		buttonSizer = wx.GridSizer(1, 2, 10, 10)
		buttonSizer.AddMany( ( (saveButton, 1, wx.ALIGN_CENTER_HORIZONTAL), (cancelButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ) )

		globalSizer = wx.BoxSizer(wx.VERTICAL)
		globalSizer.Add(warningText, flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border=10)
		globalSizer.Add(pathsSizer, flag=wx.ALL | wx.EXPAND, border=10)
		globalSizer.Add(environSizer, flag=wx.ALL | wx.EXPAND, border=10)
		globalSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER_HORIZONTAL)		
		panel.SetSizer(globalSizer)
		
		self.Layout()
		
	def SaveAll(self, evt=None):
		try:
			db = shelve.open(CONFIG_DB_LOCATION, "w")
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The configuration file cannot be opened.  Values will not be saved.", "Config file inaccessible", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()
		else:
			db["runinfoFile"] = self.runInfoDBEntry.GetValue()
			db["logfileLocation"] = self.logfileLocationEntry.GetValue()
			db["etSystemFileLocation"] = self.etSystemFileLocationEntry.GetValue()
			db["rawdataLocation"] = self.rawDataLocationEntry.GetValue()
			db["LIBoxControlLocation"] = self.LIBoxControlLocationEntry.GetValue()
			
			db.close()
			
		wx.PostEvent(self.parent, ConfigUpdatedEvent())

		self.Close()
		
	def Cancel(self, evt=None):
		self.Close()

#########################################################
#   AutoSizingListCtrl
#########################################################
class AutoSizingListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, ListRowHighlighter):
	def __init__(self, parent, id=-1, style=wx.LC_REPORT):
		wx.ListCtrl.__init__(self, parent, id, style=style)
		ListCtrlAutoWidthMixin.__init__(self)
		ListRowHighlighter.__init__(self)
		
	

#########################################################
#   ConfigUpdatedEvent
#########################################################

EVT_CONFIGUPDATED_ID = wx.NewId()
class ConfigUpdatedEvent(wx.CommandEvent):
	""" An event informing the main window that the configuration database has been updated. """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_CONFIGUPDATED_ID)


#########################################################
#   MainApp
#########################################################

class MainApp(wx.App):
	def OnInit(self):
		try:
			temp = os.environ["DAQROOT"]
			temp = os.environ["ET_HOME"]
		except KeyError:
			errordlg = wx.MessageDialog( None, "Your environment appears to be missing the necessary configuration.  Did you source the appropriate setup script(s) before starting the run control?", "Incorrect environment", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			return False
		else:
			frame = MainFrame(None, "Run Control")
			self.SetTopWindow(frame)
			frame.Show(True)
			return True

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MainApp(redirect=False)
	app.MainLoop()

