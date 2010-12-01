#!/usr/bin/python
"""
  RunControlConfiguration.py:
  Contains the graphical implementation of an options
  setter for the run control.  Mainly intended to be
  run as a standalone program, but can also be imported
  into another wx application.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import wx
import shelve
import anydbm

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.backend import ReadoutNode
from mnvruncontrol.backend import Events

#########################################################
#   OptionsFrame
#########################################################

class OptionsFrame(wx.Frame):
	""" A window for configuration of various options in the run control """
	def __init__(self, parent=None):
		wx.Frame.__init__(self, parent, -1, "Run control configuration", size=(600,400))
		
		self.parent = parent

		try:
			db = shelve.open(Defaults.CONFIG_DB_LOCATION)
		except anydbm.error:
			# the user has already been informed once (when the main frame was opened)
			# if the DB is not accessible, so we'll just silently go to the defaults here.
			runinfoFile = Defaults.RUN_SUBRUN_DB_LOCATION_DEFAULT
			logfileLocation = Defaults.LOGFILE_LOCATION_DEFAULT
			etSystemFileLocation = Defaults.ET_SYSTEM_LOCATION_DEFAULT
			rawdataLocation = Defaults.RAW_DATA_LOCATION_DEFAULT
			ResourceLocation = Defaults.RESOURCE_LOCATION_DEFAULT
			readoutNodes = [ ReadoutNode.ReadoutNode("local", "localhost") ]
		else:
			try:	runinfoFile = db["runinfoFile"]
			except KeyError: runinfoFile = Defaults.RUN_SUBRUN_DB_LOCATION_DEFAULT

			try:	logfileLocation = db["logfileLocation"]
			except KeyError: logfileLocation = Defaults.LOGFILE_LOCATION_DEFAULT
			
			try:	etSystemFileLocation = db["etSystemFileLocation"]
			except KeyError: etSystemFileLocation = Defaults.ET_SYSTEM_LOCATION_DEFAULT
			
			try:	rawdataLocation = db["rawdataLocation"]
			except KeyError: rawdataLocation = Defaults.RAW_DATA_LOCATION_DEFAULT
			
			try:	ResourceLocation = db["ResourceLocation"]
			except KeyError: ResourceLocation = Defaults.RESOURCE_LOCATION_DEFAULT
			
			try: readoutNodes = db["readoutNodes"]
			except KeyError: readoutNodes = [ ReadoutNode.ReadoutNode("local", "localhost") ]

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
		
		ResourceLocationLabel = wx.StaticText(panel, -1, "Resource files location")
		self.ResourceLocationEntry = wx.TextCtrl(panel, -1, ResourceLocation)
		
		readoutNodesLabel = wx.StaticText(panel, -1, "Readout nodes:")
#		self.readoutNodesEntry = wx.
		
		pathsGridSizer = wx.GridSizer(6, 2, 10, 10)
		pathsGridSizer.Add(runInfoDBLabel,                               flag=wx.ALIGN_CENTER_VERTICAL)
		pathsGridSizer.Add(self.runInfoDBEntry,            proportion=0, flag=wx.EXPAND)
		pathsGridSizer.Add(logfileLocationLabel,                         flag=wx.ALIGN_CENTER_VERTICAL)
		pathsGridSizer.Add(self.logfileLocationEntry,      proportion=0, flag=wx.EXPAND)
		pathsGridSizer.Add(etSystemFileLocationLabel,                    flag=wx.ALIGN_CENTER_VERTICAL)
		pathsGridSizer.Add(self.etSystemFileLocationEntry, proportion=0, flag=wx.EXPAND)
		pathsGridSizer.Add(rawDataLocationLabel,                         flag=wx.ALIGN_CENTER_VERTICAL)
		pathsGridSizer.Add(self.rawDataLocationEntry,      proportion=0, flag=wx.EXPAND)
		pathsGridSizer.Add(ResourceLocationLabel,                        flag=wx.ALIGN_CENTER_VERTICAL)
		pathsGridSizer.Add(self.ResourceLocationEntry,     proportion=0, flag=wx.EXPAND)

		pathsSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Paths"), orient=wx.VERTICAL)
		pathsSizer.Add(pathsGridSizer, 1, wx.EXPAND)
		
#		DAQrootLabel = wx.StaticText(panel, -1, "$DAQROOT")
#		DAQrootText = wx.TextCtrl(panel, -1, os.environ["DAQROOT"], style=wx.TE_READONLY)
#		DAQrootText.Disable()
#		
#		EThomeLabel = wx.StaticText(panel, -1, "$ET_HOME")
#		EThomeText = wx.TextCtrl(panel, -1, os.environ["ET_HOME"], style=wx.TE_READONLY)
#		EThomeText.Disable()
#		
#		environGridSizer = wx.GridSizer(2, 2, 10, 10)
#		environGridSizer.AddMany( ( DAQrootLabel, (DAQrootText, 1, wx.EXPAND),
#		                            EThomeLabel,  (EThomeText, 1, wx.EXPAND) ) )
#		
#		environSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Environment"), orient=wx.VERTICAL)
#		environSizer.Add(environGridSizer, flag = wx.EXPAND)
		
		saveButton = wx.Button(panel, wx.ID_SAVE)
		self.Bind(wx.EVT_BUTTON, self.SaveAll, saveButton)

		cancelButton = wx.Button(panel, wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.Cancel, cancelButton)

		buttonSizer = wx.GridSizer(1, 2, 10, 10)
		buttonSizer.AddMany( ( (saveButton, 1, wx.ALIGN_CENTER_HORIZONTAL), (cancelButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ) )

		globalSizer = wx.BoxSizer(wx.VERTICAL)
		globalSizer.Add(warningText, flag=wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, border=10)
		globalSizer.Add(pathsSizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
#		globalSizer.Add(environSizer, flag=wx.ALL | wx.EXPAND, border=10)
		globalSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER_HORIZONTAL)		
		panel.SetSizer(globalSizer)
		
		self.Layout()
		
	def SaveAll(self, evt=None):
		try:
			db = shelve.open(Defaults.CONFIG_DB_LOCATION, "w")
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The configuration file cannot be opened.  Values will not be saved.", "Config file inaccessible", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()
		else:
			db["runinfoFile"] = self.runInfoDBEntry.GetValue()
			db["logfileLocation"] = self.logfileLocationEntry.GetValue()
			db["etSystemFileLocation"] = self.etSystemFileLocationEntry.GetValue()
			db["rawdataLocation"] = self.rawDataLocationEntry.GetValue()
#			db["ResourceLocation"] = self.ResourceLocationEntry.GetValue()
			
			db.close()
		
		if self.parent is not None:	
			wx.PostEvent(self.parent, Events.ConfigUpdatedEvent())

		self.Close()
		
	def Cancel(self, evt=None):
		self.Close()

#########################################################
#   MainApp
#########################################################

class MainApp(wx.App):
	def OnInit(self):
		frame = OptionsFrame()
		self.SetTopWindow(frame)
		frame.Show(True)
		return True

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MainApp(redirect=False)
	app.MainLoop()

