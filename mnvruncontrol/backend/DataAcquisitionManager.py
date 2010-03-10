#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import wx.lib.newevent
import subprocess
import os
import sys
import signal
import threading
import select
import socket
import datetime
import time

# run control-specific modules.
# note that the folder 'mnvruncontrol' must be in the PYTHONPATH!
from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData
from mnvruncontrol.backend import LIBox
from mnvruncontrol.backend import RunSeries
from mnvruncontrol.backend import ReadoutNode

class DataAcquisitionManager(wx.EvtHandler):
	def __init__(self, main_window):
		wx.EvtHandler.__init__(self)

		self.main_window = main_window
		
		self.DAQthreads = []
		self.timerThreads = []
		self.socketThread = None
		self.DAQthreadStarters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartDAQ, self.StartRemoteDAQService]
		self.DAQthreadLabels = ["Starting ET system...", "Starting ET monitor...", "Starting event builder...", "Starting the DAQ master...", "Starting the DAQ on readout nodes..."]
#		self.DAQthreadStarters = [self.StartTestProcess] #, self.StartTestProcess, self.StartTestProcess]
		self.current_DAQ_thread = 0			# the next thread to start
		self.subrun = 0					# the next run in the series to start
		self.windows = []					# child windows opened by the process.
		
		self.LIBox = None					# this will be set in StartDataAcquisition
		self.readoutNodes = None				# will be set in RunControl.GetConfig()

		# configuration stuff
		self.etSystemFileLocation = Defaults.ET_SYSTEM_LOCATION_DEFAULT
		self.rawdataLocation      = Defaults.RAW_DATA_LOCATION_DEFAULT
