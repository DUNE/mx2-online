"""
  DataAcquisitionManager.py:
   Infrastructural objects to manage a data acquisition run.
   Used by the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-June 2010
                    
   Address all complaints to the management.
"""

import wx
import os
import re
import signal
import errno
import fcntl
import datetime
import time
import threading
import socket
import logging
import logging.handlers

# run control-specific modules.
# note that the folder 'mnvruncontrol' must be in the PYTHONPATH!
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.configuration import Configuration
from mnvruncontrol.backend import Events
from mnvruncontrol.backend import LIBox
from mnvruncontrol.backend import RunSeries
from mnvruncontrol.backend import RemoteNode
from mnvruncontrol.backend import ReadoutNode
from mnvruncontrol.backend import MonitorNode
from mnvruncontrol.backend import MTestBeamNode
from mnvruncontrol.backend import Threads
from mnvruncontrol.frontend import Frames

class DataAcquisitionManager(wx.EvtHandler):
	""" Object that does the actual coordination of data acquisition.
	    You should only ever make one of these at a time. """
	
	### Notice: like the run control front end, this class is
	### pretty large, so its methods are also grouped by category.
	###
	### The categories are as follows:
	###   * initialization/teardown            (begin around line 50)
	###   * global starters/stoppers           ( ...              125)
	###   * subrun starters/stoppers           ( ...              200)
	###   * helper methods for StartNextSubrun ( ...              475)
	###   * subprocess starters                ( ...              700)
	###   * utilities/event handlers           ( ...              825)
	
	def __init__(self, main_window):
		wx.EvtHandler.__init__(self)

		self.main_window = main_window
		
		# threads that this object will be managing.
		self.DAQthreads = {}

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


		# counters
		self.current_DAQ_thread = 0			# the next thread to start
		self.subrun = 0					# the next run in the series to start
		self.windows = []					# child windows opened by the process.
		
		self.readoutNodes         = [ReadoutNode.ReadoutNode(nodedescr["name"], nodedescr["address"]) for nodedescr in Configuration.params["Front end"]["readoutNodes"]]
		self.monitorNodes         = [MonitorNode.MonitorNode(nodedescr["name"], nodedescr["address"]) for nodedescr in Configuration.params["Front end"]["monitorNodes"]]
		self.mtestBeamDAQNodes    = [MTestBeamNode.MTestBeamNode(nodedescr["name"], nodedescr["address"]) for nodedescr in Configuration.params["Front end"]["mtestbeamNodes"]]

		self.LIBox = LIBox.LIBox(disable_LI=not(Configuration.params["Hardware"]["LIBoxEnabled"]), wait_response=Configuration.params["Hardware"]["LIBoxWaitForResponse"])

		# configuration stuff
		self.etSystemFileLocation = Configuration.params["Master node"]["etSystemFileLocation"]
		self.rawdataLocation      = Configuration.params["Master node"]["master_rawdataLocation"]

		# logging facilities
		self.logger = logging.getLogger("rc_dispatcher")
		self.logger.setLevel(logging.DEBUG)
		self.filehandler = logging.handlers.RotatingFileHandler(Configuration.params["Master node"]["master_logfileName"], maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.DEBUG)
		self.formatter = logging.Formatter("[%(asctime)s] %(levelname)s:  %(message)s")
		self.filehandler.setFormatter(self.formatter)
		self.logger.addHandler(self.filehandler)
		
		self.last_logged_gate = 0

		# these will need to be set by the run control window before the process is started.
		# that way we can be sure it's properly configured.
		self.runseries = None
		self.detector = None
		self.run = None
		self.first_subrun = None
		self.febs = None
		
		self.mtest_useBeamDAQ = None
		self.mtest_branch = None
		self.mtest_crate = None
		self.mtest_controller_type = None
		self.mtest_mem_slot = None
		self.mtest_gate_slot = None
		self.mtest_adc_slot = None
		self.mtest_tdc_slot = None
		self.mtest_tof_rst_gate_slot = None
		self.mtest_wc_rst_gate_slot = None
		
		self.running = False
		self.can_shutdown = False		# used in between subruns to prevent shutting down twice for different reasons
		
		self.last_HW_config = None		# this way we don't write the HW config more often than necessary

		self.messageHandlerLock = threading.Lock()

		self.Bind(Events.EVT_SOCKET_RECEIPT, self.HandleSocketMessage)
		self.Bind(Events.EVT_UPDATE_PROGRESS, self.RelayProgressToDisplay)

		self.Bind(Events.EVT_READY_FOR_NEXT_SUBRUN, self.StartNextSubrun)
		self.Bind(Events.EVT_THREAD_READY, self.StartNextThread)
		self.Bind(Events.EVT_END_SUBRUN, self.EndSubrun)		# if the DAQ process quits, this subrun is over
		self.Bind(Events.EVT_STOP_RUNNING, self.StopDataAcquisition)

		try:
			self.socketThread = Threads.SocketThread(self.logger)
			self.logger.info("Started master node listener on port %d." % Configuration.params["Socket setup"]["masterPort"])

			self.OldSessionCleanup()
		except Threads.SocketAlreadyBoundException:
			self.socketThread = None
			wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="notice", messagebody=["Can't bind a local listening socket.",  "Synchronization between readout nodes and the run control will be impossible.", "Check that there isn't another run control process running on this machine."], messageheader="Can't bind local socket") )
		
	def OldSessionCleanup(self):
		""" Checks if there's a session that was already open.
		    If so, cleans up (stops the remote nodes), etc.
		    """
		self.logger.info("Starting up: checking for leftover session...")
		# first check for an old session.
		# if there is one, load in the IDs from the nodes that were in use.
		try:
			sessionfile = open(Configuration.params["Master node"]["sessionfile"], "r")
		except (OSError, IOError):
			self.logger.info("No previous session detected.  Starting fresh.")
			return

		self.logger.info("Old session detected.  Restoring any old node IDs...")
		# try to get a lock on the file.  that way we know it isn't being
		# updated while we try to read it.
		fcntl.flock(sessionfile.fileno(), fcntl.LOCK_EX)
		try:
			pattern = re.compile("^(?P<type>\S+) (?P<id>[a-eA-E\w\-]+) (?P<address>\S+)$")
			node_map = { "readout": self.readoutNodes, "monitoring": self.monitorNodes, "mtestbeam": self.mtestBeamDAQNodes }
			do_reset = False
			for line in sessionfile:
				matches = pattern.match(line)
				if matches is not None and matches.group("type").lower() in node_map:
					for node in node_map[matches.group("type").lower()]:
						if node.address == matches.group("address"):
							node.id = matches.group("id")
							node.own_lock = True
							do_reset = True
		finally:
			fcntl.flock(sessionfile.fileno(), fcntl.LOCK_UN)

		sessionfile.close()
		
		self.logger.info("Resetting any nodes that are still running...")
		# now reset any nodes that were previously locked & running.
		if do_reset:
			# first inform the main window that it needs to wait until we're done cleaning up.
			wx.PostEvent(self.main_window, Events.WaitForCleanupEvent())
			
			# next, reset the monitoring nodes.  they're simple
			# because we don't really care too much about whether
			# they're actually behaving.
			for node in self.monitorNodes:
				if node.own_lock:
					try:
						node.om_stop()
					except RemoteNode.RemoteNodeNoConnectionException:
						self.logger.warning("Can't connect to OM node!...")
						pass

			# now any MTest beamline DAQ nodes
			if self.mtest_useBeamDAQ:
				for node in self.mtestBeamDAQNodes:
					if node.own_lock:
						node.stop()

			self.can_shutdown = True
			self.first_subrun = 0
			
			# finally, deal with the readout nodes.
			# remember, we need to loop twice so that all subscriptions
			# are booked before issuing any stops.
			for node in self.readoutNodes:
				if node.own_lock:
					self.socketThread.Subscribe(node.id, node.name, "daq_finished", callback=self, waiting=True, notice="Cleaning up from previous run...")
			
			wait_for_reset = False	
			for node in self.readoutNodes:
				if node.own_lock:
					success = False
					try:
						success = node.daq_stop()
					except ReadoutNode.ReadoutNodeNoDAQRunningException:
						pass
					
					if success:
						wait_for_reset = True
					# otherwise we'll be stuck... forever...
					else:
						node.completed = True
						self.socketThread.Unsubscribe(node.id, node.name, "daq_finished", callback=self)
				# if it's not locked, then we can't stop it, so it may as well be "completed"
				# (otherwise we'll stuck waiting forever)
				else:
					node.completed = True
			
			if not wait_for_reset:
				wx.PostEvent(self, Events.EndSubrunEvent(allclear=True, sentinel=False))
		
	def Cleanup(self):
		""" Any clean-up actions that need to be taken.
		    Called by the RunControl right before shutdown. """
		    
		delete_session = True
		# release any locks that might still be open
		for node in self.readoutNodes + self.monitorNodes + self.mtestBeamDAQNodes:
			if node.own_lock:
				success = node.release_lock()
				
				delete_session = delete_session and success
		
		# remove the session file, but only if there's no more
		# locks that are still open...
		if delete_session:
			try:
				os.remove(Configuration.params["Master node"]["sessionfile"])
			except (IOError, OSError):		# if the file doesn't exist, no problem
				pass
			
		if self.socketThread is not None:
			self.socketThread.Abort()
			self.socketThread.join()
		
	##########################################
	# Global starters and stoppers
	##########################################
	
	def StartDataAcquisition(self, evt=None):
		""" Starts the data acquisition process.
		    Called only for the first subrun in a series. """
		    
		if not isinstance(self.runseries, RunSeries.RunSeries):
			raise ValueError("No run series defined!")

		if self.detector == None or self.run == None or self.first_subrun == None or self.febs == None:
			raise ValueError("Run series is improperly configured.")

		# try to get a lock on each of the readout nodes
		# as well as any MTest beamline DAQ nodes
		failed_connection = None
		nodelist = self.readoutNodes + self.mtestBeamDAQNodes if self.mtest_useBeamDAQ else self.readoutNodes
		for node in nodelist:
			if node.get_lock():
				if node.nodetype == "readout":
					wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
				self.logger.info(" Got run lock on %s node (id: %s)..." % (node.name, node.id))
			else:
				failed_connection = node.name
				self.logger.critical("Couldn't lock the %s node!  Aborting." % node.name)
				break
		if failed_connection:
			wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="alarm", messagebody=["Cannot get control of dispatcher on the " + failed_connection + " node.",  "Check to make sure that the dispatcher is started on that machine", "and that there are no other run control processes connected to it."], messageheader="No lock on " + failed_connection + " node") )
			return
		
		# also try to get a lock on any monitor nodes
		# here it's not a tragedy if we can't, so no erroring.
		for node in self.monitorNodes:
			if node.get_lock():
				self.logger.info(" Got run lock on %s node (id: %s)..." % (node.name, node.id))
			else:
				self.logger.warning("Couldn't lock the %s monitoring node.  Ignoring..." % node.name)
			
		# need to make sure all the tasks are marked "not yet completed"
		for task in self.SubrunStartTasks:
			task["completed"] = False
		
		self.logger.info("Beginning data acquisition sequence...")
		self.logger.info( "  Run: " + str(self.run) + "; starting subrun: " + str(self.first_subrun) + "; number of subruns to take: " + str(len(self.runseries.Runs)) )
					
		self.subrun = 0
		self.running = True
		self.StartNextSubrun()
		
	def StopDataAcquisition(self, evt=None):
		""" Stop data acquisition altogether. """
		
		# if we're already trying to stop, there shouldn't be an auto-continuation!
		if not self.running:
			auto = False
		else:
			auto = hasattr(evt, "auto") and evt.auto
		
		self.running = False

		if evt is None or not(hasattr(evt, "allclear")):
			self.logger.info("Stopping data acquisition sequence...")
			wx.PostEvent(self, Events.EndSubrunEvent(manual=True))
			return

		for node in self.readoutNodes:
			node.release_lock()
		
		if self.mtest_useBeamDAQ:
			for node in self.mtestBeamDAQNodes:
				node.release_lock()
		
		for node in self.monitorNodes:
			try:
				node.release_lock()									
			except:		# don't worry about it.  
				pass

		self.subrun = 0
		

		self.logger.info("Data acquisition finished.")
		wx.PostEvent(self.main_window, Events.StopRunningEvent(auto=auto))		# tell the main window that we're done here.


	##########################################
	# Subrun starters and stoppers
	##########################################
		
	def StartNextSubrun(self, evt=None):
		""" Prepares to start the next subrun: waits for
		    the DAQ system to be ready, notifies the main 
		    window what run we're in, prepares the LI box
		    and slow controls, and finally initiates the
		    acquisition sequence. """
	
		self.logger.debug("StartNextSubrun() called.")
	
		quitting = not(self.running)
		self.CloseWindows()			# don't want leftover windows open.

		self.num_startup_steps = len(self.SubrunStartTasks) + len(self.DAQStartTasks)
		self.startup_step = 0

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
				wx.PostEvent(self.main_window, Events.UpdateProgressEvent(text="Setting up run:\n" + task["message"], progress=(self.startup_step, self.num_startup_steps)) )
				
				# then run the appropriate method.
				status = task["method"]()
				task["completed"] = True
			
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
				#               returned to the main wx loop, so
				#               this method needs to be exited
				#               immediately.
				if status is None:
					return
				if status == False:
					quitting = True
					break
			else:
				self.logger.debug("Skipping task (already done): %s" % task["message"])
			self.startup_step += 1
			
		# if running needs to end, there's some cleanup we need to do first.
		if quitting:
			self.logger.warning("Subrun " + str(self.first_subrun + self.subrun) + " aborted.")
			wx.PostEvent(self, Events.StopRunningEvent(allclear=True))		# tell the main window that we're done here.
			return

		# all the startup tasks were successful.
		# do the final preparation for the run.
		
		now = datetime.datetime.utcnow()

		# the ET file name is the name used for the ET system file.
		# all other data file names are based on it.
		self.ET_filename = '%s_%08d_%04d_%s_v09_%02d%02d%02d%02d%02d' % (MetaData.DetectorTypes.code(self.detector), self.run, self.first_subrun + self.subrun, MetaData.RunningModes.code(self.runinfo.runMode), now.year % 100, now.month, now.day, now.hour, now.minute)
		
		# raw data written by the MINERvA DAQ
		self.raw_data_filename = self.ET_filename + '_RawData.dat'
		
		wx.PostEvent(self.main_window, Events.SubrunStartingEvent(first_subrun=self.first_subrun, current_subrun=self.subrun, num_subruns=len(self.runseries.Runs)))

		self.current_DAQ_thread = 0

		# set up the signal handler for SIGUSR1, which is
		# the signal emitted by each of the subprocesses
		# when they are ready for execution to move on.
		signal.signal(signal.SIGUSR1, self.StartNextThread)

		# start the first thread manually.
		# the rest will be started in turn as SIGUSR1 signals
		# are received by the program.		
		self.StartNextThread()			
		
	def EndSubrun(self, evt):
		""" Performs the jobs that need to be done when a subrun ends. 
		
		    Generally it is only executed as the event handler for an
		    EndSubrunEvent. """
		
		# note: this method can be called for a lot of different reasons.
		# here are the ones I can find (more added as I discover them):
		#  - session cleanup from a previous unclean shutdown can't contact
		#     all nodes to inform them they need to shutdown.  to prevent
		#     a never-ending wait for messages that won't be coming,
		#     OldSessionCleanup() passes us an EndSubrunEvent with "allclear"
		#     and "sentinel".  this mimics the next item.
		#  - 'daq_finished' messages received from all readout nodes.  
		#      SocketThread posts us an EndSubrunEvent with "allclear" and "sentinel."
		#  - an essential process dies.  DAQthread object posts us
		#     an EndSubrunEvent with "processname".
		#  - user wants to skip to the next subrun in a run series.
		#     Run control frontend posts us an EndSubrunEvent with
		#     no special attributes.
		#  - user wants to stop the subrun or run series.  StopDataAcquisition()
		#     method of this object passes us an EndSubrunEvent with
		#     "manual".

		# block from trying to shut down twice simultaneously
		if not self.can_shutdown:
			return
		self.can_shutdown = False

		self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " finalizing...")
		
		# we need to prevent the delivery of messages while we're shutting down.
		# after we're done, there won't be any subscriptions so it won't matter
		# if messages arrive after that.
		with self.messageHandlerLock:
			self.logger.debug("Stopping remote nodes...")
			if hasattr(evt, "processname") and evt.processname is not None:
				self.running = False
				header = evt.processname + " quit prematurely!"
				message = ["The essential process '" + evt.processname + "' died before the subrun was over.", "Running has been halted for troubleshooting."]
				wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="alarm", messageheader=header, messagebody=message))
		
			num_mtest_nodes = len(self.mtestBeamDAQNodes) if self.mtest_useBeamDAQ else 0
			numsteps = num_mtest_nodes + len(self.readoutNodes) + len(self.DAQthreads) + 1		# gotta stop all the beamline DAQ nodes, readout nodes, close the DAQ threads, and close the 'done' signal socket.
			step = 0
			
			# if the subrun is being stopped for some other reason than
			# all readout nodes exiting cleanly, then we need to make sure
			# they ARE stopped.
			if not hasattr(evt, "allclear") or not evt.allclear:
				success = True
				wait = False
				for node in self.readoutNodes:
					wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping " + node.name + " node...", progress=(step, numsteps)) )
					if not node.own_lock:
						node.completed = True
						continue
					try:
						success = success and node.daq_stop()
						wait = True
					except ReadoutNode.ReadoutNodeNoConnectionException:
						self.logger.warning("The %s node cannot be reached..." % node.name)
						success = False
					except ReadoutNode.ReadoutNodeNoDAQRunningException:		# raised if the DAQ is not running on the node.  not a big deal.
						node.completed = True
				
					wx.PostEvent( self.main_window, Events.UpdateNodeEvent(node=node.name, on=False) )
				
					step += 1
			
				if not success:
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="notice", messagebody=["Not all readout nodes could be stopped.",  "The next subrun could be problematic..."], messageheader="Not all nodes stopped") )

				# if we WERE able to reach all the nodes, then we should wait
				# until they've signalled that they have finished data taking.
				elif wait:
					self.can_shutdown = True
					return
		
			if self.mtest_useBeamDAQ:
				success = True
				for node in self.mtestBeamDAQNodes:
					success = success and node.daq_stop()
					step += 1
		
				if not success:
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="notice", messagebody=["The beamline DAQ node(s) couldn't be stopped.",  "The next subrun could be problematic..."], messageheader="Beamline DAQ node(s) not stopped") )
				else:
					mtestDAQ_stopped = True
			
			self.logger.debug("Sending 'stop' signal to ET threads...")		
			for threadname in self.DAQthreads:
				wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nSignalling ET threads...", progress=(step, numsteps)) )

				thread = self.DAQthreads[threadname]
				
				# the ET system process stops on its own.  just cut off its display feed.
				if threadname == "et system":
					thread.SetRelayOutput(False)

				# the event builder needs to know if it should expect a sentinel.
				elif threadname == "event builder":
					# only signal if there's no sentinel coming.
					# if there isn't, send the process a SIGTERM.
					if not hasattr(evt, "sentinel") or not evt.sentinel:
						try:
							thread.process.terminate()
						# the process might have crashed.
						except OSError:
							pass
					
					# either way, we stop displaying its output.
					thread.SetRelayOutput(False)
					
				# any other threads should be aborted.
				elif hasattr(thread, "Abort"):
					self.logger.info("Stopping thread '%s'..." % threadname)	
					thread.Abort()
			
				step += 1
			
			# remove the threads from the dictionary.
			# we don't need a handle on them any more.
			self.DAQthreads = {}
			
			self.logger.debug("Clearing the LI system...")
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nClearing the LI system...", progress=(step, numsteps)) )
			for node in self.readoutNodes:
				try:
					node.li_configure(li_level=MetaData.LILevels.ZERO_PE.hash)
				except ReadoutNode.ReadoutNodeNoConnectionException:
					self.logger.warning("Couldn't reach '%s' node to reset the LI box!", node.name)
				except ReadoutNode.ReadoutNodeUnexpectedDataException:
					self.logger.warning("Unexpected response from '%s' readout node.  Can't reset LI box...", node.name)
					
			step += 1
		
			self.logger.debug("Unsubscribing from listener...")
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping listeners...", progress=(step, numsteps)) )
			for node in self.readoutNodes:
				self.socketThread.UnsubscribeAll(node.id)
			self.socketThread.UnsubscribeAll("*")

			self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " finished.")

			# need to make sure all the tasks are marked "not yet completed" so that they are run for the next subrun
			for task in self.SubrunStartTasks:
				task["completed"] = False

			self.current_DAQ_thread = 0			# reset the thread counter in case there's another subrun in the series
			self.subrun += 1
		
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun completed.", progress=(numsteps, numsteps)) )
			wx.PostEvent( self.main_window, Events.SubrunOverEvent(run=self.run, subrun=self.first_subrun + self.subrun) )

			if self.running and self.subrun < len(self.runseries.Runs):
				self.logger.debug("Signalling that we're ready for next subrun...")
				wx.PostEvent(self, Events.ReadyForNextSubrunEvent())
			else:
				self.logger.debug("Signalling that all subruns in this run are finished...")
				# if this isn't a manual (user-initiated) stop,
				# then the sequence is different
				auto = not hasattr(evt, "manual") or not evt.manual
				wx.PostEvent(self, Events.StopRunningEvent(allclear=True, auto=auto))

		self.logger.debug("EndSubrun() finished.")
		

	##########################################
	# Helper methods used by StartNextSubrun()
	##########################################
	
	def RunInfoAndConnectionSetup(self):
		""" Configures the run and sets up connections to the readout nodes. """
		self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " begun.")
		
		self.can_shutdown = True		# from here on it makes sense to call the EndSubrun() method
		
		self.runinfo = self.runseries.Runs[self.subrun]
		wx.PostEvent(self.main_window, Events.UpdateSeriesEvent())

		# ET needs to use a rotating port number to avoid blockages.
		# unfortunately, there's no programmatic way to determine which
		# one in the set will be free.  (modding the subrun number by
		# the number of available ports would work if the subrun number
		# never reverted back to 1, ... but it does sometimes.)
		# so we just find one that will work by inspection.
		self.logger.info("Trying to find a port for use by ET.")
		self.runinfo.ETport = None
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		for port in range(Configuration.params["Socket setup"]["etPortBase"], Configuration.params["Socket setup"]["etPortBase"] + Configuration.params["Socket setup"]["numETports"]):
			try:
				self.logger.debug("  trying port %d...", port)
				s.bind( ("", port) )
			except socket.error as e:
				continue
			else:
				s.close()
				self.runinfo.ETport = port
				break
		
		if self.runinfo.ETport is None:
			wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="All of the ET server ports assigned to the DAQ are in use.  Either wait until they finish or kill some of them before continuing.", messageheader="No ET server ports available") )
			return False
			
		
		self.logger.info("  ... will use port %d as this subrun's ET port.", self.runinfo.ETport)

		ok = True
		for node in self.readoutNodes:
			on = node.ping()
			ok = ok and on
			node.configured = False
			node.completed = False
			node.shutting_down = False
			node.sent_sentinel = False
			wx.PostEvent( self.main_window, Events.UpdateNodeEvent(node=node.name, on=on) )
		
		for node in self.monitorNodes:
			node.ready = False
				
		if not ok:
			wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="Cannot make a connection to the readout node(s).  Running aborted.", messageheader="No connection to readout node(s)") )
			
			# need to stop the run startup sequence.
			return False
		
		# ok to proceed to next step
		return True
	
	def ReadoutNodeHWConfig(self):
		""" Initializes the hardware configuration on the readout nodes.
		    This process takes some time on the full detector, so this
		    method exits after starting the process.  When the SocketThread
		    receives the appropriate message from all readout nodes then
		    we will continue. """
		    
		self.logger.info("  Using hardware configuration: " + MetaData.HardwareConfigurations.description(self.runinfo.hwConfig))
		
		# if this subrun has a different HW config from the one before
		# (which includes the cases where this is the first subrun
		#  or it's the only subrun), then
		# we need to ask the slow control to set up the HW.
		# that is, unless this configuration is the "current
		# state" version, in which case the user doesn't want
		# to use any configuration file at all (so that custom
		# configurations via the slow control can be used for testing).
		self.logger.debug("  HW config check.")
		if self.runinfo.hwConfig != MetaData.HardwareConfigurations.NOFILE.hash and self.runinfo.hwConfig != self.last_HW_config:
			# NOTE: DON'T consolidate this loop together with the next one.
			# the subscriptions need to ALL be booked before any of the nodes
			# gets a "HW configure" command.  otherwise there will be race conditions.
			for node in self.readoutNodes:
				self.logger.info("  ==> Booking a subscription for 'HW ready' and 'HW error' messages from readout nodes...")
				for node in self.readoutNodes:
					self.socketThread.Subscribe(node.id, node.name, "hw_ready", callback=self, waiting=True, notice="Configuring HW...")
					self.socketThread.Subscribe(node.id, node.name, "hw_error", callback=self)
					self.logger.debug("    ... subscribed the %s node." % node.name)
			
			for node in self.readoutNodes:
				self.logger.info("   ==> Configuring the %s node..." % node.name)
				success = False
				tries = 0
				while not success and tries < Configuration.params["Readout nodes"]["SCHWwriteAttempts"]:
					try:
						success = node.sc_loadHWfile(self.runinfo.hwConfig)
					except ReadoutNode.ReadoutNodeNoConnectionException:
						self.logger.info("    ... no connection.")
						if tries < Configuration.params["Readout nodes"]["SCHWwriteAttempts"]:
							self.logger.info("   ... will make another attempt in %ds." % Configuration.params["Socket setup"]["connAttemptInterval"])
						success = False
					tries += 1
					time.sleep(Configuration.params["Socket setup"]["connAttemptInterval"])
					
				if not success:
