"""
  Package: mnvruncontrol
   The MINERvA run control
  
  File: DataAcquisitionManager.py
  
  Notes:
   The server process that actually manages the DAQ.
   Runs only on the master readout node if there are
   multiple readout nodes.  (Otherwise runs on the
   same machine as the readout dispatcher and the
   frontend.)

   Utilizes the PostOffice system as its event dispatcher
   as well as its means for communicating with the
   frontend client(s) and the dispatcher(s).
  
  Original author: J. Wolcott (jwolcott@fnal.gov)
                   first version,  Feb.-Aug. 2010
                   second version, Aug.-Oct. 2010
                    
  Address all complaints to the management.
"""

import os
import re
import sys
import signal
import errno
import fcntl
import datetime
import time
import uuid
import copy
import pprint
import shelve
import socket
import anydbm
import threading
import logging
import logging.handlers

# run control-specific modules.
# note that the folder 'mnvruncontrol' must be in the PYTHONPATH!
import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration.DAQConfiguration import DAQConfiguration
from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import Dispatcher
from mnvruncontrol.backend import RunSeries
from mnvruncontrol.backend import RemoteNode
from mnvruncontrol.backend import Alert
from mnvruncontrol.backend import Threads
from mnvruncontrol.backend import DAQErrors


class DataAcquisitionManager(Dispatcher.Dispatcher):
	""" Object that does the actual coordination of data acquisition.
	    You should only ever make one of these at a time. """
	
	### Notice: like the run control front end, this class is
	### pretty large, so its methods are also grouped by category.
	###
	### The categories are as follows:
	###   * initialization/teardown            (begin around line 75)
	###   * message handlers & access control  ( ...              350)
	###   * global starters/stoppers           ( ...              625)
	###   * subrun starters/stoppers           ( ...              775)
	###   * helper methods for StartNextSubrun ( ...              1050)
	###   * subprocess starters                ( ...              1250)
	###   * utilities & alerts                 ( ...              1475)
	
	def __init__(self):
		Dispatcher.Dispatcher.__init__(self)

		self.pidfilename = Configuration.params["mstr_PIDfile"]

		self.socket_port = Configuration.params["sock_masterPort"]

		# threads that this object will be managing.
		self.worker_thread = None
		self.DAQ_threads = {}
		
		# timer for use in control transfers
		self.transfer_timer = None
		
		# methods that will be started sequentially
		# by various processes and accompanying messages
		self.SubrunStartTasks = [ { "method": self.RunInfoAndConnectionSetup, "message": "Testing connections" },
		                          { "method": self.LIBoxSetup,                "message": "Initializing light injection..." },
		                          { "method": self.ReadoutNodeHWConfig,       "message": "Loading hardware..." },
		                          { "method": self.ReadoutNodeHVCheck,        "message": "Checking hardware..." } ]
		self.DAQStartTasks = [ { "method": self.StartETSys,          "message": "Starting ET system..." },
		                       { "method": self.StartEBSvc,          "message": "Starting event builder..." },
		                       { "method": self.StartOM,             "message": "Starting online monitoring..." },
		                       { "method": self.StartETMon,          "message": "Starting ET monitor..." },
		                       { "method": self.StartRemoteServices, "message": "Starting remote services..."} ]

		# will be filled by the session creator.
		self.remote_nodes = {}

		# logging facilities
		self.logger = logging.getLogger("Dispatcher.DAQManager")
		
		self.last_logged_gate = 0

		# run-time configuration.
		# will be finalized by comparison with configuration sent by front end
		# and final validation/generation of run series
		self.configuration = DAQConfiguration()
		self.PrepareRunSeries()

		# status stuff
		self.running = False
		self.waiting = False
		self.started_et = False
		self.first_subrun = self.configuration.subrun
		
		self.current_state = None
		self.current_progress = (0, 0)
		self.current_gate = {}

		self.current_DAQ_thread = 0			# the next thread to start
		self.can_shutdown = False			# used in between subruns to prevent shutting down twice for different reasons

		self.problem_pmt_list = None
		self.do_pmt_check = True
		self.errors = []
		self.warnings = []
		
		# information about which client is currently in control of the DAQ
		self.control_info = None
		self.control_pending = None
		
		self.last_HW_config = None		# this way we don't write the HW config more often than necessary

		# set up the signal handler for SIGUSR1, which is
		# the signal emitted by each of the subprocesses
		# when they are ready for execution to move on.
		signal.signal(signal.SIGUSR1, self.StartNextThread)

		# make sure setup and shutdown happen smoothly
		self.startup_methods += [self.BeginSession]
		self.cleanup_methods += [self.Cleanup]
		
	def BeginSession(self):
		""" Checks if there's a session that was already open.
		    If so, cleans up (stops the remote nodes), etc.
		    
		    Otherwise, starts a new session: contacts nodes
		    to inform them that the manager is up and running, etc. """
		    
		self.logger.info("Old session resumption is disabled for now.")
		self.logger.info("Starting a fresh session.")

		self.logger.debug("Creating worker thread.")
		self.worker_thread = Threads.WorkerThread(logger=self.logger)

		self.remote_nodes = {}
		self.logger.info("Contacting nodes to announce that I am up...")
		for node_config in Configuration.params["mstr_nodeAddresses"]:
			# if we had a startup error in another thread,
			# we should bail here.
			if self.quit:
				return
				
			assert node_config["type"] in RemoteNode.NODE_TYPES
		
			node = RemoteNode.RemoteNode(node_config["type"], node_config["name"], node_config["address"])
			self.logger.info("  ... contacting node '%s' at address %s ...", node.name, node.address)
			try:
				node.InitialContact(postoffice=self.postoffice, mgr_id=self.id)
			except RemoteNode.NoContactError:
				notification = "Could not establish communication with the '%s' node at %s..." % (node_config["name"], node_config["address"])
				severity = Alert.ERROR if node.type == RemoteNode.READOUT else Alert.WARNING
				self.NewAlert(notice=notification, severity=severity)
			except RemoteNode.TooManyResponsesError:
				self.NewAlert( notice="Too many responses from '%s' node (at %s)!" % (node_config["name"], node_config["address"]), severity=Alert.ERROR )
			else:
				self.logger.info("   ... success.  Asking for forward subscriptions...")
			
				subject_map = { RemoteNode.READOUT:    "daq_status",
				                RemoteNode.MONITORING: "om_status",
				                RemoteNode.MTEST:      "beamdaq_status",
				                RemoteNode.PERIPHERAL: "device_status" }

				subscr = PostOffice.Subscription(subject=subject_map[node.type], action=PostOffice.Subscription.FORWARD, delivery_address=(None, self.socket_port))
				self.postoffice.ForwardRequest( node.address, [subscr,] )
				self.logger.info("   ... done.")

			self.remote_nodes[node_config["name"]] = node
			

#		self.logger.info("Starting up: checking for leftover session...")
#		# first check for an old session.
#		# if there is one, load in the IDs from the nodes that were in use.
#		try:
#			sessionfile = open(Configuration.params["sessionfile"], "r")
#		except (OSError, IOError):
#			self.logger.info("No previous session detected.  Starting fresh.")
#			return

#		self.logger.info("Old session detected.  Restoring any old node IDs...")
#		# try to get a lock on the file.  that way we know it isn't being
#		# updated while we try to read it.
#		fcntl.flock(sessionfile.fileno(), fcntl.LOCK_EX)
#		try:
#			pattern = re.compile("^(?P<type>\S+) (?P<id>[a-eA-E\w\-]+) (?P<address>\S+)$")
#			node_map = { "readout": self.readoutNodes, "monitoring": self.monitorNodes, "mtestbeam": self.mtestBeamDAQNodes }
#			do_reset = False
#			for line in sessionfile:
#				matches = pattern.match(line)
#				if matches is not None and matches.group("type").lower() in node_map:
#					for node in node_map[matches.group("type").lower()]:
#						if node.address == matches.group("address"):
#							node.id = matches.group("id")
#							node.own_lock = True
#							do_reset = True
#		finally:
#			fcntl.flock(sessionfile.fileno(), fcntl.LOCK_UN)

#		sessionfile.close()
#		
#		self.logger.info("Resetting any nodes that are still running...")
#		# now reset any nodes that were previously locked & running.
#		if do_reset:
#			# first inform the main window that it needs to wait until we're done cleaning up.
#			wx.PostEvent(self.main_window, Events.WaitForCleanupEvent())
#			
#			# next, reset the monitoring nodes.  they're simple
#			# because we don't really care too much about whether
#			# they're actually behaving.
#			for node in self.monitorNodes:
#				if node.own_lock:
#					node.om_stop()

#			# now any MTest beamline DAQ nodes
#			if self.mtest_useBeamDAQ:
#				for node in self.mtestBeamDAQNodes:
#					if node.own_lock:
#						node.stop()