#		self.LIBoxControlLocation  = RunControl.LI_CONTROL_LOCATION_DEFAULT


		# these will need to be set by the run control window before the process is started.
		# that way we can be sure it's properly configured.
		self.runseries = None
		self.detector = None
		self.run = None
		self.first_subrun = None
		self.febs = None
		
		self.running = False

		self.Connect(-1, -1, EVT_READY_FOR_NEXT_SUBRUN_ID, self.StartNextSubrun)
		self.Connect(-1, -1, EVT_THREAD_READY_ID, self.StartNextThread)
		self.Connect(-1, -1, EVT_DAQQUIT_ID, self.EndSubrun)		# if the DAQ process quits, this subrun is over
		self.Connect(-1, -1, EVT_UPDATE_ID, self.UpdateRunStatus)
		
	
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
			except ReadoutNode.ReadoutNodeException:
				failed_connection = node.name
				break
			else:
				self.main_window.indicators[node.name].SetBitmap(self.main_window.onImage)
		
		if failed_connection:
			errordlg = wx.MessageDialog( None, "A connection cannot be made to the " + failed_connection + " readout node.  Check to make sure that the run control dispatcher is started on that machine.", "No connection to " + failed_connection + " readout node", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			return
			
					
		self.subrun = 0
		self.running = True
		self.StartNextSubrun()
		
		
	def StartNextSubrun(self, evt=None):
		# need to be careful here.
		# the DAQ shouldn't be running in two separate processes.
		# therefore, we need to make sure we let it completely close
		# before we actually start the next subrun.	
		while len(self.DAQthreads) > 0:
			if self.DAQthreads[-1].process.returncode != None:
				self.DAQthreads.pop()

		quitting = False
				
		if self.subrun < len(self.runseries.Runs):
			self.runinfo = self.runseries.Runs[self.subrun]
			self.main_window.UpdateSeriesStatus()
		else:		# no more runs left!  return to main panel.
			quitting = True

		if not quitting:
			self.CloseWindows()			# don't want leftover windows open.
			wx.PostEvent(self.main_window, UpdateProgressEvent(text="Setting up run:\ntesting connections", progress=(0,9)) )
			ok = True
			for node in self.readoutNodes:
				on = node.ping()
				ok = ok and on
				if on:
					self.main_window.indicators[node.name].SetBitmap(self.main_window.onImage)
				else:
					self.main_window.indicators[node.name].SetBitmap(self.main_window.onImage)
					
			
			if not ok:
				errordlg = wx.MessageDialog( None, "Connection to the readout node(s) was broken.  Running aborted.", "No connection to readout node(s)", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()
				
				quitting = True

		####
		#### NEED TO DECIDE THE HARDWARE CONFIG FILE TO BE PASSED TO THE SLOW CONTROL HERE
		####
		if not quitting:
			wx.PostEvent( self.main_window, UpdateProgressEvent(text="Setting up run:\nLoading hardware...", progress=(1,9)) )
			self.hwconfigfile = "NOFILE"
				
		# set up the LI box to do what it's supposed to, if it needs to be on.
		if not quitting:
			if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
				wx.PostEvent( self.main_window, UpdateProgressEvent(text="Setting up run:\nInitializing light injection...", progress=(2,9)) )
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
						errordlg = wx.MessageDialog( None, "The LI box does not seem to be responding.  Check the connection settings and the cable and try again.  Running aborted.", "LI box not responding", wx.OK | wx.ICON_ERROR )
						errordlg.ShowModal()

						quitting = True

		#### WAIT ON THE SLOW CONTROL UNTIL IT'S READY
		if not quitting:
			wx.PostEvent(self.main_window, UpdateProgressEvent(text="Setting up run:\nWaiting on hardware...", progress=(3,9)) )

		now = datetime.datetime.utcnow()
		self.ET_filename = '%s_%08d_%04d_%s_v05_%02d%02d%02d%02d%02d' % (MetaData.DetectorTypes[self.detector, MetaData.CODE], self.run, self.first_subrun + self.subrun, MetaData.RunningModes[self.runinfo.runMode, MetaData.CODE], now.year % 100, now.month, now.day, now.hour, now.minute)
		self.raw_data_filename = self.ET_filename + '.dat'
									
		if quitting:
			self.running = False
			self.subrun = 0
			self.main_window.StopRunning()		# tell the main window that we're done here.
			return

		self.current_DAQ_thread = 0

		self.StartNextThread()			# starts the first thread.  the rest will be started in turn as ThreadReadyEvents are received by the run manager.
		

	def StartNextThread(self, evt=None):
		if self.current_DAQ_thread < len(self.DAQthreadStarters):
			wx.PostEvent( self.main_window, UpdateProgressEvent(text="Setting up run:\n" + self.DAQthreadLabels[self.current_DAQ_thread], progress=(5+self.current_DAQ_thread,9)) )
			self.DAQthreadStarters[self.current_DAQ_thread]()
			self.current_DAQ_thread += 1
		else:
			print "Thread count too high"

	def StartETSys(self):
		events = self.runinfo.gates * Defaults.FRAMES * self.febs

		etSysFrame = OutputFrame(self.main_window, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename, events, Defaults.EVENT_SIZE)

		self.windows.append( etSysFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etsys_command, output_window=etSysFrame, owner_process=self, next_thread_delay=2, env=self.environment) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self.main_window, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s" % (self.environment["ET_HOME"], self.etSystemFileLocation, self.ET_filename)
		self.windows.append( etMonFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etmon_command, output_window=etMonFrame, owner_process=self, next_thread_delay=2, env=self.environment) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self.main_window, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)

		eb_command = '%s/bin/event_builder %s/%s %s/%s' % (self.environment['DAQROOT'], self.etSystemFileLocation, self.ET_filename, self.rawdataLocation, self.raw_data_filename)

		self.windows.append( ebSvcFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(eb_command, output_window=ebSvcFrame, owner_process=self, next_thread_delay=15, env=self.environment) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self.main_window, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		
		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d -d %d -cf %s -dc %d -hw %d" % (self.environment["DAQROOT"], self.ET_filename, self.runinfo.gates, self.runinfo.runMode, self.run, self.first_subrun + self.subrun, self.detector, self.hwconfigfile, self.febs, self.hwinit)
		if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
			daq_command += " -ll %d -lg %d" % (self.runinfo.ledLevel, self.runinfo.ledGroup)

		self.windows.append(daqFrame)
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(daq_command, output_window=daqFrame, owner_process=self, env=self.environment, next_thread_delay=2) )
		
	def StartRemoteDAQService(self):
		wx.PostEvent( self.main_window, UpdateProgressEvent(text="Setting up run:\nStarting DAQ service on readout nodes...", progress=(4,9)) )
	
		for node in self.readoutNodes:
			try:
				#print self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup
				success = node.daq_start(self.ET_filename, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
			except ReadoutNode.ReadoutNodeException:
				errordlg = wx.MessageDialog( None, "Somehow the DAQ service on the " + node.name + " node has not yet stopped.  Stopping now -- but be on the lookout for weird behavior.", node.name.capitalize() + " DAQ service not yet stopped", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()

				stop_success = node.daq_stop()
				if stop_success:
					success = node.daq_start(self.ET_filename, self.run, self.first_subrun + self.subrun, self.runinfo.gates, self.runinfo.runMode, self.detector, self.febs, self.runinfo.ledLevel, self.runinfo.ledGroup, self.hwinit)
				else:
					errordlg = wx.MessageDialog( None, "Couldn't stop the " + node.name +" DAQ service.  Aborting run.", node.name.capitalize() + " DAQ service couldn't be stopped", wx.OK | wx.ICON_ERROR )
					errordlg.ShowModal()
		
					quitting = True
	
			if not success:
				errordlg = wx.MessageDialog( None, "Couldn't start the " + node.name + " DAQ service.  Aborting run.", node.name.capitalize() + " DAQ service couldn't be started", wx.OK | wx.ICON_ERROR )
				errordlg.ShowModal()
				
				self.running = False
				self.subrun = 0
				self.main_window.StopRunning()		# tell the main window that we're done here.
		
		self.socketThread = SocketThread(self, self.readoutNodes)			# start the service that listens for the 'done' signal
		
	def StartTestProcess(self):
		frame = OutputFrame(self.main_window, "test process", window_size=(600,600), window_pos=(1200,200))
		frame.Show(True)

		command = "/home/jeremy/code/mnvruncontrol/scripts/test.sh"

		self.windows.append(frame)
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(command, output_window=frame, owner_process=self, next_thread_delay=3, quit_event=DAQQuitEvent) )
		
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
		
		self.main_window.UpdateCloseWindows(len(self.windows) > 0)

	def UpdateRunStatus(self, evt=None):
		wx.PostEvent( self.main_window, UpdateProgressEvent(text="Running...\nSee ET windows for more information", progress=(0,0)) )		# 'pulse' the progress bar

	def EndSubrun(self, evt=None):
#		print "Ending subrun."
		for thread in self.DAQthreads:		# we leave these in the array so that they can completely terminate.  they'll be removed in StartNextSubrun() if necessary.
			thread.Abort()
			
		while len(self.timerThreads) > 0:
			thread = self.timerThreads.pop()	# the countdown timers would start more threads.  get rid of them.
			thread.Abort()

		self.current_DAQ_thread = 0			# reset the thread counter in case there's another subrun in the series
		self.subrun += 1

		try:
			self.LIBox.reset()					# don't want the LI box going unless it needs to be.
		except:
			print "Couldn't reset LI box at the end of the subrun..."

		self.main_window.PostSubrun()			# main window needs to update subrun #, etc.
		
		if self.running:
			wx.PostEvent(self, ReadyForNextSubrunEvent())
	
	def StopDataAcquisition(self, evt=None):
		self.running = False
#		self.subrun = 0

		needsManualStop = False
		for node in self.readoutNodes:
			try:
				success = node.daq_stop()
			except ReadoutNode.ReadoutNodeException, ReadoutNode.ReadoutNodeNoConnectionException:		# the DAQ has already quit or is unreachable
				needsManualStop = True				# if so, we'll never get the "DAQ quit" event.
		if needsManualStop:
			self.EndSubrun()								
			

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

		self.Connect(-1, -1, EVT_NEWDATA_ID, self.OnNewData)
		
	def OnNewData(self, data_event):
		self.textarea.AppendText(data_event.data)
		

#########################################################
#   DAQthread
#########################################################

class DAQthread(threading.Thread):
	""" A thread for an ET/DAQ process. """
	def __init__(self, process_info, output_window, owner_process, env, next_thread_delay=0, quit_event=None, update_event=None):
		threading.Thread.__init__(self)
		self.output_window = output_window
		self.owner_process = owner_process
		self.environment = env
		self.command = process_info
		self.next_thread_delay = next_thread_delay
		self.quit_event = quit_event
		self.update_event = update_event
		self.daemon = True				# this way the process will end when the main thread does

		self.time_to_quit = False

		self.timerthread = None			# used to count down to a hard kill if necessary

		self.start()				# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread '''
		if self.output_window:			# the user could have closed the window before the thread was ready...
			self.process = subprocess.Popen(self.command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.environment)
			self.pid = self.process.pid

			wx.PostEvent(self.output_window, NewDataEvent("Started thread with PID " + str(self.pid) + "\n"))	# post a message noting the PID of this thread
			#wx.PostEvent(self.output_window, NewDataEvent("using command '" + self.command + "'...\n"))

			if self.next_thread_delay > 0:
				# start a new thread to count down until the next one can be started.
				self.owner_process.timerThreads.append(TimerThread(self.next_thread_delay, self.owner_process))

			last_update_time = 0
			while True:
				if self.time_to_quit:
					break

				# read out the data from the process.
				# we use select() (again from the UNIX library) to check that
				# there actually IS something in the buffer before we try to read.
				# if we didn't do that, the thread would lock up until the specified
				# number of characters was read out.
				#
				# note that the reading loop includes a poll() of the process.
				# this is so that if Abort() or LastCheck() is called on this process,
				# and the communicate() finishes, we don't try to read from stdout
				# any more.  (communicate() closes stdout, so we'd get an exception
				# if we let it do that.)
				newdata = ""
				while self.process.poll() is None and select.select([self.process.stdout], [], [], 0)[0]:		
					newdata += self.process.stdout.read(1)

				# now post any data from the process to its output window
				if len(newdata) > 0 and self.output_window:		# make sure the window is still open
					wx.PostEvent(self.output_window, NewDataEvent(newdata))
				elif self.process.returncode != None:	# if the buffer is empty and the process has finished, don't loop any more
					break
				
				
		# if something special is supposed to happen when this thread quits, do it.
		if self.quit_event:
			wx.PostEvent(self.owner_process, self.quit_event())
		
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
		
		if self.process.poll() is None:				# it COULD happen that the process has already quit.
			self.process.terminate()					# first, try nicely.
			self.process.send_signal(signal.SIGINT)		# some of these processes only respond to SIGINT, strangely enough

			if self.process.poll() is None:		# they'll probably need a little time to shut down cleanly
				self.timerthread = threading.Timer(10, self.LastCheck)
				self.timerthread.start()

		else:
			# make sure there's nothing left in the buffer to read!
			newdata = self.process.stdout.read()
			if len(newdata) > 0 and self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent(newdata))
		
			if (self.timerthread):
				self.timerthread.cancel()
			#print "Process " + str(self.pid) + " has quit."
			if self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent("\n\nThread terminated cleanly."))

	def LastCheck(self):
		""" One last check to see if the process has finished gracefully.
		    If not, the user is instructed that s/he should do a manual kill. """
		if self.process.poll() is None:
			print "Thread " + str(self.pid) + " is deadlocked.  Kill it manually."
		else:
			newdata = self.process.stdout.read()
			if len(newdata) > 0 and self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent(newdata))