#					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm") )
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="Could not configure the hardware for the " + node.name + " readout node.  This subrun will be stopped.", messageheader="Hardware configuration problem") )
					self.logger.error("Could not set the hardware for the " + node.name + " readout node.  This subrun will be aborted.")
					# make sure we try to load hardware next time
					self.last_HW_config = None
					
					# need to stop the run startup sequence.
					return False
			
			# record what we did so that the next time we don't have to do it again.
			self.last_HW_config = self.runinfo.hwConfig
		else:
			self.logger.info("   ==> No HW configuration necessary.")
			return True
		
		# need to wait on HW init (it can take a while).  don't proceed to next step yet.
		return None
		
	def LIBoxSetup(self):
		""" Configures the light injection box, if needed. """
		# set up the LI box to do what it's supposed to, if it needs to be on.
		if self.runinfo.runMode == MetaData.RunningModes.LI or self.runinfo.runMode == MetaData.RunningModes.MIXED_NUMI_LI:
			self.logger.info("  Setting up LI:")
			
			for node in self.readoutNodes:
				if not node.li_configure(li_level=self.runinfo.ledLevel, led_groups=self.runinfo.ledGroup):
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="The LI box on node '%s' cannot be configured.  Check the settings and the serial connection." % node.name, messageheader="Error configuring LI box") )
					self.logger.error("  LI Box on '%s' node cannot be configured...", node.name)
					return False

			self.logger.info("     Configured for LED groups: %s", MetaData.LEDGroups.description(self.runinfo.ledGroup))
		
			
					
		# ok to proceed to next step
		return True
	
	def ReadoutNodeHVCheck(self):
		"""
		Checks if the HV deviations from setpoint and
		HV periods are acceptable.
		If not, control is passed to a window that asks
		the user for input.
		"""
		# first cancel the 'HW ready/error' subscriptions.  if we got this far, we've received them all.
		for node in self.readoutNodes:
			self.socketThread.Unsubscribe(node.id, node.name, "hw_ready", self)
			self.socketThread.Unsubscribe(node.id, node.name, "hw_error", self)
		
		# we don't need to do the check unless this subrun is the first one of its type
		if self.subrun == 0 or len(self.runseries.Runs) == 1 or self.runinfo.hwConfig != self.runseries.Runs[self.subrun - 1].hwConfig:
			thresholds = sorted(Configuration.params["Readout nodes"]["SCHVthresholds"].keys(), reverse=True)
			over = {}
			needs_intervention = False
			for node in self.readoutNodes:
				board_statuses = node.sc_readBoards()

				# this method returns 0 if there are no boards to read
				if board_statuses == 0:
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="notice", messagebody=["The " + node.name + " node is reporting that it has no FEBs attached.",  "Your data will appear suspiciously empty..."], messageheader="No boards attached to " + node.name + " node") )
					self.logger.warning(node.name + " node reports that it has no FEBs...")
					continue	# it's still ok to go on, but user should know what's happening
				elif board_statuses is None:
#					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm") )
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="The " + node.name + " node says it can't read the FEBs.  This subrun will be stopped.", messageheader="Can't read FEBs on " + node.name + " node") )
					self.logger.warning(node.name + " node reports that can't read its FEBs.  See its log.")
					return False
			
				for board in board_statuses:
					dev = abs(int(board["hv_dev"]))
					period = int(board["hv_period"])
				
					for threshold in thresholds:
						if dev > threshold:
							if threshold in over:
								over[threshold] += 1
							else:
								over[threshold] = 1
						
							if over[threshold] > Configuration.params["Readout nodes"]["SCHVthresholds"][threshold]:
								needs_intervention = True
								break
						
					if period < Configuration.params["Readout nodes"]["SCperiodThreshold"]:
						needs_intervention = True
						break

			# does the user need to look at it?
			# if so, send control back to the main thread.
			if needs_intervention:
				wx.PostEvent(self.main_window, Events.NeedUserHVCheckEvent(daqmgr=self))
				return None
	
		# ok to proceed to next step
		return True

	##########################################
	# Subprocess starters
	##########################################

	def StartNextThread(self, signum=None, sigframe=None):
		""" Starts the next thread in the sequence.
		    This method should ONLY be called
		    as the signal handler for SIGCONT
		    (otherwise race conditions will result)! """
		self.logger.debug("StartNextThread called.  Current DAQ thread: %d/%d", self.current_DAQ_thread, len(self.DAQStartTasks))
		if self.current_DAQ_thread < len(self.DAQStartTasks):
			self.logger.debug("Going to start method: %s", self.DAQStartTasks[self.current_DAQ_thread]["method"])
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent( text="Setting up run:\n" + self.DAQStartTasks[self.current_DAQ_thread]["message"], progress=(self.startup_step, self.num_startup_steps) ) )
			self.DAQStartTasks[self.current_DAQ_thread]["method"]()
			self.current_DAQ_thread += 1
			self.startup_step += 1
		else:
			signal.signal(signal.SIGUSR1, signal.SIG_IGN)		# go back to ignoring the signal...
			print "Note: requested a new thread but no more threads to start..."

	def StartETSys(self):
		""" Start the et_system process. """
		events = self.runinfo.gates * Configuration.params["Hardware"]["eventFrames"] * self.febs

		etSysFrame = Frames.OutputFrame(None, "ET system", window_size=(600,200), window_pos=(610,0))
		etSysFrame.Show(True)

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", events, Configuration.params["Hardware"]["frameSize"], os.getpid(), self.runinfo.ETport)

