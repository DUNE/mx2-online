"""
  DataAcquisitionManager.py:
  Infrastructural objects to manage a data acquisition run.
  Used by the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import wx
from wx.lib.wordwrap import wordwrap
import subprocess
import os
import sys
import fcntl
import signal
import threading
import select
import socket
import errno
import datetime
import time

# run control-specific modules.
# note that the folder 'mnvruncontrol' must be in the PYTHONPATH!
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.backend import Events
from mnvruncontrol.backend import LIBox
from mnvruncontrol.backend import RunSeries
from mnvruncontrol.backend import ReadoutNode

class DataAcquisitionManager(wx.EvtHandler):
	def __init__(self, main_window):
		wx.EvtHandler.__init__(self)

		self.main_window = main_window
		
		self.DAQthreads = []
		self.DAQthreadWatcher = None
		self.timerThreads = []
		self.socketThread = None
		self.DAQthreadStarters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartRemoteDAQService]
		self.DAQthreadLabels = ["Starting ET system...", "Starting ET monitor...", "Starting event builder...", "Starting the DAQ on readout node(s)..."]
#		self.DAQthreadStarters = [self.StartTestProcess] #, self.StartTestProcess, self.StartTestProcess]
		self.current_DAQ_thread = 0			# the next thread to start
		self.subrun = 0					# the next run in the series to start
		self.windows = []					# child windows opened by the process.
		
		self.LIBox = None					# this will be set in StartDataAcquisition
		self.readoutNodes = None				# will be set in RunControl.GetConfig()

		# configuration stuff
		self.etSystemFileLocation = Defaults.ET_SYSTEM_LOCATION_DEFAULT
		self.rawdataLocation      = Defaults.RAW_DATA_LOCATION_DEFAULT


		# these will need to be set by the run control window before the process is started.
		# that way we can be sure it's properly configured.
		self.runseries = None
		self.detector = None
		self.run = None
		self.first_subrun = None
		self.febs = None
		
		self.running = False
		self.can_shutdown = False		# used in between subruns to prevent shutting down twice for different reasons

		self.Bind(Events.EVT_READY_FOR_NEXT_SUBRUN, self.StartNextSubrun)
		self.Bind(Events.EVT_THREAD_READY, self.StartNextThread)
		self.Bind(Events.EVT_END_SUBRUN, self.EndSubrun)		# if the DAQ process quits, this subrun is over
#		self.Connect(-1, -1, EVT_UPDATE_ID, self.UpdateRunStatus)
		
	##########################################
	# Global starters and stoppers
	##########################################
	
	def StartDataAcquisition(self, evt=None):
		if not isinstance(self.runseries, RunSeries.RunSeries):
			raise ValueError("No run series defined!")

		if self.detector == None or self.run == None or self.first_subrun == None or self.febs == None:
			raise ValueError("Run series is improperly configured.")

		self.LIBox = LIBox.LIBox()
		
		failed_connection = None
		for node in self.readoutNodes:
			try:
				node.ping()
			except ReadoutNode.ReadoutNodeNoConnectionException:
				failed_connection = node.name
				break
			else:
				wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
		
		if failed_connection:
			wx.PostEvent(self.main_window, Events.ErrorMsg(text="A connection cannot be made to the " + failed_connection + " readout node.  Check to make sure that the run control dispatcher is started on that machine.", title="No connection to " + failed_connection + " readout node") )
			return
			
					
		self.subrun = 0
		self.running = True
		self.StartNextSubrun()
		
	def StopDataAcquisition(self, evt=None):
		self.running = False
#		self.subrun = 0

		# the run will need a manual stop if the readout nodes can't be properly contacted.
		needsManualStop = False
		for node in self.readoutNodes:
			try:
				success = node.daq_stop()
			except ReadoutNode.ReadoutNodeException, ReadoutNode.ReadoutNodeNoConnectionException:		# the DAQ has already quit or is unreachable
				needsManualStop = True				# if so, we'll never get the "DAQ quit" event from the SocketThread.
		if needsManualStop:
			wx.PostEvent(self, Events.EndSubrunEvent())								

	##########################################
	# Subrun starters and stoppers
	##########################################
		
	def StartNextSubrun(self, evt=None):
		""" Prepares to start the next subrun: waits for
		    the DAQ system to be ready, notifies the main 
		    window what run we're in, prepares the LI box
		    and slow controls, and finally initiates the
		    acquisition sequence. """
	
		quitting = False
		self.CloseWindows()			# don't want leftover windows open.
		
		numsteps = 4 + len(self.DAQthreadStarters)

		wx.PostEvent(self.main_window, Events.UpdateProgressEvent(text="Setting up run:\nCleaning up any prior ET processes...", progress=(0,numsteps)) )
		# need to be careful here.
		# ET & the DAQ shouldn't be running in two separate sets of processes.
		# therefore, we need to make sure we let them completely close
		# before we actually start the next subrun.  however, we can't wait
		# on them in this method, because it runs as part of the main thread,
		# and if we did, the whole program would appear to lock up: since wx also
		# runs in the main thread, the graphical interface wouldn't be updated.
		# instead, we spawn a separate thread to watch these processes and
		# issue the ReadyForNextSubrun event to the DataAcquisitionManager
		# when they are done.
		
		# if the event contains a list of PIDs that have finished, then
		# this signal is coming from the thread watcher.
		# clear out the corresponding elements in the list.
		if hasattr(evt, "pids_cleared"):
			for pid in evt.pids_cleared:
				self.DAQthreads.remove(pid)
		
		if len(self.DAQthreads) > 0:
			if self.DAQthreadWatcher is None or not self.DAQthreadWatcher.is_alive():
				self.DAQthreadWatcher = DAQWatcherThread(self)

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

			# we can't do anything more until they're done, so exit this method.
			return
		
		self.can_shutdown = True
		
		self.runinfo = self.runseries.Runs[self.subrun]
		wx.PostEvent(self.main_window, Events.UpdateSeriesEvent())

		self.runinfo.ETport = 1091 + (self.first_subrun + self.subrun) % 4		# ET needs to use a rotating port number to avoid blockages.

		if not quitting:
			wx.PostEvent(self.main_window, Events.UpdateProgressEvent(text="Setting up run:\ntesting connections", progress=(1,numsteps)) )
			ok = True
			for node in self.readoutNodes:
				on = node.ping()
				ok = ok and on
				wx.PostEvent( self.main_window, Events.UpdateNodeEvent(node=node.name, on=on) )
					
			if not ok:
				wx.PostEvent( self.main_window, Events.ErrorMsgEvent(text="Connection to the readout node(s) was broken.  Running aborted.", title="No connection to readout node(s)") )
				
				quitting = True

		####
		#### NEED TO DECIDE THE HARDWARE CONFIG FILE TO BE PASSED TO THE SLOW CONTROL HERE
		####
		if not quitting:
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Setting up run:\nLoading hardware...", progress=(2,numsteps)) )
			self.hwconfigfile = "NOFILE"
				
		# set up the LI box to do what it's supposed to, if it needs to be on.
		if not quitting:
			if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
				wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Setting up run:\nInitializing light injection...", progress=(3,numsteps)) )
				self.LIBox.LED_groups = MetaData.LEDGroups[self.runinfo.ledGroup]
			
				need_LI = True
				if self.runinfo.ledLevel == MetaData.LILevels["One PE"]:
					self.LIBox.pulse_height = 5.07					# from Brandon Eberly, 3/5/2010
				elif self.runinfo.ledLevel == MetaData.LILevels["Max PE"]:
					self.LIBox.pulse_height = 12.07
				else:
					need_LI = False
			
				if need_LI:
					try:
						self.LIBox.initialize()
						self.LIBox.write_configuration()	
					except Exception as e:
						wx.PostEvent( self.main_window, Events.ErrorMsgtEvent(text="The LI box does not seem to be responding.  Check the connection settings and the cable and try again.  Running aborted.", title="LI box not responding") )

						quitting = True

		#### WAIT ON THE SLOW CONTROL UNTIL IT'S READY
		if not quitting:
			wx.PostEvent(self.main_window, Events.UpdateProgressEvent(text="Setting up run:\nWaiting on hardware...", progress=(4,numsteps)) )

		now = datetime.datetime.utcnow()
		self.ET_filename = '%s_%08d_%04d_%s_v05_%02d%02d%02d%02d%02d' % (MetaData.DetectorTypes[self.detector, MetaData.CODE], self.run, self.first_subrun + self.subrun, MetaData.RunningModes[self.runinfo.runMode, MetaData.CODE], now.year % 100, now.month, now.day, now.hour, now.minute)
		self.raw_data_filename = self.ET_filename + '_RawData.dat'
									
		if quitting:
			self.running = False
			self.subrun = 0
			wx.PostEvent(self.main_window, Events.StopRunningEvent())		# tell the main window that we're done here.
			return

		wx.PostEvent(self.main_window, Events.SubrunStartingEvent(first_subrun=self.first_subrun, current_subrun=self.subrun, num_subruns=len(self.runseries.Runs)))

		self.current_DAQ_thread = 0

		signal.signal(signal.SIGUSR1, self.StartNextThread)
		self.StartNextThread()			# starts the first thread.  the rest will be started in turn as SIGCONT signals are received by the program.
		
	def EndSubrun(self, evt):
		""" Performs the jobs that need to be done when a subrun ends.
		    This method should only be called as the event handler
		    for the EndSubrunEvent. """

		if not self.can_shutdown:
			return

		self.can_shutdown = False
		
		if hasattr(evt, "processname") and evt.processname is not None:
			if len(self.runseries.Runs) > 1:
				dialog = wx.MessageDialog(None, "The essential process '" + evt.processname + "' died.  This subrun will be aborted.  Do you want to abort the whole run series?", evt.processname + " quit prematurely",   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION)
				self.running = self.running and (dialog.ShowModal() == wx.ID_NO)
			else:			
				wx.PostEvent(self.main_window, Events.ErrorMsgEvent(title=evt.processname + " quit prematurely", text="The essential process '" + evt.processname + "' died before the subrun was over.  The subrun will be aborted.") )
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
				except ReadoutNode.ReadoutNodeException:		# raised if the DAQ is not running on the node
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
		
		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun finishing:\nStopping the listener socket...", progress=(step, numsteps)) )
		if self.socketThread:
			self.socketThread.Abort()

		self.current_DAQ_thread = 0			# reset the thread counter in case there's another subrun in the series
		self.subrun += 1
		
		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Subrun completed.", progress=(numsteps, numsteps)) )
		wx.PostEvent( self.main_window, Events.SubrunOverEvent(run=self.run, subrun=self.first_subrun + self.subrun) )

		if self.subrun >= len(self.runseries.Runs):		# no more runs left!  need to bail.
			self.running = False
			self.subrun = 0

		if self.running:
			wx.PostEvent(self, Events.ReadyForNextSubrunEvent())
		else:
			wx.PostEvent(self.main_window, Events.StopRunningEvent())
		

	##########################################
	# Subprocess starters
	##########################################

	def StartNextThread(self, signum=None, sigframe=None):
		""" Starts the next thread in the sequence.
		    This method should ONLY be called
		    as the signal handler for SIGCONT
		    (otherwise race conditions will result)! """
		if self.current_DAQ_thread < len(self.DAQthreadStarters):
			wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Setting up run:\n" + self.DAQthreadLabels[self.current_DAQ_thread], progress=(4+self.current_DAQ_thread, 4+len(self.DAQthreadStarters) )) )
			self.DAQthreadStarters[self.current_DAQ_thread]()
			self.current_DAQ_thread += 1
		else:
			signal.signal(signal.SIGCONT, signal.SIG_IGN)		# go back to ignoring the signal...
			print "Note: requested a new thread but no more threads to start..."

	def StartETSys(self):
		events = self.runinfo.gates * Defaults.FRAMES * self.febs

		etSysFrame = OutputFrame(self.main_window, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", events, Defaults.EVENT_SIZE, os.getpid(), self.runinfo.ETport)

#		print etsys_command

		self.windows.append( etSysFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etsys_command, "ET system", output_window=etSysFrame, owner_process=self, env=self.environment, is_essential_service=True) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self.main_window, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s -c %d -p %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename + "_RawData", os.getpid(), self.runinfo.ETport)
		self.windows.append( etMonFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etmon_command, "ET monitor", output_window=etMonFrame, owner_process=self, env=self.environment) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self.main_window, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)

		eb_command = '%s/bin/event_builder %s/%s %s/%s %d %d' % (self.environment['DAQROOT'], self.etSystemFileLocation, self.ET_filename + "_RawData", self.rawdataLocation, self.raw_data_filename, self.runinfo.ETport, os.getpid())

		self.windows.append( ebSvcFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(eb_command, "event builder", output_window=ebSvcFrame, owner_process=self, env=self.environment, is_essential_service=True) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self.main_window, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		
		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d -d %d -cf %s -dc %d -hw %d" % (self.environment["DAQROOT"], self.ET_filename, self.runinfo.gates, self.runinfo.runMode, self.run, self.first_subrun + self.subrun, self.detector, self.hwconfigfile, self.febs, self.hwinit)
		if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
			daq_command += " -ll %d -lg %d" % (self.runinfo.ledLevel, self.runinfo.ledGroup)

		self.windows.append(daqFrame)
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(daq_command, "DAQ", output_window=daqFrame, owner_process=self, env=self.environment, next_thread_delay=2) )
		
	def StartRemoteDAQService(self):
		wx.PostEvent( self.main_window, Events.UpdateProgressEvent(text="Setting up run:\nStarting DAQ service on readout nodes...", progress=(4,9)) )
	
		for node in self.readoutNodes:
			errmsg = None
			errtitle = None
			try:
				# for non-LI run modes, these values are irrelevant, so we set them to some well-defined defaults.
				if not (self.runinfo.runMode in (MetaData.RunningModes["Light injection", MetaData.HASH], MetaData.RunningModes["Mixed beam/LI", MetaData.HASH])):
					self.runinfo.ledLevel = MetaData.LILevels["Zero PE"]
					self.runinfo.ledGroup = MetaData.LEDGroups["All", MetaData.HASH]

#				print self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup
					
				success = node.daq_start(self.ET_filename, self.runinfo.ETport, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
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
				
				self.running = False
				self.subrun = 0
				self.StopDataAcquisition()
			else:
				wx.PostEvent(self.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
		
		if self.running:
			self.socketThread = SocketThread(self, self.readoutNodes)			# start the service that listens for the 'done' signal
		
	def StartTestProcess(self):
		frame = OutputFrame(self.main_window, "test process", window_size=(600,600), window_pos=(1200,200))
		frame.Show(True)

		command = "/home/jeremy/code/mnvruncontrol/scripts/test.sh"

		self.windows.append(frame)
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(command, "test process", output_window=frame, owner_process=self, next_thread_delay=3, is_essential_service=True) )
		

	##########################################
	# Utilities
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
#   DAQthread
#########################################################

class DAQthread(threading.Thread):
	""" A thread for an ET/DAQ process. """
	def __init__(self, process_info, process_identity, output_window, owner_process, env, next_thread_delay=0, is_essential_service=False, update_event=None):
		threading.Thread.__init__(self)
		self.process_identity = process_identity
		self.output_window = output_window
		self.owner_process = owner_process
		self.environment = env
		self.command = process_info
		self.next_thread_delay = next_thread_delay
		self.is_essential_service = is_essential_service
		self.update_event = update_event
		self.name = self.command.split()[0] + "Thread"
		self.process = None
		self.daemon = True				# this way the process will end when the main thread does

		self.time_to_quit = False
		self.have_cleaned_up = False

		self.timerthread = None			# used to count down to a hard kill if necessary

		self.start()				# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread. '''
		self.process = subprocess.Popen(self.command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.environment)
		self.pid = self.process.pid

		if self.next_thread_delay > 0:
			# start a new thread to count down until the next DAQ process can be started.
			self.owner_process.timerThreads.append(TimerThread(self.next_thread_delay, self.owner_process))

		if self.output_window:
			wx.PostEvent(self.output_window, Events.NewDataEvent(data="Started thread with PID " + str(self.pid) + "\n"))	# post a message noting the PID of this thread


		while not self.time_to_quit and self.process.poll() is None:
			newdata = self.read()

			# now post any data from the process to its output window
			if len(newdata) > 0 and self.output_window:		# make sure the window is still open
				wx.PostEvent(self.output_window, Events.NewDataEvent(data=newdata))
					

		if self.process.poll() is None:				# if this process hasn't been stopped yet, it needs to be
			self.process.terminate()					# first, try nicely.

			if self.process.poll() is None:		# they'll probably need a little time to shut down cleanly
				self.timer_cancel = False			# ... but if it shuts down in the interim, we should be able to cancel it!
				self.timerthread = threading.Timer(5, self.LastCheck)
				self.timerthread.start()
		else:
			data = self.read(want_cleanup_read = True)
			if len(data) > 0 and self.output_window:
				wx.PostEvent(self.output_window, Events.NewDataEvent(data=data))
		
			if (self.timerthread):
				self.timerthread.cancel()
			#print "Process " + str(self.pid) + " has quit."
			if self.output_window:
				wx.PostEvent(self.output_window, Events.NewDataEvent(data="\n\nThread terminated cleanly."))

		# if this an essential service and it's not being terminated
		# due to some external signal, it's the first thing to quit.
		# the other processes should be stopped, the user should be informed,
		# and the run stopped since further data is expected to be useless.
		# however, if this thread is being watched by the thread watcher,
		# we don't need this event because the thread watcher will issue it
		# when ALL the DAQ threads are done.
		if self.is_essential_service and self.process.poll() is not None and not self.time_to_quit:
			self.timer_cancel = True
			wx.PostEvent(self.owner_process, Events.EndSubrunEvent(processname=self.process_identity))
			
	def read(self, want_cleanup_read = False):
		""" Read out the data from the process.  This method attempts
		    to be intelligent about its reads from stdout: it
		    is non-blocking (won't lock up if there's nothing there),
		    and stops reading if the process has finished. """
		    
		#	We use select() (again from the UNIX library) to check that
		#	there actually IS something in the buffer before we try to read.
		#	If we didn't do that, the thread would lock up until the specified
		#	number of characters was read out.

		#	Note that the reading loop includes a poll() of the process.
		#	This is so that if LastCheck() is called on this process,
		#	and this loop is somehow still running, we stop trying to read
		#    as soon as the process finishes.  Here's why:
		#	when the communicate() in LastCheck() finishes,
		#	it will close the pipe to stdout, and if we continue to try
		#	reading, we'll get an exception.
		#    This condition is lifted if this read is explicitly called
		#    as a "cleanup" read -- that is, if it's intended to be the
		#    last read after the process is dead.  This is only allowed to
		#    happen once (controlled by self.have_cleaned_up), which will
		#	hopefully prevent race conditions between run() and LastCheck().
		
		do_cleanup_read = want_cleanup_read and not self.have_cleaned_up
		if do_cleanup_read:
			self.have_cleaned_up = True
		
		data = ""
		while self.process.poll() is None or do_cleanup_read:
			try:
				ready_to_read = select.select([self.process.stdout], [], [], 0)[0]
			except select.error, (errnum, msg):
				if errnum == errno.EINTR:		# the code for an interrupted system call
					continue
				else:
					raise

			if not ready_to_read:
				break

			try:	
				newdata = os.read(self.process.stdout.fileno(), 1024)
			except OSError:		# if the pipe is closed mid-read
				break
			
			if newdata == "":
				break
			data += newdata
		
		return data
	
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
	

	def LastCheck(self):
		""" One last check to see if the process has finished gracefully.
		    If not, the user is instructed that s/he should do a manual kill. """
		if self.timer_cancel:
			return
			
		if self.process.poll() is None:
			print "Thread " + str(self.pid) + " seems to be deadlocked.  Kill it manually."
		else:
			data = self.read(want_cleanup_read = True)
			if self.output_window:
				if len(data) > 0:
					wx.PostEvent(self.output_window, Events.NewDataEvent(data=data))
				wx.PostEvent(self.output_window, Events.NewDataEvent(data="\n\nThread terminated cleanly."))

		if self.is_essential_service and self.process.poll() is not None and not self.time_to_quit:
			wx.PostEvent(self.owner_process, Events.EndSubrunEvent(processname=self.process_identity))
	
#########################################################
#   DAQWatcherThread
#########################################################

class DAQWatcherThread(threading.Thread):
	""" A thread whose sole purpose is to watch the other
	    DAQ threads (which contain subprocesses) until
	    their subprocesses finish, and then report that
	    information back to the main thread. """
	def __init__(self, postback_object):
		threading.Thread.__init__(self)
		self.name="DAQWatcherThread"

		self.threadsToWatch = []
		self.postback_object = postback_object
	
	def run(self):
		self.time_to_quit = False
		if len(self.threadsToWatch) == 0:
			return
	 		
		while not self.time_to_quit:
			threads_done = [thread.process.poll() is not None for thread in self.threadsToWatch]
			
#			print threads_done
			
			self.time_to_quit = self.time_to_quit or not False in threads_done
		
		pidlist = [thread.pid for thread in self.threadsToWatch]
		self.threadsToWatch = []
		wx.PostEvent(self.postback_object, Events.ReadyForNextSubrunEvent(pids_cleared=pidlist))
		
	def Abort(self):
		self.time_to_quit = True
		
#########################################################
#   SocketThread
#########################################################

class SocketThread(threading.Thread):
	""" A thread that keeps open a socket to listen for
	    the "done" signal from all readout nodes. """
	def __init__(self, owner_process, nodesToWatch):
		threading.Thread.__init__(self)
		
		self.owner_process = owner_process
		self.nodesToWatch = nodesToWatch
		self.name = "SocketThread"
		self.time_to_quit = False

		self.daemon = True
		
		self.start()
	
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)	# make this socket reusable.
		
		# we only want to bind a local socket if that's all that's necessary
		bindaddr = "localhost"		
		for node in self.nodesToWatch:
			if not node.address in ("localhost", "127.0.0.1"):
				bindaddr = ""		# allow any incoming connections on the right port number
				break
		s.bind((bindaddr, Defaults.MASTER_PORT))

		s.setblocking(0)			# we want to be able to update the display, so we can't wait on a connection
		s.listen(3)				# we might have more than one node contact us at a time, so allow multiple backlogged connections
		
		quit = False
		lastupdate = 0
		node_completed = {}
		for node in self.nodesToWatch:
			node_completed[node.name] = False
		while not self.time_to_quit:
			alldone = True
			num_complete = 0
			for nodename in node_completed:
				if not node_completed[nodename]:
					alldone = False
				else:
					num_complete += 1
			if alldone:
				break

			if select.select([s], [], [], 0)[0]:		
				client_socket, client_address = s.accept()

				request = ""
				datalen = -1
				while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
					data = client_socket.recv(1024)
					datalen = len(data)
					request += data
				
#				client_socket.close()
				
				nodeclosed = request.lower()
				
				if nodeclosed in node_completed:
					node_completed[nodeclosed] = True
					num_complete += 1
				

			if time.time() - lastupdate > 0.25:			# some throttling to make sure we don't overload the event dispatcher
#				print "run update"
				lastupdate = time.time()
				if num_complete > 0:
					wx.PostEvent(self.owner_process.main_window, Events.UpdateProgressEvent( text="Cleaning up:\nWaiting on all nodes to finish...", progress=(num_complete, len(node_completed)) ) )
				else:

					for node in self.nodesToWatch:
						try:
							node_running = node.daq_checkStatus()
						except ReadoutNode.ReadoutNodeNoConnectionException:
							wx.PostEvent(self.owner_process.main_window, Events.ErrorMsgEvent(title="Connection to " + node.name + " node broken", text="The connection to the " + node.name + " node was broken.  The subrun will be aborted.") )
							node_running = False

						if node_running:
							wx.PostEvent(self.owner_process.main_window, Events.UpdateNodeEvent(node=node.name, on=True))
							if num_complete > 0:		# if one node has quit, we need to have the other ones quit too...
								node.daq_stop()
						else:
							wx.PostEvent(self.owner_process.main_window, Events.UpdateNodeEvent(node=node.name, on=False) )
							node_completed[node.name] = True
							num_complete += 1

					wx.PostEvent(self.owner_process.main_window, Events.UpdateProgressEvent( text="Running...\nSee ET windows for more information", progress=(0,0)) )

		s.close()
		
		# all DAQs have been closed cleanly.
		# the subrun needs to end then.
		# we pass 'allclear = True' to signify this.
		if num_complete == len(self.nodesToWatch):
			wx.PostEvent(self.owner_process, Events.EndSubrunEvent(allclear=True))
		
	def Abort(self):
		self.time_to_quit = True
				

#########################################################
#   TimerThread
#########################################################

class TimerThread(threading.Thread):
	def __init__(self, countdown_time, postback_window):
		threading.Thread.__init__(self)
		self.time = countdown_time
		self.postback_window = postback_window
		self.time_to_quit = False
		self.daemon = True
		
		self.start()

	def run(self):
		time.sleep(self.time)

		if self.postback_window and not(self.time_to_quit):		# make sure the user didn't close the window while we were waiting
			wx.PostEvent(self.postback_window, Events.ThreadReadyEvent())
			
	def Abort(self):
		self.time_to_quit = True


