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
from mnvruncontrol.backend import Events
from mnvruncontrol.frontend import Tools

#########################################################
#   HVConfirmationFrame
#########################################################

class HVConfirmationFrame(wx.Frame):
	def __init__(self, parent, nodes):
		wx.Frame.__init__(self, parent, -1, "PMT voltages are not clearly ok", size=(600,400))
		
		self.nodes = nodes

		panel = wx.Panel(self)
		
		warningtext = wx.StaticText(panel, -1, wordwrap("The run control isn't sure if it's safe to start the run.  Below is a list of PMTs that might be worrisome:", 350, wx.ClientDC(self)))
		
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
		
	def Read(self, evt):
		febStatuses = {}
		for node in self.nodes:
			febStatuses[node.name] = node.sc_readBoards()
		
		self.pmtlist.DeleteAllItems()
		
		# eventually we'll want to do some sorting, but for now ...
		over300 = 0
		over100 = 0
		over60 = 0
		badPeriod = 0
		for node in febStatus:
			for board in febStatuses[node]:
				index = self.pmtlist.InsertStringItem(sys.maxint, node.name)
				self.pmtlist.SetStringItem(index, 1, board["croc"])
				self.pmtlist.SetStringItem(index, 2, board["chain"])
				self.pmtlist.SetStringItem(index, 3, board["board"])
				self.pmtlist.SetStringItem(index, 4, board["hv_dev"])
				self.pmtlist.SetStringItem(index, 5, board["hv_period"])
				
				dev = abs(int(board["hv_dev"]))
				period = int(board["hv_period"])
				
				if dev > 300:
					over300 += 1
					self.pmtlist.SetItemBackgroundColour(index, wx.Color("red"))
				elif dev > 100:
					over100 += 1
					self.pmtlist.SetItemBackgroundColour(index, wx.Color("orange"))
				elif dev > 60:
					over60 += 1
					self.pmtlist.SetItemBackgroundColour(index, wx.Color("yellow"))
				
				if period < 15000:
					badPeriod += 1
					self.pmtlist.SetItemBackgroundColour(index, wx.Color("blue"))
	
	def OnContinue(self, evt):
		pass
	
	def OnCancel(self, evt):
		pass


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
		