#		print etsys_command

		self.windows.append( etSysFrame )
		self.UpdateWindowCount()
		self.DAQthreads["et system"] = Threads.DAQthread(etsys_command, "ET system", output_window=etSysFrame, owner_process=self, env=self.environment, is_essential_service=True)

	def StartETMon(self):
		""" Start the ET monitor process.
		
		    Not strictly necessary for data aquisition, but
		    is sometimes helpful for troubleshooting. """
		    
		etMonFrame = Frames.OutputFrame(None, "ET monitor", window_size=(600,600), window_pos=(610,225))
		etMonFrame.Show(True)
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", os.getpid(), self.runinfo.ETport)
		self.windows.append( etMonFrame )
		self.UpdateWindowCount()
		self.DAQthreads["et monitor"] = Threads.DAQthread(etmon_command, "ET monitor", output_window=etMonFrame, owner_process=self, env=self.environment)

	def StartEBSvc(self):
		""" Start the event builder service.
		
		    (This does the work of stitching together the frames from the readout nodes.) """
		    
		ebSvcFrame = Frames.OutputFrame(None, "Event builder service", window_size=(600,200), window_pos=(0,700))
		ebSvcFrame.Show(True)

		eb_command = '%s/bin/event_builder %s/%s %s/%s %d %d' % (self.environment['DAQROOT'], self.etSystemFileLocation, self.ET_filename + "_RawData", self.rawdataLocation, self.raw_data_filename, self.runinfo.ETport, os.getpid())

		self.windows.append( ebSvcFrame )
		self.UpdateWindowCount()
		self.DAQthreads["event builder"] = Threads.DAQthread(eb_command, "event builder", output_window=ebSvcFrame, owner_process=self, env=self.environment, is_essential_service=True)
		
	def StartOM(self):
		""" Start the online monitoring services on the OM node.
		
		    This needs to be done BEFORE the DAQ is started on the
		    readout nodes because otherwise there is a race condition
		    between the startup of the event builder on the OM node
		    and the startup of the DAQ -- and if the DAQ starts up first,
		    the EB on the OM node might miss some of the frames from
		    the first event. """
		
		# if no monitoring nodes, just go on to the next step
		# by emitting the correct signal
		if len(self.monitorNodes) == 0:
			os.kill(os.getpid(), signal.SIGUSR1)
			return
		
		self.logger.debug("Booking subscription(s) for 'OM ready' messages from online monitoring nodes...")
		for node in self.monitorNodes:
			self.socketThread.Subscribe(node.id, node.name, "om_ready", callback=self, notice="Initializing online monitoring...")
			self.logger.debug("    ... subscribed the %s node." % node.name)
		
		# the ET system is all set up, so the online monitoring nodes
		# can be told to connect.
		for node in self.monitorNodes:
			try:
				node.om_start(self.ET_filename, self.runinfo.ETport)
			except:
				self.logger.exception("Online monitoring couldn't be started on node '%s'!", node.name)
				wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="error", messagebody=["The online monitoring system couldn't be started!"], messageheader="Couldn't start the online monitoring system!  The run has been halted.  Check the dispatcher on the '%s' online monitoring node." % node.name) )
				self.StopDataAcquisition()

	def StartRemoteServices(self):
		""" Notify all the remote services that we're ready to go.
		    Currently this includes the DAQs on the MTest beamline
		    node (if configured) and the readout node(s). """
		    
		if self.mtest_useBeamDAQ:
			for node in self.mtestBeamDAQNodes:
				try:
					node.daq_start(self.mtest_branch, self.mtest_crate, self.mtest_controller_type, self.mtest_mem_slot, self.mtest_gate_slot, self.mtest_adc_slot, self.mtest_tdc_slot, self.mtest_tof_rst_gate_slot, self.mtest_wc_rst_gate_slot, self.runinfo.gates, self.ET_filename, self.run, self.first_subrun + self.subrun, self.runinfo.runMode)
				except:
					self.logger.exception("Couldn't start MTest beamline DAQ!  Aborting run.")
					wx.PostEvent(self.main_window, Events.AlertEvent(alerttype="alarm", messageheader="Couldn't start beamline DAQ", messagebody=["Couldn't start the beamline DAQ.",  "Run has been aborted (see the log for more details)."]) )
					self.StopDataAcquisition()
				

		# DON'T consolidate this loop together with the next one.
		# ALL the subscriptions need to be booked before *any* of
		# the readout nodes is told to start (in case there's a problem
		# and it returns immediately).		    
		self.logger.info("  Booking subscriptions for 'DAQ finished' messages from readout nodes...")
		for node in self.readoutNodes:
			self.socketThread.Subscribe(node.id, node.name, "daq_finished", callback=self)
			self.logger.info("    ... subscribed the %s node." % node.name)
			
		self.last_logged_gate = 0
		self.logger.info("  Booking subscription for gate count messages from readout nodes...")
		self.socketThread.Subscribe("*", "*", "gate_count", callback=self)
		self.logger.info("    ... done.")

		# we use a lock to block message reading until all nodes have been initially contacted.
		# this will ensure that even if one readout node dies right away, things still happen
		# in the proper sequence.
		# the 'with' statement ensures that the lock is always released when this block is exited,
		# even if there's an uncaught exception.
		with self.messageHandlerLock:
			for node in self.readoutNodes:
				errmsg = None
				errtitle = None

				try:
					# for non-LI run modes, these values are irrelevant, so we set them to some well-defined defaults.
					if not (self.runinfo.runMode in (MetaData.RunningModes.LI.hash, MetaData.RunningModes.MIXED_NUMI_LI.hash)):
						self.runinfo.ledLevel = MetaData.LILevels.ZERO_PE.hash
						self.runinfo.ledGroup = MetaData.LEDGroups.ABCD.hash

	#				print self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup
					
					success = node.daq_start(self.ET_filename, self.runinfo.ETport, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
				
					self.logger.info("Started DAQ on %s node (address: %s)" % (node.name, node.address))
				except ReadoutNode.ReadoutNodeException:
					wx.PostEvent(self.main_window, Events.AlertMessage(alerttype="notice", messagebody=["Somehow the DAQ service on the " + node.name + " node has not yet stopped.",  "Stopping now -- but be on the lookout for weird behavior."], messageheader=node.name.capitalize() + " DAQ service not yet stopped") )

					stop_success = node.daq_stop()
					if stop_success:
						success = node.daq_start(self.ET_filename, self.runinfo.ETport, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
					else:
						errmsg = "Couldn't stop the " + node.name +" DAQ service.  Aborting run."
						errtitle =  title=node.name.capitalize() + " DAQ service couldn't be stopped"
						success = False
				except ReadoutNode.ReadoutNodeNoConnectionException:
					errmsg = "The connection to the " + node.name + " node couldn't be established!  Run will be aborted."
					errtitle = "No connection to the " + node.name + " node"
					success = False
	
				if not success:
					header = errtitle if errtitle is not None else node.name.capitalize() + " DAQ service couldn't be started"
					body = errmsg if errmsg is not None else "Couldn't start the " + node.name + " DAQ service.  Aborting run."
					wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messageheader=header, messagebody=body) )