#			print "Process " + str(self.pid) + " has quit."
			if self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent("\n\nThread terminated cleanly."))
		
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
		
		self.start()
	
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind(("", Defaults.MASTER_PORT))
		s.setblocking(0)			# we want to be able to update the display, so we can't wait on a connection
		s.listen(1)
		
		quit = False
		node_completed = {}
		for node in self.nodesToWatch:
			node_completed[node.name] = False
		while True:
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
				
				client_socket.close()
				
				request = request.lower()
				
				if request in node_completed:
					node_completed[request] = True
					num_completed += 1
					wx.PostEvent(self.owner_process.main_window, UpdateProgressEvent( text="Cleaning up:\nWaiting on all nodes to finish...", progress=(num_complete, len(node_completed)) ) )
			else:
				for node in self.nodesToWatch:
					if node.daq_checkStatus():
						self.owner_process.main_window.indicators[node.name].SetBitmap(self.owner_process.main_window.onImage)	# whew!
						if num_complete > 0:		# if one node has quit, we need to have the other ones quit too...
							node.daq_stop()
							
					else:
						self.owner_process.main_window.indicators[node.name].SetBitmap(self.owner_process.main_window.offImage)
				
				wx.PostEvent(self.owner_process, UpdateEvent())
				time.sleep(0.25)		# a little throttling so we don't overload the event dispatcher
			
		# all DAQs have quit: subrun is over.
		wx.PostEvent(self.owner_process, DAQQuitEvent())
				
		
	
	