#			self.can_shutdown = True
#			self.first_subrun = 0
#			
#			# finally, deal with the readout nodes.
#			# remember, we need to loop twice so that all subscriptions
#			# are booked before issuing any stops.
#			for node in self.readoutNodes:
#				if node.own_lock:
#					self.socketThread.Subscribe(node.id, node.name, "daq_finished", callback=self, waiting=True, notice="Cleaning up from previous run...")
#			
#			wait_for_reset = False	
#			for node in self.readoutNodes:
#				if node.own_lock:
#					success = False
#					try:
#						success = node.daq_stop()
#					except ReadoutNode.ReadoutNodeNoDAQRunningException:
#						pass
#					
#					if success:
#						wait_for_reset = True
#					# otherwise we'll be stuck... forever...
#					else:
#						node.completed = True
#						self.socketThread.Unsubscribe(node.id, node.name, "daq_finished", callback=self)
#				# if it's not locked, then we can't stop it, so it may as well be "completed"
#				# (otherwise we'll stuck waiting forever)
#				else:
#					node.completed = True
#			
#			if not wait_for_reset:
#				wx.PostEvent(self, Events.EndSubrunEvent(allclear=True, sentinel=False))

	def BookSubscriptions(self):
		""" Books all the standing subscriptions the DAQMgr will want
		    and assigns handlers for those messages. """
		    
		# daq_status:    from readout nodes (informs us if something happened on the readout nodes)
		# device_status: from peripherals
		# mgr_internal:  from this DAQ manager to itself
		# mgr_directive: from front-end client (tells the DAQ manager what to do)
		subscriptions = [ PostOffice.Subscription(subject="control_request", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="daq_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="om_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="beamdaq_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="device_status", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="mgr_internal", action=PostOffice.Subscription.DELIVER, delivery_address=self),
		                  PostOffice.Subscription(subject="mgr_directive", action=PostOffice.Subscription.DELIVER, delivery_address=self) ]
		handlers = [ self.ControlRequestHandler,
		             self.DAQStatusHandler,
		             self.OMStatusHandler,
		             self.BeamDAQStatusHandler,
		             self.DeviceStatusHandler,
		             self.MgrInternalHandler,
		             self.MgrDirectiveHandler ]
	
		for (subscription, handler) in zip(subscriptions, handlers):
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handler)
		
	def Cleanup(self):
		""" Any clean-up actions that need to be taken before shutdown.  """
		    
#		# release any outstanding locks
#		self.logger.info("Releasing outstanding locks...")
#		msgs = self.postoffice.SendAndWaitForResponse(PostOffice.Message(subject="lock_request", request="release", requester_id=self.id), timeout=Configuration.params["socketTimeout"])
#			
#		for message in msgs:
#			if len(message.return_path) == 0:
#				continue
#		
#			if message.success == True:
#				self.logger.info("   ... got release confirmation from '%s' node", message.sender)
#			elif message.success == False:
#				self.logger.warning("  ... couldn't release lock on '%s' node!", message.sender)
#			elif isinstance(message.success, Exception):
#				self.logger.warning("  ... error during release of lock on '%s' node.  Error text:\n%s", message.success)
		
		self.logger.info("Informing nodes I'm going down...")
		self.postoffice.Send( PostOffice.Message(subject="mgr_status", status="offline", mgr_id=self.id) )
		
		self.logger.info("Stopping worker thread...")
		self.worker_thread.queue.put("QUIT")
		self.worker_thread.join()
		self.logger.info("  ... done.")

#		delete_session = True
#		# release any locks that might still be open
#		for node in self.readoutNodes + self.monitorNodes + self.mtestBeamDAQNodes:
#			if node.own_lock:
#				success = node.release_lock()
#				
#				delete_session = delete_session and success
#		
#		# remove the session file, but only if there's no more
#		# locks that are still open...
#		if delete_session:
#			try:
#				os.remove(Configuration.params["sessionfile"])
#			except (IOError, OSError):		# if the file doesn't exist, no problem
#				pass

	##########################################
	# Message handlers & access control
	##########################################
	
	def BeamDAQStatusHandler(self, message):
		""" Handles updates from the MTest beam DAQ
		    about changes in its state. """
		
		pass	
		
	def ClientAllowed(self, client_id):
		""" Overridden from Dispatcher -- checks if a client is
		    allowed to give instructions. """
		    
		return self.control_info is not None and self.control_info["client_id"] == client_id

	def ControlRequestHandler(self, message):
		""" Handles requests from clients for control of the DAQ.
		
		    Note: locks on the DAQManager work differently than in
		    other dispatchers: anybody can request control
		    at any time (even if somebody else already has
		    control).  (We want to avoid the situation where
		    somebody has a lock then their connection gets broken,
		    preventing anybody else from controlling the DAQ until
		    the DAQ manager is reset.) """

		response_msg = message.ResponseMessage()

		# lock requests that have no return path are OUTGOING.
		# we don't want to lock ourselves!
		if len(message.return_path) == 0:
			response_msg.subject = "request_response"
			response_msg.success = Dispatcher.LockError("Not issuing a lock to my own node!")

		elif not( hasattr(message, "request") and hasattr(message, "requester_id") ):
			response_msg.subject = "invalid_request"
		else:
			response_msg.subject = "request_response"
			if message.request == "get":
				if not ( hasattr(message, "requester_name") and hasattr(message, "requester_location") ):
					response_msg.subject = "invalid_request"
				# nobody's currently in control
				elif self.control_info is None:
					self.logger.info("Granted control to client %s (reporting identity '%s') located at %s.", message.requester_id, message.requester_name, message.requester_location)
					self.control_info = { "client_id": message.requester_id,
					                      "client_identity": message.requester_name,
					                      "client_location": message.requester_location }
					response_msg.success = True
				elif message.requester_id == self.control_info["client_id"]:
					self.logger.info("Client %s is already in control.  No action taken." % message.requester_id)
					response_msg.success = True
				# another request is already pending
				elif self.control_pending is not None:
					self.logger.info("Client %s wants control, but another request is already pending.  Denying request.", message.requester_name)
					response_msg.success = False
				# new client requesting control, but
				# another client is already in control
				else:
					msg = "Client %s requests control, but client %s is already in control.  " % (message.requester_id, self.control_info["client_id"])
					msg += "Client %s has %d seconds to veto control transfer..." % (self.control_info["client_id"], Configuration.params["mstr_controlXferWait"])
					self.logger.info(msg)
					self.control_pending = { "client_id": message.requester_id,
					                         "client_identity": message.requester_name,
					                         "client_location": message.requester_location }
					response_msg.success = None
					
					# send out message soliciting objections if there are any
					self.postoffice.Send( PostOffice.Message(subject="frontend_info",
					                                         info="control_transfer_proposal",
					                                         who={"identity": message.requester_name, "location": message.requester_location }) )
					
					# set up a timer to check after the appropriate interval
					self.transfer_timer = threading.Timer(Configuration.params["mstr_controlXferWait"],
					                                      self.ControlTransfer,
					                                      kwargs={"do_transfer": True})
					self.transfer_timer.start()

			elif message.request == "release":
				if self.control_info is None or self.control_info["client_id"] != message.requester_id:
					self.logger.info("Client %s wants to relinquish control, but isn't the controlling node.  Ignoring.", message.requester_id)
				else:
					self.control_info = None
					self.logger.info("Client %s relinquished control.", message.requester_id)
					response_msg.success = True
					

		self.postoffice.Send(response_msg)
		
		# if the 'success' paramter is None,
		# nothing has changed yet.  don't send
		# an update until it does.
		if response_msg.success is not None:
			notify_msg = PostOffice.Message( subject="frontend_info", info="control_update", control_info=self.control_info )
			self.postoffice.Send(notify_msg)
	
	def ControlTransfer(self, do_transfer=True):
		""" Handles requests for transfers of control. """
		
		if self.transfer_timer is not None:
			self.transfer_timer.cancel()		# won't hurt if it's already done
			self.transfer_timer = None
		
		# nothing to do if there's no client waiting
		if self.control_pending is None:
			return
		
		if do_transfer:
			self.control_info = self.control_pending
			self.logger.info("Control transferred to new client: %s", self.control_info["client_id"])

		self.control_pending = None
		notify_msg = PostOffice.Message( subject="frontend_info", info="control_update", control_info=self.control_info )
		self.postoffice.Send(notify_msg)
	
	def DAQStatusHandler(self, message):
		""" Handles updates from the readout nodes regarding
		    the status of the DAQ on their own nodes.
		    
		    This includes readiness for data taking, the end
		    of data taking, errors, etc. """
		    
		if not hasattr(message, "state"):
			self.logger.info("DAQ status message from '%s' node is badly formed.  Ignoring.  Message:\n%s", message.sender, message)
			return
			