#					wx.PostEvent(self.main_window, Events.ErrorMsgEvent(title=errtitle, text=errmsg) )
				
					self.StopDataAcquisition()
					break
				else:
					wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
		##end## with self.messageHandlerLock
	
		if self.running:
			self.logger.info("  All DAQ services started.  Data acquisition for subrun %d underway." % (self.subrun + self.first_subrun) )
		
	def StartTestProcess(self):
		frame = Frames.OutputFrame(self.main_window, "test process", window_size=(600,600), window_pos=(1200,200))
		frame.Show(True)

		command = "/home/jeremy/code/mnvruncontrol/scripts/test.sh"

		self.windows.append(frame)
		self.UpdateWindowCount()
		self.DAQthreads["test process"] = Threads.DAQthread(command, "test process", output_window=frame, owner_process=self, next_thread_delay=3, is_essential_service=True)
		

	##########################################
	# Utilities, event handlers, etc.
	##########################################

	def CloseWindows(self):
		""" Close any windows owned by ET/DAQ processes. """
		while len(self.windows) > 0:		
			window = self.windows.pop()
			
			if window:		# wx guarantees that 'dead' windows will evaluate to False
				window.Destroy()
				
		self.UpdateWindowCount()
		
	def UpdateWindowCount(self):
		for window in self.windows:
			if not(window):
				window.pop()
		
		wx.PostEvent( self.main_window, Events.UpdateWindowCountEvent(count=len(self.windows)) )

	def HandleSocketMessage(self, evt):
		""" Decides what to do with messages received from remote nodes. """
				
		# need a lock to prevent race conditions (for example, a second node sending a "daq_finished" event
		# while the "daq_finished" event for a previous node is still being processed)
		self.logger.log(5, "Acquiring message handler lock...")
		self.messageHandlerLock.acquire()
		self.logger.log(5, "Successfully acquired message handler lock.")
		
		# if it's a gate count, send the appropriate event to the front end.
		if evt.message == "gate_count":
			gate_count = int(evt.data)
			
			# we can't rely on getting a notice for every single gate
			# (MTest in particular reads out too fast for that).
			# so we use the integer division (//) construction below.
			stride = Configuration.params["Master node"]["logfileGateCount"]
			if gate_count // stride > self.last_logged_gate // stride:
				self.logger.info("  DAQ has reached gate %d..." % gate_count)
				self.last_logged_gate = gate_count
				
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Running...\nGate %d/%d" % (gate_count, self.runinfo.gates), progress=(gate_count, self.runinfo.gates)) )
			
		# if the OM nodes are ready, then we can proceed to the next step
		elif evt.message == "om_ready":
			self.logger.info("OM node '%s' reports that it is ready.", evt.sender)
			all_configured = True
			for node in self.monitorNodes:
				if node.name == evt.sender:
					node.ready = True
				elif not node.ready:
					all_configured = False
			
			# start up the next step ...
			if all_configured:
				self.StartNextThread()
			
		# if it's a HW error message, we need to abort the subrun.
		elif evt.message == "hw_error":	
			# make sure we try to load hardware next time
			self.last_HW_config = None

			self.logger.error("The " + evt.sender + " readout node reports a hardware error.")
			if self.running:
				wx.PostEvent( self.main_window, Events.AlertEvent(alerttype="alarm", messagebody="There was a hardware error while configuring the " + evt.sender + " readout node.  Subrun stopped.", messageheader="Hardware configuration problem") )
				self.logger.error("This subrun will be aborted.")
			
				self.logger.warning("Subrun " + str(self.first_subrun + self.subrun) + " aborted.")
			
				self.logger.info("Cancelling any message subscriptions in preparation for early shutdown...")
				for node in self.readoutNodes:
					self.socketThread.UnsubscribeAll(node.id)
				
				# if there's more than one HW error, we don't want to
				# go through the shutdown sequence more than once.
				self.running = False
			
				wx.PostEvent(self, Events.StopRunningEvent(allclear=True))

		# if it's a HW ready message, then we should see if all the other nodes are ready too
		elif evt.message == "hw_ready":
			allconfigured = True
			for node in self.readoutNodes:
				# first set the node we've been notified about to "configured."
				if node.name == evt.sender:
					self.logger.debug("    ==> %s node reports it's ready." % node.name)
					node.configured = True
				# now, check if any other ones are still unconfigured.
				elif not node.configured:
					allconfigured = False

			# if everybody's configured, we're ready to move on to the next step.
			if allconfigured:
				self.logger.info("    ==> all nodes ready.")
				wx.PostEvent(self, Events.ReadyForNextSubrunEvent())

		# if it's a DAQ finished message, we need to make sure all the nodes stop
		# and then do the subrun shutdown stuff.
		elif evt.message == "daq_finished":
			alldone = True
			haveSentinel = False

			matches = re.match("sentinel=(?P<status>YES|NO)", evt.data)
			try:
				sentinelStatus = matches.group("status") == "YES"
			except IndexError:		# thrown when there is no such group
				sentinelStatus = False
				
			for node in self.readoutNodes:
				# first set the node we've been notified about to "done."
				if node.name == evt.sender:
					sentSentinel = "DID" if sentinelStatus else "DID NOT"
					self.logger.debug("    ==> %s node reports it's done taking data and %s send a sentinel." % (node.name, sentSentinel))
					node.completed = True
					node.shutting_down = False
					node.sent_sentinel = sentinelStatus
					
					self.socketThread.Unsubscribe(node.id, node.name, "daq_finished", self)
					
				else:
					alldone = alldone and node.completed
					
				# either way, we need to know if a sentinel frame was sent.
				haveSentinel = haveSentinel or node.sent_sentinel

					
					
				# we DON'T force the other nodes to shut down because
				# the nodes depend on each other for gate synchronization
				# (when there are more than one).  therefore they SHOULD
				# all shut down when the first one goes down anyway.
				#
				# this can of course be re-implemented if necessary, but
				# it suffers from a synchronization problem that will need
				# to be addressed:
				#    this method needs to use a lock to make sure it
				#    doesn't try to process two messages simultaneously
				#    and interfere with itself.  however, usually the
				#    second node to finish finishes (and sends its message)
				#    while the message from the first node is still being
				#    processed.  that means that the daq_stop() command in
				#    the implementation below is issued AFTER the node has
				#    already finished -- and so we SHOULD wait for that signal
				#    to arrive (which would mean one more call of this method)
				#    rather than stopping it via daq_stop() (since it's already
				#    stopped anyway).
				#
				# another question is whether waiting on the remote nodes
				# is the right method for deciding whether a subrun is done
				# altogether.  if communication is too fast, we might stop
				# the event builder before it has completely assembled the
				# last gate ...
				

