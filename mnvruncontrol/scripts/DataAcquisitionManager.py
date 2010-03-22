#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import subprocess
import os
import sys
import signal
import threading
import datetime
import time

import RunSeries
import RunControl
import MetaData

# globals.
# do these need to be calculated somehow?
# or are they always fixed?
EVENT_SIZE = 2048 
FRAMES = 8


class DataAcquisitionManager(wx.EvtHandler):
	def __init__(self, main_window):
		wx.EvtHandler.__init__(self)

		self.main_window = main_window
		
		self.DAQthreads = []
		self.timerThreads = []
		self.DAQthreadStarters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartDAQ]
#		self.DAQthreadStarters = [self.StartTestProcess] #, self.StartTestProcess, self.StartTestProcess]
		self.current_DAQ_thread = 0			# the next thread to start
		self.subrun = 0					# the next run in the series to start
		self.windows = []					# child windows opened by the process.

		# configuration stuff
		self.etSystemFileLocation = RunControl.ET_SYSTEM_LOCATION_DEFAULT
		self.rawdataLocation      = RunControl.RAW_DATA_LOCATION_DEFAULT
		self.LIBoxControlLocation = RunControl.LI_CONTROL_LOCATION_DEFAULT


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
		
	
	def StartDataAcquisition(self, evt=None):
		if not isinstance(self.runseries, RunSeries.RunSeries):
			raise ValueError("No run series defined!")

		if self.detector == None or self.run == None or self.first_subrun == None or self.febs == None:
			raise ValueError("Run series is improperly configured.")

		self.CloseWindows()			# same for the windows

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
				
		if self.subrun < len(self.runseries.Runs):
			self.runinfo = self.runseries.Runs[self.subrun]
			self.main_window.UpdateStatus()
		else:		# no more runs left!  return to main panel.
			self.running = False
			self.subrun = 0
			self.main_window.StopRunning()		# tell the main window that we're done here.
			return

		self.CloseWindows()			# don't want leftover windows open.

		####
		#### NEED TO DECIDE THE HARDWARE CONFIG FILE TO BE PASSED TO THE SLOW CONTROL HERE
		#### AND THEN WAIT ON THE SLOW CONTROL UNTIL IT'S READY
		####
		self.hwconfigfile = "NOFILE"

		self.current_DAQ_thread = 0

		now = datetime.datetime.utcnow()
		self.ET_filename = '%s_%08d_%04d_%s_v04_%02d%02d%02d%02d%02d' % (MetaData.DetectorTypes[self.detector, MetaData.CODE], self.run, self.first_subrun + self.subrun, MetaData.RunningModes[self.runinfo.runMode, MetaData.CODE], now.year % 100, now.month, now.day, now.hour, now.minute)
		self.raw_data_filename = self.ET_filename + '.dat'

		self.StartNextThread()			# starts the first thread.  the rest will be started in turn as ThreadReadyEvents are received by the run manager.
		

	def StartNextThread(self, evt=None):
		if self.current_DAQ_thread < len(self.DAQthreadStarters):
			self.DAQthreadStarters[self.current_DAQ_thread]()
			self.current_DAQ_thread += 1
		else:
			print "Thread count too high"

	def StartETSys(self):
		events = self.runinfo.gates * FRAMES * self.febs

		etSysFrame = OutputFrame(self.main_window, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d" % (os.environ["ET_HOME"], self.etSystemFileLocation, self.ET_filename, events, EVENT_SIZE)

		self.windows.append( etSysFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etsys_command, output_window=etSysFrame, owner_process=self, next_thread_delay=2) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self.main_window, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s" % (os.environ["ET_HOME"], self.etSystemFileLocation, self.ET_filename)
		self.windows.append( etMonFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(etmon_command, output_window=etMonFrame, owner_process=self, next_thread_delay=2) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self.main_window, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)

		eb_command = '%s/bin/event_builder %s/%s %s/%s' % (os.environ['DAQROOT'], self.etSystemFileLocation, self.ET_filename, self.rawdataLocation, self.raw_data_filename)

		self.windows.append( ebSvcFrame )
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(eb_command, output_window=ebSvcFrame, owner_process=self, next_thread_delay=15) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self.main_window, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		
		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d -d %d -cf %s -dc %d" % (os.environ["DAQROOT"], self.ET_filename, self.runinfo.gates, self.runinfo.runMode, self.run, self.subrun, self.detector, self.hwconfigfile, self.febs)
		if self.runinfo.runMode == MetaData.RunningModes["Light injection", MetaData.HASH] or self.runinfo.runMode == MetaData.RunningModes["Mixed beam/LI", MetaData.HASH]:
			daq_command += " -ll %d -lg %d" % (self.runinfo.ledLevel, self.runinfo.ledGroup)
		
#		print daq_command
	
		self.windows.append(daqFrame)
		self.UpdateWindowCount()
		self.DAQthreads.append( DAQthread(daq_command, output_window=daqFrame, owner_process=self, quit_event=DAQQuitEvent) )

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

	def EndSubrun(self, evt=None):
#		print "Ending subrun."
		for thread in self.DAQthreads:		# we leave these in the array so that they can completely terminate.  they'll be removed in StartNextSubrun() if necessary.
			thread.Abort()
			
		while len(self.timerThreads) > 0:
			thread = self.timerThreads.pop()	# the countdown timers would start more threads.  get rid of them.
			thread.Abort()

		self.current_DAQ_thread = 0			# reset the thread counter in case there's another subrun in the series
		self.subrun += 1
		
		self.main_window.PostSubrun()			# main window needs to update subrun #, etc.
		
		if self.running:
			wx.PostEvent(self, ReadyForNextSubrunEvent())
	
	def StopDataAcquisition(self, evt=None):
		self.running = False
		self.subrun = 0
		self.EndSubrun()
		
		while len(self.DAQthreads) > 0:		# won't be needing these any more.
			self.DAQthreads.pop()


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
	def __init__(self, process_info, output_window, owner_process, next_thread_delay=0, quit_event=None):
		threading.Thread.__init__(self)
		self.output_window = output_window
		self.owner_process = owner_process
		self.command = process_info
		self.next_thread_delay = next_thread_delay
		self.quit_event = quit_event

		self.time_to_quit = False

		self.timerthread = None			# used to count down to a hard kill if necessary

		self.start()				# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread '''
		if self.output_window:			# the user could have closed the window before the thread was ready...
			self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			self.pid = self.process.pid

			wx.PostEvent(self.output_window, NewDataEvent("Started thread with PID " + str(self.pid) + "\n"))	# post a message noting the PID of this thread
			#wx.PostEvent(self.output_window, NewDataEvent("using command '" + self.command + "'...\n"))

			if self.next_thread_delay > 0:
				# start a new thread to count down until the next one can be started.
				# need to do this since the reads from STDOUT are BLOCKING, that is,
				# they lock up the thread until they read the specified number of characters from STDOUT.
				# that means that we can't count on THIS thread to do the countdown.
				self.owner_process.timerThreads.append(TimerThread(self.next_thread_delay, self.owner_process))

			while True:
				self.process.poll()		# check if the process is still alive
				newdata = self.process.stdout.read(1)	# not every process is careful to spit things out with line breaks, so I can't use readline()

				if len(newdata) > 0:		# shouldn't be a problem since reads are BLOCKING in python, but it's always better to check
					wx.PostEvent(self.output_window, NewDataEvent(newdata))


				if (self.time_to_quit or self.process.returncode != None):
#					print "Data in buffer at last read: '" + newdata + "'"
					break


		# if something special is supposed to happen when this thread quits, do it.
		if self.quit_event:
			wx.PostEvent(self.owner_process, self.quit_event())
		
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
		
		if (self.process.returncode == None):			# it COULD happen that the process has already quit.
			self.process.send_signal(signal.SIGINT)		# first, try nicely.

			self.process.poll()
			if (self.process.returncode == None):		# if that doesn't work, give it a few seconds, then kill it the brute force way
				print "Process", self.pid, "not yet exited.  Waiting 5 seconds before hard kill..."
				self.timerthread = threading.Timer(5, self.HardKill)
				self.timerthread.start()
		else:
			# make sure there's nothing left in the buffer to read!
#			self.process.stdout.flush()
			(newdata, tmp) = self.process.communicate()
			if len(newdata) > 0 and self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent(newdata))
		
			if self.process.returncode != None:
				if (self.timerthread):
					self.timerthread.cancel()
				print "Process", self.pid, "has quit."
				if self.output_window:
					wx.PostEvent(self.output_window, NewDataEvent("\n\nThread terminated cleanly."))

	def HardKill(self):
		print "Thread", self.pid, "was unresponsive.  Checking if hard kill is necessary..."
		
#		self.process.stdout.flush()
#		(newdata, tmp) = self.process.communicate()
#		if len(newdata) > 0 and self.output_window:
#			wx.PostEvent(self.output_window, NewDataEvent(newdata))
		
		self.process.poll()
		
		if self.process.returncode == None:
			print "Thread", self.pid, "not responding to SIGINT.  Issuing SIGTERM..."
			self.process.terminate()
			
			time.sleep(2)
			
			if self.process.returncode == None:
				print "Thread", self.pid, "is deadlocked.  Issuing SIGKILL..."
				self.process.kill()
	
				print "Process", self.pid, "was killed."
				if self.output_window:
					wx.PostEvent(self.output_window, NewDataEvent("\n\nThread killed."))
			else:
				print "Thread", self.pid, "forcibly terminated but clean exit."
				if self.output_window:
					wx.PostEvent(self.output_window, NewDataEvent("\n\nThread terminated cleanly."))
		else:
			print "Process", self.pid, "has quit."
			if self.output_window:
				wx.PostEvent(self.output_window, NewDataEvent("\n\nThread terminated cleanly."))
		


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