#		self.logger.debug("DAQ status message:\n%s", message)
		
		if message.state == "hw_error":
			self.NewAlert(notice="A hardware error was reported on the '%s' node.  Error text:\n%s" % (message.sender, message.error), severity=Alert.ERROR)
			self.remote_nodes[message.sender].status = RemoteNode.ERROR
			self.StopDataAcquisition(do_auto_start=False)
			self.last_HW_config = None

			self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )
		
		elif message.state == "hw_ready":
			self.remote_nodes[message.sender].status = RemoteNode.OK
			self.logger.debug("    ==> '%s' node reports it's finished loading hardware.", message.sender)

			self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )
			
			# are they all ready yet?
			for node in self.remote_nodes:
				if self.remote_nodes[node].type == RemoteNode.READOUT and self.remote_nodes[node].status is not RemoteNode.OK:
					return

			# all nodes are ready.  continue the startup sequence.
			self.logger.info("    ==> all readout nodes ready.")
			self.StartNextSubrun()
		
		elif message.state == "running" and hasattr(message, "gate_count"):
			# updates are only relevant if we're still doing the same subrun...
			if message.run_num != self.configuration.run or message.subrun_num != self.configuration.subrun:
				return

			# we can't rely on getting a notice for every single gate
			# (the test stand and MTest read out too fast for that in some modes).
			# so we use the integer division (//) construction below.
			stride = Configuration.params["mstr_logfileGateCount"]
			if message.gate_count // stride > self.last_logged_gate // stride:
				self.logger.info("  DAQ has reached gate %d..." % message.gate_count)
				self.last_logged_gate = message.gate_count

			if message.gate_count > self.current_gate["number"]:
				self.current_gate["number"] = message.gate_count
				self.current_gate["type"]   = message.last_trigger_type
				self.current_gate["time"]   = message.last_trigger_time
				
				self.postoffice.Send( self.StatusReport( items=["current_gate", "waiting"], do_log=False ) )
			
		elif message.state == "finished":
			self.remote_nodes[message.sender].completed = True
			self.remote_nodes[message.sender].sent_sentinel = message.sentinel
			self.remote_nodes[message.sender].status = RemoteNode.IDLE
			self.postoffice.Send( self.StatusReport(items=["remote_nodes",]) )
			self.logger.debug("    ==> '%s' node reports it's done taking data and %s send a sentinel.", message.sender, "DID" if message.sentinel else "DID NOT")
			
			# loop and check if they're all finished
			sentinel = False
			for node in self.remote_nodes:
				if self.remote_nodes[node].type == RemoteNode.READOUT:
					if not self.remote_nodes[node].completed:
						self.logger.debug( "    ... still waiting on '%s' node.", node)
						return
					sentinel = sentinel or self.remote_nodes[node].sent_sentinel
			
			# all nodes are finished.  end the subrun.
			self.logger.info("All nodes finished.  Sentinel status: %s", str(sentinel))
			self.EndSubrun(sentinel=sentinel)

	def DeviceStatusHandler(self, message):
		""" Handles updates from various peripherals about
		    changes in their state. """
		
		pass	
		
	def MgrDirectiveHandler(self, message):
		""" Handles messages from front-end clients: requests
		    for status updates, instructions for starting/stopping,
		    requests for control, etc. """
		
		# ignore ill-formed messages
		if not hasattr(message, "directive") or not hasattr(message, "client_id"):
			self.logger.info("Directive message is badly formed and will be ignored:\n%s", message)
			return
		
		response = message.ResponseMessage()
		response.sender = self.id
		
		# there are a few directives for which 
		# a lock is unnecessary, so we consider them first.
		if message.directive == "status_report":
			self.StatusReport(response)
		elif message.directive == "pmt_hv_list":
			self.worker_thread.queue.put( {"method": self.GetProblemPMTs, "kwargs": {"send_results": True}} )
			status = True
		elif message.directive == "series_info" and hasattr(message, "series"):
			self.worker_thread.queue.put( {"method": self.SeriesInfo, "kwargs": {"series": message.series}} )
			status = True
		
		# the rest are commands, so we first need to verify
		# that this client is allowed to issue them.
		else:
			if not self.ClientAllowed(message.client_id):
				self.logger.info("Got directive message from unallowed client ('%s') -- ignoring.  Message:\n%s", message.client_id, message)
				response.subject = "not_allowed"
			else:
				status = None
				
				# some of these use the worker_thread because
				# they start tasks that don't return immediately.
				# the rule of thumb is, if they don't return quickly,
				# use the worker_thread by putting the appropriate
				# dictionary into its queue.  
				# (see the documentation at
				#  mnvruncontrol.backend.Threads.WorkerThread.run() ...)
				if message.directive == "start":
					self.logger.info("Client wants to begin data acquisition.")
					# we need to make sure the configuration we got makes sense.
					# we will compare the requested configuration
					# with the one from our last run here to make sure
					# that all of the parameters are valid.
					last_config = DAQConfiguration()
					
					if self.running:
						self.logger.warning("  ... but we are already running!  Request is invalid.")
						status = DAQErrors.RunError("Can't start running because DAQ is already running.")

					elif len(self.errors) > 0:
						self.logger.warning("There are errors left unaddressed.  These must be handled before starting the next run.")
						status = DAQErrors.AlertError("There are unaddressed errors.  Handle those before starting a run!")
					elif not hasattr(message, "configuration") or not isinstance(message.configuration, DAQConfiguration):
						self.logger.error("Directive message does not properly specify configuration...")
						status = DAQErrors.ConfigurationError("Run configuration is improperly specified.")
					elif not message.configuration.Validate():
						self.logger.error("Directive message's configuration is invalid:\n%s", pprint.pformat(message.configuration.__dict__))
						status = DAQErrors.ConfigurationError("Invalid configuration.")
					elif not( (message.configuration.run > last_config.run) or (message.configuration.run == last_config.run and message.configuration.subrun >= last_config.subrun) ):
						self.logger.error("Directive message requests invalid run/subrun numbers: %d/%d (last config was %d/%d)", message.configuration.run, message.configuration.subrun, last_config.run, last_config.subrun)
						status = DAQErrors.ConfigurationError("Invalid run/subrun pair.")
					else:
						self.logger.debug("Client's proposed configuration:\n%s", pprint.pformat(message.configuration.__dict__))
						self.worker_thread.queue.put( {"method": self.StartDataAcquisition, "kwargs": {"configuration": message.configuration}} )
						status = True
				elif message.directive == "continue":
					self.logger.info("Frontend client requests continuation of running.")
					self.worker_thread.queue.put({"method": self.StartNextSubrun})
					status = True
			
				elif message.directive == "stop":
					self.logger.info("Frontend client requests stoppage of data acquisition.")
					self.worker_thread.queue.put( {"method": self.StopDataAcquisition, "kwargs": {"do_auto_start": False}} )
					status = True
					
				elif message.directive == "skip":
					self.logger.info("Frontend client requests skip to next subrun.")
					self.postoffice.Send( PostOffice.Message(subject="mgr_internal", event="subrun_end", auto_start=True) )
					status = True
				
				elif message.directive == "alert_acknowledge":
					if not hasattr(message, "alert_id"):
						self.logger.warning("Got 'alert_acknowledge' message with no alert ID!  Ignoring...")
					self.logger.info("Frontend client '%s' acknowledged alert %s.", message.client_id, message.alert_id)
					status = self.AcknowledgeAlert(message.alert_id)
				
				elif message.directive == "pmt_dismiss":
					self.logger.info("Frontend client '%s' dismissed PMT HV/period notification.", message.client_id)

					# clear out the PMT list (otherwise non-control clients will always be stuck on it)
					self.problem_pmt_list = None
					self.postoffice.Send( self.StatusReport(items=["problem_pmt_list",]) )
					status = True
					
				elif message.directive == "control_transfer_allow":
					self.logger.info("Frontend client '%s' is ok transferring control.", message.client_id)
					self.ControlTransfer(do_transfer=True)
				
				elif message.directive == "control_transfer_deny":
					self.logger.info("Frontend client '%s' refused to transfer control.", message.client_id)
					self.ControlTransfer(do_transfer=False)
			
				if status is None:
					response.subject = "invalid_request"
				else:
					response.subject = "request_response"
					response.success = status
		self.postoffice.Send(response)
	
	def MgrInternalHandler(self, message):
		""" Handles messages that are passed around internally
		    by the DAQMgr.  Always insists that the messages
		    have no return_path (i.e., haven't been transmitted
		    over the network). """	

		# ignore ill-formed messages
		if not hasattr(message, "event"):
			self.logger.warning("Internal message is badly formed!  Message:\n%s", message)
			return
		
		# internal messages better actually be internal! ...
		if len(message.return_path) > 0:
			self.logger.info("Got 'DAQMgr internal' message over the network.  Ignoring.  Message:\n%s", message)
			return
		
		
		if message.event == "subrun_auto_start":
			self.worker_thread.queue.put({"method": self.StartNextSubrun})
			
		elif message.event == "subrun_end":
			auto_start = True if not hasattr(message, "auto_start") else message.auto_start
			self.worker_thread.queue.put({"method": self.EndSubrun, "kwargs": {"auto_start": auto_start} })

		elif message.event == "series_auto_start":
			self.configuration.run += 1
			self.configuration.subrun = 1
			self.worker_thread.queue.put({"method": self.StartDataAcquisition, "args": [self.configuration]})
		
		elif message.event == "series_end":
			if hasattr(message, "early_abort") and message.early_abort:
				warning_msg = "Aborting early!"
				if hasattr(message, "lost_process"):
					warning_msg += "  (due to crash of '%s' process).  Last 2000 characters of output from this process:\n%s" % (message.lost_process, message.output_history)
					self.logger.warning(warning_msg)
					self.NewAlert(notice="'%s' process crashed!\nRunning has been halted for troubleshooting." % message.lost_process, severity=Alert.ERROR)
				auto_start = False
			else:
				auto_start = True if not hasattr(message, "auto_start") else message.auto_start
			# should auto-start next series if configuration allows it
			# and the series ended nicely
			self.worker_thread.queue.put( {"method": self.StopDataAcquisition, "kwargs": {"do_auto_start": auto_start}} )
		
	##########################################
	# Global starters and stoppers
	##########################################
	
	def StartDataAcquisition(self, configuration):
		""" Starts the data acquisition process.
		    Called only for the first subrun in a series. """
		    
		assert len(self.errors) == 0
		assert configuration.Validate()

		# if the run number is changing, we should
		# save the run/subrun number NOW.  that way
		# if we stop the run before everything gets going
		# (for example, if the user clicks "stop" 
		#  when the PMT voltage verification window
		#  is up) the numbers will still be sane.
		if configuration.run > self.configuration.run:
			configuration.Save(filepath=Configuration.params["mstr_runinfoFile"])
		
		self.configuration = configuration
		
		# get the run series ready
		self.logger.debug("   preparing run series...")
		success = self.PrepareRunSeries()
		if success != True:
			return success
		
		self.logger.debug("   locking remote nodes...")
		# lock each of the remote nodes that's currently taking orders from this manager.
		try:
			responses = self.NodeSendWithResponse(PostOffice.Message(subject="lock_request", request="get", requester_id=self.id), timeout=10)
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the remote node(s) has become unresponsive.  Check the logs for more details.  Running will be halted...", severity=Alert.ERROR)
			return False
		
		for response in responses:
			if response.sender in self.remote_nodes:
				self.remote_nodes[response.sender].SetLocked(response.success)
			self.logger.debug("  response from remote node: %s", response)
		
		# if we can't lock one of the nodes, the user should be informed.
		# moreover, if it's a READOUT node, we can't start the run anyway,
		# so in that case we should abort immediately.
		ok = True
		for node_name in self.remote_nodes:
			node = self.remote_nodes[node_name]
			if not node.locked:
				node.status = RemoteNode.ERROR
				notice = "Cannot lock node '%s'!" % node_name
				if node.type == RemoteNode.READOUT:
					severity = Alert.ERROR
					ok = False
				else:
					severity = Alert.WARNING
				# alerts are automatically logged
				self.NewAlert(notice=notice, severity=severity)
			else:
				# for now, these nodes are 'ok' so long as we have control of them
				if node.type not in (RemoteNode.READOUT, RemoteNode.MONITORING):
					node.status = RemoteNode.OK
				self.logger.info("     got lock confirmation from node '%s'...", node.name)
		
		self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )		
		
		if not ok:
			return False

			
		# need to make sure all the tasks are marked "not yet completed"
		for task in self.SubrunStartTasks:
			task["completed"] = False
		
		self.logger.info("Beginning data acquisition sequence...")
		self.logger.info( "  Run: %d; starting subrun: %d; number of subruns to take: %d", self.configuration.run, self.configuration.subrun, len(self.run_series.Runs) )
					
