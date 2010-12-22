#!/usr/bin/env python
"""
  Package: mnvruncontrol
   The MINERvA run control
   
  File: RunControl.py
  
  Notes:
   Main wxPython objects for the presentation of a graphical
   run control interface to the user.
  
  Original author: J. Wolcott (jwolcott@fnal.gov)
                   first implementation,  Feb.-Jun. 2010
                   second implementation, Aug.-Oct. 2010
                    
  Address all complaints to the management.
"""

import os
import sys
import time
import copy
import logging
import socket
import pprint
import urllib2
import subprocess
import wx
from wx import xrc

from mnvruncontrol.configuration import Logging
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import MetaData

from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import Threads
from mnvruncontrol.backend import Events
from mnvruncontrol.backend import Alert
from mnvruncontrol.backend import RemoteNode		# needed for 'status' enumeration

#########################################################
#   MainApp
#########################################################

class MainApp(wx.App, PostOffice.MessageTerminus):

	### Notice: this class is pretty large and has a lot
	### of methods, so I have grouped them by category.
	### Within each category they are arranged roughly 
	### alphabetically.
	###
	### The categories are as follows:
	###   * initialization/teardown            (begin around line 50)
	###   * message handlers & access control  ( ...              225)
	###   * wx event handlers                  ( ...              300)
	###   * 'real work' methods                ( ...              1200)

	def OnInit(self):
		sys.stdout.write("Setting up.  Please wait a moment... ")
		sys.stdout.flush()
		
		PostOffice.MessageTerminus.__init__(self)

		# prepare the logging		
		self.logger = logging.getLogger("Frontend")
		self.logger.info("Starting up.")
		
		# load and show the graphics
		self.res = xrc.XmlResource('../resources/frontend.xrc')
		self.frame = self.res.LoadFrame(None, 'main_frame')
		self.frame.SetDimensions(0, 0, 1000, 1000)
		self.SetTopWindow(self.frame)
		self.frame.Show()

		# prepare the post office and threads
		try:
			self.postoffice = PostOffice.PostOffice(listen_port=Configuration.params["frnt_listenPort"])
		except socket.error:
			self.logger.exception("Socket error trying to start up the post office:")
			self.logger.fatal("Can't get a socket.  Quitting.")
			sys.stderr.write("I can't bind my listening socket.  Are you sure there's no other copy of the run control running?\n")
			sys.stderr.write("Wait 60 seconds and try again.  If you see this message again, contact your expert shifter.\n")
			return False

		self.worker_thread = Threads.WorkerThread()
		self.alert_thread = Threads.AlertThread(parent_app=self)

		# get the system ready to react to stimuli
		self.BindChoices()
		self.BindEvents()
		self.SetupHandlers()
		
		# load up the configuration
		self.LoadConfig()
		
		# initialize variables
		self.daq = False
		self.ssh_processes = []
		self.ssh_details = {}
		self.in_control = False
		self.status = None
		self.problem_pmt_list = None

		self.panel_stack = { "main": [], "status": [] }
		self.current_alert = None
		self.last_bknd_color = None
		
		self.stop_connecting = False
		
		# other resources that can't be stored in the resource file
		path_template = Configuration.params["frnt_resourceLocation"] + "/%s"
		self.audio_resources = { Alert.ERROR:  wx.Sound(path_template % "error.wav"),
		                         Alert.WARNING: wx.Sound(path_template % "alert.wav") }
		self.image_resources = { "LED on":    wx.Bitmap(path_template % "LED_on.png", type=wx.BITMAP_TYPE_PNG),
		                         "LED off":   wx.Bitmap(path_template % "LED_off.png", type=wx.BITMAP_TYPE_PNG),
		                         "LED error": wx.Bitmap(path_template % "LED_error.png", type=wx.BITMAP_TYPE_PNG) }

		self.Redraw()

		# collections of panels
		self.panel_collections = {}
		self.panel_collections["main"] = (xrc.XRCCTRL(self.frame, "notebook"), xrc.XRCCTRL(self.frame, "pmt_check_panel"), xrc.XRCCTRL(self.frame, "alert_panel"), xrc.XRCCTRL(self.frame, "connection_panel"))
		self.panel_collections["status"] = (xrc.XRCCTRL(self.frame, "summary_info_panel"), xrc.XRCCTRL(self.frame, "summary_alert_panel"))

		# try to figure out what my externally-visible IP address is
		try:
			self.ip_addr = urllib2.urlopen("http://www.whatismyip.com/automation/n09230945.asp").read()
		except urllib2.URLError:
			self.ip_addr = None


		# make sure the controls are set up as we expect
		self.ConfigControlsEnable()

		# if the config has us auto-connecting,
		# we should behave as if the 'connect' button was clicked
		if self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autoconnect")).IsChecked():
			ctrl = xrc.XRCCTRL(self.frame, "control_connection_button")	 
			ctrl.Command(wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, ctrl.GetId()))
		

		sys.stdout.write("done.\n")
		sys.stdout.flush()

		return True
	
	def BindEvents(self):
		""" The resource file's event handlers are evidently ignored by wxPython.
		    So I need to specify them here. """

		self.Bind(wx.EVT_MENU, self.OnClose, id=xrc.XRCID("menu_exit"))
		self.Bind(wx.EVT_MENU, self.OnSave, id=xrc.XRCID("menu_save"))
		self.Bind(wx.EVT_MENU, self.ConfigControlsEnable, id=xrc.XRCID("menu_lockdown"))

		self.frame.Bind(wx.EVT_BUTTON, self.OnAlertAcknowledgeClick, id=xrc.XRCID("alert_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnStartClick, id=xrc.XRCID("control_start_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnSkipClick, id=xrc.XRCID("control_skip_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnStopClick, id=xrc.XRCID("control_stop_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnConnectClick, id=xrc.XRCID("control_connection_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnControlClick, id=xrc.XRCID("control_connection_owner_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnHVDismissClick, id=xrc.XRCID("pmt_check_dismiss_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnHVRefreshClick, id=xrc.XRCID("pmt_check_refresh_button"))
		
		self.frame.Bind(wx.EVT_RADIOBUTTON, self.OnSeriesClick, id=xrc.XRCID("config_global_singlerun_button"))
		self.frame.Bind(wx.EVT_RADIOBUTTON, self.OnSeriesClick, id=xrc.XRCID("config_global_runseries_button"))

		self.frame.Bind(wx.EVT_CHECKBOX, self.OnSSHTunnelClick, id=xrc.XRCID("config_connection_usessh_entry"))

		self.frame.Bind(wx.EVT_CHOICE, self.OnSeriesTypeSelect,   id=xrc.XRCID("config_runseries_type_entry"))
		self.frame.Bind(wx.EVT_CHOICE, self.ConfigControlsEnable, id=xrc.XRCID("config_singlerun_runmode_entry"))

		self.frame.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)

		self.frame.Bind(wx.EVT_SPINCTRL, self.OnRunNumberAdjust, id=xrc.XRCID("config_global_run_entry"))

		self.Bind(Events.EVT_ALERT, self.OnAlert)
		self.Bind(Events.EVT_COMM_STATUS, self.OnCommStateChange)
		self.Bind(Events.EVT_CONTROL_STATUS, self.OnControlStateChange)
		self.Bind(Events.EVT_DAQ_QUIT, self.OnConnectClick)
		self.Bind(Events.EVT_PMT_VOLTAGE_UPDATE, self.OnHVUpdate)
		self.Bind(Events.EVT_STATUS_UPDATE, self.OnStatusUpdate)
		self.Bind(Events.EVT_UPDATE_PROGRESS, self.OnProgressUpdate)
		self.Bind(Events.EVT_UPDATE_SERIES, self.OnSeriesUpdate)
		
	def BindChoices(self):
		""" The lists of items in the drop-down choice boxes
		    are not hard-coded into the GUI; they need to be
		    loaded from the MetaData at runtime. """
		
		entries      = [ "config_singlerun_runmode_entry", "config_singlerun_hwconfig_entry",
		                 "config_singlerun_lilevel_entry", "config_runseries_type_entry" ]
		choice_lists = [ MetaData.RunningModes, MetaData.HardwareConfigurations,
		                 MetaData.LILevels, MetaData.RunSeriesTypes ]
		
		for (entry_name, choice_list) in zip(entries, choice_lists):
			entry = xrc.XRCCTRL(self.frame, entry_name)
			for item in choice_list.descriptions(): 
				entry.Append(item)
			entry.SetSelection(0)
			
		# also take care of the list controls, while we're at it
		controls = (xrc.XRCCTRL(self.frame, "status_daq_series_list"), xrc.XRCCTRL(self.frame, "config_runseries_details"))
		big_col = (3, 2)
		for series_ctrl in controls:
			if series_ctrl == xrc.XRCCTRL(self.frame, "status_daq_series_list"):
				series_ctrl.InsertColumn(0, u"\u00a0", width=30)		# which subrun is currently being executed
			
			for column_name in ("Subrun", "# gates", "Configuration"):
				series_ctrl.InsertColumn(series_ctrl.GetColumnCount(), column_name, width=100)

		# extra details for the 'configuration' one
		config_ctrl = xrc.XRCCTRL(self.frame, "config_runseries_details")
		for column_name in ("LED grps", "LI level"):
			config_ctrl.InsertColumn(series_ctrl.GetColumnCount(), column_name, width=100)
				
		column_map = { 0: "Node",
		               1: "CROC",
		               2: "Chain",
		               3: "Board",
		               4: "HV dev (V)",
		               5: "HV period" }
		pmt_ctrl = xrc.XRCCTRL(self.frame, "pmt_check_list")
		for column in column_map:
			pmt_ctrl.InsertColumn(column, column_map[column], width=100)
		
	def SetupHandlers(self):
		""" Set up the handlers for PostOffice messages. """
		
		subscriptions = [ PostOffice.Subscription(subject="mgr_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="client_alert", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="frontend_internal", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="frontend_info", action=PostOffice.Subscription.DELIVER, delivery_address=self) ]
		handlers = [ self.DAQMgrStatusHandler,
		             self.ClientAlertHandler,
		             self.FrontendInternalHandler,
		             self.FrontendInfoHandler ]
	
		for (subscription, handler) in zip(subscriptions, handlers):
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handler)
		
		
	######################################################
	# Message handlers
	######################################################

	def ClientAlertHandler(self, message):
		""" Handles alert messages. """
		
		if not (hasattr(message, "mgr_id") and hasattr(message, "alert") and hasattr(message, "action")):
			self.logger.warning("DAQMgr's 'client_alert' message is poorly formed.  Ignoring...   Message:\n%s", message)
		
		if message.action == "new":
			self.alert_thread.NewAlert(message.alert)
		elif message.action == "clear":
			self.alert_thread.AcknowledgeAlert(message.alert)
				
	def DAQMgrStatusHandler(self, message):
		""" Decides what to do when the DAQ manager changes status. """
		
		if not (hasattr(message, "status") and hasattr(message, "mgr_id")):
			self.logger.warning("Received poorly-formed DAQ manager status message (ignoring):\n%s", message)
			return
		
		# for now, the only message we care about
		# is when the DAQ goes down.
		if self.daq is not True:
			return
			
		if message.status == "offline":
			self.alert_thread.NewAlert( Alert.Alert(notice="The DAQ manager is shutting down.  Further use of this DAQ won't be possible until it is restarted.", severity=Alert.WARNING) )
			wx.PostEvent(self, Events.DAQQuitEvent())
	
	def FrontendInfoHandler(self, message):
		""" The DAQMgr uses "frontend_info" messages to send us
		    updates that aren't coming in response to a specific
		    request we made. 
		    
		    This method handles those messages. """
		    
		if not hasattr(message, "info"):
			self.logger.warning("DAQMgr's 'frontend_info' message is poorly formed.  Ignoring...   Message:\n%s", message)
			return
		
		if message.info == "control_update" and hasattr(message, "control_info"):
			self.in_control = message.control_info is not None and "client_id" in message.control_info and message.control_info["client_id"] == self.id
			wx.PostEvent( self, Events.ControlStatusEvent(control_info=message.control_info) )

		elif message.info == "status_update" and hasattr(message, "status"):
#			self.logger.debug("Got status report.")
			wx.PostEvent( self, Events.StatusUpdateEvent(status=message.status) )
			
		elif message.info == "HV_warning" and hasattr(message, "pmt_info"):
			self.logger.info("DAQ manager warns about out-of-range HV voltages/periods.")
			wx.PostEvent( self, Events.PMTVoltageUpdateEvent(pmt_info=message.pmt_info, warning=True) )
		
		elif message.info == "pmt_update" and hasattr(message, "pmt_info"):
			wx.PostEvent( self, Events.PMTVoltageUpdateEvent(pmt_info=message.pmt_info, warning=False) )
			
		elif message.info == "series_update" and hasattr(message, "series") and hasattr(message, "series_details"):
			wx.PostEvent( self, Events.UpdateSeriesEvent(series=message.series, details=message.series_details) )
			
	def FrontendInternalHandler(self, message):
		""" Handles messages that are passed around internally
		    by the front end.  Always insists that the messages
		    have no return_path (i.e., haven't been transmitted
		    over the network). """	

		# ignore ill-formed messages
		if not hasattr(message, "event"):
			self.logger.warning("Internal message is badly formed!  Message:\n%s", message)
			return
		
		# internal messages better actually be internal! ...
		if len(message.return_path) > 0:
			self.logger.info("Got 'frontend internal' message over the network.  Ignoring.  Message:\n%s", message)
			return
		
	
	######################################################
	# (wx) Event handlers / wx object manipulators
	######################################################
	
	def ConfigControlsEnable(self, evt=None):
		""" Enables or disables the configuration buttons as appropriate
		    (depending on whether or not we're running, have control, etc.) """

		enabled =    self.status is not None \
		          and ("running" in self.status and self.status["running"] == False) \
		          and self.in_control

		menu_items = [ self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autostart")),
		               self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_lockdown")) ]

		for item in menu_items:
			item.Enable(enabled)

		# the start button has the same stipulations.
		xrc.XRCCTRL(self.frame, "control_start_button").Enable(enabled)


		enabled = enabled and not self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_lockdown")).IsChecked()
		controls = [ xrc.XRCCTRL(self.frame, "config_global_run_entry"),
		             xrc.XRCCTRL(self.frame, "config_global_singlerun_button"),
		             xrc.XRCCTRL(self.frame, "config_global_runseries_button"),
		             xrc.XRCCTRL(self.frame, "config_global_hwreload_button"),

		             xrc.XRCCTRL(self.frame, "config_singlerun_gates_entry"),
		             xrc.XRCCTRL(self.frame, "config_singlerun_runmode_entry"),
		             xrc.XRCCTRL(self.frame, "config_singlerun_hwconfig_entry"),
		             xrc.XRCCTRL(self.frame, "config_singlerun_gates_entry"),
		             
		             xrc.XRCCTRL(self.frame, "config_runseries_type_entry") ]
		             
		for control in controls:
			control.Enable(enabled)

		# it only makes sense to enable the LI options
		# if the selected run is an LI run!
		li_enabled = enabled and xrc.XRCCTRL(self.frame, "config_singlerun_runmode_entry").GetSelection() in (MetaData.RunningModes.LI.index(), MetaData.RunningModes.MIXED_NUMI_LI.index())

		li_controls = [ xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_A_entry"),
		                xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_B_entry"),
		                xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_C_entry"),
		                xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_D_entry"),
		                xrc.XRCCTRL(self.frame, "config_singlerun_lilevel_entry") ]
		                
		for control in li_controls:
			control.Enable(li_enabled)
			
		# the 'skip' and 'stop' buttons should be enabled when we ARE running
		control_enabled =     self.status is not None\
		                  and ("running" in self.status and self.status["running"] == True) \
		                  and self.in_control
		for control in (xrc.XRCCTRL(self.frame, "control_skip_button"), xrc.XRCCTRL(self.frame, "control_stop_button")):
			control.Enable(control_enabled)

	def OnAlert(self, evt):
		""" Makes sure the appropriate things happen
		    when an alert is received. """
		
		self.logger.debug("Alert received: %s", evt.alert)
		
		alert_panel = xrc.XRCCTRL(self.frame, "alert_panel")
		
		# we do DRASTICALLY different things depending on
		# if this user is in control or not.
		# (it is irrelevant whether we're in control for non-manager alerts
		#  so they are given full treatment.)
		if self.in_control or not evt.alert.is_manager_alert:
			# show the alert panel, etc.
			if self.current_alert is None:
				self.logger.info("Showing alert: %s", evt.alert)
				self.ShowPanel(alert_panel, save_state=True)
			
				xrc.XRCCTRL(self.frame, "alert_header").SetLabel( "ERROR" if evt.alert.severity == Alert.ERROR else "WARNING" )
				xrc.XRCCTRL(self.frame, "alert_details").SetLabel(evt.alert.notice)
				xrc.XRCCTRL(self.frame, "alert_details").Wrap(xrc.XRCCTRL(self.frame, "alert_panel").GetClientSize().width - 10)
			
				self.current_alert = evt.alert
		
			if hasattr(evt, "bell") and evt.bell:
				if evt.alert.severity in self.audio_resources:
					self.logger.debug("Playing bell.")
					self.audio_resources[evt.alert.severity].Play(wx.SOUND_ASYNC)
		
			# only errors blink the window.
			if evt.alert.severity == Alert.ERROR and hasattr(evt, "blink") and evt.blink:
				new_bknd_color = self.last_bknd_color if self.last_bknd_color is not None else wx.RED
				self.last_bknd_color = alert_panel.GetBackgroundColour()
				alert_panel.SetBackgroundColour(new_bknd_color)
		else:
			# when we're not in control,
			# we DON'T show the alert panel.
			# instead, we just make sure that
			# the status area shows that we've got
			# an alert (and what it is).
			titles = { Alert.ERROR:   "ERROR",
			           Alert.WARNING: "Warning" }
			text = "%s:\n%s" % (titles[evt.alert.severity], evt.alert.notice)
			xrc.XRCCTRL(self.frame, "summary_alert_text").SetLabel(text)
			xrc.XRCCTRL(self.frame, "summary_alert_text").Wrap(xrc.XRCCTRL(self.frame, "summary_alert_panel").GetClientSize().width - 10)
			
			if len(self.panel_state) == 0:
				self.ShowPanel("summary_alert_panel", save_state=True)
			
	def OnAlertAcknowledgeClick(self, evt):
		""" Informs the alert thread that an alert
		    has been acknowledged (when the button
		    is clicked). """

		alert_id = self.current_alert.id		    
		self.current_alert = None

		# restore the previous window state
		self.RestorePanelState()
		
		# save this until last because it might have
		# another alert waiting.  we want to be set
		# up and ready before it sends us the next
		# notice.
		self.alert_thread.AcknowledgeAlert(alert_id)
		
			
	def OnClose(self, evt=None):
		""" Shuts everything down nicely. """
		
		if self.in_control:
			self.RelinquishControl(self.id)
		
		self.logger.info("Shutting down post office...")
		self.postoffice.Shutdown()

		self.logger.info("Shutting down message terminus...")
		self.Close()

		self.logger.info("Clearing any SSH connections...")
		self.KillSSHProcesses()

		self.logger.info("Shutting down worker thread...")
		self.worker_thread.queue.put("QUIT")
		self.worker_thread.join()
		
		self.logger.info("Shutting down alert thread...")
		self.alert_thread.time_to_quit = True
		self.alert_thread.join()
		
		self.logger.info("Saving configuration...")
		self.SaveConfig()
		
		self.logger.info("Closing the window...")
		self.frame.Destroy()
	
	def OnCommStateChange(self, evt):
		""" Performs the GUI stuff needed when a connection
		    to the DAQ manager changes state. """
		
		if not hasattr(evt, "connected"):
			return

		# restore the panels to their former state
		self.RestorePanelState()

		# and erase any alerts (we're not in control any more)
		self.current_alert = None

		connect_button = xrc.XRCCTRL(self.frame, "control_connection_button")
		connect_statustext = xrc.XRCCTRL(self.frame, "control_connection_content")
		connect_who_indication = xrc.XRCCTRL(self.frame, "control_connection_client_text")

		control_button_panel = xrc.XRCCTRL(self.frame, "control_button_panel")

		if evt.connected:
			connect_statustext.SetLabel("Connected")
			connect_button.SetLabel("Disconnect")

			control_button_panel.Show()
			self.ShowPanel("notebook")

			for page in (xrc.XRCCTRL(self.frame, "control_page"), xrc.XRCCTRL(self.frame, "configuration_page")):
				page.Show()

			# make sure the right panel (single run or series) is showing
			self.OnSeriesClick()

			self.Redraw()
		
#			# format the run series display now that it's visible.
#			series_ctrl = xrc.XRCCTRL(self.frame, "status_daq_series_list")
#			width_left = series_ctrl.GetClientSize().width
#			for col in range(series_ctrl.GetColumnCount()-1):
#				width_left -= series_ctrl.GetColumnWidth(col)
#			series_ctrl.SetColumnWidth(series_ctrl.GetColumnCount()-1, width_left-5)		# leave 5 px buffer
		else:
			control_button_panel.Hide()
			self.ShowPanel("connection_panel")

			xrc.XRCCTRL(self.frame, "config_connection_identity_entry").Enable()
			xrc.XRCCTRL(self.frame, "config_connection_host_entry").Enable()
			xrc.XRCCTRL(self.frame, "config_connection_remoteport_entry").Enable()
			xrc.XRCCTRL(self.frame, "config_connection_usessh_entry").Enable()
			xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry").Enable()
			
			connect_statustext.SetLabel("Not connected")
			connect_button.SetLabel("Connect")
			connect_who_indication.SetLabel("(none)")	
			
			wx.PostEvent( self, Events.UpdateProgressEvent(progress=(0,1), text="Not connected.") )

	def OnConnectClick(self, evt):
		""" Starts the connection/disconnection process in a separate thread. """
		connect_button = xrc.XRCCTRL(self.frame, "control_connection_button")
		connect_statustext = xrc.XRCCTRL(self.frame, "control_connection_content")
		connect_who_indication = xrc.XRCCTRL(self.frame, "control_connection_client_text")
		connect_who_entry = xrc.XRCCTRL(self.frame, "config_connection_host_entry")
		use_ssh_entry = xrc.XRCCTRL(self.frame, "config_connection_usessh_entry")
		ssh_user_entry = xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry")
		remote_port_entry = xrc.XRCCTRL(self.frame, "config_connection_remoteport_entry")

		self.ssh_details = { "use_ssh": use_ssh_entry.IsChecked(), "ssh_user": ssh_user_entry.GetValue(), 
		                     "remote_host": connect_who_entry.GetValue(), "remote_port": remote_port_entry.GetValue() }
	
		#  not connected
		if self.daq is False:
			connect_statustext.SetLabel("Connecting...")
			connect_who_indication.SetLabel(connect_who_entry.GetValue())
			connect_button.SetLabel("Cancel connection")

			xrc.XRCCTRL(self.frame, "config_connection_identity_entry").Disable()
			xrc.XRCCTRL(self.frame, "config_connection_host_entry").Disable()
			xrc.XRCCTRL(self.frame, "config_connection_remoteport_entry").Disable()
			xrc.XRCCTRL(self.frame, "config_connection_usessh_entry").Disable()
			xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry").Disable()

			work = { "method": self.ConnectDAQ, "kwargs": self.ssh_details }

		# in the process of setting up the connection
		elif self.daq is None:
			self.stop_connecting = True
			work = { "method": self.DisconnectDAQ, "kwargs": self.ssh_details }
		else:
			# if the DAQ manager quit, we don't have control any more,
			# and it's down so we can't run the RelinquishControl method.
			# so check what kind of event we're getting so that we do
			# the right thing if it's a 'DAQ quit' one.
			if evt.GetEventType() == Events.EVT_DAQ_QUIT.typeId:
				self.in_control = False
				wx.PostEvent(self, Events.ControlStatusEvent())
			work = { "method": self.DisconnectDAQ, "kwargs": self.ssh_details }
			
		control_page = xrc.XRCCTRL(self.frame, "control_page")
		self.Redraw()

		self.worker_thread.queue.put(work)
		
	def OnControlClick(self, evt):
		""" Starts the control request process using the worker thread. """
		
		# disable the control so that this doesn't happen twice simultaneously.
		# when confirmation or timeout is received, it will be re-enabled.
		xrc.XRCCTRL(self.frame, "control_connection_owner_button").Disable()

		if not self.in_control:
			# this is a bit ugly, but it doesn't seem worth the effort to carry around
			# a whole other property for who else is in control when it will only be used here.
			if xrc.XRCCTRL(self.frame, "control_connection_owner_entry").GetLabel() != "--":
				dlg = wx.MessageDialog(self.frame, message="Another client currently has control of the DAQ.  Are you sure you want to take over?", caption="Confirm control request", style=wx.YES_NO | wx.ICON_EXCLAMATION | wx.NO_DEFAULT)
				if dlg.ShowModal() == wx.ID_NO:
					xrc.XRCCTRL(self.frame, "control_connection_owner_button").Enable()
					return
			
			my_location = socket.gethostbyname(socket.gethostname()) if self.ip_addr is None else self.ip_addr
				
			work = { "method": self.GetControl, 
			         "kwargs": { "my_name": xrc.XRCCTRL(self.frame, "config_connection_identity_entry").GetValue(),
			                     "my_id": self.id,
			                     "my_location": my_location } }
		else:
			work = { "method": self.RelinquishControl, "kwargs": {"my_id": self.id} }

		self.worker_thread.queue.put(work)
	
	def OnControlStateChange(self, evt):
		""" Adjust the appropriate GUI elements when control
		    of the DAQ changes hands. """
		button = xrc.XRCCTRL(self.frame, "control_connection_owner_button")
		button.Enable()

		entry = xrc.XRCCTRL(self.frame, "control_connection_owner_entry")
		label = xrc.XRCCTRL(self.frame, "control_connection_owner_label")
		status = xrc.XRCCTRL(self.frame, "control_connection_owner_status")
		if self.in_control:
			label.Hide()
			entry.Hide()
			status.SetLabel("In control")
			button.SetLabel("Relinquish control")
		else:
			entry.Show()
			label.Show()
			status.SetLabel("Not in control")
			button.SetLabel("Request control")
		
			if hasattr(evt, "control_info"):
				if evt.control_info is None:
					entry.SetLabel("--")
				else:
					entry.SetLabel( "%s\n(%s)" % (evt.control_info["client_identity"], evt.control_info["client_location"]) )

		self.ConfigControlsEnable()
		
		self.RestorePanelState()

		# erase any alerts (start fresh)
		self.current_alert = None
		
		# if the PMT high voltages are still awaiting confirmation,
		# send out a new event
		if self.problem_pmt_list is not None:
			wx.PostEvent( self, Events.PMTVoltageUpdateEvent(pmt_info=self.problem_pmt_list, warning=True) )
		
		self.Redraw()

	def OnHVDismissClick(self, evt):
		""" Continues the run sequence after a PMT HV/period check. """

		self.RestorePanelState()
		self.problem_pmt_list = None
		
		self.postoffice.Send( PostOffice.Message(subject="mgr_directive", directive="pmt_dismiss", client_id=self.id) )
		
	def OnHVUpdate(self, evt):
		""" Presents the user with a list of PMT voltages
		    that are likely to be problematic and solicits
		    user input on whether it is safe to continue. """
		
		assert hasattr(evt, "pmt_info")
		
		# only if the DAQ manager is explicitly asking
		# for confirmation do we force the PMT display to be shown.
		if hasattr(evt, "warning") and evt.warning:
			self.problem_pmt_list = evt.pmt_info
			if self.in_control:
				self.ShowPanel("pmt_check_panel", save_state=True)
			else:
				xrc.XRCCTRL(self.frame, "summary_alert_text").SetLabel("PMT high voltage or period state is outside tolerances.")
				self.ShowPanel("summary_alert_panel", save_state=True)
		elif evt.pmt_info is None:
			self.RestorePanelState()
			return
		
		pmt_list = xrc.XRCCTRL(self.frame, "pmt_check_list")
		pmt_list.DeleteAllItems()
		
		colors = { 1: "red", 2: "orange", 3: "yellow" }		# used to demarcate the boards that have exceeded certain thresholds
		color_norange = "white"
		
		# eventually we'll want to do some sorting, but for now ...
		for board in evt.pmt_info:
			index = pmt_list.InsertStringItem(sys.maxint, board["node"])
			pmt_list.SetStringItem(index, 1, str(board["croc"]))
			pmt_list.SetStringItem(index, 2, str(board["chain"]))
			pmt_list.SetStringItem(index, 3, str(board["board"]))
			pmt_list.SetStringItem(index, 4, str(board["hv_deviation"]))
			pmt_list.SetStringItem(index, 5, str(board["period"]))
			
			# low-HV period boards will probably show up at the top this way.
			if board["failure"] == "period":
				pmt_list.SetItemData(index, int(board["period"]))
				pmt_list.SetItemBackgroundColour(index, wx.NamedColour("blue"))
			elif board["failure"] == "hv_range":
				data = abs(int(board["hv_deviation"]))
				pmt_list.SetItemData(index, data)
				color = color_norange if board["range"] not in colors else colors[board["range"]]
				pmt_list.SetItemBackgroundColour(index, wx.NamedColour(color))

		# sort them in DESCENDING order.
		pmt_list.SortItems(lambda a,b : 0 if a == b else (-1 if a > b else 1))
		
		# now convert the deviations from ADC counts to volts
		index = pmt_list.GetNextItem(-1)
		while index != -1:
			listitem = pmt_list.GetItem(index, 4)
			dev = int(listitem.GetText())
			
			pmt_list.SetStringItem(index, 4, str(int(dev / 60)))

			index = pmt_list.GetNextItem(index)
	
		self.Redraw()

		width_left = pmt_list.GetClientSize().width
		for col in range(pmt_list.GetColumnCount()-1):
			width_left -= pmt_list.GetColumnWidth(col)
		pmt_list.SetColumnWidth(pmt_list.GetColumnCount()-1, width_left-5)		# leave 5 px buffer

	
	def OnHVRefreshClick(self, evt):
		""" Asks the DAQ mgr to send a new list of PMT high voltages. """

		self.postoffice.Send( PostOffice.Message(subject="mgr_directive", directive="pmt_hv_list", client_id=self.id) )
	
	def OnProgressUpdate(self, evt):
		""" Updates the progress gauge text label and value.
		
		    Values are set via the attributes of the event:
		    any text to be displayed below the progress bar
		    should be contained in the attribute 'text'.
		    If you want the gauge in 'indeterminate' mode,
		    set 'progress' to (0,0); otherwise, 'progress'
		    should be (current, total). """
		    
		progress_label = xrc.XRCCTRL(self.frame, "status_progress_label")
		progress_gauge = xrc.XRCCTRL(self.frame, "status_progress_gauge")
		if hasattr(evt, "text") and evt.text is not None:
			progress_label.Show()
			progress_label.SetLabel(evt.text)
			progress_label.Wrap(progress_label.GetClientSize().width)
		elif hasattr(evt, "text") and evt.text is None:
			progress_label.Hide()
		
		if hasattr(evt, "progress"):
			if evt.progress is not None:
				progress_gauge.Show()
				if evt.progress == (0,0):		# indeterminate mode
					progress_gauge.Pulse()
				else:
					# be sure that if the alert thread 
					# is currently 'pulsing' the gauge,
					# we tell it to stop
					if self.alert_thread.do_pulse:
						self.alert_thread.do_pulse = False
					
					progress_gauge.SetRange(evt.progress[1])
					progress_gauge.SetValue(evt.progress[0])
			else:
				progress_gauge.Hide()

		self.Redraw()

		
	def OnRunNumberAdjust(self, evt):
		""" Ensures that the run number can't be lowered
		    past the current run number, and sets the 
		    subrun number accordingly. """
		    
		run_entry = xrc.XRCCTRL(self.frame, "config_global_run_entry")
		subrun_entry = xrc.XRCCTRL(self.frame, "config_global_subrun_entry")
		    
		if run_entry.GetValue() < run_entry.GetMin():
			run_entry.SetValue(run_entry.GetMin())
		
		if run_entry.GetValue() > run_entry.GetMax():
			run_entry.SetValue(run_entry.GetMax())
		
		if run_entry.GetValue() == run_entry.GetMin():
			subrun_entry.SetValue(self.min_subrun)
		else:
			subrun_entry.SetValue(1)

	def OnSave(self, evt):
		self.SaveConfig()
		
	def OnSeriesClick(self, evt=None):
		""" Updates the configuration panels to show the relevant
		    run configuration: single-run or run series. """

		singlerun = xrc.XRCCTRL(self.frame, "config_global_singlerun_button").GetValue()
		xrc.XRCCTRL(self.frame, "config_singlerun_panel").Show(singlerun)
		xrc.XRCCTRL(self.frame, "config_runseries_panel").Show(not singlerun)

		# be sure to get the newest version
		# of whichever series is currently selected
		# if the user wants a run series
		if not singlerun:
			self.OnSeriesTypeSelect()

			# also format the run series display now that it's visible.
#			width_left = series_ctrl.GetClientSize().width
#			for col in range(series_ctrl.GetColumnCount()-1):
#				width_left -= series_ctrl.GetColumnWidth(col)
#			series_ctrl.SetColumnWidth(series_ctrl.GetColumnCount()-1, width_left)

		self.Redraw()
		
	def OnSeriesTypeSelect(self, evt=None):
		""" Initiates the process of retrieving the appropriate
		    run series from the DAQ Mgr. """

		series = MetaData.RunSeriesTypes.item(xrc.XRCCTRL(self.frame, "config_runseries_type_entry").GetSelection())
		    
		series_ctrl = xrc.XRCCTRL(self.frame, "config_runseries_details")
		series_ctrl.DeleteAllItems()
		series_ctrl.InsertStringItem(sys.maxint, "Please wait while the '%s' series description is downloaded..." % series.description)
		series_ctrl.SetColumnWidth(0, series_ctrl.GetClientSize().width)
		
		self.postoffice.Send( PostOffice.Message(subject="mgr_directive", directive="series_info", client_id=self.id, series=series) )
	
	def OnSeriesUpdate(self, evt):
		""" Fills in the series list on the config page
		    with an updated list from the DAQ manager. """
		
		assert hasattr(evt, "series") and hasattr(evt, "details")

		# make sure that this client actually WANTS this update
		if MetaData.RunSeriesTypes.index(evt.series) != xrc.XRCCTRL(self.frame, "config_runseries_type_entry").GetSelection():
			return
		
		series_ctrl = xrc.XRCCTRL(self.frame, "config_runseries_details")
		series_ctrl.DeleteAllItems()

		series_ctrl.SetColumnWidth(0, wx.LIST_AUTOSIZE_USEHEADER)
#		
		for runinfo in evt.details.Runs:
			index = series_ctrl.InsertStringItem(sys.maxint, "")         # first column is which subrun is currently being executed
			series_ctrl.SetStringItem( index, 0, str(evt.details.Runs.index(runinfo)+1) )
			series_ctrl.SetStringItem( index, 1, str(runinfo.gates))
			series_ctrl.SetStringItem( index, 2, MetaData.RunningModes.description(runinfo.runMode) )
			if runinfo.runMode in (MetaData.RunningModes.LI, MetaData.RunningModes.MIXED_NUMI_LI):
				li_level = MetaData.LILevels.description(runinfo.ledLevel)
				led_groups = MetaData.LEDGroups.description(runinfo.ledGroup)
			else:
				li_level = "--"
				led_groups = "--"
			
			series_ctrl.SetStringItem( index, 3, led_groups )
			series_ctrl.SetStringItem( index, 4, li_level )

		
		
	def OnSkipClick(self, evt):
		""" Tell the DAQ to skip to the next subrun. """
		
		# disable the skip button so it can't be clicked twice in a row.
		# it will be re-enabled by the call to ConfigControlsEnable()
		# that comes with the beginning-of-subrun status update.
		xrc.XRCCTRL(self.frame, "control_skip_button").Disable()
		
		self.postoffice.Send( PostOffice.Message(subject="mgr_directive", directive="skip", client_id=self.id) )
		
	
	def OnSSHTunnelClick(self, evt):
		""" Flip the entry's enabled status. """
		xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry").Enable(xrc.XRCCTRL(self.frame, "config_connection_usessh_entry").IsChecked())
		
	def OnStartClick(self, evt):
		""" Initiate the startup sequence, if the conditions are right. """

		# the 'start' button shouldn't be enabled if we aren't connected
		# or aren't in control, but it's always better to check anyway
		if self.daq is not True or not self.in_control:
			xrc.XRCCTRL(self.frame, "control_start_button").Disable()
			return
			
		# this is supposed to be set when the DAQ is connected.
		# since it passed the check above, there should be no way this happens.
		assert self.status is not None
		
		# make sure the controls get disabled so nothing can be changed
		# while the startup sequence is going.
		self.status["running"] = True
		self.ConfigControlsEnable()
		
		# assemble the information needed to properly start the run
		self.status["configuration"].run               = xrc.XRCCTRL(self.frame, "config_global_run_entry").GetValue()
		self.status["configuration"].subrun            = xrc.XRCCTRL(self.frame, "config_global_subrun_entry").GetValue()
		self.status["configuration"].is_single_run     = xrc.XRCCTRL(self.frame, "config_global_singlerun_button").GetValue()
		self.status["configuration"].num_gates         = xrc.XRCCTRL(self.frame, "config_singlerun_gates_entry").GetValue()
		self.status["configuration"].force_hw_config   = xrc.XRCCTRL(self.frame, "config_global_hwreload_button").GetValue()
		self.status["configuration"].run_mode          = MetaData.RunningModes.item(xrc.XRCCTRL(self.frame, "config_singlerun_runmode_entry").GetSelection())
		self.status["configuration"].hw_config         = MetaData.HardwareConfigurations.item(xrc.XRCCTRL(self.frame, "config_singlerun_hwconfig_entry").GetSelection())
		self.status["configuration"].li_level          = MetaData.LILevels.item(xrc.XRCCTRL(self.frame, "config_singlerun_lilevel_entry").GetSelection())
		self.status["configuration"].run_series        = MetaData.RunSeriesTypes.item(xrc.XRCCTRL(self.frame, "config_runseries_type_entry").GetSelection())
		self.status["configuration"].auto_start_series = self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autostart")).IsChecked()
		LEDs = ""
		for char in "ABCD":
			if xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_%s_entry" % char).GetValue():
				LEDs += char
		self.status["configuration"].led_groups = MetaData.LEDGroups[LEDs]
		
		# automatically select the "status" tab in the notebook
		xrc.XRCCTRL(self.frame, "notebook").ChangeSelection(0)
		
		self.worker_thread.queue.put( {"method": self.StartRunning} )
		
	def OnStatusUpdate(self, evt):
		""" Updates the panels to reflect the current DAQ status
		    as indicated by the status report in 'status'. """
		
		if not hasattr(evt, "status"):
			return
		
		status = evt.status
		
		if self.status is None:
			self.status = status
		else:
			for item in status:
				self.status[item] = status[item]
		
		# keep the gate count current
		if "current_gate" in status and status["current_gate"] is not None \
		   and "running" in self.status and self.status["running"]:
			xrc.XRCCTRL(self.frame, "status_trigger_run").SetLabel( "%d/%d" % (self.status["configuration"].run, self.status["configuration"].subrun) )
			xrc.XRCCTRL(self.frame, "status_trigger_number").SetLabel( str(status["current_gate"]["number"]) )
			xrc.XRCCTRL(self.frame, "status_trigger_type").SetLabel( status["current_gate"]["type"].description )
			xrc.XRCCTRL(self.frame, "status_trigger_time_label").SetLabel( "time (%s):" % time.strftime("%Z") )
			xrc.XRCCTRL(self.frame, "status_trigger_time").SetLabel( time.strftime("%H:%M:%S", time.localtime(status["current_gate"]["time"])) )
			
			self.alert_thread.TriggerUpdate()
			
			update_event = Events.UpdateProgressEvent()
#			update_event.progress = (status["current_gate"]["number"], self.status["configuration"].num_gates)
#			update_event.text = "Running:\nGate %d/%d" % (status["current_gate"]["number"], self.status["configuration"].num_gates)
			update_event.text = "Running"
			wx.PostEvent(self, update_event)
		
		# make sure that status changes are reflected
		if "current_state" in status or "current_progress" in status:
			update_event = Events.UpdateProgressEvent()
			if "current_state" in status:
				update_event.text = status["current_state"]
			if "current_progress" in status:
				update_event.progress = status["current_progress"]
			wx.PostEvent(self, update_event)

		
		# update the remote node indicators
		if "remote_nodes" in status:
			# can't guarantee that there are always
			# the same set of nodes.  (it's up to the
			# DAQ manager to enforce that -- and what
			# if we switch DAQ managers?)  so we
			# delete them all and replace them every time.
			node_panel = xrc.XRCCTRL(self.frame, "status_daq_hw_panel")
			node_sizer = node_panel.GetSizer()
			node_sizer.Clear(deleteWindows=True)
			node_sizer.AddStretchSpacer(prop=1)
			for node in status["remote_nodes"]:
				node_obj = status["remote_nodes"][node]
				sizer = wx.BoxSizer(wx.VERTICAL)
				img = wx.StaticBitmap(node_panel)
				
				if node_obj.status == RemoteNode.OK:
					img.SetBitmap(self.image_resources["LED on"])
				elif node_obj.status == RemoteNode.ERROR:
					img.SetBitmap(self.image_resources["LED error"])
				else:
					img.SetBitmap(self.image_resources["LED off"])
				
				sizer.Add(img, proportion=0, flag=wx.ALIGN_CENTER_HORIZONTAL)
				sizer.Add(wx.StaticText(node_panel, id=-1, label=node+" node"), \
				          proportion=0, \
				          border=5, \
				          flag=wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT)
				
				node_sizer.Add(sizer)
				node_sizer.AddStretchSpacer(prop=1)
			node_sizer.ShowItems(True)

		series_ctrl = xrc.XRCCTRL(self.frame, "status_daq_series_list")
		
		# update the 'status' areas at the bottom
		if "running" in status:
			if status["running"] is None:
				status_text = "TRANSITION"
			elif status["running"] == False:
				status_text = "IDLE"
			elif status["running"] == True:
				
				status_text = "RUNNING"
			
			# should stop measuring 'last trigger' updates
			# if we're not actually running.
			if status["running"] != True:
				self.alert_thread.TriggerUpdate(turn_off=True)
			
			# a right-facing triangle (like a "play" symbol)
			# or a square (like a "stop" symbol), respectively
			status_symbol = u"\u25b7" if status["running"] else u"\u25a1"
			
			xrc.XRCCTRL(self.frame, "status_daq_status").SetLabel(status_text)
			xrc.XRCCTRL(self.frame, "status_text").SetLabel(status_text)
			xrc.XRCCTRL(self.frame, "status_symbol").SetLabel(status_symbol)

			if "configuration" in status:
				run = str(status["configuration"].run) 
				subrun = str(status["configuration"].subrun) 
				
				xrc.XRCCTRL(self.frame, "status_runinfo_run").SetLabel(run)
				xrc.XRCCTRL(self.frame, "status_daq_run").SetLabel(run)
				xrc.XRCCTRL(self.frame, "status_runinfo_subrun").SetLabel(subrun)

			self.ConfigControlsEnable()
			
			for menu_item in [ "menu_lockdown", ]:
				self.frame.GetMenuBar().FindItemById(xrc.XRCID(menu_item)).Enable(self.in_control and not status["running"])

		if "first_subrun" in status:
			self.min_subrun = status["first_subrun"]

		# display the run series
		if "run_series" in status and "first_subrun" in status:
			series_ctrl.DeleteAllItems()
			
			for runinfo in status["run_series"].Runs:
				index = series_ctrl.InsertStringItem(sys.maxint, "")         # first column is which subrun is currently being executed
				series_ctrl.SetStringItem( index, 1, str(status["run_series"].Runs.index(runinfo) + status["first_subrun"]) )
				series_ctrl.SetStringItem( index, 2, str(runinfo.gates) )
				series_ctrl.SetStringItem( index, 3, MetaData.RunningModes.description(runinfo.runMode) )

		# now get the configuration and fill the appropriate boxes
		if "configuration" in status:
			runnum_ctrl = xrc.XRCCTRL(self.frame, "config_global_run_entry")
			runnum_ctrl.SetValue(status["configuration"].run)
			runnum_ctrl.SetRange(status["configuration"].run, runnum_ctrl.GetMax())
			xrc.XRCCTRL(self.frame, "config_global_subrun_entry").SetValue(status["configuration"].subrun)
			xrc.XRCCTRL(self.frame, "config_global_singlerun_button").SetValue(status["configuration"].is_single_run)
			xrc.XRCCTRL(self.frame, "config_global_runseries_button").SetValue(not status["configuration"].is_single_run)
			xrc.XRCCTRL(self.frame, "config_global_hwreload_button").SetValue(status["configuration"].force_hw_reload)
			xrc.XRCCTRL(self.frame, "config_singlerun_gates_entry").SetValue(status["configuration"].num_gates)
			xrc.XRCCTRL(self.frame, "config_singlerun_runmode_entry").SetSelection(MetaData.RunningModes.index(status["configuration"].run_mode))
			xrc.XRCCTRL(self.frame, "config_singlerun_hwconfig_entry").SetSelection(MetaData.HardwareConfigurations.index(status["configuration"].hw_config))
			xrc.XRCCTRL(self.frame, "config_singlerun_lilevel_entry").SetSelection(MetaData.LILevels.index(status["configuration"].li_level))
			xrc.XRCCTRL(self.frame, "config_runseries_type_entry").SetSelection(MetaData.RunSeriesTypes.index(status["configuration"].run_series))
			self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autostart")).Check(status["configuration"].auto_start_series)
			for char in "ABCD":
				xrc.XRCCTRL(self.frame, "config_singlerun_ledgroups_%s_entry" % char).SetValue( char in status["configuration"].led_groups.description )


			if not "running" in self.status or not self.status["running"]:
				symbol = u"\u25a1"		# a square: like a "stop" symbol
				color = wx.NamedColour("yellow")
			else:
				symbol = u"\u25b7"		# a right-facing triangle: like a "play" symbol
				color = wx.NamedColour("green")

			index = -1
			while True:
				index = series_ctrl.GetNextItem(index)
		
				if index == -1:
					break
		
				if index == status["configuration"].subrun - self.status["first_subrun"]:
					series_ctrl.SetStringItem(index, 0, symbol)
					series_ctrl.SetItemBackgroundColour(index, color)
					series_ctrl.EnsureVisible(index)
				else:
					series_ctrl.SetStringItem(index, 0, "")
					series_ctrl.SetItemBackgroundColour(index, wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
		
		# who's in control?
		if "control_info" in status and status["control_info"] is not None:
			wx.PostEvent(self, Events.ControlStatusEvent(have_control=False, control_info=status["control_info"]))
			
		# make sure any pending alerts are added to our stack
		for item in ("warnings", "errors"):
			if item not in status:
				status[item] = []
		for alert in status["warnings"] + status["errors"]:
			self.alert_thread.NewAlert(alert)
		
		# and if there's a PMT HV warning, be sure the user knows
		if "problem_pmt_list" in status:
			warning = status["problem_pmt_list"] is not None
			wx.PostEvent( self, Events.PMTVoltageUpdateEvent(pmt_info=status["problem_pmt_list"], warning=warning) )
			
		# make sure the alert thread is doing the right thing
		# about the status bar ('pulsing' while waiting, and
		# leaving it alone when not).
		if "waiting" in status:
			self.alert_thread.do_pulse = status["waiting"]

		# in case anything moved
		self.Redraw()
	
	def OnStopClick(self, evt=None):
		""" Begin the shutdown sequence. """

		assert self.status["running"] == True

		# make sure we're showing the right panel...
		self.ShowPanel("notebook")

		# disable ALL the controls so shutdown can't be interrupted
		# ("Start" will be re-enabled when we reach idle)
		self.status["running"] = None
		self.ConfigControlsEnable()
		
		# make sure it's clear to the user that we're trying to stop
		wx.PostEvent( self, Events.UpdateProgressEvent(progress=(0, 0), text="Stopping...") )

		# clear the PMT list now so that we don't accidentally keep showing the window.
		# if there still are problem PMTs, they will be added BACK to the list when
		# the next status report comes.
		self.problem_pmt_list = None
		
		self.worker_thread.queue.put( {"method": self.StopRunning} )
	
	def Redraw(self):
		""" Makes sure that everything is completely
		    repositioned and redrawn as necessary. """

#		self.frame.Refresh()

		if not xrc.XRCCTRL(self.frame, "control_panel").IsShown():
			self.logger.debug("Control panel not shown.  Not redrawing.")
			return
		
		# force the auto-layout algorithms to run
		xrc.XRCCTRL(self.frame, "control_page").Layout()
		xrc.XRCCTRL(self.frame, "configuration_page").Layout()
		self.frame.Layout()
		
		# then make sure our list controls look right		
		controls = ( xrc.XRCCTRL(self.frame, "status_daq_series_list"),
		             xrc.XRCCTRL(self.frame, "config_runseries_details") )
		big_col = (3, 2)
		for series_ctrl, focus_col in zip(controls, big_col):
			series_ctrl.Layout()
			width_left = series_ctrl.GetClientSize().width
			for col in range(series_ctrl.GetColumnCount()):
				# the "Configuration" column is supposed to be the big one
				if col == focus_col:
					continue
				series_ctrl.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)
				width_left -= series_ctrl.GetColumnWidth(col)
				
			series_ctrl.SetColumnWidth(focus_col, width_left-2)
	
	def RestorePanelState(self):
		""" Restores the panel state previously set
		    by using SavePanelState(). """
		
		self.logger.debug("Restoring panel state.")

		# if the alert panel is still "blinked", reset it
		panel = xrc.XRCCTRL(self.frame, "alert_panel")
		if panel.GetBackgroundColour() == wx.RED:
			panel.SetBackgroundColour(self.last_bknd_color)
		self.last_bknd_color = None
		
		for collection in self.panel_stack:
			if len(self.panel_stack[collection]) > 0:
				panel_to_show = self.panel_stack[collection].pop()
				for panel in self.panel_collections[collection]:
					panel_id = panel.GetId()
					shown = panel_id == panel_to_show
					self.logger.debug("Restoring panel %s to shown state: %s", panel_id, shown)
					panel.Show(shown)
				do_redraw = True

		self.logger.debug("Panel stack state: %s", pprint.pformat(self.panel_stack))
		#self.Redraw()
	
	def SavePanelState(self):
		""" Puts the display state of the panels
		    into a storage 'register' for later retrieval. """

		self.logger.debug("Saving panel state.")
		
		for collection in self.panel_collections:
			for panel in self.panel_collections[collection]:
				if panel.IsShown():
					if len(self.panel_stack[collection]) == 0 or self.panel_stack[collection][-1] != panel.GetId():
						self.panel_stack[collection].append(panel.GetId())
						break
	
	def ShowPanel(self, panel_in, save_state=False):
		""" Show a particular panel and (optionally)
		    save the state using SavePanelState. """
		
		self.logger.debug("Showing panel: %s", panel_in)
		
		# if it's not a panel object, then maybe it's an XRC ID...
		if isinstance(panel_in, wx.Window):
			panel = panel_in
		else:
			panel = xrc.XRCCTRL(self.frame, panel_in)
			
			if panel is None:
				panel = wx.FindWindowById(panel_in)
				
		if panel is None:
			self.logger.warning("Asked to show a non-panel!")
			raise ValueError("'panel' must be a wx.Panel object, the xrc identifier of a panel object in the resource file, or the wx ID of a panel.")


		collection = None
		for c in self.panel_collections:
			if panel in self.panel_collections[c]:
				collection = c
				break
		
		assert collection is not None

		# if there is an alert currently up, that needs to take precedence.
		# just put the window that wants to be shown on the stack;
		# when the "restore" comes after the alert, it'll be shown then.
		if (collection == "main" and xrc.XRCCTRL(self.frame, "alert_panel").IsShown()) \
		  or (collection == "status" and xrc.XRCCTRL(self.frame, "summary_alert_panel").IsShown()):
		  	self.logger.debug("Alert is up... won't hide it.")
			self.panel_stack[collection].append(panel.GetId())
#			self.logger.debug("Panel stack state: %s", pprint.pformat(self.panel_stack))
			return
		# only store the state & show the new panel if the alert panel isn't being shown...
		elif save_state:
			self.SavePanelState()
		
		for other_panel in self.panel_collections[collection]:
			if panel != other_panel:
				other_panel.Hide()
		
		self.logger.debug("Panel shown: %s", panel.GetLabel())
#		self.logger.debug("Panel stack state: %s", pprint.pformat(self.panel_stack))
		panel.Show()
		self.Redraw()
		
		
	######################################################
	# Methods that actually do something substantial
	#  (might be run in their own thread -- watch out!
	#   don't try to change any wx items; ONLY use
	#   wx.PostEvent().)
	######################################################
	
	def ConnectDAQ(self, use_ssh=True, ssh_user="mnvonline", remote_host="mnvonlinemaster.fnal.gov", remote_port=3000):
		""" Does the actual work of connecting to the DAQ manager. """

		if self.daq is not False:
			return

		self.stop_connecting = False
		self.daq = None

		# set up the SSH tunnels if necessary
		if use_ssh:
			success = self.PrepareSSHTunnels(ssh_user=ssh_user, remote_host=remote_host, remote_port=remote_port)
			
			if not success:
				self.alert_thread.NewAlert( Alert.Alert(notice="Could not make a connection to the DAQ manager!", severity=Alert.ERROR) )
				self.DisconnectDAQ(use_ssh, remote_host, remote_port)
				return
		
		host = "localhost" if use_ssh else remote_host
				
		# set up forwarding subscriptions
		self.postoffice.AddSubscription( PostOffice.Subscription(subject="control_request", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )
		self.postoffice.AddSubscription( PostOffice.Subscription(subject="mgr_directive", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )
		
		# get the current status of the DAQ and draw it
		response = self.DAQSendWithResponse( PostOffice.Message(subject="mgr_directive", directive="status_report", client_id=self.id), timeout=Configuration.params["sock_messageTimeout"] )
		
		if response is None:
			self.DisconnectDAQ(use_ssh, remote_host, remote_port)
			return
		else:
			wx.PostEvent(self, Events.StatusUpdateEvent(status=response.status))
		
		# ask for the necessary forwarding subscriptions from the DAQ manager
		subscriptions = []
		for subscription in self.handlers:
			newsub = copy.copy(subscription)
			newsub.action = PostOffice.Subscription.FORWARD
			newsub.delivery_address = PostOffice.IPv4Address(None, self.postoffice.listen_port)
			subscriptions.append(newsub)
		self.postoffice.ForwardRequest( host=(host, remote_port), subscriptions=subscriptions )
				
		self.daq = True

		wx.PostEvent( self, Events.UpdateProgressEvent(progress=(0,1), text="Connected.") )
		wx.PostEvent(self, Events.CommStatusEvent(connected=True))

	def DAQSendWithResponse(self, message, panic_if_no_connection=True, timeout=None, with_exception=False):
		""" Sends a message to the DAQ and waits for a response.
		    Verifies that there is indeed exactly one response
		    and notifies the user if there isn't. """
		
		responses = self.postoffice.SendAndWaitForResponse( message, timeout=timeout, with_exception=with_exception )
		
		if len(responses) == 0:
			if panic_if_no_connection:
				self.alert_thread.NewAlert( Alert.Alert(notice="Can't connect to DAQ manager!", severity=Alert.ERROR) )
				if self.daq:
					self.DisconnectDAQ(**self.ssh_details)
				return None
			else:
				return []
		elif len(responses) > 1:
			self.alert_thread.NewAlert( Alert.Alert(notice="Got too many DAQ manager responses!  Check the network setup...", severity=Alert.ERROR) )
			return None
		else:
			return responses[0]

	def DisconnectDAQ(self, use_ssh, remote_host, remote_port, **kwargs):
		""" Does the actual disconnection process from the DAQ. """
		if self.daq is False:
			return
			
		self.logger.debug("Disconnecting from DAQ.")
		
		if self.in_control:
			self.RelinquishControl(self.id)
			
		self.problem_pmt_list = None

		host = "localhost" if use_ssh else remote_host

		self.postoffice.DropSubscription( PostOffice.Subscription(subject="mgr_directive", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )
		self.postoffice.DropSubscription( PostOffice.Subscription(subject="control_request", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )

		subscriptions = []
		for subscription in self.handlers:
			newsub = copy.copy(subscription)
			newsub.action = PostOffice.Subscription.FORWARD
			newsub.delivery_address = PostOffice.IPv4Address(None, self.postoffice.listen_port)

			subscriptions.append(newsub)
		self.postoffice.ForwardCancel( host=(host, remote_port), subscriptions=subscriptions )
			
		if use_ssh:
			self.KillSSHProcesses()

		self.alert_thread.DropManagerAlerts()

		self.daq = False
		wx.PostEvent(self, Events.CommStatusEvent(connected=False))
	
	def GetControl(self, my_id, my_name, my_location):
		""" Requests control of the DAQ from the DAQ manager. """
		
		response = self.DAQSendWithResponse( PostOffice.Message(subject="control_request", request="get", requester_id=my_id, requester_name=my_name, requester_location=my_location), timeout=Configuration.params["sock_messageTimeout"] )
		
		if response is not None:
			self.in_control = True
			wx.PostEvent(self, Events.ControlStatusEvent())

	def LoadConfig(self):
		""" Loads the connection settings from the
		    file they were stored in and sets the
		    values of the entries appropriately. """

		self.cfg = wx.Config('mnvruncontrol')
		
		identity     = self.cfg.Read("identity", "Anonymous coward")
		remote_host  = self.cfg.Read("remote_host", "mnvonlinemaster.fnal.gov")
		remote_port  = self.cfg.ReadInt("remote_port", 1090)
		use_ssh      = self.cfg.ReadBool("use_ssh", True)
		ssh_user     = self.cfg.Read("ssh_user", "mnvonline")
		lockdown     = self.cfg.ReadBool("lockdown", False)
		auto_connect = self.cfg.ReadBool("auto_connect", False)
		
		xrc.XRCCTRL(self.frame, "config_connection_identity_entry").SetValue(identity)
		xrc.XRCCTRL(self.frame, "config_connection_host_entry").SetValue(remote_host)
		xrc.XRCCTRL(self.frame, "config_connection_remoteport_entry").SetValue(remote_port)
		xrc.XRCCTRL(self.frame, "config_connection_usessh_entry").SetValue(use_ssh)
		xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry").SetValue(ssh_user)
		self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_lockdown")).Check(lockdown)
		self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autoconnect")).Check(auto_connect)
		
	def PrepareSSHTunnels(self, ssh_user, remote_host, remote_port):
		""" Prepares the SSH tunnels needed for the run control.
		
		    Note that you must have already performed 'kinit'
		    BEFORE starting the run control for this to work! """
		
		if len(self.ssh_processes) > 0:
			self.logger.warning("Found SSH processes already running... terminating them before creating new ones.")
			self.KillSSHProcesses()
		
		if subprocess.call("klist -s", shell=True) != 0:
			self.alert_thread.NewAlert( Alert.Alert(notice="Can't use SSH if Kerberos hasn't yet been initialized!  Aborting...", severity=Alert.ERROR) )
			return False
		
		# the SSH commands for port forwarding the local listening port
		# back from the remote host and vice versa
		option_string = "-o ServerAliveInterval=30" # -o ServerAlivecountMax=0"
		remote_command = "ssh %s -NR %d:localhost:%d %s@%s" % (option_string, self.postoffice.listen_port, self.postoffice.listen_port, ssh_user, remote_host)
		local_command = "ssh %s -NL %d:localhost:%d %s@%s" % (option_string, remote_port, remote_port, ssh_user, remote_host)
		
		for ssh_command in (local_command, remote_command):
			self.ssh_processes.append(subprocess.Popen(ssh_command.split(), shell=False))
			self.logger.info("Trying to establish SSH tunnel using command '%s' (PID: %d)", ssh_command, self.ssh_processes[-1].pid)
		
		# give the SSH processes 60 seconds to set up.
		# normally we won't need all that time, but if
		# for some reason the connection is taking a
		# long time to set up, we want to give it a chance.
		# we use the socket construction below to check
		# if the tunnel is ready.
		starttime = time.time()
		outgoing_connection = False
		incoming_connection = False
		test_msg = PostOffice.Message(subject="ping")
		recipients = [("localhost", remote_port), ]
		while time.time() - starttime < 60:
			time.sleep(0.25)

			# bail right away
			if self.stop_connecting:
				raise Threads.StopWorkingException()

			for process in self.ssh_processes:
				if process.poll() is not None:
					self.alert_thread.NewAlert( Alert.Alert(notice="Couldn't establish SSH tunnel using process %d" % process.pid, severity=Alert.ERROR) )
					return False

			# we test for a connection in two stages:
			#  (1) outgoing connection.  just try to connect to the remote
			#      socket.  if we can't make a socket on this side, it's
			#      not ready yet.
			#  (2) incoming connection.  this takes a bit longer (usually)
			#      since the SSH process has to make the connection
			#      and then set up forwarding back to this end.  we contact
			#      the postoffice on the other end with a message that
			#      won't be delivered anywhere and ask for delivery confirmation.
			#      once we GET the delivery confirmation message (saying
			#      the message wasn't delivered anywhere), we know the route
			#      is open.
			if not outgoing_connection:
				wx.PostEvent( self, Events.UpdateProgressEvent(progress=(0,0), text="Setting up SSH tunnels...") )
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect( ("localhost", remote_port) )
					s.shutdown(socket.SHUT_RDWR)
					s.close()
					outgoing_connection = True
				except socket.error as e:
					pass
			else:
				wx.PostEvent( self, Events.UpdateProgressEvent(progress=(0,0), text="Waiting for confirmation from DAQ...") )
				try:
					deliveries = None
					deliveries = self.postoffice.SendTo(message=test_msg, recipient_list=recipients, timeout=3.0, with_exception=True)
					incoming_connection = True
					break
				except PostOffice.TimeoutError:
					pass
					
		return outgoing_connection and incoming_connection
	
	def KillSSHProcesses(self):
		""" Kills any SSH processes that are running. """

		# first ask all processes to quit
		for process in self.ssh_processes:
			if process.poll() is None:
				self.logger.info("Terminating SSH process %d...", process.pid)
				process.terminate()

		# now wait until they have all finished
		# (we need to do this so that the dead processes
		#  get 'reaped' -- otherwise we get a bunch of
		#  'defunct' processes cluttering up the process
		#  table while the run control is still open)
		while len(self.ssh_processes) > 0:
			process = self.ssh_processes.pop()
			if process.poll() is None:
				self.ssh_processes.insert(0, process)
	
	def RelinquishControl(self, my_id):
		""" Relinquishes control of the DAQ. """
		
		response = self.DAQSendWithResponse( PostOffice.Message(subject="control_request", request="release", requester_id=my_id), timeout=Configuration.params["sock_messageTimeout"], panic_if_no_connection=False )
		
		if response is not None:
			self.in_control = False
			wx.PostEvent(self, Events.ControlStatusEvent())
	
	def SaveConfig(self):
		""" Saves the run control-specific settings
		    (i.e., connection information) so that
		    the user doesn't have to enter them every time. """
		
		self.cfg.Write("identity", xrc.XRCCTRL(self.frame, "config_connection_identity_entry").GetValue())
		self.cfg.Write("remote_host", xrc.XRCCTRL(self.frame, "config_connection_host_entry").GetValue())
		self.cfg.WriteInt("remote_port", xrc.XRCCTRL(self.frame, "config_connection_remoteport_entry").GetValue())
		self.cfg.WriteBool("use_ssh", xrc.XRCCTRL(self.frame, "config_connection_usessh_entry").GetValue())
		self.cfg.Write("ssh_user", xrc.XRCCTRL(self.frame, "config_connection_sshuser_entry").GetValue())
		self.cfg.WriteBool("lockdown", self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_lockdown")).IsChecked())
		self.cfg.WriteBool("auto_connect", self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_autoconnect")).IsChecked())
	
		self.cfg.Flush()
		
	def StartRunning(self):
		""" Communicate with the DAQMgr to start a run. """
		
		success = True
		response = self.DAQSendWithResponse( PostOffice.Message(subject="mgr_directive",
		                                                        directive="start",
		                                                        client_id=self.id,
		                                                        configuration=self.status["configuration"]),
		                                     timeout=Configuration.params["sock_messageTimeout"]  )

		if response is None:
			success = False
		else:
			if response.subject == "invalid_request":
				self.alert_thread.NewAlert( Alert.Alert(notice="DAQ manager rejected the 'start' directive as invalid!", severity=Alert.ERROR) )
				success = False
			elif response.subject == "not_allowed":
				self.alert_thread.NewAlert( Alert.Alert(notice="DAQ Manager rejected the 'start' directive because you are not currently in control of the DAQ.  (Probably somebody else grabbed it while you were adjusting the run parameters.)  Regain control using the 'request control' button and try again.", severity=Alert.WARNING) )
				success = False
			elif response.subject == "request_response":
				if isinstance(response.success, Exception):
					self.alert_thread.NewAlert( Alert.Alert(notice="Run start failed with an error: %s" % response.success, severity=Alert.ERROR) )
					success = False
				elif response.success != True:
					self.alert_thread.NewAlert( Alert.Alert(notice="Run start failed for an unspecified reason.  Have an expert check the DAQ manager log...", severity=Alert.ERROR) ) 
					success = False
		
		if not success:
			# be sure that everything gets reset
			self.status["running"] = False
			wx.PostEvent(self, Events.StatusUpdateEvent(status=self.status))
		else:
			# the baseline time that trigger updates ought to be measured from
			# should be when the run starts.  that's now.
			self.alert_thread.TriggerUpdate()
			self.logger.info("Startup sequence initiated on DAQ.")
		
	def StopRunning(self):
		""" Communicate with the DAQMgr to stop a run. """
		
		success = True
		response = self.DAQSendWithResponse( PostOffice.Message(subject="mgr_directive",
		                                                        directive="stop",
		                                                        client_id=self.id),
		                                     timeout=Configuration.params["sock_messageTimeout"]  )
		
		if response is None:
			success = False
		else:
			if response.subject == "not_allowed":
				self.alert_thread.NewAlert( Alert.Alert(notice="DAQ Manager rejected the 'stop' directive because you are not currently in control of the DAQ.  Gain control using the 'request control' button and try again.", severity=Alert.WARNING) )
			elif response.success != True:
				self.alert_thread.NewAlert( Alert.Alert(notice="The DAQ could not be stopped for an unspecified reason.  Have an expert check the DAQ manager log..."), severity=Alert.ERROR )
			else:
				self.logger.info("DAQ reports it was successfully stopped.")

#########################################################
#   Global-scope functions
#########################################################

def BeginSession():
	""" Checks that no other copy of the RC is running
	    on this machine via a PID file.  If not,
	    creates its own PID file. """

	if os.path.isfile(Configuration.params["frnt_PIDfile"]):
		pidfile = open(Configuration.params["frnt_PIDfile"])
		pid = int(pidfile.readline())
		pidfile.close()

		try:
			os.kill(pid, 0)		# send it the null signal to check if it's there and alive.
		except OSError:			# you get an OSError if the PID doesn't exist.  it's safe to clean up then.
			os.remove(Configuration.params["frnt_PIDfile"])
		else:
			sys.stderr.write("There is already a copy of the run control running with process ID %d.\n" % pid)
			sys.stderr.write("Close that instance first, then try starting this one again.\n")
			return False

	pidfile = open(Configuration.params["frnt_PIDfile"], 'w')
	pidfile.write(str(os.getpid()) + "\n")
	pidfile.close()
	
	return True


def EndSession():
	""" Removes the PID file for this copy of the RC. """

	if os.path.isfile(Configuration.params["frnt_PIDfile"]):
		os.remove(Configuration.params["frnt_PIDfile"])


#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = None
	
	# try to make sure that an organized cleanup happens no matter what
	try:
		if BeginSession():
			app = MainApp(redirect=False)
			app.MainLoop()
			app.logger.info("Bye.")
			EndSession()

		sys.stdout.write("Shutting down.  Bye.\n")
	except Exception as e:
		try:
			print "Unhandled exception!  Trying close down in an orderly fashion...."
			if app:
				app.OnClose()
		except:
			pass
		raise e
		

