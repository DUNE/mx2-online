"""
  DataAcquisitionManager.py:
  Infrastructural objects to manage a data acquisition run.
  Used by the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

import wx
import os
import signal
import errno
import datetime
import time
import threading
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
from mnvruncontrol.backend import ReadoutNode
from mnvruncontrol.backend import RemoteNode
from mnvruncontrol.backend import Threads
from mnvruncontrol.frontend import Frames

class DataAcquisitionManager(wx.EvtHandler):
	def __init__(self, main_window):
		wx.EvtHandler.__init__(self)

		self.main_window = main_window
		
		# threads that this object will be managing.
		self.DAQthreads = []
		self.DAQthreadWatcher = None
		self.timerThreads = []

		# methods that will be started sequentially
		# by various processes and accompanying messages
		self.SubrunStartTasks = [ { "method": self.ETCleanup,                 "message": "Cleaning up any prior ET processes..." },
		                          { "method": self.RunInfoAndConnectionSetup, "message": "Testing connections" },
		                          { "method": self.LIBoxSetup,                "message": "Initializing light injection..." },
		                          { "method": self.ReadoutNodeHWConfig,       "message": "Loading hardware..." },
		                          { "method": self.ReadoutNodeHVCheck,        "message": "Checking hardware..." } ]
		self.DAQStartTasks = [ { "method": self.StartETSys,          "message": "Starting ET system..." },
		                       { "method": self.StartETMon,          "message": "Starting ET monitor..." },
		                       { "method": self.StartEBSvc,          "message": "Starting event builder..." },
		                       { "method": self.StartRemoteServices, "message": "Starting remote services..."} ]


		# counters
		self.current_DAQ_thread = 0			# the next thread to start
		self.subrun = 0					# the next run in the series to start
		self.windows = []					# child windows opened by the process.
		
		self.LIBox = None					# this will be set in StartDataAcquisition
		self.readoutNodes = None				# will be set in RunControl.GetConfig()
		self.monitorNodes = None				# ditto.

		# configuration stuff
		self.etSystemFileLocation = Configuration.params["Front end"]["etSystemFileLocation"]
		self.rawdataLocation      = Configuration.params["Front end"]["master_rawdataLocation"]

		# logging facilities
		self.logger = logging.getLogger("rc_dispatcher")
		self.logger.setLevel(logging.DEBUG)
		self.filehandler = logging.handlers.RotatingFileHandler(Configuration.params["Front end"]["master_logfileName"], maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.DEBUG)
		self.formatter = logging.Formatter("[%(asctime)s] %(levelname)s:  %(message)s")
		self.filehandler.setFormatter(self.formatter)
		self.logger.addHandler(self.filehandler)

		# these will need to be set by the run control window before the process is started.
		# that way we can be sure it's properly configured.
		self.runseries = None
		self.detector = None
		self.run = None
		self.first_subrun = None
		self.febs = None
		
		self.running = False
		self.can_shutdown = False		# used in between subruns to prevent shutting down twice for different reasons

		try:
			self.socketThread = Threads.SocketThread(self.logger)
		except Threads.SocketAlreadyBoundException:
			wx.PostEvent(self.main_window, Events.ErrorMsgEvent(text="Can't bind a local listening socket.  Synchronization between readout nodes and the run control will be impossible.  Check that there isn't another run control process running on this machine.", title="Can't bind local socket") )
			
		self.logger.info("Started master node listener on port %d." % Configuration.params["Socket setup"]["masterPort"])
		self.messageHandlerLock = threading.Lock()

		self.Bind(Events.EVT_SOCKET_RECEIPT, self.HandleSocketMessage)
		self.Bind(Events.EVT_UPDATE_PROGRESS, self.RelayProgressToDisplay)

		self.Bind(Events.EVT_READY_FOR_NEXT_SUBRUN, self.StartNextSubrun)
		self.Bind(Events.EVT_THREAD_READY, self.StartNextThread)
		self.Bind(Events.EVT_END_SUBRUN, self.EndSubrun)		# if the DAQ process quits, this subrun is over
		self.Bind(Events.EVT_STOP_RUNNING, self.StopDataAcquisition)
		
	def Cleanup(self):
		self.socketThread.Abort()
		self.socketThread.join()
		
	##########################################
	# Global starters and stoppers
	##########################################
	
	def StartDataAcquisition(self, evt=None):
		if not isinstance(self.runseries, RunSeries.RunSeries):
			raise ValueError("No run series defined!")

		if self.detector == None or self.run == None or self.first_subrun == None or self.febs == None:
			raise ValueError("Run series is improperly configured.")

		self.LIBox = LIBox.LIBox(disable_LI=not(Configuration.params["Hardware"]["LIBoxEnabled"]), wait_response=Configuration.params["Hardware"]["LIBoxWaitForResponse"])
		
		# try to get a lock on each of the readout nodes.
		failed_connection = None
		for node in self.readoutNodes:
			if node.get_lock():
				wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
			else:
				failed_connection = node.name
				break
		
		if failed_connection:
			wx.PostEvent(self.main_window, Events.ErrorMsgEvent(text="Cannot get control of dispatcher on the " + failed_connection + " readout node.  Check to make sure that the readout dispatcher is started on that machine and that there are no other run control processes connected to it.", title="No lock on " + failed_connection + " readout node") )
			return
			
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
		self.running = False
		self.subrun = 0

		self.logger.info("Stopping data acquisition sequence...")

		# this method can be initiated either from the main GUI
		# or by EndSubrun() on the last subrun of the series.
		# in the latter case, the event contains an attribute
		# 'allclear', which signifies that we don't need to
		# do any more checking on the readout nodes.
		if not( evt is not None and hasattr(evt, "allclear") ):
			# the run will need a manual stop if the readout nodes can't be properly contacted.
			needsManualStop = False
			for node in self.readoutNodes:
				try:
					success = node.daq_stop()
				except ReadoutNode.ReadoutNodeNoDAQRunningException, ReadoutNode.ReadoutNodeNoConnectionException:		# the DAQ has already quit or is unreachable
					needsManualStop = True				# if so, we'll never get the "DAQ quit" event from the SocketThread.
			if needsManualStop:
				wx.PostEvent(self, Events.EndSubrunEvent())
		for node in self.readoutNodes:
			node.release_lock()										

		wx.PostEvent(self.main_window, Events.StopRunningEvent())		# tell the main window that we're done here.


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
	
		quitting = False
		self.CloseWindows()			# don't want leftover windows open.

		# if the event contains a list of PIDs that have finished, then
		# this signal is coming from the thread watcher.
		# clear out the corresponding elements in the list.
		if hasattr(evt, "pids_cleared"):
			for pid in evt.pids_cleared:
				self.DAQthreads.remove(pid)
		
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
		self.ET_filename = '%s_%08d_%04d_%s_v05_%02d%02d%02d%02d%02d' % (MetaData.DetectorTypes[self.detector, MetaData.CODE], self.run, self.first_subrun + self.subrun, MetaData.RunningModes[self.runinfo.runMode, MetaData.CODE], now.year % 100, now.month, now.day, now.hour, now.minute)
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
		    This method should only be called as the event handler
		    for the EndSubrunEvent. """

		if not self.can_shutdown:
			return

		self.can_shutdown = False

		self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " finalizing...")
		
		if hasattr(evt, "processname") and evt.processname is not None:
			if len(self.runseries.Runs) > 1:
				dialog = wx.MessageDialog(None, "The essential process '" + evt.processname + "' died.  This subrun will be need to be terminated.  Do you want to continue with the rest of the run series?  (Selecting 'no' will stop the run series and return you to the idle state.)", evt.processname + " quit prematurely",   wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
				self.running = self.running and (dialog.ShowModal() == wx.ID_YES)
			else:			
				wx.PostEvent(self.main_window, Events.ErrorMsgEvent(title=evt.processname + " quit prematurely", text="The essential process '" + evt.processname + "' died before the subrun was over.  The subrun will be need to be terminated.") )
				self.running = False
			
		numsteps = len(self.readoutNodes) + len(self.DAQthreads) + 2		# gotta stop all the readout nodes, close the DAQ threads, clear the LI system, and close the 'done' signal socket.
		step = 0
			
		# if the subrun is being stopped for some other reason than
		# all readout nodes exiting cleanly, then we need to make sure
		# they ARE stopped.
		if not hasattr(evt, "allclear") or not evt.allclear:
			success = True
			for node in self.readoutNodes:
				wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping " + node.name + " node...", progress=(step, numsteps)) )
				try:
					success = success and node.daq_stop()
				except ReadoutNode.ReadoutNodeNoConnectionException:
					success = False
				except ReadoutNode.ReadoutNodeNoDAQRunningException:		# raised if the DAQ is not running on the node.  not a big deal.
					pass
				
				wx.PostEvent( self.main_window, Events.UpdateNodeEvent(node=node.name, on=False) )
				
				step += 1
			
			if not success:
				wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="Not all nodes could be stopped.  The next subrun could be problematic...", title="Not all nodes stopped") )
		
		for thread in self.DAQthreads:		# we leave these in the array so that they can completely terminate.  they'll be removed in StartNextSubrun() if necessary.
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping ET threads...", progress=(step, numsteps)) )

			# we might have clicked the 'stop' button while the DAQthreadWatcher is watching these threads,
			# in which case the list only contains a list of PIDs as placeholders.
			# in that case, we need to abort the DAQthreadWatcher instead.
			if hasattr(thread, "Abort"):		
				thread.Abort()
			else:
				self.DAQthreadWatcher.Abort()
			
			step += 1
			
		while len(self.timerThreads) > 0:
			thread = self.timerThreads.pop()	# the countdown timers would start more threads.  get rid of them.
			thread.Abort()