#		self.subrun = 0
		self.first_subrun = self.configuration.subrun
		self.running = True

		for node_name in self.remote_nodes:
			node = self.remote_nodes[node_name]
			if node.type == RemoteNode.READOUT:
				node.completed = False

		# want to return so that client knows we started ok
		self.postoffice.Send( PostOffice.Message(subject="mgr_internal", event="subrun_auto_start") )
		self.postoffice.Send( self.StatusReport( items=["running", "run_series", "first_subrun"]) )
		return True
		
	def StopDataAcquisition(self, do_auto_start=True):
		""" Stop data acquisition altogether. """

		# if we are currently still running, the subrun needs to be stopped first!
		if self.running:
			self.running = False
			self.logger.info("Stopping data acquisition sequence...")
			self.postoffice.Send(PostOffice.Message(subject="mgr_internal", event="subrun_end", auto_start=do_auto_start))
			return
		else:
			self.logger.debug("Not running, so we don't need to stop the DAQ.")

		self.logger.info("Unlocking remote nodes...")
		# release locks from the remote nodes
		try:
			responses = self.NodeSendWithResponse(PostOffice.Message(subject="lock_request", request="release", requester_id=self.id), timeout=10)
		except DAQErrors.NodeError:
			pass

		# if we can't unlock one of the nodes, the user should be informed.
		# we should finish the shutdown sequence, nevertheless.
		for response in responses:
			self.remote_nodes[response.sender].SetLocked(False)
		for node_name in self.remote_nodes:
			if self.remote_nodes[node_name].locked:
				notice = "Cannot unlock node '%s'..." % node_name
				self.NewAlert(notice=notice, severity=Alert.WARNING)
			else:
				self.logger.info("Got unlock confirmation from node '%s'...", node_name)
		
		# EndSubrun() sometimes increments self.configuration.subrun...
		if self.configuration.subrun - self.first_subrun <= 1:
			subrun_string = "subrun %d" % self.first_subrun
		else:
			# the subrun number will have been incremented if we started ET
			# but not if we didn't
			subrun_adjust = 1 if self.started_et else 0
			subrun_string = "subruns %d-%d" % (self.first_subrun, self.configuration.subrun - subrun_adjust)
		self.logger.info("Data acquisition for run %d, %s finished.", self.configuration.run, subrun_string)

		# now that we're finished, the first subrun
		# will be wherever we left off...
		self.first_subrun = self.configuration.subrun
		
		# be sure to reset this just in case it somehow wasn't.
		self.problem_pmt_list = None

#		self.subrun = 0
		
#		self.logger.info("Informing frontend that run series is over.")
#		self.postoffice.Send( PostOffice.Message(subject="frontend_info", info="series_end") )
#		print "do_auto_start is: ", do_auto_start
		
		if not self.configuration.is_single_run and self.configuration.auto_start_series and do_auto_start:
			self.logger.info("Auto-starting next run series...")
			self.postoffice.Send(PostOffice.Message(subject="mgr_internal", event="series_auto_start"))
		else:
			self.logger.info("Running ended.")
			self.current_state = "Idle."
			self.current_progress = (0, 1)
			# inform the frontend clients where we now stand.
			self.postoffice.Send( self.StatusReport() )


	##########################################
	# Subrun starters and stoppers
	##########################################
		
	def StartNextSubrun(self):
		""" Prepares to start the next subrun: waits for
		    the DAQ system to be ready, notifies the main 
		    window what run we're in, prepares the LI box
		    and slow controls, and finally initiates the
		    acquisition sequence. """
	
		self.logger.debug("StartNextSubrun() called.")
		
#		self.configuration.subrun = self.first_subrun + self.subrun
	
		quitting = not(self.running)
		
		if quitting:
			return

		self.num_startup_steps = len(self.SubrunStartTasks) + len(self.DAQStartTasks)
		self.startup_step = 0
		self.last_logged_gate = 0

		# run the startup tasks sequentially.
		for task in self.SubrunStartTasks:
			# StartNextSubrun() will sometimes get called more than once
			# (if, for example, some of the DAQ threads from a previous
			#  subrun have not yet exited or if we're waiting on the HV
			#  to settle down).  in that case we don't want to run the
			# startup tasks more than once.
			if not task["completed"]:
				self.logger.debug("Starting task: %s" % task["message"])

				# notify the main window which step we're on so that the user has some feedback.
				self.current_state = "Setting up run:\n" + task["message"]
				self.current_progress = (self.startup_step, self.num_startup_steps)
				self.postoffice.Send( self.StatusReport( items=["current_state", "current_progress"] ) )
				
				# then run the appropriate method.
				try:
					status = task["method"]()
				except Exception as e:
					self.logger.exception("Error in task execution:")
					status = False

				task["completed"] = True
				self.logger.debug("Finished task: %s" % task["message"])
			
				# the return value of each task can be one of three things:
				#   (1) True.   in this case it's safe to move on.
				#   (2) False.  some necessary process or procedure
				#               was unable to complete.  we'll need
				#               to stop running altogether.
				#   (3) None.   this indicates that we will need to
				#               wait an indeterminate amount of time
				#               before the next task can be started.
				#               (we might be waiting on user input,
				#                or maybe a process to shut down.)
				#               in this case whatever background
				#               thread is waiting for the appropriate
				#               condition will issue a ReadyForNextSubrunEvent
				#               to the DataAcquisitionManager and
				#               StartNextSubrun() will be called again.
				#               in the meantime, control must be
				#               returned to the main dispatcher loop, so
				#               this method needs to be exited
				#               immediately.
				#
				# finally, we should inform the front end any time
				# the 'waiting' status changes.

				do_update = self.waiting != (status is None)
				self.waiting = (status is None)
				if do_update:
					self.postoffice.Send( self.StatusReport(items=["waiting"]) )

				if status is None:
					return
										
				if status == False:
					quitting = True
					break
			else:
				self.logger.debug("Skipping task (already done): %s", task["message"])
			self.startup_step += 1

		# if running needs to end, there's some cleanup we need to do first.
		if quitting:
			self.logger.warning("Subrun %d aborted.", self.configuration.subrun)
			self.postoffice.Send(PostOffice.Message(subject="mgr_internal", event="series_end", early_abort=True))
			return

		# all the startup tasks were successful.
		# do the final preparation for the run.
		
		now = datetime.datetime.utcnow()

		# the ET file name is the name used for the ET system file.
		# all other data file names are based on it.
		self.configuration.et_filename = "%(det)s_%(run)08d_%(subrun)04d_%(mode)s_%(ver)s_%(year)02d%(month)02d%(day)02d%(hour)02d%(minute)02d"
		values = { "det":    self.configuration.detector.code,
		           "run":    self.configuration.run,
		           "subrun": self.configuration.subrun,
		           "mode":   self.configuration.run_mode.code,
		           "ver":    Defaults.DAQ_HEADER_VERSION_STRING,
		           "year":   now.year % 100,
		           "month":  now.month,
		           "day":    now.day,
		           "hour":   now.hour,
		           "minute": now.minute }
		self.configuration.et_filename %= values

		
		# raw data written by the event builder
		self.raw_data_filename = self.configuration.et_filename + '_RawData.dat'
		
