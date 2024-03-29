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
import dbm
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
	metadata_ctrls = { "mstr_detectorType" : MetaData.DetectorTypes,
	                   "mstr_hwInitLevel"  : MetaData.HardwareInitLevels }

	ID_FRONTEND = wx.NewIdRef()
	ID_MASTER   = wx.NewIdRef()
	ID_READOUT  = wx.NewIdRef()
	ID_OM       = wx.NewIdRef()
	ID_MTEST    = wx.NewIdRef()
	option_collections = { ID_FRONTEND : "Front end client",
	                       ID_MASTER   : "Master node",
	                       ID_READOUT  : "Readout node",
	                       ID_OM       : "Online monitoring node", 
	                       ID_MTEST    : "MTest beam DAQ node" }
	
	tabs_enabled = { ID_FRONTEND: [Configuration.prefixes["frnt"], Configuration.prefixes["log"]],
	                 ID_MASTER:   [Configuration.prefixes["log"], Configuration.prefixes["gen"],
	                               Configuration.prefixes["hw"], Configuration.prefixes["mstr"],
	                               Configuration.prefixes["sock"]],
	                 ID_READOUT:  [Configuration.prefixes["log"], Configuration.prefixes["gen"],
	                               Configuration.prefixes["hw"], Configuration.prefixes["read"],
	                               Configuration.prefixes["sock"]],
	                 ID_OM:       [Configuration.prefixes["log"], Configuration.prefixes["gen"],
	                               Configuration.prefixes["hw"], Configuration.prefixes["mon"],
	                               Configuration.prefixes["sock"]],
	                 ID_MTEST:    [Configuration.prefixes["log"], Configuration.prefixes["gen"],
	                               Configuration.prefixes["hw"], Configuration.prefixes["mtst"],
	                               Configuration.prefixes["sock"]] }

	#########################################################
	#   Configuration
	#########################################################

	class ConfigurationFrame(wx.Frame):
		""" A window for configuration of various options in the run control """
		def __init__(self, parent=None):
			wx.Frame.__init__(self, parent, -1, "Run control configuration", size=(800,700))
		
			self.parent = parent

			self.menu = wx.Menu()
			for collection_id in option_collections:
				collection_name = option_collections[collection_id]
				self.menu.Append(collection_id, collection_name, collection_name, kind=wx.ITEM_CHECK)
			self.menuBar = wx.MenuBar()
			self.menuBar.Append(self.menu, "&Show these options...");
			self.SetMenuBar(self.menuBar)
			
			self.Bind(wx.EVT_MENU, self.OnShowOptionsClick)

			panel = wx.Panel(self)
			self.nb = wx.Notebook(panel)
			self.pages = {}
			for pagename in Configuration.categories:
				self.pages[pagename] = wx.Panel(self.nb)
		
		
			###########################################################################
			# first, the items that can be automatically placed on the panels
			###########################################################################
		
			labels = {}
			self.entries = {}
			gridSizers = {}
		
			for param_set in Configuration.categories:
				labels[param_set] = {}
				self.entries[param_set] = {}

				for param_name in sorted(Configuration.categories[param_set]):
					# any iterable types will need to be added by hand, except strings
					if (hasattr(Configuration.params[param_name], '__iter__') and \
					type (Configuration.params[param_name])!=str) \
					or param_name in metadata_ctrls:
						continue

					labels[param_set][param_name] = wx.StaticText(self.pages[param_set], -1, Configuration.names[param_name])
					# booleans are special.  they need checkboxes instead of textctrls
					if isinstance(Configuration.params[param_name], bool):
						self.entries[param_set][param_name] = wx.CheckBox(self.pages[param_set], -1)
						self.entries[param_set][param_name].SetValue(Configuration.params[param_name])
					else:
						self.entries[param_set][param_name] = wx.TextCtrl(self.pages[param_set], -1, str(Configuration.params[param_name]))
					
				gridSizers[param_set] = wx.FlexGridSizer(0, 2, 5, 5)
				gridSizers[param_set].SetFlexibleDirection(wx.HORIZONTAL)
				gridSizers[param_set].AddGrowableCol(1)
				for param_name in labels[param_set]:
					gridSizers[param_set].Add(labels[param_set][param_name], flag=wx.ALIGN_CENTER_VERTICAL)
					gridSizers[param_set].Add(self.entries[param_set][param_name], proportion=0, flag=wx.EXPAND)
				
				self.pages[param_set].SetSizer(gridSizers[param_set])
			
		
			###########################################################################
			# now anything that needs to be added by hand
			###########################################################################
		
			self.AddButtons = {}
			self.DeleteButtons = {}

			# first: config choices that need list boxes.
			for key in metadata_ctrls:
				labels["Master node"][key] = wx.StaticText(self.pages["Master node"], -1, Configuration.names[key])
				self.entries["Master node"][key] = wx.Choice(self.pages["Master node"], -1, choices=metadata_ctrls[key].descriptions())
				self.entries["Master node"][key].SetSelection( metadata_ctrls[key].index(Configuration.params[key]) )
				gridSizers["Master node"].Add(labels["Master node"][key], flag=wx.ALIGN_CENTER_VERTICAL)
				gridSizers["Master node"].Add(self.entries["Master node"][key], proportion=1, flag=wx.EXPAND)
			
			# next: remote node config
			labels["Master node"]["mstr_nodeAddresses"] = wx.StaticText(self.pages["Master node"], -1, Configuration.names["mstr_nodeAddresses"])
			self.entries["Master node"]["mstr_nodeAddresses"] = AutoSizingEditableListCtrl(self.pages["Master node"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["Master node"]["mstr_nodeAddresses"].InsertColumn(0, "Node type")
			self.entries["Master node"]["mstr_nodeAddresses"].InsertColumn(1, "Name")
			self.entries["Master node"]["mstr_nodeAddresses"].InsertColumn(2, "Address (IPv4/DNS)")
		
			for node in Configuration.params["mstr_nodeAddresses"]:
				index = self.entries["Master node"]["mstr_nodeAddresses"].InsertItem(sys.maxsize, str(node["type"]))
				self.entries["Master node"]["mstr_nodeAddresses"].SetItem(index, 1, node["name"])
				self.entries["Master node"]["mstr_nodeAddresses"].SetItem(index, 2, node["address"])

			self.AddButtons["mstr_nodeAddresses"] = wx.Button(self.pages["Master node"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["mstr_nodeAddresses"])

			self.DeleteButtons["mstr_nodeAddresses"] = wx.Button(self.pages["Master node"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["mstr_nodeAddresses"])
		
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons["mstr_nodeAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["mstr_nodeAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
		
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.AddMany( ( (self.entries["Master node"]["mstr_nodeAddresses"], 1, wx.EXPAND), (buttonSizer, 0, wx.EXPAND) ) )
		
			gridSizers["Master node"].Add(labels["Master node"]["mstr_nodeAddresses"], flag=wx.ALIGN_CENTER_VERTICAL)
			gridSizers["Master node"].Add(entrySizer, proportion=0, flag=wx.EXPAND)
	
			gridSizers["Master node"].SetFlexibleDirection(wx.BOTH)
			
			# next: HV thresholds
			labels["Master node"]["mstr_HVthresholds"] = wx.StaticText(self.pages["Master node"], -1, Configuration.names["mstr_HVthresholds"])
			self.entries["Master node"]["mstr_HVthresholds"] = AutoSizingEditableListCtrl(self.pages["Master node"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["Master node"]["mstr_HVthresholds"].InsertColumn(0, "HV dev (ADC)")
			self.entries["Master node"]["mstr_HVthresholds"].InsertColumn(1, "# PMTs allowed above threshold")
		
			for thresh in Configuration.params["mstr_HVthresholds"]:
				index = self.entries["Master node"]["mstr_HVthresholds"].InsertItem(sys.maxsize, str(thresh))
				self.entries["Master node"]["mstr_HVthresholds"].SetItem(index, 1, str(Configuration.params["mstr_HVthresholds"][thresh]))

			self.AddButtons["mstr_HVthresholds"] = wx.Button(self.pages["Master node"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["mstr_HVthresholds"])

			self.DeleteButtons["mstr_HVthresholds"] = wx.Button(self.pages["Master node"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["mstr_HVthresholds"])
		
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons["mstr_HVthresholds"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["mstr_HVthresholds"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
		
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.AddMany( ( (self.entries["Master node"]["mstr_HVthresholds"], 1, wx.EXPAND), (buttonSizer, 0, wx.EXPAND) ) )
		
			gridSizers["Master node"].Add(labels["Master node"]["mstr_HVthresholds"], flag=wx.ALIGN_CENTER_VERTICAL)
			gridSizers["Master node"].Add(entrySizer, proportion=0, flag=wx.EXPAND)
	
			gridSizers["Master node"].SetFlexibleDirection(wx.BOTH)
			
			# then: boards to ignore in HV threshold check
			labels["Master node"]["mstr_HVignoreFEBs"] = wx.StaticText(self.pages["Master node"], -1, Configuration.names["mstr_HVignoreFEBs"])
			self.entries["Master node"]["mstr_HVignoreFEBs"] = AutoSizingEditableListCtrl(self.pages["Master node"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["Master node"]["mstr_HVignoreFEBs"].InsertColumn(0, "Node")
			self.entries["Master node"]["mstr_HVignoreFEBs"].InsertColumn(1, "Croc")
			self.entries["Master node"]["mstr_HVignoreFEBs"].InsertColumn(2, "Chain")
			self.entries["Master node"]["mstr_HVignoreFEBs"].InsertColumn(3, "Board")
		
			for addr in Configuration.params["mstr_HVignoreFEBs"]:
				index = self.entries["Master node"]["mstr_HVignoreFEBs"].InsertItem(sys.maxsize, addr["node"])
				self.entries["Master node"]["mstr_HVignoreFEBs"].SetItem(index, 1, str(addr["croc"]))
				self.entries["Master node"]["mstr_HVignoreFEBs"].SetItem(index, 2, str(addr["chain"]))
				self.entries["Master node"]["mstr_HVignoreFEBs"].SetItem(index, 3, str(addr["board"]))

			self.AddButtons["mstr_HVignoreFEBs"] = wx.Button(self.pages["Master node"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["mstr_HVignoreFEBs"])

			self.DeleteButtons["mstr_HVignoreFEBs"] = wx.Button(self.pages["Master node"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["Master node"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["mstr_HVignoreFEBs"])
		
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons["mstr_HVignoreFEBs"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["mstr_HVignoreFEBs"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
		
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.Add(self.entries["Master node"]["mstr_HVignoreFEBs"], proportion=1, flag=wx.EXPAND)
			entrySizer.Add(buttonSizer, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
		
			gridSizers["Master node"].Add(labels["Master node"]["mstr_HVignoreFEBs"], flag=wx.ALIGN_CENTER_VERTICAL, proportion=0)
			gridSizers["Master node"].Add(entrySizer, proportion=1, flag=wx.EXPAND)
	
			gridSizers["Master node"].SetFlexibleDirection(wx.BOTH)
		
			
			# finally: notification addresses
			labels["General"]["gen_notifyAddresses"] = wx.StaticText(self.pages["General"], -1, Configuration.names["gen_notifyAddresses"])
			self.entries["General"]["gen_notifyAddresses"] = AutoSizingEditableListCtrl(self.pages["General"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["General"]["gen_notifyAddresses"].InsertColumn(0, "Address")
		
			for addr in Configuration.params["gen_notifyAddresses"]:
				self.entries["General"]["gen_notifyAddresses"].InsertItem(sys.maxsize, addr)

			self.AddButtons["gen_notifyAddresses"] = wx.Button(self.pages["General"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["General"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons["gen_notifyAddresses"])

			self.DeleteButtons["gen_notifyAddresses"] = wx.Button(self.pages["General"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["General"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons["gen_notifyAddresses"])
		
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons["gen_notifyAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons["gen_notifyAddresses"], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
		
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.Add(self.entries["General"]["gen_notifyAddresses"], proportion=1, flag=wx.EXPAND)
			entrySizer.Add(buttonSizer, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL)
		
			gridSizers["General"].Add(labels["General"]["gen_notifyAddresses"], flag=wx.ALIGN_CENTER_VERTICAL, proportion=0)
			gridSizers["General"].Add(entrySizer, proportion=1, flag=wx.EXPAND)
	
			gridSizers["General"].SetFlexibleDirection(wx.BOTH)

			###########################################################################
			# and finally, assemble the panel
			###########################################################################
#			for name in sorted(Configuration.categories.keys()):
#				self.nb.AddPage(self.pages[name], name)
			
			self.LoadConfig()
			self.OnShowOptionsClick()
			
			saveButton = wx.Button(panel, wx.ID_SAVE)
			self.Bind(wx.EVT_BUTTON, self.SaveAll, saveButton)

			cancelButton = wx.Button(panel, wx.ID_CANCEL)
			self.Bind(wx.EVT_BUTTON, self.Cancel, cancelButton)

			buttonSizer = wx.GridSizer(1, 2, 10, 10)
			buttonSizer.AddMany( ( (saveButton, 1, wx.ALIGN_CENTER_HORIZONTAL), (cancelButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ) )

			globalSizer = wx.BoxSizer(wx.VERTICAL)
			globalSizer.Add(self.nb, flag=wx.EXPAND, proportion=1)
			globalSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER_HORIZONTAL, proportion=0)		
			panel.SetSizer(globalSizer)

		
			for page in self.pages:
				self.pages[page].Layout()
				
			self.Layout()
		
		def AddNode(self, evt):
			""" Add a node to the list. """
			for itemname in self.AddButtons:
				if evt.EventObject == self.AddButtons[itemname]:
					for page in self.entries:
						if itemname in self.entries[page]:
							itemlocation = self.entries[page]
							break
				
					index = itemlocation[itemname].InsertItem(sys.maxsize, "[text]")
					for col in range(1, itemlocation[itemname].GetColumnCount()):
						itemlocation[itemname].SetItem(index, col, "[text]")
	
		def DeleteNodes(self, evt):
			""" Delete all selected nodes from the list. """
			for itemname in self.DeleteButtons:
				if evt.EventObject == self.DeleteButtons[itemname]:
					index = -1
					toDelete = []

					for page in self.entries:
						if itemname in self.entries[page]:
							itemlocation = self.entries[page]
							break

					while True:
						index = itemlocation[itemname].GetNextSelected(index)
		
						if index == -1:
							break
						else:
							toDelete.append(index)
			
					# want to delete from the back to the front so that we don't skip any
					toDelete = sorted(toDelete, reverse=True)
					for item in toDelete:
						itemlocation[itemname].DeleteItem(item)
		
		def LoadConfig(self):
			""" Loads the saved GUI settings from the
			    file they were stored in and sets the
			    values of the checkboxes appropriately. """

			self.cfg = wx.Config('mnvrcc')
		
			enable_frontend = self.cfg.ReadBool("frontend", False)
			enable_master   = self.cfg.ReadBool("master", False)
			enable_readout  = self.cfg.ReadBool("readout", False)
			enable_om       = self.cfg.ReadBool("om", False)
			enable_mtest    = self.cfg.ReadBool("mtest", False)
		
			self.GetMenuBar().FindItemById(ID_FRONTEND).Check(enable_frontend)
			self.GetMenuBar().FindItemById(ID_MASTER).Check(enable_master)
			self.GetMenuBar().FindItemById(ID_READOUT).Check(enable_readout)
			self.GetMenuBar().FindItemById(ID_OM).Check(enable_om)
			self.GetMenuBar().FindItemById(ID_MTEST).Check(enable_mtest)

		def OnShowOptionsClick(self, evt=None):
			""" Update the options shown when the user
			    clicks on a menu item. """
	
			tabs_to_enable = {}
			for tab_name in self.pages:
				tabs_to_enable[tab_name] = False
	
			for item_id in option_collections:
				if not self.GetMenuBar().FindItemById(item_id).IsChecked():
					continue
				
				for tab_name in tabs_enabled[item_id]:
					tabs_to_enable[tab_name] = True
			
			# don't use DeleteAllPages() because that
			# destroys the panels too (which would mean
			# they couldn't be used again later)
			while self.nb.GetPageCount() > 0:
				self.nb.RemovePage(0)

			page_count = 0
			for page_name in sorted(self.pages.keys()):
				if tabs_to_enable[page_name]:
					self.nb.AddPage(self.pages[page_name], page_name)
					page_count += 1
			
			# display an informational notice if nothing is enabled
			if page_count == 0:
				panel = wx.Panel(self.nb)
				sizer = wx.BoxSizer(wx.HORIZONTAL)
				text = wx.StaticText(panel, -1, "Select the arrangement(s) corresponding to your installation from the menu...")
				sizer.AddStretchSpacer()
				sizer.Add(text, proportion=0, flag=wx.ALIGN_CENTER)
				sizer.AddStretchSpacer()
				panel.SetSizer(sizer)
				self.nb.AddPage(panel, "Select configuration!")
				self.nb.Layout()
				
			self.Layout()
		
		def SaveAll(self, evt=None):
			""" Save the configuration. """
		
			# first do the automatic ones
			for param_set in self.entries:
				for param_name in self.entries[param_set]:
					if isinstance(self.entries[param_set][param_name], wx.TextCtrl) or isinstance(self.entries[param_set][param_name], wx.CheckBox):
						# note that this must saved as the correct type (hence the Configuration.types() call).
						Configuration.params[param_name] = Configuration.types[param_name](self.entries[param_set][param_name].GetValue())
	
			# now any that need to be handled in a particular way
	
			# first: choices
			for item in metadata_ctrls:
				Configuration.params[item] = metadata_ctrls[item].item(self.entries["Master node"][item].GetSelection()).hash
	
			# now remote nodes
			nodelist= []
			index = -1
			while True:
				index = self.entries["Master node"]["mstr_nodeAddresses"].GetNextItem(index)
				if index == -1:
					break
				
				try:
					nodetype = int(self.entries["Master node"]["mstr_nodeAddresses"].GetItem(index, 0).GetText())
				except ValueError:
					nodetype = 1		# default to READOUT
		
				nodedescr = { "type":     nodetype,
				              "name":     self.entries["Master node"]["mstr_nodeAddresses"].GetItem(index, 1).GetText(),
				              "address" : self.entries["Master node"]["mstr_nodeAddresses"].GetItem(index, 2).GetText() }
				nodelist.append(nodedescr)
			Configuration.params["mstr_nodeAddresses"] = nodelist
			
			# then HV thresholds
			thresholds = {}
			index = -1
			while True:
				index = self.entries["Master node"]["mstr_HVthresholds"].GetNextItem(index)
				if index == -1:
					break
				
				try:
					thresh = int(self.entries["Master node"]["mstr_HVthresholds"].GetItem(index, 0).GetText())
					count = int(self.entries["Master node"]["mstr_HVthresholds"].GetItem(index, 1).GetText())
				except ValueError:
					dlg = wx.MessageDialog(None, 'Invalid threshold value/count!', 'Error', wx.OK | wx.ICON_ERROR)
					dlg.ShowModal()
					return
				
				thresholds[thresh] = count
			Configuration.params["mstr_HVthresholds"] = thresholds

			# after that, the boards to ignore in HV threshold check
			boards = []
			index = -1
			while True:
				index = self.entries["Master node"]["mstr_HVignoreFEBs"].GetNextItem(index)
				if index == -1:
					break
				
				board_info = {}
				try:
					board_info["node"] = self.entries["Master node"]["mstr_HVignoreFEBs"].GetItem(index, 0).GetText()
					board_info["croc"] = int(self.entries["Master node"]["mstr_HVignoreFEBs"].GetItem(index, 1).GetText())
					board_info["chain"] = int(self.entries["Master node"]["mstr_HVignoreFEBs"].GetItem(index, 2).GetText())
					board_info["board"] = int(self.entries["Master node"]["mstr_HVignoreFEBs"].GetItem(index, 3).GetText())
					boards.append(board_info)
				except ValueError:
					dlg = wx.MessageDialog(None, 'Invalid FEB info!', 'Error', wx.OK | wx.ICON_ERROR)
					dlg.ShowModal()
					return
			Configuration.params["mstr_HVignoreFEBs"] = boards

			# then finally, notification addresses
			addresses = []
			index = -1
			while True:
				index = self.entries["General"]["gen_notifyAddresses"].GetNextItem(index)
				if index == -1:
					break
				
				addresses.append(self.entries["General"]["gen_notifyAddresses"].GetItem(index, 0).GetText())
			Configuration.params["gen_notifyAddresses"] = addresses
			
			# now save everything
			Configuration.SaveToDB()
			self.SaveConfig()

			self.Close()
		
		def SaveConfig(self):
			""" Saves the GUI-specific settings. """
		
			self.cfg.WriteBool("frontend", self.GetMenuBar().FindItemById(ID_FRONTEND).IsChecked())
			self.cfg.WriteBool("master", self.GetMenuBar().FindItemById(ID_MASTER).IsChecked())
			self.cfg.WriteBool("readout", self.GetMenuBar().FindItemById(ID_READOUT).IsChecked())
			self.cfg.WriteBool("om", self.GetMenuBar().FindItemById(ID_OM).IsChecked())
			self.cfg.WriteBool("mtest", self.GetMenuBar().FindItemById(ID_MTEST).IsChecked())
	
			self.cfg.Flush()
		
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

else:
	#########################################################
	#   TextApp
	#########################################################

	class TextApp:
		def ConsoleLoop(self):
			""" A text-entry interface. """
			
			quit = False
			
			while not quit:
				current_section = None
				while current_section is None:
					current_section = self.MenuSelection(list(Configuration.categories.keys()))
					
					# user just pushed 'enter'
					if current_section is None:
						quit = True
						break
				
					while current_section is not None:
						print("Section '%s'" % current_section)
						print("===========================================================")
						params = []
						for key in Configuration.categories[current_section]:
							params.append(key)
						param = self.MenuSelection(params, [Configuration.names[k] for k in params])
						
						if param is None:
							current_section = None
							continue
						
						# lists are trickier.  not supported...
						if Configuration.types[param] not in (list, dict):
							print("Changing value for '%s'." % param)
							print("Old value: ", Configuration.params[param])
							print("Enter new value (just press 'Enter' to cancel):")
							
							try:
								v = input(">>> ")
							except EOFError:
								return
							
							if v == "":
								continue
							
							try:
								# beware.  bool(<string>) = len(<string>) > 0!
								if Configuration.types[param] == bool and isinstance(v, str):
									Configuration.params[param] = v in ("True", "true", "1")
								else:
									Configuration.params[param] = Configuration.types[param](v)
							except ValueError:
								print("Invalid input!")
								continue
					
						else:
							print("List/dictionary editing doesn't work yet in text-only mode.")
							print("Either use the GUI editor or edit the Configuration by hand")
							print("in a Python shell and use its SaveToDB() function.\n")
			### while not quit
			
			Configuration.SaveToDB()
		
		def MenuSelection(self, choices, descriptions=None):
			""" Displays a menu to the user and requests
			    that s/he pick one of the options. """
			
			print("Choices:")
			print("--------")
			
			for i in range(len(choices)):
				descr = " " if descriptions is None else (" (%s)" % descriptions[i])
				print("[%d] %-25s%s" % (i+1, choices[i], descr))
			
			while True:
				print("\nPlease enter the number of the menu item you want")
				print("(just press 'Enter' to go back/quit)")

				try:
					r = input(">>> ")
				except EOFError:
					return None

				if r == "":
					return None
			
				try:
					if int(r) - 1 in range(len(choices)):
						return choices[int(r)-1]
					else:
						raise ValueError()
				except ValueError:
					print("Invalid entry.")
		

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	if "DISPLAY" in os.environ and len(os.environ["DISPLAY"]) > 0:
		app = MainApp(redirect=False)
		app.MainLoop()
	# a VERY simple text-mode dump of the values
	else:
#		for section in Configuration.params:
#			print "Section '%s':" % section
#			for key in Configuration.params[section]:
#				print "   %-25s:  %s" % ("'" + key + "'", Configuration.params[section][key])
		app = TextApp()
		app.ConsoleLoop()

