"""
   Frames.py:
   Contains some extra frames used by the run control.
   Extracted here to prevent clutter in the main file.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import wx
from wx.lib.wordwrap import wordwrap
import sys

from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.backend import Events
from mnvruncontrol.frontend import Tools

#########################################################
#   HVConfirmationFrame
#########################################################

class HVConfirmationFrame(wx.Frame):
	def __init__(self, evt):
		wx.Frame.__init__(self, evt.daqmgr.main_window, -1, "PMTs are not clearly ready", size=(600,400))
		
		self.DAQmgr = evt.daqmgr
		self.nodes = self.DAQmgr.readoutNodes

		panel = wx.Panel(self)
		
		warningtext = wx.StaticText(panel, -1, wordwrap("The run control isn't sure if it's safe to start the run.  Below is a list of the PMTs with those that might be worrisome highlighted (red is worst, then orange, then yellow):", 350, wx.ClientDC(self)))
		
		self.pmtlist = Tools.AutoSizingListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_VRULES)
		self.pmtlist.InsertColumn(0, "Node")
		self.pmtlist.InsertColumn(1, "CROC")
		self.pmtlist.InsertColumn(2, "Chain")
		self.pmtlist.InsertColumn(3, "Board")
		self.pmtlist.InsertColumn(4, "HV target-actual")
		self.pmtlist.InsertColumn(5, "HV period")
		self.pmtlist.setResizeColumn(5)
		
		refreshButton = wx.Button(panel, wx.ID_REFRESH)
		self.Bind(wx.EVT_BUTTON, self.Read, refreshButton)
		
		continueButton = wx.Button(panel, wx.ID_FORWARD, "Start run")
		cancelButton   = wx.Button(panel, wx.ID_STOP,    "Cancel run")
		self.Bind(wx.EVT_BUTTON, self.OnContinue, continueButton)
		self.Bind(wx.EVT_BUTTON, self.OnCancel,   cancelButton)
		
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttonSizer.Add(continueButton, flag=wx.LEFT | wx.RIGHT, border=10)
		buttonSizer.Add(cancelButton, flag=wx.LEFT | wx.RIGHT, border=10)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(warningtext, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL)
		mainSizer.Add(self.pmtlist, proportion=1, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)
		mainSizer.Add(refreshButton, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, border=10)
		mainSizer.Add(buttonSizer, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM | wx.BOTTOM, border=10)
		
		panel.SetSizer(mainSizer)
		
		self.Show(True)
		self.Read()
		
	def Read(self, evt=None):
		febStatuses = {}
		for node in self.nodes:
			febStatuses[node.name] = node.sc_readBoards()
		
		self.pmtlist.DeleteAllItems()
		
		colors = ["red", "orange", "yellow"]		# used to demarcate the boards that have exceeded certain thresholds
		
		# eventually we'll want to do some sorting, but for now ...
		thresholds = sorted(Configuration.params["Readout nodes"]["SCHVthresholds"].keys(), reverse=True)
		over = {}
		needs_intervention = False
		for node in self.nodes:
			for board in febStatuses[node.name]:
				# if this board isn't an alarm, don't show it.
				if abs(int(board["hv_dev"])) < min(thresholds) and int(board["hv_period"]) >= Configuration.params["Readout nodes"]["SCperiodThreshold"]:
					continue
					
				index = self.pmtlist.InsertStringItem(sys.maxint, node.name)
				self.pmtlist.SetStringItem(index, 1, board["croc"])
				self.pmtlist.SetStringItem(index, 2, board["chain"])
				self.pmtlist.SetStringItem(index, 3, board["board"])
				self.pmtlist.SetStringItem(index, 4, board["hv_dev"])
				self.pmtlist.SetStringItem(index, 5, board["hv_period"])
				
				# low-HV period boards will probably show up at the top this way.
				if int(board["hv_period"]) < Configuration.params["Readout nodes"]["SCperiodThreshold"]:
					self.pmtlist.SetItemData(index, int(board["hv_period"]))
				else:
					data = abs(int(board["hv_dev"]))
					self.pmtlist.SetItemData(index, data)

		index = self.pmtlist.GetNextItem(-1)
		while index != -1:
			listitem = self.pmtlist.GetItem(index, 4)
			dev = abs(int(listitem.GetText()))
			listitem = self.pmtlist.GetItem(index, 5)
			period = int(listitem.GetText())
			
			for threshold in thresholds:
				if dev > threshold:
					self.pmtlist.SetItemBackgroundColour(index, wx.NamedColour(colors[thresholds.index(threshold)]))
					if threshold in over:
						over[threshold] += 1
					else:
						over[threshold] = 1
					
					break
					
			if period < Configuration.params["Readout nodes"]["SCperiodThreshold"]:
				self.pmtlist.SetItemBackgroundColour(index, wx.Color("blue"))
			
			index = self.pmtlist.GetNextItem(index)
			
		# sort them in descending order.
		self.pmtlist.SortItems(lambda a,b : 0 if a == b else (-1 if a > b else 1))

	def OnContinue(self, evt):
		wx.PostEvent(self.DAQmgr, Events.ReadyForNextSubrunEvent())
		self.Close()
	
	def OnCancel(self, evt):
		wx.PostEvent(self.DAQmgr, Events.StopRunningEvent())
		self.Close()

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
#   OutputFrame
#########################################################

class OutputFrame(wx.Frame):
	def __init__(self, parent, title, window_size=(400,300), window_pos=None):
		if window_pos:
			wx.Frame.__init__(self, parent, -1, title, size=window_size)
		else:
			wx.Frame.__init__(self, parent, -1, title, size=window_size, pos=window_pos)
		self.textarea = wx.TextCtrl(self, -1, style = wx.TE_MULTILINE | wx.TE_READONLY)

		self.Bind(Events.EVT_NEWDATA, self.OnNewData)
		
	def OnNewData(self, data_event):
		self.textarea.AppendText(data_event.data)
		


#########################################################
#   RunSeriesInfoFrame
#########################################################

class RunSeriesInfoFrame(wx.Frame):
	""" A window for configuration of paths, etc. """
	def __init__(self, parent, filename, runseries):
		wx.Frame.__init__(self, parent, -1, "Run series: " + filename, size=(600,400))

		panel = wx.Panel(self)

		infoList = Tools.AutoSizingListCtrl(panel, -1, style=wx.LC_REPORT | wx.LC_VRULES)
		infoList.setResizeColumn(2)

		infoList.InsertColumn(0, "# gates")
		infoList.InsertColumn(1, "Running mode")
		infoList.InsertColumn(2, "LI level")
		infoList.InsertColumn(3, "LED group(s)")
		
		# center the columns
		col = wx.ListItem()
		col.SetAlign(wx.LIST_FORMAT_CENTER)
		for i in range(4):
			infoList.SetColumn(i, col)

		for runinfo in runseries.Runs:
			index = infoList.InsertStringItem(sys.maxint, str(runinfo.gates))
			infoList.SetStringItem(index, 1, MetaData.RunningModes[runinfo.runMode])
			if runinfo.runMode == MetaData.RunningModes.hash("Light injection") or runinfo.runMode == MetaData.RunningModes.hash("Mixed beam/LI"):
				infoList.SetStringItem(index, 2, MetaData.LILevels[runinfo.ledLevel])
				infoList.SetStringItem(index, 3, MetaData.LEDGroups[runinfo.ledGroup])
			else:
				infoList.SetStringItem(index, 2, "--")
				infoList.SetStringItem(index, 3, "--")
			
		
		okButton = wx.Button(panel, wx.ID_OK)

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(infoList, 1, wx.EXPAND | wx.ALIGN_TOP)
		sizer.Add(okButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)

		panel.SetSizer(sizer)

		self.Bind(wx.EVT_BUTTON, self.CloseOut, okButton)
		
	def CloseOut(self, evt=None):
		self.Close()
		