#		wx.PostEvent(self.main_window, Events.SubrunStartingEvent(first_subrun=self.first_subrun, current_subrun=self.subrun, num_subruns=len(self.run_series.Runs)))

		self.current_DAQ_thread = 0
		
		# start the first thread manually.
		# the rest will be started in turn as SIGUSR1 signals
		# are received by the program.		
		self.StartNextThread()

		self.logger.debug("StartNextSubrun() finished.")
		
	def EndSubrun(self, sentinel=False, auto_start=True):
		""" Performs the jobs that need to be done when a subrun ends. 
		
		    Generally it is only executed as the handler for a
		    'subrun_end' message."""
		
		# block from trying to shut down twice simultaneously
		if not self.can_shutdown:
			return
		self.can_shutdown = False

		self.logger.info("Subrun %d finalizing...", self.configuration.subrun)
		
		self.logger.info("  ... instructing readout and MTest nodes to shut down...")

		step = 0
		numsteps = 1
		
		# check if we need to stop any of the nodes
		stop_readout = False
		stop_mtest = False
		for node_name in self.remote_nodes:
			node = self.remote_nodes[node_name]
			if node.type == RemoteNode.READOUT and node.completed == False:
				stop_readout = True
			
			if node.type == RemoteNode.MTEST and node.completed == False:
				stop_mtest = True

			# other node types don't need to be forcibly 'stopped'
			# so they are 'idle' as of now
			if node.type not in (RemoteNode.READOUT, RemoteNode.MTEST):
				node.status = RemoteNode.IDLE
		
		self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )
		responses = []

		try:
			if stop_readout:
				responses += self.NodeSendWithResponse( PostOffice.Message(subject="readout_directive", directive="daq_stop", mgr_id=self.id), node_type=RemoteNode.READOUT, timeout=10 )
			if stop_mtest:
				responses += self.NodeSendWithResponse( PostOffice.Message(subject="mtest_directive", directive="beamdaq_stop", mgr_id=self.id), node_type=RemoteNode.MTEST, timeout=10 )
		except DAQErrors.NodeError:
			self.NewAlert(notice="Couldn't contact all the nodes to stop them.  The next subrun could be problematic...", severity=Alert.ERROR)

		wait_for_DAQ = False
		for response in responses:
			if hasattr(response, "success"):
				if isinstance(response.success, Exception):
					self.NewAlert(notice="Couldn't stop the DAQ on the '%s' node!" % response.sender, severity=Alert.ERROR)
				elif response.success == True:
					self.logger.info("   => '%s' node is stopping...", response.sender)
				elif response.success == False:
					self.logger.info("   => '%s' node was not in data acquisition...", response.sender)
					self.remote_nodes[response.sender].completed = True
					self.remote_nodes[response.sender].status = RemoteNode.IDLE
					self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )
			else:
				self.logger.info("   Bogus message from '%s' node:\n%s", response.sender, response)
				
			# the node sends back 'True' when a DAQ has been stopped.
			# it returns 'False' when there's no DAQ to stop:
			# in that case we don't need to wait for a signal.
			if node.type == RemoteNode.READOUT:
				wait_for_DAQ = wait_for_DAQ or response.success
		
		# if there was a DAQ node still running,
		# we need to wait until it signals us it's done!
		# check once more, though, before we quit -- maybe
		# all the DAQs finished while we were processing
		# the responses to the request.
		all_completed = True
		for node_name in self.remote_nodes:
			node = self.remote_nodes[node_name]
			all_completed = all_completed and (node.type == RemoteNode.READOUT and node.completed)
			
		if wait_for_DAQ and not all_completed:
			self.can_shutdown = True
			return
		
		self.waiting = False
		
		for node_name in self.remote_nodes:
			node = self.remote_nodes[node_name]
			if node.type in (RemoteNode.READOUT, RemoteNode.MTEST) and not node.completed:
				self.NewAlert(notice="Not all nodes were stopped.  The next subrun could be problematic...", severity=Alert.WARNING)
				break
		
		for threadname in self.DAQ_threads:		
			self.current_state = "Subrun finishing:\nSignalling ET threads..."
			self.current_progress = (step, numsteps)
			self.postoffice.Send( self.StatusReport( items=["current_state", "current_progress", "waiting"] )  )

			thread = self.DAQ_threads[threadname]
			
			# the ET system process stops on its own.  just cut off its display feed.
			# we also don't want a notification if it crashes now...
			if threadname == "et system":
				thread.relay_output = False
				thread.is_essential_service = False

			# the event builder needs to know if it should expect a sentinel.
			elif threadname == "event builder":
				# only signal if there's no sentinel coming.
				# if there isn't, send the process a SIGTERM.
				if not sentinel:
					try:
						thread.process.terminate()
					# the process might have crashed.
					except OSError:
						pass
				
				# either way, we stop displaying its output
				# and ask that alerts be suppressed if it crashes.
				thread.relay_output = False
				thread.is_essential_service = False
				
			# any other threads should be aborted.
			elif hasattr(thread, "Abort"):
				self.logger.info("Stopping thread '%s'...", threadname)	
				thread.Abort()
				
			step += 1
		
		# remove the threads from the dictionary.
		# we don't need a handle on them any more.
		self.DAQ_threads = {}
			
			
		# try to reset the LI box...
		# but don't worry too much if it can't be--
		# it might already be unset, etc.  we'll
		# panic on the startup end if need be.
		self.logger.info("Resetting the light injection box(es)...")
		message = PostOffice.Message(subject="readout_directive", mgr_id=self.id,
		                             directive="li_configure",
		                             li_level=MetaData.LILevels.ZERO_PE,
		                             led_groups=MetaData.LEDGroups.ABCD)
		responses = self.postoffice.Send(message)
		step += 1
		
		self.logger.info("Subrun %d finished.", self.configuration.subrun)

		# need to make sure all the tasks are marked "not yet completed" so that they are run for the next subrun
		for task in self.SubrunStartTasks:
			task["completed"] = False

		# we should only increment the subrun number if we
		# started up ET.  otherwise there's nothing on disk
		# with the old subrun number, which means we can
		# reuse it.
		if self.started_et:
			self.configuration.subrun += 1

		self.current_state = "Subrun completed."
		self.current_progress = (numsteps, numsteps)
		self.postoffice.Send( self.StatusReport( items=["current_state", "current_progress"] ) )
		
		if self.running and (self.configuration.subrun - self.first_subrun) < len(self.run_series.Runs):
			self.postoffice.Send(PostOffice.Message(subject="mgr_internal", event="subrun_auto_start"))
		else:
			self.running = False
			self.postoffice.Send(PostOffice.Message(subject="mgr_internal", event="series_end", early_abort=False, auto_start=auto_start))		

	##########################################
	# Helper methods used by StartNextSubrun()
	##########################################
	
	def RunInfoAndConnectionSetup(self):
		""" Configures the run and sets up connections to the readout nodes. """
		self.logger.info("Subrun %d begun.", self.configuration.subrun)
		
		self.can_shutdown = True		# from here on it makes sense to call the EndSubrun() method
		self.started_et = False		# we haven't started ET yet this subrun
		self.current_gate = { "number": 0, "type": MetaData.TriggerTypes.UNKNOWN, "time": 0 }
		
		# copy the information from this subrun into the configuration
		runinfo = self.run_series.Runs[self.configuration.subrun - self.first_subrun]

		self.configuration.num_gates  = runinfo.gates
		self.configuration.run_mode   = MetaData.RunningModes[runinfo.runMode]
		self.configuration.hw_config  = MetaData.HardwareConfigurations[runinfo.hwConfig]
		self.configuration.li_level   = MetaData.LILevels.MAX_PE if runinfo.ledLevel == "--" else MetaData.LILevels[runinfo.ledLevel]
		self.configuration.led_groups = MetaData.LEDGroups.ABCD if runinfo.ledLevel == "--" else MetaData.LEDGroups[runinfo.ledGroup]


