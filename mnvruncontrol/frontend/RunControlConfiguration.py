#!/usr/bin/python
"""
  RunControlConfiguration.py:
  Contains the graphical implementation of an options
  setter for the run control.  Mainly intended to be
  run as a standalone program, but can also be imported
  into another wx application as necessary.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import os
import sys
import shelve
import anydbm
import os.path

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import MetaData

# only do the graphical stuff if $DISPLAY is defined!
if "DISPLAY" in os.environ and len(os.environ["DISPLAY"]) > 0:
	import wx
	from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
	from wx.lib.mixins.listctrl import ListRowHighlighter
	from wx.lib.mixins.listctrl import TextEditMixin
	from mnvruncontrol.backend import Events

	# there are a couple controls for simple types that can't be done automatically
	# because they use the metadata as the source of their options
	metadata_ctrls = { "detectorType" : MetaData.DetectorTypes,
	                   "hwInitLevel"  : MetaData.HardwareInitLevels }

	#########################################################
	#   Configuration
	#########################################################

	class ConfigurationFrame(wx.Frame):
		""" A window for configuration of various options in the run control """
		def __init__(self, parent=None):
			wx.Frame.__init__(self, parent, -1, "Run control configuration", size=(600,600))
		
			self.parent = parent

			panel = wx.Panel(self)
			nb = wx.Notebook(panel)
			self.pages = {}
			for pagename in Configuration.names:
				self.pages[pagename] = wx.Panel(nb)
		
		
			###########################################################################
			# first, the ones that can be automatically placed on the panels
			###########################################################################
		
			labels = {}
			self.entries = {}
			gridSizers = {}
		
			for param_set in Configuration.params:
				labels[param_set] = {}
				self.entries[param_set] = {}

				for param_name in Configuration.params[param_set]:
					# any iterable types will need to be added by hand.
					if hasattr(Configuration.params[param_set][param_name], '__iter__') \
					  or param_name in metadata_ctrls:
						continue

					labels[param_set][param_name] = wx.StaticText(self.pages[param_set], -1, Configuration.names[param_set][param_name])
					# booleans are special.  they need checkboxes instead of textctrls
					if isinstance(Configuration.params[param_set][param_name], bool):
						self.entries[param_set][param_name] = wx.CheckBox(self.pages[param_set], -1)
						self.entries[param_set][param_name].SetValue(Configuration.params[param_set][param_name])
					else:
						self.entries[param_set][param_name] = wx.TextCtrl(self.pages[param_set], -1, str(Configuration.params[param_set][param_name]))
					
				gridSizers[param_set] = wx.FlexGridSizer(len(labels), 2, 5, 5)
				for param_name in labels[param_set]:
					gridSizers[param_set].Add(labels[param_set][param_name], flag=wx.ALIGN_CENTER_VERTICAL)
					gridSizers[param_set].Add(self.entries[param_set][param_name], proportion=0, flag=wx.EXPAND)
					gridSizers[param_set].SetFlexibleDirection(wx.HORIZONTAL)
					gridSizers[param_set].AddGrowableCol(1)
				
				self.pages[param_set].SetSizer(gridSizers[param_set])
			
		
			###########################################################################
			# now anything that needs to be added by hand
			###########################################################################
		
			self.AddButtons = {}
			self.DeleteButtons = {}

#			# first: log file locations
#			labels["Front end"]["logFileLocations"] = wx.StaticText(self.pages["Front end"], -1, Configuration.names["Front end"]["logFileLocations"])
#			self.entries["Front end"]["logFileLocations"] = AutoSizingEditableListCtrl(self.pages["Front end"], style=wx.LC_REPORT | wx.LC_HRULES)
#			self.entries["Front end"]["logFileLocations"].InsertColumn(0, "Location")
#		
#			for location in Configuration.params["Front end"]["logFileLocations"]:
#				self.entries["Front end"]["logFileLocations"].InsertStringItem(sys.maxint, location)

#			self.AddButtons["logFileLocations"] = wx.Button(self.pages["Front end"], wx.ID_ADD, style=wx.BU_EXACTFIT)
#			self.pages["Front end"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["logFileLocations"])

#			self.DeleteButtons["logFileLocations"] = wx.Button(self.pages["Front end"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
#			self.pages["Front end"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["logFileLocations"])
#		
#			buttonSizer = wx.BoxSizer(wx.VERTICAL)
#			buttonSizer.AddMany ( ( (self.AddButtons["logFileLocations"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["logFileLocations"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
#		
#			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
#			entrySizer.AddMany( ( (self.entries["Front end"]["logFileLocations"], 1, wx.EXPAND), (buttonSizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL) ) )
#		
#			gridSizers["Front end"].Add(labels["Front end"]["logFileLocations"], flag=wx.ALIGN_CENTER_VERTICAL)
#			gridSizers["Front end"].Add(entrySizer, proportion=0, flag=wx.EXPAND)

			# first: config choices that need list boxes.
			for key in metadata_ctrls:
				labels["Master node"][key] = wx.StaticText(self.pages["Master node"], -1, Configuration.names["Master node"][key])
				self.entries["Master node"][key] = wx.Choice(self.pages["Master node"], -1, choices=metadata_ctrls[key].descriptions())
				self.entries["Master node"][key].SetSelection( metadata_ctrls[key].index(Configuration.params["Master node"][key]) )
				gridSizers["Master node"].Add(labels["Master node"][key], flag=wx.ALIGN_CENTER_VERTICAL)
				gridSizers["Master node"].Add(self.entries["Master node"][key], proportion=0, flag=wx.EXPAND)
			
			# next: remote node config
			labels["Master node"]["nodeAddresses"] = wx.StaticText(self.pages["Master node"], -1, Configuration.names["Master node"]["nodeAddresses"])
			self.entries["Master node"]["nodeAddresses"] = AutoSizingEditableListCtrl(self.pages["Master node"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["Master node"]["nodeAddresses"].InsertColumn(0, "Node type")
			self.entries["Master node"]["nodeAddresses"].InsertColumn(1, "Name")
			self.entries["Master node"]["nodeAddresses"].InsertColumn(2, "Address (IPv4/DNS)")
		
			for node in Configuration.params["Master node"]["nodeAddresses"]:
				index = self.entries["Master node"]["nodeAddresses"].InsertStringItem(sys.maxint, str(node["type"]))
				self.entries["Master node"]["nodeAddresses"].SetStringItem(index, 1, node["name"])
				self.entries["Master node"]["nodeAddresses"].SetStringItem(index, 2, node["address"])

			self.AddButtons["nodeAddresses"] = wx.Button(self.pages["Master node"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["nodeAddresses"])

			self.DeleteButtons["nodeAddresses"] = wx.Button(self.pages["Master node"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["nodeAddresses"])
		
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons["nodeAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["nodeAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
		
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.AddMany( ( (self.entries["Master node"]["nodeAddresses"], 1, wx.EXPAND), (buttonSizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL) ) )
		
			gridSizers["Master node"].Add(labels["Master node"]["nodeAddresses"], flag=wx.ALIGN_CENTER_VERTICAL)
			gridSizers["Master node"].Add(entrySizer, proportion=0, flag=wx.EXPAND)
	
			gridSizers["Master node"].SetFlexibleDirection(wx.BOTH)

			# these are added like this so that they show up in a predictable order
			for name in ("Front end", "Hardware", "Socket setup", "Master node", "Readout nodes", "Monitoring nodes", "MTest beam nodes", "Logging"):
				nb.AddPage(self.pages[name], name)
			
			saveButton = wx.Button(panel, wx.ID_SAVE)
			self.Bind(wx.EVT_BUTTON, self.SaveAll, saveButton)

			cancelButton = wx.Button(panel, wx.ID_CANCEL)
			self.Bind(wx.EVT_BUTTON, self.Cancel, cancelButton)

			buttonSizer = wx.GridSizer(1, 2, 10, 10)
			buttonSizer.AddMany( ( (saveButton, 1, wx.ALIGN_CENTER_HORIZONTAL), (cancelButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ) )

			globalSizer = wx.BoxSizer(wx.VERTICAL)
			globalSizer.Add(nb, flag=wx.EXPAND, proportion=1)
			globalSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER_HORIZONTAL, proportion=0)		
			panel.SetSizer(globalSizer)

		
			self.Layout()
		
		def AddNode(self, evt):
			""" Add a node to the list. """
			for itemname in self.AddButtons:
				if evt.EventObject == self.AddButtons[itemname]:
					for page in self.entries:
						if itemname in self.entries[page]:
							itemlocation = self.entries[page]
							break
				
					index = itemlocation[itemname].InsertStringItem(sys.maxint, "[text]")
					for col in range(1, itemlocation[itemname].GetColumnCount()):
						itemlocation[itemname].SetStringItem(index, col, "[text]")
	
		def DeleteNodes(self, evt):
			""" Delete all selected nodes from the list. """
			for nodename in self.DeleteButtons:
				if evt.EventObject == self.DeleteButtons[nodename]:
					index = -1
					toDelete = []

					for page in self.entries:
						if itemname in self.entries[page]:
							itemlocation = self.entries[page]
							break

					while True:
						index = itemlocation[nodename].GetNextSelected(index)
		
						if index == -1:
							break
						else:
							toDelete.append(index)
			
					# want to delete from the back to the front so that we don't skip any
					toDelete = sorted(toDelete, reverse=True)
					for item in toDelete:
						itemlocation[nodename].DeleteItem(item)
		
		def SaveAll(self, evt=None):
			""" Save the configuration. """
		
			locations_to_try = ["%s/%s" % (Defaults.CONFIG_DB_LOCATION, Defaults.CONFIG_DB_NAME)]
			if Configuration.user_specified_db:
				locations_to_try = [Configuration.user_specified_db] + locations_to_try
			
			found_location = False
			for location in locations_to_try:
				try:
					db = shelve.open(os.path.abspath(location), "c")  
				except anydbm.error, e:
					continue
				else:
					found_location = True
					# first do the automatic ones
					for param_set in self.entries:
						for param_name in self.entries[param_set]:
							if isinstance(self.entries[param_set][param_name], wx.TextCtrl) or isinstance(self.entries[param_set][param_name], wx.CheckBox):
								# note that this must saved as the correct type (hence the Configuration.types() call).
								db[param_name] = Configuration.types[param_set][param_name](self.entries[param_set][param_name].GetValue())
			
					# now any that need to be handled in a particular way
			
					# first: choices
					for item in metadata_ctrls:
						db[item] = metadata_ctrls[item].item(self.entries["Master node"][item].GetSelection()).hash
			
					# now remote nodes
					nodelist= []
					index = -1
					while True:
						index = self.entries["Master node"]["nodeAddresses"].GetNextItem(index)
				
						if index == -1:
							break
						
						try:
							nodetype = int(self.entries["Master node"]["nodeAddresses"].GetItem(index, 0).GetText())
						except ValueError:
							nodetype = 1		# default to READOUT
				
						nodedescr = { "type":     nodetype,
						              "name":     self.entries["Master node"]["nodeAddresses"].GetItem(index, 1).GetText(),
						              "address" : self.entries["Master node"]["nodeAddresses"].GetItem(index, 2).GetText() }
						nodelist.append(nodedescr)
				
					db["nodeAddresses"] = nodelist
			
					# need to specifically close the DB so that it saves correctly
					db.close()
				
					break
		
			if found_location:
				if self.parent is not None:	
					wx.PostEvent(self.parent, Events.ConfigUpdatedEvent())
				else:
					print "Wrote configuration to '%s'." % location

			self.Close()
		
		def Cancel(self, evt=None):
			self.Close()

	#########################################################
	#   AutoSizingEditableListCtrl
	#########################################################
	class AutoSizingEditableListCtrl(wx.ListCtrl,  ListCtrlAutoWidthMixin, ListRowHighlighter, TextEditMixin):
		def __init__(self, parent, id=-1, style=wx.LC_REPORT):
			wx.ListCtrl.__init__(self, parent, id, style=style)
			ListCtrlAutoWidthMixin.__init__(self)
			ListRowHighlighter.__init__(self)
			TextEditMixin.__init__(self)	

	#########################################################
	#   MainApp
	#########################################################

	class MainApp(wx.App):
		def OnInit(self):
			frame = ConfigurationFrame()
			self.SetTopWindow(frame)
			frame.Show(True)
			return True

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	if "DISPLAY" in os.environ and len(os.environ["DISPLAY"]) > 0:
		app = MainApp(redirect=False)
		app.MainLoop()
	# a VERY simple text-mode dump of the values
	else:
		for section in Configuration.params:
			print "Section '%s':" % section
			for key in Configuration.params[section]:
				print "   %-25s:  %s" % ("'" + key + "'", Configuration.params[section][key])