#				# now, check if any other ones are still running.
#				elif not node.completed:
#					# makes sure that if this is an abnormal shutdown,
#					# all the other nodes are shut down too.
#					if not node.daq_checkStatus():
#						
#					
#					if not node.shutting_down:
#						try:
#							success = node.daq_stop()
#						
#							if not success:
#								wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="Couldn't stop the %s node.  The dispatcher on that node will probably need to be restarted and any leftover DAQ processes killed." % node.name, title="Couldn't stop %s DAQ" % node.name) )
#								self.logger.error("Couldn't stop the DAQ on the %s node!")
#						
#								# we mark this one as shut down because otherwise we'll never stop!
#								# however, we DON'T set alldone to False here because this node is effectively "done" now.
#								node.completed = True
#								node.shutting_down = False
#							# if we successfully got through to the node to tell it to stop,
#							# we'll need to wait on it to give us the right signal.
#							# that will mean this method will be called again ==> not done.
#							else:
#								alldone = False
#						except ReadoutNode.ReadoutNodeNoDAQRunningException:			# if it's already closed, then it's no problem.  (see above.)
#							node.completed = True
#					else:
#						alldone = False
				
#				if node.completed:
#					print "%s node is done." % node.name
#				else:
#					print "%s node is not done yet." % node.name
#				
#				print "alldone? %d" % alldone
				
			if alldone:
				# all DAQs have been closed cleanly.
				# the subrun needs to end then.
				# we pass 'allclear = True' to signify this.
				self.logger.info("All nodes finished.  Sentinel status: %s" % str(haveSentinel))
				wx.PostEvent(self, Events.EndSubrunEvent(allclear=True, sentinel=haveSentinel))

		else:
			self.logger.debug("Got a message I don't know how to handle (subject: '%s').  Ignoring.", evt.message)
			

		self.messageHandlerLock.release()
		self.logger.log(5, "Released message handler lock.")

	def RelayProgressToDisplay(self, evt):
		""" Pass along an 'update progress' event (usu. from the SocketThread) to the main run control. """
		# just pass the event along (so long as we're running).
		if self.running:
			wx.PostEvent(self.main_window, evt)