#		wx.PostEvent(self.main_window, Events.UpdateSeriesEvent())


		# ET needs to use a rotating port number to avoid blockages.
		# unfortunately, there's no programmatic way to determine which
		# one in the set will be free.  (modding the subrun number by
		# the number of available ports would work if the subrun number
		# never reverted back to 1, ... but it does sometimes.)
		# so we just find one that will work by inspection.
		self.logger.info("Trying to find a port for use by ET.")
		self.configuration.et_port = None
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		for port in range(Configuration.params["sock_etPortBase"], Configuration.params["sock_etPortBase"] + Configuration.params["sock_numETports"]):
			try:
				self.logger.debug("  trying port %d...", port)
				s.bind( ("", port) )
			except socket.error as e:
				continue
			else:
				s.close()
				self.configuration.et_port = port
			break

		if self.configuration.et_port is None:
			self.NewAlert(notice="All of the ET server ports assigned to the DAQ are in use.  Either wait until they finish or kill some of them before continuing.", severity=Alert.ERROR )
			return False

		self.logger.info("  ... will use port %d as this subrun's ET port.", self.configuration.et_port)

		self.postoffice.Send( self.StatusReport( items=["running", "configuration"]) )
		
		# ok to proceed to next step
		return True
	
	def ReadoutNodeHWConfig(self):
		""" Initializes the hardware configuration on the readout nodes.
		    This process takes some time on the full detector, so this
		    method exits after starting the process.  When the SocketThread
		    receives the appropriate message from all readout nodes then
		    we will continue. """
		
		self.logger.info("  Using hardware configuration: %s", self.configuration.hw_config.description)
		
		# if this subrun has a different HW config from the one before
		# (which includes the cases where this is the first subrun
		#  or it's the only subrun), or the user forces a reload, then
		# we need to ask the slow control to set up the HW.
		# that is, unless this configuration is the "current
		# state" version, in which case the user doesn't want
		# to use any configuration file at all (so that custom
		# configurations via the slow control can be used for testing).
		# NOTICE THAT THE SELECTION OF THE "CURRENT STATE" OPTION
		# OVERRIDES THE "FORCE HW RELOAD" OPTION.  this is because
		# you wouldn't want to try to force a reload when the
		# selected hardware is "no configuration".
		self.logger.debug("  HW config check.")
		if self.configuration.force_hw_reload:
			self.logger.info("  ... client explicitly requests hardware configuration be done.")
		if self.configuration.hw_config != MetaData.HardwareConfigurations.NOFILE \
		   and ( self.configuration.hw_config != self.last_HW_config or self.configuration.force_hw_reload ):
			for node_name in self.remote_nodes:
				if self.remote_nodes[node_name].type == RemoteNode.READOUT:
					self.remote_nodes[node_name].status = RemoteNode.IDLE
					self.remote_nodes[node_name].hw_init = False
			
			try:
				self.logger.info("Instructing readout nodes to initialize hardware...")
				responses = self.NodeSendWithResponse(PostOffice.Message(subject="readout_directive", directive="hw_config", hw_config=self.configuration.hw_config, mgr_id=self.id), node_type=RemoteNode.READOUT, timeout=10)
			except DAQErrors.NodeError:
				self.NewAlert(notice="At least one of the remote node(s) has become unresponsive.  Check the logs for more details.  Running will be halted...", severity=Alert.ERROR)
				return False
			
			for response in responses:
				if response.success == True:
					self.remote_nodes[response.sender].hw_init = True
					self.logger.info("  ==> '%s' node has initialized.", response.sender)
				else:
					if response.success == False:
						self.NewAlert( notice="Hardware configuration file for configuration '%s' could not be found on the '%s' readout node..." % (self.configuration.hw_config, response.sender), severity=Alert.ERROR )
					elif isinstance(response.success, Exception):
						self.NewAlert( notice="Error configuring hardware on '%s' node.  Error text:\n%s" % (response.sender, response.success), severity=Alert.ERROR )
					
					self.remote_nodes[response.sender].status = RemoteNode.ERROR
					
					# this will force HW to be reloaded next time a subrun is started
					self.last_HW_config = None
					return False
					
			# we've succeeded if initialization of all the hardware
			# on the readout nodes was successful.
			# what the other nodes are doing is irrelevant at the moment.
			success = True
			for node_name in self.remote_nodes:
				node = self.remote_nodes[node_name]
				success = success and (node.type != RemoteNode.READOUT or node.hw_init)
				if not success:
					self.NewAlert(notice="Couldn't initialize hardware on '%s' node... " % node.name, severity=Alert.ERROR)
					return False
			
			
			# record what we did so that the next time we don't have to do it again.
			self.last_HW_config = self.configuration.hw_config
			
			# if this was a 'force-reload', and it happened successfully,
			# we don't want to do it again unless the user requests it.
			# therefore turn it off.
			self.configuration.force_hw_reload = False
			
			# always check the PMT HVs and periods after setting a new HW config
			self.do_pmt_check = True
		else:
			for node_name in self.remote_nodes:
				node = self.remote_nodes[node_name]
				if node.type == RemoteNode.READOUT:
					node.hw_init = True
					node.status = RemoteNode.OK

			self.postoffice.Send( self.StatusReport(items=["remote_nodes",]) )
			self.last_HW_config = self.configuration.hw_config

			if self.configuration.hw_config == MetaData.HardwareConfigurations.NOFILE:
				self.logger.info("   ==> Hardware config is 'current state': won't reload hardware.")
			else:
				self.logger.info("   ==> No HW configuration necessary.")

			return True
		
		# need to wait on HW init (it can take a while).  don't proceed to next step yet.
		return None
		
	def LIBoxSetup(self):
		""" Configures the light injection box, if needed. """

		# set up the LI box to do what it's supposed to, if it needs to be on.
		if self.configuration.run_mode in (MetaData.RunningModes.LI, MetaData.RunningModes.MIXED_NUMI_LI):
			li_level   = self.configuration.li_level
			led_groups = self.configuration.led_groups
		else:
			li_level   = MetaData.LILevels.ZERO_PE
			led_groups = MetaData.LEDGroups.ABCD
		
		message = PostOffice.Message(subject="readout_directive", mgr_id=self.id, directive="li_configure",
		                             li_level=li_level, led_groups=led_groups)
		
		skip = False
		
		try:
			responses = self.NodeSendWithResponse(message, node_type=RemoteNode.READOUT, timeout=10)
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the readout node(s) has become unresponsive during LI box setup.  Please document this in CRL (with run, subrun, and this message) and notify the expert shifter.  I will skip to the next subrun and try again...", severity=Alert.WARNING)
			skip = True
		else:
			for response in responses:
				if response.success != True:
					self.NewAlert( notice="The LI box on the '%s' node could not be configured!  Please document this in CRL (with run, subrun, and this message) and notify the expert shifter.  I will skip to the next subrun and try again..." % response.sender, severity=Alert.WARNING )
					if isinstance(response.success, Exception):
						self.logger.error("LI error text:\n%s", response.success)
			
					self.remote_nodes[response.sender].status = RemoteNode.ERROR
					skip = True
		
		if skip:
			# for now, if the LI configuration didn't work,
			# we just go on to the next subrun.  we'll make that
			# happen manually here.
			self.postoffice.Send( PostOffice.Message(subject="mgr_internal", event="subrun_end", auto_start=True) )
			
			# return None so that the subrun doesn't try to continue,
			# but also doesn't abort the run series altogether.
			return None
		else:
			# ok to proceed to next step
			return True
	
	def ReadoutNodeHVCheck(self):
		"""
		Checks if the HV deviations from setpoint and
		HV periods are acceptable.
		If not, control is passed to a window that asks
		the user for input.
		"""

		# this check is only done at the beginning of a run series
		# or if the hardware configuration has changed
		if self.do_pmt_check:
			self.problem_pmt_list = None

			problem_boards = self.GetProblemPMTs()
			thresholds = sorted(Configuration.params["mstr_HVthresholds"].keys(), reverse=True)
			ranges = {}
			for i in range(len(thresholds)):
				ranges[i+1] = Configuration.params["mstr_HVthresholds"][thresholds[i]]
			
			over = {}
			needs_intervention = False
			for board in problem_boards:
				if board["failure"] == "period":
					needs_intervention = True
					break
				elif board["failure"] == "hv_range":
					rng = board["range"]
					if rng in over:
						over[rng] += 1
					else:
						over[rng] = 1

					if over[rng] > ranges[rng]:
						notify = True
						break

			# we've done the PMT check now, so unless the HW config changes,
			# we don't need to do it again this run series.
			self.do_pmt_check = False

			# does the user need to look at it?
			# if so, send out a notice.
			if notify:
				  self.logger.info("  ... warning user about errant PMT high voltages.")
				  self.postoffice.Send(PostOffice.Message(subject="frontend_info", info="HV_warning", pmt_info=problem_boards))
				  self.problem_pmt_list = problem_boards
			else:
				self.logger.info("  ... PMT voltages are ok.")
		else:
			self.logger.info("  ... don't need to check PMT voltages.")

		# ok to proceed to next step
		return True

	##########################################
	# Subprocess starters
	##########################################

	def StartNextThread(self, signum=None, sigframe=None):
		""" Starts the next thread in the sequence.
		    This method should ONLY be called
		    as the signal handler for SIGUSR1
		    (otherwise race conditions will result)! """
		
		if not self.running:
			return    
		
		if self.current_DAQ_thread < len(self.DAQStartTasks):
			self.current_state = "Setting up run:\n" + self.DAQStartTasks[self.current_DAQ_thread]["message"]
			self.current_progress = (self.startup_step, self.num_startup_steps)
			self.postoffice.Send( self.StatusReport( items=["current_state", "current_progress"] ) )
			
			# do the increments first to prevent race conditions
			# (i.e., some subsidiary task spawned by a DAQStartTask
			#  might signal before the DAQStartTask has fully finished)
			self.startup_step += 1
			self.current_DAQ_thread += 1
			try:
				self.DAQStartTasks[self.current_DAQ_thread-1]["method"]()
			except Exception as e:
				self.NewAlert(notice="There was an error executing a DAQ startup task: '%s'.  Running will be halted..." % e, severity=Alert.ERROR)
				self.StopDataAcquisition(do_auto_start=False)
		else:
			signal.signal(signal.SIGUSR1, signal.SIG_IGN)		# go back to ignoring the signal...
			self.logger.warning("Note: requested a new thread but no more threads to start...")

	def StartETSys(self):
		""" Start the et_system process. """
		
		self.logger.info("  starting the ET system (using ET filename: '%s_RawData')...", self.configuration.et_filename)
		
		events = self.configuration.num_gates * Configuration.params["hw_eventFrames"] * Configuration.params["hw_numFEBs"]

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d -c %d -p %d" % ( os.environ["ET_HOME"],
		                                                                                          Configuration.params["mstr_etSystemFileLocation"],
		                                                                                          self.configuration.et_filename + "_RawData",
		                                                                                          events, Configuration.params["hw_frameSize"],
		                                                                                          os.getpid(),
		                                                                                          self.configuration.et_port )

		self.DAQ_threads["et system"] = Threads.DAQthread(process_info=etsys_command, process_identity="ET system", postoffice=self.postoffice, env=os.environ, is_essential_service=True)

	def StartETMon(self):
		""" Start the ET monitor process.
		
		    Not strictly necessary for data aquisition, but
		    is sometimes helpful for troubleshooting. """
		    
		self.logger.info("  starting the ET monitor...")
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s -c %d -p %d" % ( os.environ["ET_HOME"], 
		                                                                             Configuration.params["mstr_etSystemFileLocation"],
		                                                                             self.configuration.et_filename + "_RawData",
		                                                                             os.getpid(),
		                                                                             self.configuration.et_port )
		self.DAQ_threads["et monitor"] = Threads.DAQthread(process_info=etmon_command, process_identity="ET monitor", postoffice=self.postoffice, env=os.environ)

	def StartEBSvc(self):
		""" Start the event builder service.
		
		    (This does the work of stitching together the frames from the readout nodes.) """

		self.logger.info("  starting the event builder...")
		    
		eb_command = '%s/bin/event_builder %s/%s %s/%s %d %d' % ( os.environ['DAQROOT'],
		                                                          Configuration.params["mstr_etSystemFileLocation"],
		                                                          self.configuration.et_filename + "_RawData",
		                                                          Configuration.params["mstr_rawdataLocation"],
		                                                          self.raw_data_filename,
		                                                          self.configuration.et_port, os.getpid())

		self.DAQ_threads["event builder"] = Threads.DAQthread(process_info=eb_command, process_identity="event builder", postoffice=self.postoffice, env=os.environ, is_essential_service=True)
		self.started_et = True

	def StartOM(self):
		""" Start the online monitoring services on the OM node.
		
		    This needs to be done BEFORE the DAQ is started on the
		    readout nodes because otherwise there is a race condition
		    between the startup of the event builder on the OM node
		    and the startup of the DAQ -- and if the DAQ starts up first,
		    the EB on the OM node might miss some of the frames from
		    the first event. """
		    
		num_remote_nodes = 0
		for node in self.remote_nodes:
			if self.remote_nodes[node].type == RemoteNode.MONITORING:
				num_remote_nodes += 1
		
		# if no monitoring nodes, just go on to the next step
		# by emitting the correct signal
		if num_remote_nodes == 0:
			os.kill(os.getpid(), signal.SIGUSR1)
			return
		
		# the ET system is all set up, so the online monitoring nodes
		# can be told to connect.
		self.logger.info("  initializing any online monitoring nodes...")
		message = PostOffice.Message(subject="om_directive", directive="start", mgr_id=self.id, et_pattern=self.configuration.et_filename, et_port=self.configuration.et_port)

		responses = None

		try:
			responses = self.NodeSendWithResponse(message, node_type=RemoteNode.MONITORING, timeout=10)
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the monitoring node(s) has become unresponsive.  Check the logs for more details.  The run will be allowed to continue, but you will not have online monitoring...", severity=Alert.ERROR)

		for response in responses:
			if response.subject == "invalid_request" \
			  or response.success == False:
				self.NewAlert(notice="Couldn't start the '%s' online monitoring node.  The run will be allowed to continue, but you will not have online monitoring..." % response.sender, severity=Alert.ERROR)
			elif isinstance(response.success, Exception):
				self.NewAlert(notice="Error starting the '%s' online monitoring node.  Error message text:\n%s\nThe run will be allowed to continue, but you will not have online monitoring..." % (response.sender, response.success), severity=Alert.ERROR)
			else:
				self.remote_nodes[response.sender].status = RemoteNode.OK
				self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )

				self.logger.info("    ... '%s' node started.", response.sender)
		
		os.kill(os.getpid(), signal.SIGUSR1)

	def StartRemoteServices(self):
		""" Notify all the remote services that we're ready to go.
		    Currently this includes the online monitoring system
		    as well as the DAQs on the MTest beamline node (if
		    configured) and the readout node(s). """
		    
