#!/usr/bin/env python
"""
  RunControl.py:
   Main wxPython objects for the presentation of a graphical
   run control interface to the user.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

import wx
from wx.lib.wordwrap import wordwrap
import subprocess
import os
import os.path
import sys
import signal
import threading
import time
import shelve
import anydbm		# if a shelve database doesn't exist, this module contains the error raised
import re			# regular expressions

# run control-specific modules.  note that the folder 'mnvruncontrol' must be in the PYTHONPATH!
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import Defaults

from mnvruncontrol.backend import Events
from mnvruncontrol.backend import RunSeries
from mnvruncontrol.backend import DataAcquisitionManager
from mnvruncontrol.backend import ReadoutNode
from mnvruncontrol.backend import MonitorNode
from mnvruncontrol.backend import SortTools
from mnvruncontrol.backend import Threads

from mnvruncontrol.frontend import Frames
from mnvruncontrol.frontend import Tools


#########################################################
#    MainFrame
#########################################################
ID_START = wx.NewId()
ID_PICKFILE = wx.NewId()
ID_MOREINFO = wx.NewId()
ID_PATHS = wx.NewId()
ID_AUTOCLOSE = wx.NewId()
ID_LOCKDOWN = wx.NewId()
class MainFrame(wx.Frame):
	""" The main control window. """
	
	### Note:
	###   this class is pretty long and has a lot of methods.
	###   to make them easier to find, they're loosely grouped by category:
	###    * initialization                (begin around line 75)
	###    * "master" run control          ( ...         line 375)
	###    * "mid-run"                     ( ...         line 475)
	###    * configuration                 ( ...         line 525)
	###    * GUI-related (+ evt. handling) ( ...         line 675)
	###    * new window/dialog creators    ( ...         line 900)
	###  within each category (which is indicated by a block comment like the one below),
	###  they are sorted alphabetically.
	### You can also get a sense of what they do by importing this module
	###  into an interactive Python session and doing "help(MainFrame)".
	###  Note that the 'help' function arranges everything alphabetically though.

	################################################################################################
	# Initialization methods :
	#   __init__ and graphics initialization
	################################################################################################

	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title,
				      pos=(0, 0), size=(600, 650) ) 
		self.runmanager = DataAcquisitionManager.DataAcquisitionManager(self)

		self.GetGlobalConfig()		# load up the configuration entries from the file.
		self.BuildGraphics()	# build and draw the GUI panel.
		
		# now initialize some member variables we'll need:
		self.logfileNames = None
		self.blinkThread = None
		self.default_background = None

		# finally, make sure the display is current
		self.GetLastRunConfig()
		self.UpdateLogFiles()
		self.UpdateRunConfig()
		
		# any wx events that need to be handled
		self.Bind(wx.EVT_CLOSE, self.OnTimeToClose, self)
		
		self.Bind(Events.EVT_ALERT,               self.UserAlert)
		self.Bind(Events.EVT_BLINK,               self.BlinkWindow)
		self.Bind(Events.EVT_NEED_USER_HV_CHECK,  Frames.HVConfirmationFrame)
		self.Bind(Events.EVT_SUBRUN_STARTING,     self.PreSubrun)
		self.Bind(Events.EVT_SUBRUN_OVER,         self.PostSubrun)
		self.Bind(Events.EVT_STOP_RUNNING,        self.StopRunning)
		self.Bind(Events.EVT_UPDATE_NODE,         self.UpdateNodeStatus)
		self.Bind(Events.EVT_UPDATE_PROGRESS,     self.UpdateRunStatus)
		self.Bind(Events.EVT_UPDATE_SERIES,       self.UpdateSeriesStatus)
		self.Bind(Events.EVT_UPDATE_WINDOW_COUNT, self.UpdateCloseWindows)
		self.Bind(Events.EVT_WAIT_FOR_CLEANUP,    self.WaitOnCleanup)

		self.Bind(Events.EVT_ERRORMSG, self.ShowErrorMsg)
		
	def BuildGraphics(self):
		""" Constructs the wxPython graphics for the run control. """
		menuBar = wx.MenuBar()

		fileMenu = wx.Menu()
		fileMenu.Append(wx.ID_SAVE, "&Save values", "Save the currently-specified values for next time.")
		fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit the run control")
	
		self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.StoreLastRunConfig, id=wx.ID_SAVE)
		menuBar.Append(fileMenu, "&File")

		optionsMenu = wx.Menu()
		self.autocloseEntry = optionsMenu.Append(ID_AUTOCLOSE, "Auto-close windows", "Automatically close the ET/DAQ windows at the end of a subrun.", kind=wx.ITEM_CHECK)
		self.lockdownEntry = optionsMenu.Append(ID_LOCKDOWN, "Lock global config", "Lock the global configuration fields to prevent accidental changes.", kind=wx.ITEM_CHECK)
		self.Bind(wx.EVT_MENU, self.UpdateLockedEntries, id=ID_LOCKDOWN)
		menuBar.Append(optionsMenu, "&Options")

		self.SetMenuBar(menuBar)

		self.statusbar = self.CreateStatusBar(2)
		self.SetStatusWidths([-6, -1])
		self.SetStatusText("STOPPED", 1)

		self.nb = wx.Notebook(self)

		# the main page (main config / run controls)
		self.mainPage = wx.Panel(self.nb)
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
		self.HWinitEntry =  wx.Choice(self.mainPage, -1, choices=MetaData.HardwareInitLevels.descriptions())

		detConfigEntryLabel = wx.StaticText(self.mainPage, -1, "Detector")
		self.detConfigEntry = wx.Choice(self.mainPage, -1, choices=MetaData.DetectorTypes.descriptions())
		self.detConfigEntry.SetSelection(MetaData.DetectorTypes.MINERVA.index())

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
		self.runModeEntry =  wx.Choice(self.singleRunConfigPanel, -1, choices=MetaData.RunningModes.descriptions())
		self.Bind(wx.EVT_CHOICE, self.UpdateLEDgroups, self.runModeEntry)

		hwConfigEntryLabel = wx.StaticText(self.singleRunConfigPanel, -1, "HW config")
		self.hwConfigEntry = wx.Choice(self.singleRunConfigPanel, -1, choices=MetaData.HardwareConfigurations.descriptions())

		LEDgroupLabel = wx.StaticText(self.singleRunConfigPanel, -1, "LED groups used in LI")
		LEDgroupSizer = wx.GridSizer(2, 2)
		self.LEDgroups = []
		for letter in "ABCD":
			cb = wx.CheckBox(self.singleRunConfigPanel, -1, letter)
			cb.SetValue(True)
			cb.Disable()		# will be enabled when necessary
			self.LEDgroups.append(cb)
			LEDgroupSizer.Add(cb)

		LILevelEntryLabel = wx.StaticText(self.singleRunConfigPanel, -1, "LI light level")
		self.LILevelEntry = wx.Choice(self.singleRunConfigPanel, -1, choices=MetaData.LILevels.descriptions())
		self.LILevelEntry.SetSelection(MetaData.LILevels.MAX_PE.index())
		self.LILevelEntry.Disable()		# will be enabled when necessary

		singleRunConfigSizer = wx.GridSizer(3, 2, 10, 10)
		singleRunConfigSizer.AddMany([ (gatesEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.gatesEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (runModeEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.runModeEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (hwConfigEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.hwConfigEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (LEDgroupLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (LEDgroupSizer, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                               (LILevelEntryLabel, 0, wx.ALIGN_CENTER_VERTICAL),
		                               (self.LILevelEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL) ])
		singleRunConfigBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.singleRunConfigPanel, -1, "Single run Configuration"), wx.VERTICAL)
		singleRunConfigBoxSizer.Add(singleRunConfigSizer, 1, wx.EXPAND)

		self.singleRunConfigPanel.SetSizer(singleRunConfigBoxSizer)

		# run series config: allows user to select a predefined run series file and see what's in it.
		
		seriesFileLabel = wx.StaticText(self.runSeriesConfigPanel, -1, "Series Type: ")

		self.seriesFile = wx.Choice(self.runSeriesConfigPanel, -1, choices=MetaData.RunSeriesTypes.descriptions())
		self.Bind(wx.EVT_CHOICE, self.LoadRunSeriesFile, self.seriesFile)	

		seriesFileSizer = wx.BoxSizer(wx.HORIZONTAL)
		seriesFileSizer.Add(seriesFileLabel, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		seriesFileSizer.Add(self.seriesFile, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		
		self.seriesDescription = Tools.AutoSizingListCtrl(self.runSeriesConfigPanel, -1, style=wx.LC_REPORT | wx.LC_VRULES)
		self.seriesDescription.setResizeColumn(3)
		self.seriesDescription.InsertColumn(0, "", width=20)		# which subrun is currently being executed
		self.seriesDescription.InsertColumn(1, "#", width=25)
		self.seriesDescription.InsertColumn(2, "Run mode")#, width=150)
		self.seriesDescription.InsertColumn(3, "# gates")#, width=125)

		# center the "currently running indicator" column
		col = wx.ListItem()
		col.SetAlign(wx.LIST_FORMAT_CENTER)
		self.seriesDescription.SetColumn(0, col)
		
		self.moreInfoButton = wx.Button(self.runSeriesConfigPanel, ID_MOREINFO, "More details...")
		self.Bind(wx.EVT_BUTTON, self.SeriesMoreInfo, self.moreInfoButton)
		self.moreInfoButton.Disable()		# will be enabled when a file is loaded.
		
		runSeriesConfigSizer = wx.StaticBoxSizer(wx.StaticBox(self.runSeriesConfigPanel, -1, "Run series configuration"), wx.VERTICAL)
		runSeriesConfigSizer.Add(seriesFileSizer, flag=wx.EXPAND)
		runSeriesConfigSizer.Add(self.seriesDescription, 1, flag=wx.EXPAND)
		runSeriesConfigSizer.Add(self.moreInfoButton, flag=wx.ALIGN_CENTER_HORIZONTAL)
		runSeriesConfigSizer.InsertSpacer(0,10)
		runSeriesConfigSizer.InsertSpacer(2,10)	
		runSeriesConfigSizer.InsertSpacer(4,10)	

		self.runSeriesConfigPanel.SetSizer(runSeriesConfigSizer)
		

		# put the configuration stuff together in one sizer.
		runConfigSizer = wx.BoxSizer(wx.VERTICAL)
		runConfigSizer.Add(self.singleRunConfigPanel, proportion=1, flag=wx.EXPAND)
		runConfigSizer.Add(self.runSeriesConfigPanel, proportion=1, flag=wx.EXPAND)
		
		configSizer = wx.BoxSizer(wx.VERTICAL)
		configSizer.Add(globalConfigBoxSizer, flag=wx.EXPAND | wx.BOTTOM, border=5)
		configSizer.Add(runConfigSizer, proportion=1, flag=wx.EXPAND)

		# run control: start, stop, close windows
		self.startButton = wx.Button(self.mainPage, ID_START, "S&tart")
		self.startButton.SetBackgroundColour("green")
		self.Bind(wx.EVT_BUTTON, self.StartRunning, self.startButton)
		self.startButton.Disable()
		
		self.skipButton = wx.Button(self.mainPage, wx.ID_FORWARD, "Skip to &next subrun")
		self.skipButton.SetBackgroundColour("yellow")
		self.Bind(wx.EVT_BUTTON, self.SkipToNextSubrun, self.skipButton)
		self.skipButton.Disable()
		
		self.stopButton = wx.Button(self.mainPage, wx.ID_STOP)
		self.stopButton.SetBackgroundColour("red")
		self.Bind(wx.EVT_BUTTON, self.StopRunning, self.stopButton)
		self.stopButton.Disable()		# disabled until the 'start' button is pressed

		self.closeAllButton = wx.Button(self.mainPage, wx.ID_CLOSE, "&Close ET/DAQ windows")
		self.Bind(wx.EVT_BUTTON, self.CloseAllWindows, self.closeAllButton)
		self.closeAllButton.Disable()
		
		controlBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Run Control"), wx.VERTICAL)
		controlBoxSizer.AddMany( [ (self.startButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.skipButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.stopButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.closeAllButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ] )
		
		
		# a sizer for all the run control stuff (as separate from the status indicator)
		topSizer = wx.BoxSizer(wx.HORIZONTAL)
		topSizer.AddMany( [(configSizer, 1, wx.EXPAND | wx.RIGHT, 5), (controlBoxSizer, 1, wx.EXPAND | wx.LEFT, 5)] )
		
		# now the 'status' area
		self.onImage = wx.Bitmap(self.runmanager.ResourceLocation + "/LED_on.png", type=wx.BITMAP_TYPE_PNG)
		self.offImage = wx.Bitmap(self.runmanager.ResourceLocation + "/LED_off.png", type=wx.BITMAP_TYPE_PNG)
		
		self.runningIndicator = wx.StaticBitmap(self.mainPage, -1)
		self.runningIndicator.SetBitmap(self.offImage)

		runningIndicatorText = wx.StaticText(self.mainPage, -1, "Running?")
		
		runningIndicatorSizer = wx.BoxSizer(wx.VERTICAL)
		runningIndicatorSizer.Add(self.runningIndicator, 0, wx.ALIGN_CENTER_HORIZONTAL)
		runningIndicatorSizer.Add(runningIndicatorText, 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.indicators = {}
		indicatorTexts = {}
		indicatorSizers = {}
		for node in self.runmanager.readoutNodes:
			self.indicators[node.name] = wx.StaticBitmap(self.mainPage, -1)
			self.indicators[node.name].SetBitmap(self.offImage)
			indicatorTexts[node.name] = wx.StaticText(self.mainPage, -1, "%s\nnode" % node.name)
		
			indicatorSizers[node.name] = wx.BoxSizer(wx.VERTICAL)
			indicatorSizers[node.name].Add(self.indicators[node.name], 0, wx.ALIGN_CENTER_HORIZONTAL)
			indicatorSizers[node.name].Add(indicatorTexts[node.name], 0, wx.ALIGN_CENTER_HORIZONTAL)
		
		self.progressIndicator = wx.Gauge(self.mainPage, -1, range=6, name="Progress")		
		self.progressLabel = wx.StaticText(self.mainPage, -1, "No run in progress", style=wx.ALIGN_CENTER)
		progressSizer = wx.BoxSizer(wx.VERTICAL)
		progressSizer.Add(self.progressIndicator, 1, wx.EXPAND)
		progressSizer.Add(self.progressLabel, 1, wx.ALIGN_CENTER_HORIZONTAL)

		statusSizer = wx.StaticBoxSizer(wx.StaticBox(self.mainPage, -1, "Status"), wx.HORIZONTAL)
		statusSizer.Add(runningIndicatorSizer, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, border=15)
		for nodename in indicatorSizers:
			statusSizer.Add(indicatorSizers[nodename], 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, border=5)
		statusSizer.Add(progressSizer, 1, wx.ALIGN_RIGHT | wx.LEFT | wx.RIGHT, border=5)

		# one sizer to rule them all, one sizer to bind them...
		globalSizer = wx.BoxSizer(wx.VERTICAL)
		globalSizer.Add(topSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP | wx.ALL, border=10)
		globalSizer.Add(statusSizer, 0, wx.EXPAND | wx.ALIGN_TOP | wx.ALL, border=10)

		self.mainPage.SetSizer(globalSizer)

		# now the log page panel.
		self.logPage = wx.Panel(self.nb)

		logfileText = wx.StaticText( self.logPage, -1, wordwrap("Select log files you want to view (ctrl+click for multiple selections) and click the \"View log file(s)\" button below...", 400, wx.ClientDC(self)) )
		self.logfileList = Tools.AutoSizingListCtrl(self.logPage, -1, style=wx.LC_REPORT | wx.LC_VRULES | wx.LC_SORT_DESCENDING)
		self.logfileList.setResizeColumn(6)
		self.logfileList.InsertColumn(0, "Run")
		self.logfileList.InsertColumn(1, "Subrun")
		self.logfileList.InsertColumn(2, "Date")
		self.logfileList.InsertColumn(3, "Time (GMT)")
		self.logfileList.InsertColumn(4, "Run type")
		self.logfileList.InsertColumn(5, "Detector")
		self.logfileList.InsertColumn(6, "Controller")
		
		self.logFileButton = wx.Button(self.logPage, -1, "View selected log files")
		self.Bind(wx.EVT_BUTTON, self.ShowLogFiles, self.logFileButton)
		
		logBoxSizer = wx.StaticBoxSizer(wx.StaticBox(self.logPage, -1, "Logs"), orient=wx.VERTICAL)
		logBoxSizer.AddMany( [ (logfileText, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 10),
		                       (self.logfileList, 1, wx.EXPAND),
		                       (self.logFileButton, 0, wx.ALIGN_CENTER_HORIZONTAL) ] )
		                       
		self.logPage.SetSizer(logBoxSizer)
		
		# add the pages into the notebook.
		self.nb.AddPage(self.mainPage, "Run control")
		self.nb.AddPage(self.logPage, "Log files")
		
		self.Layout()

		self.Bind(Events.EVT_CONFIGUPDATED, self.UpdateLogFiles)
	
	################################################################################################
	# "Master" run control methods:
	#   starting and stopping data acquisition.
	################################################################################################

	def StartRunning(self, evt=None):
		""" Initiates the data acquisition process and disables the graphical controls.
		    Also does some preliminary checking to make sure values are sane. 

		    This method is usually called as the event handler for the "button" event
		    generated by clicking the green "Start" button.  """
		    
		if (self.singleRunButton.GetValue() == True):		# if this is a single run
			self.runmanager.runseries = RunSeries.RunSeries()
			
			LEDgroups = ""
			for cb in self.LEDgroups:
				if cb.GetValue() == True:
					LEDgroups += cb.GetLabelText()
			LEDcode = MetaData.LEDGroups.hash(MetaData.LEDGroups.LEDgroupsToLIgroupCode(LEDgroups))

			if LEDgroups == "ABC":
				errordlg = wx.MessageDialog( None, "The LED group combination \"ABC\" is not supported by the LI cards.  You probably want to use \"ABCD\" instead.", "LED group \"ABC\" not supported", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()
				
				return

			gates    = int(self.gatesEntry.GetValue())
			runMode  = MetaData.RunningModes.item(int(self.runModeEntry.GetSelection()), MetaData.HASH)
			hwcfg    = MetaData.HardwareConfigurations.item(int(self.hwConfigEntry.GetSelection()), MetaData.HASH)
			LIlevel  = MetaData.LILevels.item(int(self.LILevelEntry.GetSelection()), MetaData.HASH)

			run = RunSeries.RunInfo(gates, runMode, hwcfg, LIlevel, LEDcode)
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
		self.runmanager.hwinit       = MetaData.HardwareInitLevels.item(self.HWinitEntry.GetSelection(), MetaData.HASH)
		
		self.runmanager.StartDataAcquisition()
		if (self.runmanager.running):
			self.runEntry.Disable()
			self.subrunEntry.Disable()
			self.HWinitEntry.Disable()
			self.gatesEntry.Disable()
			self.detConfigEntry.Disable()
			self.runModeEntry.Disable()
			self.hwConfigEntry.Disable()
			self.febsEntry.Disable()
			
			self.singleRunButton.Disable()
			self.runSeriesButton.Disable()
			
			self.seriesFile.Disable()

			self.startButton.Disable()
			self.stopButton.Enable()
			
			self.lockdownEntry.Enable(False)

			self.SetStatusText("RUNNING", 1)
			self.runningIndicator.SetBitmap(self.onImage)
			
	def StopRunning(self, evt=None):
		""" Stops the data acquisition sequence and re-enables the controls.
		    Usually invoked as the event handler for the "button" event
		    generated by clicking the red "Stop" button. """
		    
		if self.runmanager.running:		
			self.runmanager.StopDataAcquisition()

		self.SetStatusText("STOPPED", 1)
		self.runningIndicator.SetBitmap(self.offImage)
		for nodename in self.indicators:
			self.indicators[nodename].SetBitmap(self.offImage)
		
		self.runEntry.Enable()
		self.gatesEntry.Enable()
		self.detConfigEntry.Enable()
		self.runModeEntry.Enable()
		self.hwConfigEntry.Enable()

		self.singleRunButton.Enable()
		self.runSeriesButton.Enable()
			
		self.seriesFile.Enable()

		self.UpdateLockedEntries()
		self.lockdownEntry.Enable()

		self.UpdateLockedEntries()
		self.lockdownEntry.Enable()

		self.stopButton.Disable()
		self.startButton.Enable()
		self.UpdateSeriesStatus()
		self.UpdateLogFiles()
		
		self.UpdateRunStatus( Events.UpdateProgressEvent(text="No run in progress", progress=(0,1)) )
		self.SetStatusText("Ready for next run.", 0)
	
	def WaitOnCleanup(self, evt):
		self.startButton.Disable()
		self.SetStatusText("Please wait while the previous run is cleaned up...", 0)
		self.SetStatusText("CLEANING UP", 1)
		
		dlg = wx.MessageDialog(self, "The last run was not stopped cleanly.  Please wait until it is cleaned up (the status bar will let you know when ready for next run).", "Last shutdown not clean", wx.OK | wx.ICON_INFORMATION )
		dlg.ShowModal()

	################################################################################################
	# "Mid-run" methods:
	#   pre-subrun, post-subrun, skipping to next subrun
	################################################################################################

	def PreSubrun(self, evt):
		""" Front-panel stuff that needs to happen before every subrun. """
		self.StoreLastRunConfig(evt)
		
		if evt.num_subruns > 1 and evt.current_subrun + 1 < evt.num_subruns:
			self.skipButton.Enable()
		else:
			self.skipButton.Disable()
		
	def PostSubrun(self, evt=None):
		""" Front-panel stuff that needs to happen after every subrun. """
		if hasattr(evt, "run") and evt.run is not None and hasattr(evt, "subrun") and evt.subrun is not None:
			self.subrunEntry.SetValue(evt.subrun)
			self.minRunSubrun = evt.subrun
			self.runEntry.SetRange(evt.run, 1000000)

		if self.autocloseEntry.IsChecked():
			self.CloseAllWindows()
					
		self.UpdateLogFiles()
		
	def SkipToNextSubrun(self, evt):
		""" Front-panel stuff that needs to happen when skipping to the next subrun. 

		    Usually invoked as the event handler for the "button" event generated
		    by clicking the yellow "Skip to next subrun" button in run series mode. """
		wx.PostEvent(self.runmanager, Events.EndSubrunEvent())		# tell the run manager that it's time to move on

	################################################################################################
	# Methods dealing with configuration:
	#   global config, last run config
	################################################################################################

	def GetGlobalConfig(self):
		"""
		Loads up configuration values from the master configuration database
		and configures the run manager appropriately.
		"""
		if Configuration.config_file_inaccessible:
			errordlg = wx.MessageDialog( None, "The configuration file does not exist.  Default values are being used.", "Config file inaccessible", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()

		self.runinfoFile                     = Configuration.params["Front end"]["runinfoFile"]
#		self.logfileLocation                 = Configuration.params["Master node"]["master_logfileLocation"]
		self.runmanager.ResourceLocation     = Configuration.params["Front end"]["ResourceLocation"]
		
	def GetLastRunConfig(self, evt=None):
		"""
		Loads up the configuration values used in the last subrun (as well as the run/subrun number)
		so as to give a hopefully intelligent set of default values.
		"""
		
		# default values.   they'll be updated below if the db exists and has the appropriate keys.
		key_values = { "run"            : 1, 
		               "subrun"         : 1,
		               "hwinit"         : MetaData.HardwareInitLevels.NO_HW_INIT.hash,
		               "detector"       : MetaData.DetectorTypes.UPSTREAM.hash,
		               "febs"           : 114,
		               "is_single_run"  : True,
		               "gates"          : 1500,
		               "runmode"        : "One shot",
		               "hwconfig"       : "Current state",
		               "ledgroups"      : "ABCD",
		               "lilevel"        : "Max PE",
		               "runseries_path" : None,
		               "runseries_file" : None,
		               "lockdown"       : True,
		               "autoclose"      : True }

		if not os.path.exists(self.runinfoFile):
			errordlg = wx.MessageDialog( None, "The database storing the last run configuration data appears to be missing.  Default configuration will be used...", "Last run configuration database missing", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()
		else:
			db = shelve.open(self.runinfoFile, 'r')
			
			has_all_keys = True
			for key in key_values.keys():
				if db.has_key(key):
					key_values[key] = db[key]
				else:
					has_all_keys = False
			
			if not has_all_keys:
				errordlg = wx.MessageDialog( None, "The database storing the last run configuration data appears to be corrupted.  Default configuration will be used for any unreadable values...", "Last run configuration database corrupted", wx.OK | wx.ICON_WARNING )
				errordlg.ShowModal()

			db.close()
			
		self.runEntry.SetRange(key_values["run"], 100000)
		self.runEntry.SetValue(key_values["run"])
		self.subrunEntry.SetValue(key_values["subrun"])
		self.HWinitEntry.SetSelection(MetaData.HardwareInitLevels.index(key_values["hwinit"]))
		self.detConfigEntry.SetSelection(MetaData.DetectorTypes.index(key_values["detector"]))
		self.febsEntry.SetValue(key_values["febs"])
		self.singleRunButton.SetValue(key_values["is_single_run"])
		self.runSeriesButton.SetValue(not(key_values["is_single_run"]))
		self.gatesEntry.SetValue(key_values["gates"])
		
		self.runModeEntry.SetSelection(MetaData.RunningModes.index(key_values["runmode"]))
		self.hwConfigEntry.SetSelection(MetaData.HardwareConfigurations.index(key_values["hwconfig"]))
		self.LILevelEntry.SetSelection(MetaData.LILevels.index(key_values["lilevel"]))
		
		self.lockdownEntry.Check(key_values["lockdown"])
		self.autocloseEntry.Check(key_values["autoclose"])
	
		for cb in self.LEDgroups:
			cb.SetValue(cb.GetLabelText() in key_values["ledgroups"])
		
		# these are initialized here to None, but will be updated
		self.seriesFilename = None
		self.seriesPath = None

		if key_values["runseries_path"] != None:
			self.seriesFile.SetStringSelection(MetaData.RunSeriesTypes.description((key_values["runseries_file"])))

		self.LoadRunSeriesFile()
		
		# the minimum subrun allowed for the lowest run.  
		# if the user raises the run number, the subrun will be returned to 1,
		# so if s/he subsequently lowers it again, we need to know what to set the the minimum
		# back to.
		self.minRunSubrun = self.subrunEntry.GetValue()		

		self.UpdateLockedEntries()
		self.UpdateLEDgroups()
		self.runEntry.Enable()
		self.startButton.Enable()
	
	def StoreLastRunConfig(self, evt=None):
		"""
		Stores the currently selected configuration for use as default values the next time.
		Prevents shifters from having to necessarily remember the settings between runs.
		"""
		
		try:
			db = shelve.open(self.runinfoFile)
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The database storing the run/subrun data cannot be accessed.  Run/subrun will not be retained...", "Run/subrun database inaccessible", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
		else:
			if hasattr(evt, "first_subrun") and hasattr(evt, "current_subrun"):
				subrun = evt.first_subrun + evt.current_subrun
			else:
				subrun = int(self.subrunEntry.GetValue())
				
			if self.runmanager.running:		# this function can be called from the menu, too
				subrun += 1	# INCREMENT it to avoid data overwriting in the event of a crash

			db["run"] = int(self.runEntry.GetValue())
			db["subrun"] = subrun
			db["hwinit"] = int(MetaData.HardwareInitLevels.item(self.HWinitEntry.GetSelection(), MetaData.HASH))
			db["detector"] = int(MetaData.DetectorTypes.item(self.detConfigEntry.GetSelection(), MetaData.HASH))
			db["febs"] = int(self.febsEntry.GetValue())
			db["is_single_run"] = self.singleRunButton.GetValue()
			db["gates"] = int(self.gatesEntry.GetValue())
			db["runmode"] = MetaData.RunningModes.item(self.runModeEntry.GetSelection(), MetaData.HASH)
			db["hwconfig"] = MetaData.HardwareConfigurations.item(self.hwConfigEntry.GetSelection(), MetaData.HASH)

			LEDgroups = ""
			for cb in self.LEDgroups:
				if cb.GetValue() == True:
					LEDgroups += cb.GetLabelText()
			db["ledgroups"] = LEDgroups
			db["lilevel"] = MetaData.LILevels.item(self.LILevelEntry.GetSelection(), MetaData.HASH)
			db["runseries_file"] = self.seriesFilename
			db["runseries_path"] = self.seriesPath
			
			db["autoclose"] = self.autocloseEntry.IsChecked()
			db["lockdown"] = self.lockdownEntry.IsChecked()

			db.close()

	################################################################################################
	# GUI-related methods (mostly handling events)
	#  
	################################################################################################
	
	def BlinkWindow(self, evt=None):
		""" Makes the window "blink" by alternating
		    the normal background color with an obnoxious one. """
		
		if self.default_background is None:
			self.default_background = self.mainPage.GetBackgroundColour()		

		# create a new tab in the notebook
		# to receive the acknowledgement
		if self.nb.GetPageCount() == 2:
			self.notificationPage = wx.Panel(self.nb)
			text1 = wx.StaticText(self.notificationPage, -1, "    Data taking \nwas interrupted!")
			font1 = text1.GetFont()
			font1.SetPointSize(24)
			text1.SetFont(font1)
			text2 = wx.StaticText(self.notificationPage, -1, "Click the button to acknowledge and begin a new run.")
			acknowledgeButton = wx.Button(self.notificationPage, -1, "Acknowledge data taking stoppage")
			self.Bind(wx.EVT_BUTTON, self.StopBlinking, acknowledgeButton)
		
			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(text1, proportion=1, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, border = 100)
			sizer.Add(acknowledgeButton, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.TOP, border=25)
			sizer.Add(text2, proportion=1, flag=wx.ALIGN_CENTER_HORIZONTAL)
			self.notificationPage.SetSizer(sizer)
			self.nb.AddPage(self.notificationPage, "Data taking interrupted")
			
		if self.default_background is None:
			self.default_background = self.mainPage.GetBackgroundColour()		

		self.nb.ChangeSelection(2)
		
		colors = (wx.RED, self.default_background)
		bg = self.notificationPage.GetBackgroundColour()
		newcolor = colors[0] if bg == colors[1] else colors[1]

		self.notificationPage.SetBackgroundColour(newcolor)
			
	def CheckRunNumber(self, evt=None):
		""" Ensures that the run number can't be lowered
		    past the current run number, and sets the 
		    subrun number accordingly. """
		    
		if self.runEntry.GetValue() < self.runEntry.GetMin():
			self.runEntry.SetValue(self.runEntry.GetMin())
		
		if self.runEntry.GetValue() > self.runEntry.GetMax():
			self.runEntry.SetValue(self.runEntry.GetMax())
		
		if self.runEntry.GetValue() == self.runEntry.GetMin():
			self.subrunEntry.SetValue(self.minRunSubrun)
		else:
			self.subrunEntry.SetValue(1)

	def CloseAllWindows(self, evt=None):
		""" Closes any open ET/DAQ windows and disables the 'close windows' button. """
		self.runmanager.CloseWindows()
		self.runmanager.UpdateWindowCount()

	def LoadRunSeriesFile(self, evt=None):
		""" Loads the run series file corresponding to the selection
		    the user has made in the drop-down box.
		    
		    Usually invoked as the event handler for the wx.CHOICE event
		    generated by making a selection in the list. """
		    
		# don't want to switch run series in the middle of a run!
		if self.runmanager.running:
			return
			
		self.seriesDescription.DeleteAllItems()
		self.moreInfoButton.Disable()

		filename = MetaData.RunSeriesTypes.code(self.seriesFile.GetStringSelection())
		
		try:
			db = shelve.open(Configuration.params["Front end"]["runSeriesLocation"]+"/"+filename,'r')
			self.runmanager.runseries = db["series"]
			db.close()
		except (anydbm.error, KeyError):
			errordlg = wx.MessageDialog( None, "Unable to load file for selected run series.", "Load Error", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			return False

		self.seriesFilename = filename
		self.seriesPath = Configuration.params["Front end"]["runSeriesLocation"]

		for runinfo in self.runmanager.runseries.Runs:
			index = self.seriesDescription.InsertStringItem(sys.maxint, "")         # first column is which subrun is currently being executed
			self.seriesDescription.SetStringItem(index, 1, str(self.runmanager.runseries.Runs.index(runinfo)+1))
			self.seriesDescription.SetStringItem(index, 2, MetaData.RunningModes.description(runinfo.runMode))
			self.seriesDescription.SetStringItem(index, 3, str(runinfo.gates))

		self.runmanager.subrun = 0
		self.moreInfoButton.Enable()
		self.UpdateSeriesStatus()

		return True

	def OnTimeToClose(self, evt):
		""" The event handler invoked when exiting via the menu
		    or via the 'close' button on the window border. 
		    
		    Tries to make sure any running is stopped and the
		    run manager has been shut down cleanly before allowing
		    itself to be closed.  """
		    
		if self.runmanager.running:
			# try to stop things nicely.
			try:
				self.runmanager.StopDataAcquisition()
			except:
				pass		# if we can't, oh well.  we're closing anyway.
		if self.blinkThread is not None and self.blinkThread.is_alive():
			self.blinkThread.Abort()
			self.blinkThread.join()

		self.runmanager.Cleanup()
			
		self.CloseAllWindows()

		self.Destroy()
		
	def StopBlinking(self, evt=None):
		self.blinkThread.Abort()
		self.blinkThread.join()
		
		self.nb.DeletePage(2)
		self.nb.ChangeSelection(0)
		
		
	def UserAlert(self, evt):
		""" Gets the user's attention. """
		
		# sets the window manager hint
		self.RequestUserAttention()
		
		# now... if it's a real emergency, we need to do some other stuff.
		if hasattr(evt, "alerttype") and evt.alerttype == "alarm":
			if self.blinkThread is not None and self.blinkThread.is_alive():
				self.blinkThread.Abort()
				self.blinkThread.join()
			
			self.blinkThread = Threads.BlinkThread(self)
		
	def UpdateCloseWindows(self, evt):
		""" Enables/disables the "close all windows" button
		    according to how many windows are open. """
		    
		if evt.count > 0:
			self.closeAllButton.Enable()
		else:
			self.closeAllButton.Disable()

	def UpdateLEDgroups(self, evt=None):
		""" Enables/disables the LED selection checkboxes
		    based on whether or not the current run type
		    includes light injection. """
		   
		runMode = self.runModeEntry.GetSelection()
		if runMode == MetaData.RunningModes.LI.index() or runMode == MetaData.RunningModes.MIXED_NUMI_LI.index():
			for cb in self.LEDgroups:
				cb.Enable()
			self.LILevelEntry.Enable()
		else:
			for cb in self.LEDgroups:
				cb.Disable()
			self.LILevelEntry.Disable()

	def UpdateLockedEntries(self, evt=None):
		""" Enables/disables the "global" configuration options
		    based on whether the "lock down global entries" menu
		    option is checked. """
		    
		for entry in (self.HWinitEntry, self.febsEntry, self.detConfigEntry):
			if self.lockdownEntry.IsChecked():
				entry.Disable()
			else:
				entry.Enable()		

	def UpdateLogFiles(self, evt=None):
		""" Updates the log files shown in the list on the log file tab. """
		
		if evt is not None and evt.GetEventType() == EVT_CONFIGUPDATED:		# we only need to reload the config if it's changed!
			self.GetGlobalConfig()

		self.logfileList.DeleteAllItems()
		self.logfileNames = []
		self.logfileInfo = []
		
		for path in Configuration.params["Front end"]["logFileLocations"]:
			try:
				for filename in os.listdir(path):
					if os.path.isdir(filename):
						continue
					fileinfo = SortTools.parseLogfileName(filename)
					if fileinfo is not None:
						fileinfo["path"] = path
						self.logfileNames.append(filename)
						self.logfileInfo.append(fileinfo)
			except OSError:
				continue
				
		if len(self.logfileNames) > 0:
			self.logfileNames.sort(SortTools.SortLogFiles)
			self.logfileInfo.sort(SortTools.SortLogData)
			
			self.logfileNames.reverse()
			self.logfileInfo.reverse()
		else:
			self.logfileNames = None
			self.logfileInfo = None
			
		column_map = {0: "run", 1: "subrun", 2: "date", 3: "time", 4: "type", 5: "detector", 6: "controller"}

		if self.logfileNames is not None and len(self.logfileNames) > 0:
			for fileinfo in self.logfileInfo:
				index = self.logfileList.InsertStringItem(sys.maxint, fileinfo["run"])
				for i in range(1,len(column_map)):
					self.logfileList.SetStringItem(index, i, fileinfo[column_map[i]])
		else:
			self.logfileList.InsertStringItem(0, "Log directory is empty or inaccessible.")
		
	def UpdateNodeStatus(self, evt):
		""" Updates the 'LED' indicating the status of a particular readout node. 
		
		    The event passed should contain two attributes:
		        'node', the name of the node,
		    and 'on',   a boolean indicating whether this node's 'LED' should be on or not. """
		img = self.onImage if evt.on else self.offImage
		self.indicators[evt.node].SetBitmap(img)

	def UpdateRunConfig(self, evt=None):
		""" Shows either the 'single run' or 'run series' panel
		    depending on which radio button is selected.
		    
		    Usually invoked as the event handler for the EVT_RADIO
		    that's generated by picking one or the other of the buttons. """
		    
		showSingleRun = self.singleRunButton.GetValue()
		self.singleRunConfigPanel.Show(showSingleRun)
		self.runSeriesConfigPanel.Show(not(showSingleRun))
		self.skipButton.Show(not(showSingleRun))

		if not showSingleRun:
			self.LoadRunSeriesFile()
		
		self.mainPage.Layout()
		self.mainPage.Refresh()
		self.mainPage.Update()

	def UpdateRunStatus(self, evt):
		""" Updates the progress gauge text label and value.
		
		    Values are set via the attributes of the event:
		    any text to be displayed below the progress bar
		    should be contained in the attribute 'text'.
		    If you want the gauge in 'indeterminate' mode,
		    set 'progress' to (0,0); otherwise, 'progress'
		    should be (current, total). """
		if evt.text is not None:
			self.progressLabel.SetLabel(evt.text)
		
		if evt.progress == (0,0):		# indeterminate mode
			self.progressIndicator.Pulse()
		else:
			self.progressIndicator.SetRange(evt.progress[1])
			self.progressIndicator.SetValue(evt.progress[0])
		
	def UpdateSeriesStatus(self, evt=None):
		""" Updates the run series list so that the run
		    that is currently executing is highlighted in green
		    and has a little 'play' symbol next to it.
		    
		    If the run is stopped, the next subrun to be
		    executed is highlighted in yellow and a 'stop'
		    symbol is displayed next to it."""
		symbol = ""
		color = ""
		if self.runmanager.running:
			symbol = u"\u25b7"		# a right-facing triangle: like a "play" symbol
			color = wx.NamedColour("green")
		else:
			symbol = u"\u25a1"		# a square: like a "stop" symbol
			color = wx.NamedColour("yellow")

		if self.runSeriesButton.GetValue() == True:		# if this is a run SERIES
			index = -1
			while True:
				index = self.seriesDescription.GetNextItem(index)
			
				if index == -1:
					break
			
				if index == self.runmanager.subrun:
					self.seriesDescription.SetStringItem(index, 0, symbol)
					self.seriesDescription.SetItemBackgroundColour(index, color)
					self.seriesDescription.EnsureVisible(index)
				else:
					self.seriesDescription.SetStringItem(index, 0, "")
					self.seriesDescription.SetItemBackgroundColour(index, wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
	
	################################################################################################
	# Methods that create new windows or dialogs
	#  
	################################################################################################

	def SeriesMoreInfo(self, evt=None):
		""" Opens a new window giving more info about the currently-selected run series. """
		infowindow = Frames.RunSeriesInfoFrame(self, self.seriesFilename, self.runmanager.runseries)
		infowindow.Show()
			
	def ShowLogFiles(self, evt=None):
		""" Opens a new window with a tabbed interface displaying all of the selected log files. """
		# if there are no log files in the display...
		if self.logfileNames is None:
			return
	
		filenames = []
		
		index = -1
		while True:
			index = self.logfileList.GetNextSelected(index)
			
			if index == -1:
				break
			
			filenames.append(self.logfileInfo[index]["path"] + "/" + self.logfileNames[index])
	
		logframe = Frames.LogFrame(self, filenames)
		logframe.Show()

	def ShowErrorMsg(self, evt):
		""" Shows an error notification window to the user.
		
		    The dialog title should be passed as 'evt.title' and 
		    text to be displayed should be passed as 'evt.text'. """
		errordlg = wx.MessageDialog( self, evt.text, evt.title, wx.OK | wx.ICON_ERROR )
		errordlg.ShowModal()
		

	
#########################################################
#   MainApp
#########################################################

class MainApp(wx.App):
	def OnInit(self):
		try:
			environment = {}
			environment["DAQROOT"] = os.environ["DAQROOT"]
			environment["ET_HOME"] = os.environ["ET_HOME"]
			environment["ET_LIBROOT"] = os.environ["ET_LIBROOT"]
			environment["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
		except KeyError:
			errordlg = wx.MessageDialog( None, "Your environment appears to be missing the necessary configuration.  Did you source the appropriate setup script(s) before starting the run control?", "Incorrect environment", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			return False
		else:
			frame = MainFrame(None, "MINERvA run control")
			frame.runmanager.environment = environment
			self.SetTopWindow(frame)
			frame.Show(True)
			return True

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MainApp(redirect=False)
	app.MainLoop()

