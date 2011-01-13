#!/usr/bin/env python
"""
  Package: mnvruncontrol
   The MINERvA run control
   
  File: ClientManager.py
  
  Notes:
   DAQ client manager program.  In addition to viewing
   current sessions, someone equipped with the proper
   credentials can assign or clear control of the DAQ
   to/from a client or forcibly end a client's session.
  
  Original author: J. Wolcott (jwolcott@fnal.gov), Jan. 2011
                    
  Address all complaints to the management.
"""

# you might notice that this file is heavily patterned on RunControl.py.
# you'd be right.  however, there are some important differences in the
# implementations of most of the methods, so don't bother trying to
# abstract them into some superclass.  you'll just give yourself a headache.

import wx
import wx.lib.newevent
from wx import xrc
import sys
import time
import copy
import socket
import hashlib
import subprocess

from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import Threads

#########################################################
#   Custom events used herein
#########################################################
ClientListEvent, EVT_CLIENT_LIST = wx.lib.newevent.NewEvent()
ErrorEvent,      EVT_ERROR       = wx.lib.newevent.NewEvent()
ConnectionEvent, EVT_CONNECTION  = wx.lib.newevent.NewEvent()


#########################################################
#   MainApp
#########################################################

class MainApp(wx.App, PostOffice.MessageTerminus):
	def OnInit(self):
		PostOffice.MessageTerminus.__init__(self)

		# load and show the graphics
		self.res = xrc.XmlResource('%s/clientmanager.xrc' % Configuration.params["frnt_resourceLocation"])
		self.frame = self.res.LoadFrame(None, 'main_frame')
		self.frame.SetDimensions(-1, -1, 550, 550)
		self.SetTopWindow(self.frame)
		self.frame.SetIcon( wx.Icon("%s/minerva-small.png" % Configuration.params["frnt_resourceLocation"], wx.BITMAP_TYPE_PNG) )
		self.frame.Show()
		

		# prepare the post office and threads
		try:
			self.postoffice = PostOffice.PostOffice(listen_port=2900)
		except socket.error:
			self.logger.exception("Socket error trying to start up the post office:")
			self.logger.fatal("Can't get a socket.  Quitting.")
			sys.stderr.write("I can't bind my listening socket.  Are you sure there's no other copy of the manager running?\n")
			sys.stderr.write("Wait 60 seconds and try again.  If you see this message again, contact your expert shifter.\n")
			return False

		self.worker_thread = Threads.WorkerThread()

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
		self.stop_connecting = False
		
		self.client_list = []
		
		return True
	
	def BindEvents(self):
		""" Bind events to their handler methods. """

		self.frame.Bind(wx.EVT_BUTTON, self.OnAssignControlClick, id=xrc.XRCID("control_assign_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)
		self.frame.Bind(wx.EVT_BUTTON, self.OnConnectClick, id=xrc.XRCID("connect_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnKillSessionClick, id=xrc.XRCID("session_kill_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnRevokeControlClick, id=xrc.XRCID("control_revoke_button"))
		self.frame.Bind(wx.EVT_BUTTON, self.OnRefreshClick, id=wx.ID_REFRESH)

		self.frame.Bind(wx.EVT_CHECKBOX, self.OnSSHTunnelClick, id=xrc.XRCID("connection_usessh_entry"))

		self.frame.Bind(wx.EVT_CLOSE, self.OnClose, self.frame)

		self.Bind(EVT_ERROR, self.OnError)
		self.Bind(EVT_CLIENT_LIST, self.OnClientListUpdate)
		self.Bind(EVT_CONNECTION, self.OnCommStateChange)
		
	def BindChoices(self):
		""" Fix up the list box. """
		
		control = xrc.XRCCTRL(self.frame, "client_list")
		cols = ("Identity", "Location", "In control")
		for col in cols:
			control.InsertColumn(control.GetColumnCount(), col, format=wx.LIST_FORMAT_CENTER, width=140)
			
	def SetupHandlers(self):
		""" Set up the handlers for PostOffice messages. """
		
		subscriptions = [ PostOffice.Subscription(subject="mgr_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="client_info", action=PostOffice.Subscription.DELIVER, delivery_address=self) ]
		handlers = [ self.DAQMgrStatusHandler,
		             self.ClientInfoHandler ]
	
		for (subscription, handler) in zip(subscriptions, handlers):
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handler)
		
		
	######################################################
	# Message handlers
	######################################################

	def ClientInfoHandler(self, message):
		""" Handles alert messages. """
		
		if not hasattr(message, "client_info"):
			return
		
		if message.subject == "client_info" and hasattr(message, "client_info"):
			self.client_list = message.client_info
			wx.PostEvent(self, ClientListEvent())
				
	def DAQMgrStatusHandler(self, message):
		""" Decides what to do when the DAQ manager changes status. """
		
		if not (hasattr(message, "status") and hasattr(message, "mgr_id")):
			return
		
		# for now, the only message we care about
		# is when the DAQ goes down.
		if self.daq is not True:
			return
			
		if message.status == "offline":
			wx.PostEvent(self, ErrorEvent(message="DAQ manager shut down.  Reconnect if you wish.", caption="Manager shut down"))
			work = { "method": self.DisconnectDAQ, "kwargs": self.ssh_details }
			self.worker_thread.queue.put(work)
	
	######################################################
	# (wx) Event handlers / wx object manipulators
	######################################################
	
	def ClientAction(self, action):
		""" Initiates an action on a client. """

		# determine the selected client's index
		# in self.client_list
		list_ctrl = xrc.XRCCTRL(self.frame, "client_list")
		index = list_ctrl.GetFirstSelected()
		if index == -1:	# nothing selected
			return
		client_index = list_ctrl.GetItemData(index)

		# now authenticate
		password = self.GetCredentials()
		if password is None:
			return

		# disable the buttons so we don't make
		# multiple concurrent requests
		buttons = [ xrc.XRCCTRL(self.frame, "control_assign_button"),
		            xrc.XRCCTRL(self.frame, "control_revoke_button"),
		            xrc.XRCCTRL(self.frame, "session_kill_button"),
		            xrc.XRCCTRL(self.frame, "wxID_REFRESH") ]
		for button in buttons:
			button.Disable()
		
		# finally, put together the details so
		# the password hasher can do its thing and send
		msg = PostOffice.Message( subject="client_admin",
		                          action=action,
		                          client=self.client_list[client_index] )
		work = { "method": self.SendWithPasswordHash,
		         "kwargs": { "message": msg,
		                     "password": password } }
		self.worker_thread.queue.put(work)
	
	def GetCredentials(self):
		""" Asks the user for credentials. """
		
		msg = "Enter your password to perform the selected action:"
		caption = "Enter credentials"
		dlg = wx.TextEntryDialog(parent=self.frame, message=msg, caption=caption,
		                         style=wx.OK|wx.CANCEL|wx.TE_PASSWORD, defaultValue="")
		
		return_val = dlg.ShowModal()
		return None if return_val == wx.ID_CANCEL else dlg.GetValue()
	
	def LoadConfig(self):
		""" Loads the connection settings from the
		    file they were stored in and sets the
		    values of the entries appropriately. """

		self.cfg = wx.Config('client_manager')
		
		remote_host  = self.cfg.Read("remote_host", "mnvonlinemaster.fnal.gov")
		remote_port  = self.cfg.ReadInt("remote_port", 1090)
		use_ssh      = self.cfg.ReadBool("use_ssh", True)
		ssh_user     = self.cfg.Read("ssh_user", "mnvonline")
		
		xrc.XRCCTRL(self.frame, "connection_host_entry").SetValue(remote_host)
		xrc.XRCCTRL(self.frame, "connection_remoteport_entry").SetValue(remote_port)
		xrc.XRCCTRL(self.frame, "connection_usessh_entry").SetValue(use_ssh)
		xrc.XRCCTRL(self.frame, "connection_sshuser_entry").SetValue(ssh_user)
	
	def OnAssignControlClick(self, evt):
		""" Do the right stuff when the user clicks
		    the 'assign control' button. """

		self.ClientAction("assign_control")
	
	def OnClientListUpdate(self, evt):
		""" Update the list on the panel when a new
		    list is received from the DAQ. """
		
		control = xrc.XRCCTRL(self.frame, "client_list")
		control.DeleteAllItems()
		for i in range(len(self.client_list)):
			client = self.client_list[i]
			index = control.InsertStringItem(sys.maxint, client["client_identity"])
			control.SetStringItem(index, 1, client["client_location"])
			if client["in_control"]:
				control.SetStringItem(index, 2, u"\u2714")	# a check mark
			control.SetItemData(index, i)

		# re-enable the buttons, etc.
		buttons = [ xrc.XRCCTRL(self.frame, "control_assign_button"),
		            xrc.XRCCTRL(self.frame, "control_revoke_button"),
		            xrc.XRCCTRL(self.frame, "session_kill_button"),
		            xrc.XRCCTRL(self.frame, "wxID_REFRESH") ]
		for button in buttons:
			button.Enable()
				
	def OnClose(self, evt=None):
		""" Shuts everything down nicely. """
		
		self.postoffice.Shutdown()
		self.Close()		# message terminus
		self.KillSSHProcesses()
		self.worker_thread.queue.put(Threads.StopWorkingException())
		self.worker_thread.join()
		self.SaveConfig()
		self.frame.Destroy()
	
	def OnCommStateChange(self, evt):
		""" Performs the GUI stuff needed when a connection
		    to the DAQ manager changes state. """
		
		if not hasattr(evt, "connected"):
			return

		connect_button = xrc.XRCCTRL(self.frame, "connect_button")
		connect_statustext = xrc.XRCCTRL(self.frame, "connection_status")
		
		disable_on_connect = [ xrc.XRCCTRL(self.frame, "connection_host_entry"),
		                       xrc.XRCCTRL(self.frame, "connection_usessh_entry"),
		                       xrc.XRCCTRL(self.frame, "connection_sshuser_entry"),
		                       xrc.XRCCTRL(self.frame, "connection_remoteport_entry") ]
		enable_on_connect = [ xrc.XRCCTRL(self.frame, "control_assign_button"),
		                      xrc.XRCCTRL(self.frame, "control_revoke_button"),
		                      xrc.XRCCTRL(self.frame, "session_kill_button"),
		                      xrc.XRCCTRL(self.frame, "wxID_REFRESH") ]
		
		if evt.connected:
			connect_statustext.SetLabel("Connected")
			connect_button.SetLabel("Disconnect")
			
			for ctrl in disable_on_connect:
				ctrl.Disable()
			for ctrl in enable_on_connect:
				ctrl.Enable()

		else:
			connect_statustext.SetLabel("Not connected")
			connect_button.SetLabel("Connect")

			for ctrl in disable_on_connect:
				ctrl.Enable()
			for ctrl in enable_on_connect:
				ctrl.Disable()
				
		xrc.XRCCTRL(self.frame, "client_list").DeleteAllItems()
			
		self.frame.Layout()

	def OnConnectClick(self, evt):
		""" Starts the connection/disconnection process in a separate thread. """
		connect_button = xrc.XRCCTRL(self.frame, "connect_button")
		connect_statustext = xrc.XRCCTRL(self.frame, "connection_status")
		connect_who_entry = xrc.XRCCTRL(self.frame, "connection_host_entry")
		use_ssh_entry = xrc.XRCCTRL(self.frame, "connection_usessh_entry")
		ssh_user_entry = xrc.XRCCTRL(self.frame, "connection_sshuser_entry")
		remote_port_entry = xrc.XRCCTRL(self.frame, "connection_remoteport_entry")

		self.ssh_details = { "use_ssh": use_ssh_entry.IsChecked(), "ssh_user": ssh_user_entry.GetValue(), 
		                     "remote_host": connect_who_entry.GetValue(), "remote_port": remote_port_entry.GetValue() }
	
		#  not connected
		if self.daq is False:
			connect_statustext.SetLabel("Connecting...")
			connect_button.SetLabel("Cancel connection")

			connect_who_entry.Disable()
			remote_port_entry.Disable()
			use_ssh_entry.Disable()
			ssh_user_entry.Disable()

			work = { "method": self.ConnectDAQ, "kwargs": self.ssh_details }

		# in the process of setting up the connection
		elif self.daq is None:
			self.stop_connecting = True
			work = { "method": self.DisconnectDAQ, "kwargs": self.ssh_details }
		else:
			work = { "method": self.DisconnectDAQ, "kwargs": self.ssh_details }
			
		self.worker_thread.queue.put(work)
		
		self.frame.Layout()
	
	def OnError(self, evt):
		""" Shows an error dialog. """
		
		if not hasattr(evt, "message"):
			return
		
		caption = "" if not hasattr(evt, "caption") else evt.caption
		
		dlg = wx.MessageDialog(parent=self.frame, message=evt.message, caption=caption, style=wx.OK|wx.ICON_ERROR)
		dlg.ShowModal()

	def OnKillSessionClick(self, evt):
		password = self.GetCredentials()
		if password is None:
			return	
			
	def OnRefreshClick(self, evt):
		""" Asks for an updated client list from the DAQ mgr. """
		
		# disable the various buttons
		# to avoid sending multiple messages.
		# they'll be re-enabled when the message comes back.
		buttons = [ xrc.XRCCTRL(self.frame, "control_assign_button"),
		            xrc.XRCCTRL(self.frame, "control_revoke_button"),
		            xrc.XRCCTRL(self.frame, "session_kill_button"),
		            xrc.XRCCTRL(self.frame, "wxID_REFRESH") ]
		for button in buttons:
			button.Disable()
	
		self.postoffice.Send(PostOffice.Message(subject="client_admin", action="list_request"))
	
	def OnRevokeControlClick(self, evt):
		self.ClientAction("revoke_control")
				
	def OnSSHTunnelClick(self, evt):
		""" Flip the entry's enabled status. """
		xrc.XRCCTRL(self.frame, "connection_sshuser_entry").Enable(xrc.XRCCTRL(self.frame, "connection_usessh_entry").IsChecked())

	def SaveConfig(self):
		""" Saves the connection information so that
		    the user doesn't have to enter it every time. """
		
		self.cfg.Write("remote_host", xrc.XRCCTRL(self.frame, "connection_host_entry").GetValue())
		self.cfg.WriteInt("remote_port", xrc.XRCCTRL(self.frame, "connection_remoteport_entry").GetValue())
		self.cfg.WriteBool("use_ssh", xrc.XRCCTRL(self.frame, "connection_usessh_entry").GetValue())
		self.cfg.Write("ssh_user", xrc.XRCCTRL(self.frame, "connection_sshuser_entry").GetValue())
	
		self.cfg.Flush()
		
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
				self.DisconnectDAQ(use_ssh, remote_host, remote_port)
				return
		
		host = "localhost" if use_ssh else remote_host
				
		# set up forwarding subscriptions
		self.postoffice.AddSubscription( PostOffice.Subscription(subject="client_admin", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )
		
#		# get the current status of the DAQ and draw it
#		response = self.DAQSendWithResponse( PostOffice.Message(subject="mgr_directive", directive="status_report", client_id=self.id), timeout=Configuration.params["sock_messageTimeout"] )
#		
#		if response is None:
#			wx.PostEvent(self, ErrorEvent(message="Couldn't connect to DAQ manager!", caption="Connection failed"))
#			self.DisconnectDAQ(use_ssh, remote_host, remote_port)
#			return
		
		# ask for the necessary forwarding subscriptions from the DAQ manager
		subscriptions = []
		for subscription in self.handlers:
			newsub = copy.copy(subscription)
			newsub.action = PostOffice.Subscription.FORWARD
			newsub.delivery_address = PostOffice.IPv4Address(None, self.postoffice.listen_port)
			subscriptions.append(newsub)
		self.postoffice.ForwardRequest( host=(host, remote_port), subscriptions=subscriptions )
				
		self.daq = True

		self.postoffice.Send(PostOffice.Message(subject="client_admin", action="list_request"))

		wx.PostEvent(self, ConnectionEvent(connected=True))

	def DAQSendWithResponse(self, message, panic_if_no_connection=True, timeout=None, with_exception=False):
		""" Sends a message to the DAQ and waits for a response.
		    Verifies that there is indeed exactly one response
		    and notifies the user if there isn't. """
		
		responses = self.postoffice.SendAndWaitForResponse( message, timeout=timeout, with_exception=with_exception )
		
		if len(responses) == 0:
			if panic_if_no_connection:
				wx.PostEvent(self, ErrorEvent(message="Lost connection to the DAQ manager!", caption="Connection lost") )
				if self.daq:
					self.DisconnectDAQ(**self.ssh_details)
				return None
			else:
				return []
		elif len(responses) > 1:
			wx.PostEvent(self, ErrorEvent(message="Got too many DAQ manager responses!  Check the network setup...", caption="Connection problem") )
			return None
		else:
			return responses[0]

	def DisconnectDAQ(self, use_ssh, remote_host, remote_port, **kwargs):
		""" Does the actual disconnection process from the DAQ. """
		if self.daq is False:
			return
			
		host = "localhost" if use_ssh else remote_host

		self.postoffice.DropSubscription( PostOffice.Subscription(subject="client_admin", action=PostOffice.Subscription.FORWARD, delivery_address=(host, remote_port)) )

		subscriptions = []
		for subscription in self.handlers:
			newsub = copy.copy(subscription)
			newsub.action = PostOffice.Subscription.FORWARD
			newsub.delivery_address = PostOffice.IPv4Address(None, self.postoffice.listen_port)

			subscriptions.append(newsub)
		self.postoffice.ForwardCancel( host=(host, remote_port), subscriptions=subscriptions )
			
		if use_ssh:
			self.KillSSHProcesses()

		self.daq = False
		wx.PostEvent(self, ConnectionEvent(connected=False))

	def KillSSHProcesses(self):
		""" Kills any SSH processes that are running. """

		# first ask all processes to quit
		for process in self.ssh_processes:
			if process.poll() is None:
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
	
	def PrepareSSHTunnels(self, ssh_user, remote_host, remote_port):
		""" Prepares the SSH tunnels needed for the run control.
		
		    Note that you must have already performed 'kinit'
		    BEFORE starting the run control for this to work! """
		
		if len(self.ssh_processes) > 0:
			self.KillSSHProcesses()
		
		if subprocess.call("klist -s", shell=True) != 0:
			wx.PostEvent(self, ErrorEvent(message="Can't use SSH if Kerberos hasn't yet been initialized!  Aborting...", caption="Kerberos not set up") )
			return False
		
		# the SSH commands for port forwarding the local listening port
		# back from the remote host and vice versa
		option_string = "-o ServerAliveInterval=30" # -o ServerAlivecountMax=0"
		remote_command = "ssh %s -NR %d:localhost:%d %s@%s" % (option_string, self.postoffice.listen_port, self.postoffice.listen_port, ssh_user, remote_host)
		local_command = "ssh %s -NL %d:localhost:%d %s@%s" % (option_string, remote_port, remote_port, ssh_user, remote_host)
		
		for ssh_command in (local_command, remote_command):
			self.ssh_processes.append(subprocess.Popen(ssh_command.split(), shell=False))
		
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
					wx.PostEvent(self, ErrorEvent(message="Couldn't establish SSH tunnel using process %d" % process.pid, caption="SSH problem") )
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
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect( ("localhost", remote_port) )
					s.shutdown(socket.SHUT_RDWR)
					s.close()
					outgoing_connection = True
				except socket.error as e:
					pass
			else:
				try:
					deliveries = None
					deliveries = self.postoffice.SendTo(message=test_msg, recipient_list=recipients, timeout=3.0, with_exception=True)
					incoming_connection = True
					break
				except PostOffice.TimeoutError:
					pass
					
		return outgoing_connection and incoming_connection
		
	def SendWithPasswordHash(self, message, password):
		""" Performs the grunt work of properly
		    hashing the token using the password 
		    so that the DAQ manger can understand it,
		    then sends the message with the hashed
		    password attached. 
		    
		    Be sure you don't call this from within a
		    message handler or you'll get a deadlock."""
		
		# first, we need a token.
		token_request = PostOffice.Message(subject="client_admin", action="get_token")
		response = self.DAQSendWithResponse(token_request, timeout=10)
		
		# broken connection or some such
		if response is None:
			return
		
		# use the token + the password to generate a hash
		# that the server can check (since it knows the
		# right password & it specified the token)
		pwd_hash = hashlib.sha224(response.token + password).hexdigest()
		
		# now send the message.
		message.token = response.token
		message.password_hash = pwd_hash
		response = self.DAQSendWithResponse(message, timeout=10)
	
		if response is None:
			return
		
		if not response.success:
			wx.PostEvent(self, ErrorEvent(message=response.error_msg, caption="Action failed"))
			wx.PostEvent(self, ClientListEvent())
	
#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = None
	
	# try to make sure that an organized cleanup happens no matter what
	try:
		app = MainApp(redirect=False)
		app.MainLoop()
	except Exception as e:
		try:
			print "Unhandled exception!  Trying close down in an orderly fashion...."
			if app:
				app.OnClose()
		except:
			pass
		raise e
		