# TODO: someday this needs to be updated for v5 series run control
#		if self.mtest_useBeamDAQ:
#			for node in self.mtestBeamDAQNodes:
#				try:
#					node.daq_start(self.configuration)
#				except:
#					self.logger.exception("Couldn't start MTest beamline DAQ!  Aborting run.")
#					wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="alarm", messageheader="Couldn't start beamline DAQ", messagebody=["Couldn't start the beamline DAQ.",  "Run has been aborted (see the log for more details)."]) )
#					self.StopDataAcquisition()
		
		# for non-LI run modes, these values are irrelevant, so we set them to some well-defined defaults.
		if not (self.configuration.run_mode in (MetaData.RunningModes.LI, MetaData.RunningModes.MIXED_NUMI_LI)):
			self.configuration.li_level = MetaData.LILevels.ZERO_PE
			self.configuration.led_groups = MetaData.LEDGroups.ABCD
		
		# issue the 'stop' command to the DAQ(s)
		# to make sure we are in a well-defined starting state
		self.logger.info("  clearing the DAQ to make sure it's ready...")
		
		try:
			responses = self.NodeSendWithResponse( PostOffice.Message(subject="readout_directive", directive="daq_stop", mgr_id=self.id), node_type=RemoteNode.READOUT, timeout=10 )
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the readout node(s) has become unresponsive.  Check the logs for more details.  Running will be halted...", severity=Alert.ERROR)
			self.StopDataAcquisition(do_auto_start=False)
			return

		for response in responses:
			if isinstance(response.success, Exception):
				self.NewAlert(notice="Error stopping the DAQ on the '%s' readout node.  Error message text:\n%s" % (response.sender, response.success), severity=Alert.ERROR)
				self.StopDataAcquisition(do_auto_start=False)
				return

		# now start the DAQ(s)
		self.logger.info("  starting the DAQ on the readout nodes...")

		try:
			responses = self.NodeSendWithResponse( PostOffice.Message(subject="readout_directive", directive="daq_start", mgr_id=self.id, configuration=self.configuration), node_type=RemoteNode.READOUT, timeout=10 )
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the readout node(s) has become unresponsive.  Check the logs for more details.  Running will be halted...", severity=Alert.ERROR)
			self.StopDataAcquisition(do_auto_start=False)
			return


		for response in responses:
			if isinstance(response.success, Exception):
				self.NewAlert(notice="Error starting the DAQ on the '%s' readout node.  Error message text:\n%s" % (response.sender, response.success), severity=Alert.ERROR)
				self.StopDataAcquisition(do_auto_start=False)
				return
			elif response.success == False:
				self.NewAlert(notice="The DAQ on the '%s' node is already running (even after being issued a 'STOP' command)!  Stopping run for troubleshooting..." % response.sender, severity=Alert.ERROR)
			elif response.success == True:
				self.logger.info("   '%s' node started...", response.sender)
				self.remote_nodes[response.sender].running = True
				self.remote_nodes[response.sender].completed = False
				
		if self.running:
			self.current_state = "Running"
			# increment the subrun number so that if this run crashes,
			# the next one won't overwrite it -- then decrement it again
			# so that our bookkeeping is accurate
			self.configuration.subrun += 1
			self.configuration.Save(filepath=Configuration.params["mstr_runinfoFile"])
			self.configuration.subrun -= 1
			
			# we're waiting now for the 'done' signal from the DAQ
			self.waiting = True
			self.postoffice.Send( self.StatusReport(items=["current_state", "waiting"]) )
			
			self.logger.info("  All DAQ services started.  Data acquisition for subrun %d underway." % (self.configuration.subrun) )
		