#		print self.first_subrun, self.subrun

		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nClearing the LI system...", progress=(step, numsteps)) )

		try:
			self.LIBox.reset()					# don't want the LI box going unless it needs to be.
		except LIBox.LIBoxException:				# ... but maybe there isn't one connected, or it's not on.  that's ok.
			pass
		finally:
			step += 1
		
		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping listeners...", progress=(step, numsteps)) )
		for node in self.readoutNodes:
			self.socketThread.UnsubscribeAll(node.id)

		self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " finished.")

		# need to make sure all the tasks are marked "not yet completed" so that they are run for the next subrun
		for task in self.SubrunStartTasks:
			task["completed"] = False

		self.current_DAQ_thread = 0			# reset the thread counter in case there's another subrun in the series
		self.subrun += 1
		
		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun completed.", progress=(numsteps, numsteps)) )
		wx.PostEvent( self.main_window, Events.SubrunOverEvent(run=self.run, subrun=self.first_subrun + self.subrun) )

		if self.running and self.subrun < len(self.runseries.Runs):
			wx.PostEvent(self, Events.ReadyForNextSubrunEvent())
		else:
			self.logger.info("Data acquisition finished.")
			wx.PostEvent(self, Events.StopRunningEvent(allclear=True))
		

	##########################################
	# Helper methods used by StartNextSubrun()
	##########################################
	
	def ETCleanup(self):
		# ET & the DAQ shouldn't be running in two separate sets of processes.
		# therefore, we need to make sure we let them completely close
		# before we actually start the next subrun.  however, we can't wait
		# on them in StartNextSubrun(), because it runs as part of the main thread,
		# and if we did, the whole program would appear to lock up: since wx also
		# runs in the main thread, the graphical interface wouldn't be updated.
		# instead, we spawn a separate thread to watch these processes and
		# issue the ReadyForNextSubrun event to the DataAcquisitionManager
		# when they are done.
		
		if len(self.DAQthreads) > 0:
			if self.DAQthreadWatcher is None or not self.DAQthreadWatcher.is_alive():
				self.DAQthreadWatcher = Threads.DAQWatcherThread(self)

				# transfer all the thread references to the DAQthreadWatcher
				# to prevent race conditions.  replace them with PIDs in the
				# DataAcquisitionManager's list as placeholders.
				pids = []
				while len(self.DAQthreads) > 0:
					tmp = self.DAQthreads.pop()
					self.DAQthreadWatcher.threadsToWatch.append(tmp)
					pids.append(tmp.pid)
				self.DAQthreads = pids

				# now watch them.
				self.DAQthreadWatcher.start()

			# we can't do anything more until they're done,
			# so signal to StartNextSubrun() to exit immediately (no cleanup).
			return None
		
		# it's safe to go on to the next step 
		return True
	
	def RunInfoAndConnectionSetup(self):
		self.logger.info("Subrun " + str(self.first_subrun + self.subrun) + " begun.")
		
		self.can_shutdown = True		# from here on it makes sense to call the EndSubrun() method
		
		self.runinfo = self.runseries.Runs[self.subrun]
		wx.PostEvent(self.main_window, Events.UpdateSeriesEvent())

		# ET needs to use a rotating port number to avoid blockages.
		self.runinfo.ETport = Configuration.params["Socket setup"]["etPortBase"] + (self.first_subrun + self.subrun) % Configuration.params["Socket setup"]["numETports"]		
		self.logger.info("  ET port for this subrun: " + str(self.runinfo.ETport))

		ok = True
		for node in self.readoutNodes:
			on = node.ping()
			ok = ok and on
			node.configured = False
			node.completed = False
			node.shutting_down = False
			wx.PostEvent( self.main_window, Events.UpdateNodeEvent(node=node.name, on=on) )
				
		if not ok:
			wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="Cannot make a connection to the readout node(s).  Running aborted.", title="No connection to readout node(s)") )
			
			# need to stop the run startup sequence.
			return False
		
		# ok to proceed to next step
		return True
	
	def ReadoutNodeHWConfig(self):
		self.logger.info("  Using hardware configuration: " + self.runinfo.hwConfig)
		
		# if this is the first subrun, it's the only subrun,
		# or it has a different HW config from the one before,
		# we need to ask the slow control to set up the HW.
		# that is, unless this configuration is the "current
		# state" version, in which case the user doesn't want
		# to use any configuration file at all (so that custom
		# configurations via the slow control can be used for testing).
		self.logger.debug("  HW config check.")
		if self.runinfo.hwConfig != MetaData.HardwareConfigurations["Current state"] and (self.subrun == 0 or len(self.runseries.Runs) == 1 or self.runinfo.hwConfig != self.runseries.Runs[self.subrun - 1].hwConfig):
			# NOTE: DON'T consolidate this loop together with the next one.
			# the subscriptions need to ALL be booked before any of the nodes
			# gets a "HW configure" command.  otherwise there will be race conditions.
			for node in self.readoutNodes:
				self.logger.info("  Booking a subscription for 'HW ready' and 'HW error' messages from readout nodes...")
				for node in self.readoutNodes:
					self.socketThread.Subscribe(node.id, node.name, "hw_ready", callback=self, waiting=True, notice="Configuring HW...")
					self.socketThread.Subscribe(node.id, node.name, "hw_error", callback=self)
					self.logger.debug("    ... subscribed the %s node." % node.name)
			
			for node in self.readoutNodes:
				self.logger.info("  Configuring the %s node..." % node.name)
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
					wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="Could not configure the hardware for the " + node.name + " readout node.  This subrun will be stopped.", title="Hardware configuration problem") )
					self.logger.error("Could not set the hardware for the " + node.name + " readout node.  This subrun will be aborted.")
					# need to stop the run startup sequence.
					return False
		else:
			self.logger.info("No HW configuration necessary.")
			return True
		
		# need to wait on HW init (it can take a while).  don't proceed to next step yet.
		return None
		
	def LIBoxSetup(self):
		# set up the LI box to do what it's supposed to, if it needs to be on.
		if self.runinfo.runMode == MetaData.RunningModes.hash("Light injection") or self.runinfo.runMode == MetaData.RunningModes.hash("Mixed beam/LI"):
			self.logger.info("  Setting up LI:")
			self.LIBox.LED_groups = MetaData.LEDGroups[self.runinfo.ledGroup]
			self.logger.info("     Configured for LED groups: " + MetaData.LEDGroups[self.runinfo.ledGroup])
		
			need_LI = True
			if self.runinfo.ledLevel == MetaData.LILevels["One PE"]:
				self.LIBox.pulse_height = Defaults.LI_ONE_PE_VOLTAGE					
			elif self.runinfo.ledLevel == MetaData.LILevels["Max PE"]:
				self.LIBox.pulse_height = Defaults.LI_MAX_PE_VOLTAGE
			else:
				need_LI = False
				
			
			if need_LI:
				self.logger.info("     LI level: " + MetaData.LILevels[self.runinfo.ledLevel])
				try:
					self.LIBox.write_configuration()
				except LIBox.LIBoxException, e:
					wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="The LI box does not seem to be responding.  Check the connection settings and the cable and try again.  Running aborted.", title="LI box not responding") )
					self.logger.warning("  LI Box is not responding...")
					return False
				finally:
					self.logger.info( "     Commands issued to the LI box:\n" + "\n".join(self.LIBox.get_command_history()) )
					
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
					wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="The " + node.name + " node is reporting that it has no FEBs attached.  Your data will appear suspiciously empty...", title="No boards attached to " + node.name + " node") )
					self.logger.warning(node.name + " node reports that it has no FEBs...")
					continue	# it's still ok to go on, but user should know what's happening
			
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
		if self.current_DAQ_thread < len(self.DAQStartTasks):
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent( text="Setting up run:\n" + self.DAQStartTasks[self.current_DAQ_thread]["message"], progress=(self.startup_step, self.num_startup_steps) ) )
			self.DAQStartTasks[self.current_DAQ_thread]["method"]()
			self.current_DAQ_thread += 1
			self.startup_step += 1
		else:
			signal.signal(signal.SIGCONT, signal.SIG_IGN)		# go back to ignoring the signal...
			print "Note: requested a new thread but no more threads to start..."

	def StartETSys(self):
		events = self.runinfo.gates * Configuration.params["Hardware"]["eventFrames"] * self.febs

		etSysFrame = Frames.OutputFrame(self.main_window, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", events, Configuration.params["Hardware"]["frameSize"], os.getpid(), self.runinfo.ETport)

#		print etsys_command

		self.windows.append( etSysFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( Threads.DAQthread(etsys_command, "ET system", output_window=etSysFrame, owner_process=self, env=self.environment, is_essential_service=True) ) 

	def StartETMon(self):
		etMonFrame = Frames.OutputFrame(self.main_window, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", os.getpid(), self.runinfo.ETport)
		self.windows.append( etMonFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( Threads.DAQthread(etmon_command, "ET monitor", output_window=etMonFrame, owner_process=self, env=self.environment) )

	def StartEBSvc(self):
		ebSvcFrame = Frames.OutputFrame(self.main_window, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)

		eb_command = '%s/bin/event_builder %s/%s %s/%s %d %d' % (self.environment['DAQROOT'], self.etSystemFileLocation, self.ET_filename + "_RawData", self.rawdataLocation, self.raw_data_filename, self.runinfo.ETport, os.getpid())

		self.windows.append( ebSvcFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( Threads.DAQthread(eb_command, "event builder", output_window=ebSvcFrame, owner_process=self, env=self.environment, is_essential_service=True) )	

	def StartDAQ(self):
		daqFrame = Frames.OutputFrame(self.main_window, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		
		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d -d %d -cf %s -dc %d -hw %d" % (self.environment["DAQROOT"], self.ET_filename, self.runinfo.gates, self.runinfo.runMode, self.run, self.first_subrun + self.subrun, self.detector, self.hwconfigfile, self.febs, self.hwinit)
		if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
			daq_command += " -ll %d -lg %d" % (self.runinfo.ledLevel, self.runinfo.ledGroup)

		self.windows.append(daqFrame)
		self.UpdateWindowCount()
		self.DAQthreads.append( Threads.DAQthread(daq_command, "DAQ", output_window=daqFrame, owner_process=self, env=self.environment, next_thread_delay=2) )
		
	def StartRemoteServices(self):
		""" Notify all the remote services that we're ready to go.
		    Currently this includes the online monitoring system
		    as well as the DAQ on the readout nodes. """
		    
		# the ET system is all set up, so the online monitoring nodes
		# can be told to connect.  the run control doesn't care if they
		# actually start up properly; all it does is try to send the
		# appropriate signal.
		for node in self.monitorNodes:
			try:
				node.om_start(self.ET_filename, self.runinfo.ETport)
			except:
				self.logger.exception("Online monitoring couldn't be started on node %s.  Ignoring." % name)
				continue

		# DON'T consolidate this loop together with the next one.
		# ALL the subscriptions need to be booked before *any* of
		# the readout nodes is told to start (in case there's a problem
		# and it returns immediately).		    
		self.logger.info("  Booking subscriptions for 'DAQ finished' messages from readout nodes...")
		for node in self.readoutNodes:
			self.socketThread.Subscribe(node.id, node.name, "daq_finished", callback=self, waiting=True, notice="Running...")
			self.logger.info("    ... subscribed the %s node." % node.name)

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
					if not (self.runinfo.runMode in (MetaData.RunningModes["Light injection", MetaData.HASH], MetaData.RunningModes["Mixed beam/LI", MetaData.HASH])):
						self.runinfo.ledLevel = MetaData.LILevels["Zero PE"]
						self.runinfo.ledGroup = MetaData.LEDGroups["ABCD", MetaData.HASH]

	#				print self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup
					
					success = node.daq_start(self.ET_filename, self.runinfo.ETport, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
				
					self.logger.info("Started DAQ on %s node (address: %s)" % (node.name, node.address))
				except ReadoutNode.ReadoutNodeException:
					wx.PostEvent(self.main_window, Events.ErrorMsgEvent(text="Somehow the DAQ service on the " + node.name + " node has not yet stopped.  Stopping now -- but be on the lookout for weird behavior.", title=node.name.capitalize() + " DAQ service not yet stopped") )

					stop_success = node.daq_stop()
					if stop_success:
						success = node.daq_start(self.ET_filename, self.runinfo.ETport, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
					else:
						errmsg = "Couldn't stop the " + node.name +" DAQ service.  Aborting run."
						errtitle =  title=node.name.capitalize() + " DAQ service couldn't be stopped"
						success = False
				except ReadoutNode.ReadoutNodeNoConnectionException:
					errmsg = "The connect to the " + node.name + " couldn't be established!  Run will be aborted."
					errtitle = "No connection to the " + node.name + " node"
					success = False
	
				if not success:
					errmsg = errmsg if errmsg is not None else "Couldn't start the " + node.name + " DAQ service.  Aborting run."
					errtitle = errtitle if errtitle is not None else node.name.capitalize() + " DAQ service couldn't be started"
					wx.PostEvent(self.main_window, Events.ErrorMsgEvent(title=errtitle, text=errmsg) )
				
					self.StopDataAcquisition()
				else:
					wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
	
		if self.running:
			self.logger.info("  All DAQ services started.  Data acquisition underway.")
		
	def StartTestProcess(self):
		frame = Frames.OutputFrame(self.main_window, "test process", window_size=(600,600), window_pos=(1200,200))
		frame.Show(True)

		command = "/home/jeremy/code/mnvruncontrol/scripts/test.sh"

		self.windows.append(frame)
		self.UpdateWindowCount()
		self.DAQthreads.append( Threads.DAQthread(command, "test process", output_window=frame, owner_process=self, next_thread_delay=3, is_essential_service=True) )
		

	##########################################
	# Utilities, event handlers, etc.
	##########################################

	def CloseWindows(self):
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
		#addressee=matches.group("addressee"), sender=matches.group("sender"), message=matches.group("message")
		
		# first of all, messages that arrive while we're not runing
		# are irrelevant.
		if not self.running:
			return
		
		# need a lock to prevent race conditions (for example, a second node sending a "daq_finished" event
		# while the "daq_finished" event for a previous node is still being processed)
		self.logger.debug("Acquiring message handler lock...")
		self.messageHandlerLock.acquire()
		self.logger.debug("Successfully acquired message handler lock.")
		
		# if it's a HW error message, we need to abort the subrun.
		if evt.message == "hw_error" :	
			wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="There was a hardware error while configuring the " + evt.sender + " readout node.  This subrun will need to be stopped.", title="Hardware configuration problem") )
			self.logger.error("There was a hardware error on the " + node.name + " readout node.  This subrun will be aborted.")
			
			self.logger.warning("Subrun " + str(self.first_subrun + self.subrun) + " aborted.")
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
			for node in self.readoutNodes:
				# first set the node we've been notified about to "done."
				if node.name == evt.sender:
					self.logger.debug("    ==> %s node reports it's done taking data." % node.name)
					node.completed = True
					node.shutting_down = False
					
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
				#    processed.  that means that daq_stop() command in
				#    the implementation below arrives AFTER the node has
				#    already finished -- and so we SHOULD wait for that signal
				#    to arrive (which will mean one more call of this method)
				#    rather than stopping it like this since it's already
				#    stopped.
				#
				# another question is whether waiting on the remote nodes
				# is the right method for deciding whether a subrun is done
				# altogether.  if communication is too fast, we might stop
				# the event builder before it has completely assembled the
				# last gate ...
				
				else:
					alldone = alldone and node.completed

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
				wx.PostEvent(self, Events.EndSubrunEvent(allclear=True))

		else:
			self.logger.debug("Got a message I don't know how to handle.  Ignoring.")
			

		self.messageHandlerLock.release()
		self.logger.debug("Released message handler lock.")

	def RelayProgressToDisplay(self, evt):
		# just pass the event along.
		wx.PostEvent(self.main_window, evt)
