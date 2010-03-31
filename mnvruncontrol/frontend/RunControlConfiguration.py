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
import sys
import shelve
import anydbm

from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import ListRowHighlighter
from wx.lib.mixins.listctrl import TextEditMixin
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.backend import Events

from mnvruncontrol.backend.ReadoutNode import ReadoutNode
from mnvruncontrol.backend.MonitorNode import MonitorNode

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
		
#		warningText = wx.StaticText(self.frontendPage, -1, "** PLEASE don't change these values unless you know what you're doing! **")
		
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
				if hasattr(Configuration.params[param_set][param_name], '__iter__'):
					continue

				labels[param_set][param_name] = wx.StaticText(self.pages[param_set], -1, Configuration.names[param_set][param_name])
				# booleans are special.  they need checkboxes instead of textctrls
				if isinstance(Configuration.params[param_set][param_name], bool):
					self.entries[param_set][param_name] = wx.CheckBox(self.pages[param_set], -1)
					self.entries[param_set][param_name].SetValue(Configuration.params[param_set][param_name])
				else:
					self.entries[param_set][param_name] = wx.TextCtrl(self.pages[param_set], -1, str(Configuration.params[param_set][param_name]))
					
			gridSizers[param_set] = wx.GridSizer(len(labels), 2, 5, 5)
			for param_name in labels[param_set]:
				gridSizers[param_set].Add(labels[param_set][param_name], flag=wx.ALIGN_CENTER_VERTICAL)
				gridSizers[param_set].Add(self.entries[param_set][param_name], proportion=0, flag=wx.EXPAND)
				
			self.pages[param_set].SetSizer(gridSizers[param_set])
			
		
		###########################################################################
		# now anything that needs to be added by hand
		###########################################################################
		
		self.AddButtons = {}
		self.DeleteButtons = {}
		for nodetype in ("readoutNodes", "monitorNodes"):
			labels["Front end"][nodetype] = wx.StaticText(self.pages["Front end"], -1, Configuration.names["Front end"][nodetype])
			self.entries["Front end"][nodetype] = AutoSizingEditableListCtrl(self.pages["Front end"], style=wx.LC_REPORT | wx.LC_HRULES)
			self.entries["Front end"][nodetype].InsertColumn(0, "Name")
			self.entries["Front end"][nodetype].InsertColumn(1, "Address (IPv4/DNS)")
			
			for node in Configuration.params["Front end"][nodetype]:
				index = self.entries["Front end"][nodetype].InsertStringItem(sys.maxint, node.name)
				self.entries["Front end"][nodetype].SetStringItem(index, 1, node.address)

			self.AddButtons[nodetype] = wx.Button(self.pages["Front end"], wx.ID_ADD, style=wx.BU_EXACTFIT)
			self.pages["Front end"].Bind(wx.EVT_BUTTON, self.AddNode, self.AddButtons[nodetype])

			self.DeleteButtons[nodetype] = wx.Button(self.pages["Front end"], wx.ID_DELETE, style=wx.BU_EXACTFIT)
			self.pages["Front end"].Bind(wx.EVT_BUTTON, self.DeleteNodes, self.DeleteButtons[nodetype])
			
			buttonSizer = wx.BoxSizer(wx.VERTICAL)
			buttonSizer.AddMany ( ( (self.AddButtons[nodetype], 0, wx.ALIGN_CENTER_HORIZONTAL), (self.DeleteButtons[nodetype], 0, wx.ALIGN_CENTER_HORIZONTAL) ) )
			
			entrySizer = wx.BoxSizer(wx.HORIZONTAL)
			entrySizer.AddMany( ( (self.entries["Front end"][nodetype], 1, wx.EXPAND), (buttonSizer, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL) ) )
			
			gridSizers["Front end"].Add(labels["Front end"][nodetype], flag=wx.ALIGN_CENTER_VERTICAL)
			gridSizers["Front end"].Add(entrySizer, proportion=0, flag=wx.EXPAND)

		# these are added like this so that they show up in a predictable order
		for name in ("Front end", "Socket setup", "Dispatchers", "Readout nodes", "Monitoring nodes"):
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
		for nodename in self.AddButtons:
			if evt.EventObject == self.AddButtons[nodename]:
				index = self.entries["Front end"][nodename].InsertStringItem(sys.maxint, "[new node]")
				self.entries["Front end"][nodename].SetStringItem(index, 1, "[new node address]")
	
	def DeleteNodes(self, evt):
		for nodename in self.DeleteButtons:
			if evt.EventObject == self.DeleteButtons[nodename]:
				index = -1
				toDelete = []
				while True:
					index = self.entries["Front end"][nodename].GetNextSelected(index)
		
					if index == -1:
						break
					else:
						toDelete.append(index)
			
				# want to delete from the back to the front so that we don't skip any
				toDelete = sorted(toDelete, reverse=True)
				for item in toDelete:
					self.entries["Front end"][nodename].DeleteItem(item)
		
	def SaveAll(self, evt=None):
		try:
			db = shelve.open(Defaults.CONFIG_DB_LOCATION, "w")
		except anydbm.error:
			errordlg = wx.MessageDialog( None, "The configuration file cannot be opened.  Values will not be saved.", "Config file inaccessible", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()
		else:
			# first do the automatic ones
			for param_set in self.entries:
				for param_name in self.entries[param_set]:
					if isinstance(self.entries[param_set][param_name], wx.TextCtrl) or isinstance(self.entries[param_set][param_name], wx.CheckBox):
						# note that this must saved as the correct type (hence the Configuration.types() call).
						db[param_name] = Configuration.types[param_set][param_name](self.entries[param_set][param_name].GetValue())
			
			# now any that need to be handled in a particular way
			nodeobjects = {"readoutNodes" : ReadoutNode, "monitorNodes" : MonitorNode}
			nodelist = {}
			for nodetype in nodeobjects:
				nodelist[nodetype] = []
				index = -1
				while True:
					index = self.entries["Front end"][nodetype].GetNextItem(index)
					
					if index == -1:
						break
					
					nodelist[nodetype].append( nodeobjects[nodetype](self.entries["Front end"][nodetype].GetItem(index, 0).GetText(), self.entries["Front end"][nodetype].GetItem(index, 1).GetText()) )
					
				db[nodetype] = nodelist[nodetype]
			
			# need to specifically close the DB so that it saves correctly
			db.close()
		
		if self.parent is not None:	
			wx.PostEvent(self.parent, Events.ConfigUpdatedEvent())

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
	app = MainApp(redirect=False)
	app.MainLoop()