####################################################################
#  Utilities & alerts
####################################################################

	def AcknowledgeAlert(self, alert):
		""" Clears an alert from the stack. """
		
		for notice_collection in (self.warnings, self.errors):
			if alert in notice_collection:
				notice_collection.remove(alert)
		
		# make sure ALL clients know that this alert was cleared
		self.postoffice.Send( PostOffice.Message(subject="client_alert", action="clear", alert=alert, mgr_id=self.id) )
	
	def GetProblemPMTs(self, send_results=False):
		""" Requests PMT high voltage and period information
		    from the readout nodes and returns any that are
		    over the specified thresholds. """

		thresholds = sorted(Configuration.params["mstr_HVthresholds"].keys(), reverse=True)

		try:		
			responses = self.NodeSendWithResponse( PostOffice.Message(subject="readout_directive", directive="sc_read_boards", mgr_id=self.id), node_type=RemoteNode.READOUT, timeout=10 )
		except DAQErrors.NodeError:
			self.NewAlert(notice="At least one of the readout node(s) has become unresponsive.  Check the logs for more details.  Running will be halted...", severity=Alert.ERROR)
			self.StopDataAcquisition(do_auto_start=False)
		
		nodes_checked = 0
		problem_boards = []
		for response in responses:
			if isinstance(response.sc_board_list, Exception):
				self.NewAlert(notice="The '%s' node reports a slow control error while trying to read the boards.  Error text: '%s'" % (response.sender, response.sc_board_list), severity=Alert.ERROR)
				self.StopDataAcquisition(do_auto_start=False)
				return

			if len(response.sc_board_list) == 0:
				self.NewAlert(notice="The '%s' node is reporting that it has no FEBs attached.  Your data will appear suspiciously empty..." % response.sender, severity=Alert.WARNING)
			
			voltage_list = "  voltage deviations & HV periods of PMTs attached to the '%s' node:\ncroc-channel-board: HV dev, HV period\n=====================================\n" % response.sender
			for board in response.sc_board_list:
				board["node"] = response.sender
				voltage_list += "%d-%d-%d: %5d, %5d\n" % (board["croc"], board["chain"], board["board"], board["hv_deviation"], board["period"])
				
				# don't consider FEB IDs that are in our blacklist
				board_id_info = { "node": board["node"], "croc": board["croc"], "chain": board["chain"], "board": board["board"] }
				if board_id_info in Configuration.params["mstr_HVignoreFEBs"]:
					continue
				
				if abs(board["hv_deviation"]) > min(thresholds) or board["period"] < Configuration.params["mstr_HVperiodThreshold"]:
					problem_boards.append(board)
					
			self.logger.info(voltage_list)
				
			nodes_checked += 1

		if nodes_checked == 0:
			self.NewAlert(notice="No nodes responded with PMT voltages.  Check the dispatchers on your readout nodes!", severity=Alert.ERROR)
			self.StopDataAcquisition(do_auto_start=False)

		for board in problem_boards:
			if board["period"] < Configuration.params["mstr_HVperiodThreshold"]:
				self.logger.warning("Board (node-croc-chain-board) %s-%d-%d-%d is below the period threshold (period: %d)", board["node"], board["croc"], board["chain"], board["board"], board["period"])
				board["failure"] = "period"
			else:
				self.logger.warning("Board (node-croc-chain-board) %s-%d-%d-%d is outside the minimum HV range tolerance (deviation from target in ADC counts: %d)", board["node"], board["croc"], board["chain"], board["board"], board["hv_deviation"])
				board["failure"] = "hv_range"
			
				# which HV range is it?
				# the frontend uses this to color-code
				assigned_range = False
				i = 0
				for threshold in thresholds:
					i += 1
					if abs(board["hv_deviation"]) > threshold:
						if not assigned_range:
							assigned_range = True
							board["range"] = i

		if send_results:
			self.postoffice.Send( PostOffice.Message(subject="frontend_info", info="pmt_update", pmt_info=problem_boards) )
		else:
			return problem_boards

	def NodeSendWithResponse(self, message, node_type=None, timeout=None, with_exception=False):
		""" Utility method to send a message to the readout nodes.
		    It verifies that the senders of response messages are
		    actually within the node list.  It can also optionally
		    verify that a response was received from each node
		    of a certain type (or every node in the list). """
		    
		responses = self.postoffice.SendAndWaitForResponse( message, timeout=timeout, with_exception=with_exception )

		out_responses = []
		responses_received = dict( [ (node_name, False) for node_name in self.remote_nodes ] )
		for response in responses:
			# occasionally we get responses from the local node.  ignore those.
			if len(response.return_path) == 0:
				continue
			elif response.sender not in self.remote_nodes:
				self.logger.warning("Got response from a node I don't have in my list.  Who are you?? (name: %s, address: %s)", response.sender, response.return_path[0])
				continue
			
			responses_received[response.sender] = True
			out_responses.append(response)

		missing_nodes = []
		
		if node_type is not None:
			for node in responses_received:
				if (node_type == RemoteNode.ANY or node_type == self.remote_nodes[node].type) and not responses_received[node]:
					missing_nodes.append(node)
		
		if len(missing_nodes) > 0:
			e = DAQErrors.NodeError("Responses were not received from the following nodes: %s" % missing_nodes)
			self.logger.warning( str(e) )
			raise e
		
		return out_responses
		

	def NewAlert(self, notice, severity):
		""" Adds a new alert to the stack and sends a message
		    out to clients indicating there's a notice waiting.
		    
		    In addition, if the alert is an ERROR, running is
		    halted. """
		
		alert = Alert.Alert(notice, severity, manager=True)
		
		if severity == Alert.WARNING:
			self.logger.warning(alert.notice)
			self.warnings += [alert,]
		else:
			self.logger.error(alert.notice)
			self.errors += [alert,]
#			self.running = False
		
		self.postoffice.Send( PostOffice.Message(subject="client_alert", mgr_id=self.id, alert=alert, action="new") )

	def OMStatusHandler(self, message):
		""" Handles updates from an online monitoring node
		    about changes in its state. """
		
		if not hasattr(message, "state"):
			self.logger.info("OM status message from '%s' node is badly formed.  Ignoring.  Message:\n%s", message.sender, message)
			return
		
		if message.state == "om_error":
			self.NewAlert(notice="An error was reported on the '%s' monitoring node.  Error text:\n%s" % (message.sender, message.error), severity=Alert.ERROR)
			self.remote_nodes[message.sender].status = RemoteNode.ERROR
			self.StopDataAcquisition(do_auto_start=False)

			self.postoffice.Send( self.StatusReport(items=["remote_nodes"]) )


		# DON'T HANDLE THE "om_ready" CASE HERE.
		# it will deadlock because the StartOM()
		# method is ALREADY waiting for that response!
		
	def PrepareRunSeries(self):
		""" Prepares a run series based on the values
		    found in the current configuration.  """
		    
		if self.configuration.is_single_run:
			self.run_series = RunSeries.RunSeries()
			run = RunSeries.RunInfo( gates=self.configuration.num_gates, \
			                         runMode=self.configuration.run_mode.hash,\
			                         hwcfg=self.configuration.hw_config.hash,\
			                         ledLevel=self.configuration.li_level.hash,\
			                         ledGroup=self.configuration.led_groups.hash ) 
			self.run_series.AppendRun(run)
		else:
			try:
				dblocation = "%s/%s" % (Configuration.params["mstr_runSeriesLocation"], self.configuration.run_series.code)
				db = shelve.open(dblocation)
				self.run_series = db["series"]
				db.close()
			except (anydbm.error, KeyError):
				self.logger.error("Cannot load run series file '%s'!", dblocation)
				return DAQErrors.FileError("Run series file '%s' cannot be loaded..." % self.configuration.run_series.code)
		
		# we always check the PMT HVs and periods at the beginning of a run series
		self.do_pmt_check = True
		
		return True

	def SeriesInfo(self, series):
		""" Answers inquiries from clients asking about
		    the details of particular run series. """
		
		self.logger.info("Client wants info about run series '%s'.", series.description)
		message = PostOffice.Message(subject="frontend_info", info="series_update", series=series)
		
		try:
			dblocation = "%s/%s" % (Configuration.params["mstr_runSeriesLocation"], series.code)
			db = shelve.open(dblocation)
			message.series_details = db["series"]
			db.close()
		except (anydbm.error, KeyError):
			# if we can't load it, we'll send them a blank run series
			self.logger.warning("Couldn't open file for run series '%s' (tried: '%s')!  Returning a blank series...", series.description, dblocation)
			message.series_details = RunSeries.RunSeries()
		
		self.postoffice.Send(message)
	
	def StatusReport(self, message=None, items=[], do_log=True):
		""" Fills a message with a bunch of status information.
		
		    It is only all given when a client
		    specifically requests it or a subrun is beginning
		    (it generates a fair bit of information and sending
		    it over the network unasked-for would probably
		    slow things down). 
		    
		    Otherwise, methods throughout the DAQ manager
		    use the items[] list to specify which pieces of
		    information should be given."""
		
		
		# some defaults
		if message is None:
			message = PostOffice.Message( subject="frontend_info", info="status_update" )
		if len(items) == 0:
			items = ( "configuration", "current_state", "current_progress", "current_gate", "first_subrun",
			          "errors", "warnings", "problem_pmt_list", "remote_nodes", "running", "run_series",
			          "control_info", "waiting" )

		if do_log:
			self.logger.debug("Generating status report with the following items: %s", items)

		message.status = {}
		for item in items:
			message.status[item] = copy.deepcopy(self.__dict__[item])
			
		message.status["time_generated"] = time.time()
		
		return message
		
####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process
  coordinating the pieces of the DAQ proper with input
  from a frontend client over a socket.
  
  Otherwise this implementation will bail with an error.
"""
if __name__ == "__main__":
	environment = {}
	try:
		os.environ["DAQROOT"]
		os.environ["ET_HOME"]
		os.environ["ET_LIBROOT"]
		os.environ["LD_LIBRARY_PATH"]
	except KeyError:
		sys.stderr.write("Your environment is not properly configured.  You must run the 'setupdaqenv.sh' script before launching the dispatcher.\n")
		sys.exit(1)

	dispatcher = DataAcquisitionManager()
	dispatcher.Bootstrap()
	
	sys.exit(0)
else:
	raise RuntimeError("This module is not designed to be imported!")
