"""
  OMReset.py:
   A simple tool designed to reset online monitoring
   nodes if their underlying processes crash but
   the dispatcher is still running.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Apr. 2010
                    
   Address all complaints to the management.
"""

import wx
import re

from mnvruncontrol.configuration import Configuration
from mnvruncontrol.backend import MonitorNode

#########################################################
#   MainFrame
#########################################################

class MainFrame(wx.Frame):
	""" The main window. """
	def __init__(self, parent=None):
		wx.Frame.__init__(self, parent, -1, "Reset online monitoring processes", size=(300,150))

		self.panel = wx.Panel(self)
		
		instructionText = wx.StaticText(self.panel, -1, "Click the 'reset' button to reset\nthe online monitoring processes \non the OM node(s).")
		self.resetButton = wx.Button(self.panel, wx.ID_REFRESH, "Reset")
		self.closeButton = wx.Button(self.panel, wx.ID_CLOSE)
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.AddMany( ((instructionText, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.resetButton, 0, wx.ALIGN_CENTER_HORIZONTAL), (self.closeButton, 0, wx.ALIGN_CENTER_HORIZONTAL)) )
		self.panel.SetSizer(self.sizer)

		self.statusbar = self.CreateStatusBar(1)
		self.SetStatusText("Ready.")
		
		self.Bind(wx.EVT_BUTTON, self.OnReset, self.resetButton)
		self.Bind(wx.EVT_BUTTON, self.OnClose, self.closeButton)
	
	def OnReset(self, evt):
		for button in (self.resetButton, self.closeButton):
			button.Disable()
			
		self.SetStatusText("Working...")
		
		try:
			omfile = open(Configuration.params["Master node"]["monitor_idfile"])
		except OSError:
			omfile = None
		
		all_stopped = True
		if omfile is not None:
			pattern = re.compile("^(?P<id>[a-eA-E\w\-]+) (?P<address>\S+)$")
			for line in omfile:
				matches = pattern.match(line)
				if matches is not None:
					try:
						node = MonitorNode.MonitorNode("node", matches.group("address"), matches.group("id"))
						success = node.om_stop()
						if success:
							print "stopped %s node at address %s" % (node.name, node.address)
					except Exception as e:
						print e
						success = False
					all_stopped = all_stopped and success
		
		if all_stopped:
			dlg = wx.MessageDialog( None, "All nodes were successfully reset.  Monitoring should resume as normal when the next subrun is started.", "Success", wx.OK | wx.ICON_INFORMATION )
		else:
			dlg = wx.MessageDialog( None, "Could not reset one or more monitoring nodes.  You will probably need to log in and restart the monitoring dispatchers on those nodes by hand...", "Could not reset all nodes", wx.OK | wx.ICON_ERROR )
		dlg.ShowModal()

		for button in (self.resetButton, self.closeButton):
			button.Enable()
		self.SetStatusText("Ready.")
					
	def OnClose(self, evt=None):
		self.Close()	
		
#########################################################
#   MainApp
#########################################################

class MainApp(wx.App):
	def OnInit(self):
		frame = MainFrame()
		self.SetTopWindow(frame)
		frame.Show(True)
		return True

#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MainApp(redirect=False)
	app.MainLoop()