#########################################################
#   TimerThread
#########################################################

class TimerThread(threading.Thread):
	def __init__(self, countdown_time, postback_window):
		threading.Thread.__init__(self)
		self.time = countdown_time
		self.postback_window = postback_window
		self.time_to_quit = False
		self.start()

	def run(self):
		time.sleep(self.time)

		if self.postback_window and not(self.time_to_quit):		# make sure the user didn't close the window while we were waiting
			wx.PostEvent(self.postback_window, ThreadReadyEvent())
			
	def Abort(self):
		self.time_to_quit = True

#########################################################
#   NewDataEvent
#########################################################

EVT_NEWDATA_ID = wx.NewId()
class NewDataEvent(wx.PyEvent):
	""" An event to carry data between the threaded processes and the windows built to display their output. """
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.data = data	
		self.SetEventType(EVT_NEWDATA_ID)
		
#########################################################
#   UpdateEvent
#########################################################

EVT_UPDATE_ID = wx.NewId()
class UpdateEvent(wx.PyEvent):
	""" An event that notifies the data acquisition handler that things are still running. """
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_UPDATE_ID)

#########################################################
#   UpdateProgressEvent
#########################################################

#EVT_UPDATEPROGRESS_ID = wx.NewId()
#class UpdateProgressEvent(wx.NotifyEvent):
	#""" An event informing the main window what progress has been made in the run. """
	#def __init__(self, text=None, progress=(0,0)):
		#wx.NotifyEvent.__init__(self)
		#self.text = text
		#self.progress = progress
		#self.SetEventType(EVT_UPDATEPROGRESS_ID)

UpdateProgressEvent, EVT_UPDATEPROGRESS_ID = wx.lib.newevent.NewEvent()

#########################################################
#   ThreadReadyEvent
#########################################################

EVT_THREAD_READY_ID = wx.NewId()
class ThreadReadyEvent(wx.CommandEvent):
	""" An event that informs the next process that it's done """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_THREAD_READY_ID)

#########################################################
#   DAQQuitEvent
#########################################################

EVT_DAQQUIT_ID = wx.NewId()
class DAQQuitEvent(wx.CommandEvent):
	""" An event informing the main window that the DAQ has quit (and thus all other processes should be stopped). """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_DAQQUIT_ID)


#########################################################
#   ReadyForNextSubrunEvent
#########################################################

EVT_READY_FOR_NEXT_SUBRUN_ID = wx.NewId()
class ReadyForNextSubrunEvent(wx.CommandEvent):
	""" An event used internally to indicate that the manager is ready to start the next subrun. """
	def __init__(self):
		wx.CommandEvent.__init__(self)
		self.SetEventType(EVT_READY_FOR_NEXT_SUBRUN_ID)


