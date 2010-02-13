#!/usr/bin/python

import wx
from wx.lib.wordwrap import wordwrap
import subprocess
import os
import sys
import signal
import threading

import RunSeries

class DataAcquisitionManager(wx.EvtHandler):
	def __init__(self):
		wx.EvtHandler.__init(self)
		
		self.DAQthreads = []
		self.timerThreads = []
		self.DAQthreadStarters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartDAQ]
#		self.DAQthreadStarters = [self.StartTestProcess, self.StartTestProcess, self.StartTestProcess]
		self.current_DAQ_thread = 0			# the next thread to start
		self.windows = []					# child windows opened by the process.
		self.runseries = None
		self.

		self.Connect(-1, -1, EVT_THREAD_READY_ID, self.StartNextThread)
		self.Connect(-1, -1, EVT_DAQQUIT_ID, self.DAQShutdown)		# if the DAQ process quits, everything should be stopped.
		
	
	def StartDataAcquisition(self, evt):
		if not isinstance(self.runseries, RunSeries.RunSeries):
			raise ValueError("No run series defined!")

		try:
			self.nextrun = self.runseries.next()
		except StopIteration:		# no more runs left!  return to main panel.
			return
		
		while len(self.DAQthreads) > 0:		# if there are any leftover threads from a previous run, remove them
			self.DAQthreads.pop()
	
		self.CloseAllWindows()			# same for the windows

		now = datetime.datetime.utcnow()
	
		self.ETNAME = '%s_%08d_%04d_%s_v04_%02d%02d%02d%02d%02d' % (self.detectorCodes[self.detector], int(self.run), int(self.subrun), self.RunningModes[self.runMode], now.year % 100, now.month, now.day, now.hour, now.minute)

		self.OUTFL = self.ETNAME + '.dat'

		self.startButton.Disable()
		self.stopButton.Enable()

		self.SetStatusText("RUNNING", 1)
		self.runningIndicator.SetBitmap(self.onImage)
		self.StartNextThread()			# starts the first thread.  the rest will be started in turn as ThreadReadyEvents are received by this window.

	def StartETSys(self):
		EVENT_SIZE=2048 
		FRAMES=8
		EVENTS=int(self.gates)*FRAMES*int(self.febs)

		etSysFrame = OutputFrame(self, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)
		self.closeAllButton.Enable()

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d" % (os.environ["ET_HOME"], self.etSystemFileLocation, self.ETNAME, EVENTS, EVENT_SIZE)

		self.windows.append( etSysFrame )
		self.DAQthreads.append( DAQthread(etsys_command, output_window=etSysFrame, owner_window=self, next_thread_delay=2) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		self.closeAllButton.Enable()
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s" % (os.environ["ET_HOME"], self.etSystemFileLocation, self.ETNAME)
		self.windows.append( etMonFrame )
		self.DAQthreads.append( DAQthread(etmon_command, output_window=etMonFrame, owner_window=self, next_thread_delay=2) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)
		self.closeAllButton.Enable()

		eb_command = '%s/bin/event_builder %s/%s %s/%s' % (os.environ['DAQROOT'], self.etSystemFileLocation, self.ETNAME, self.rawdataLocation, self.OUTFL)

		self.windows.append( ebSvcFrame )
		self.DAQthreads.append( DAQthread(eb_command, output_window=ebSvcFrame, owner_window=self, next_thread_delay=15) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		self.closeAllButton.Enable()

		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d" % (os.environ["DAQROOT"], self.ETNAME, self.gates, self.runMode, self.run, self.subrun)

		self.windows.append(daqFrame)
		self.DAQthreads.append( DAQthread(daq_command, output_window=daqFrame, owner_window=self, quit_event=DAQQuitEvent) )

	def StartTestProcess(self):
		frame = OutputFrame(self, "test process", window_size=(600,600), window_pos=(1200,200))
		frame.Show(True)
		self.closeAllButton.Enable()

		command = "/home/jeremy/code/mnvruncontrol/scripts/test.sh"

		self.windows.append(frame)
		self.DAQthreads.append( DAQthread(command, output_window=frame, owner_window=self, next_thread_delay=3) )
		
	def CloseWindows(self):
		while len(self.windows) > 0:		
			window = self.windows.pop()
			
			if window:		# wx guarantees that 'dead' windows will evaluate to False
				window.Destroy()

	def StopDataAcquisition(self):
		while len(self.DAQthreads) > 0:
			thread = self.DAQthreads.pop()	# pull the threads out of the list one by one.  this way they go out of scope and are garbage collected.
			thread.Abort()
			
		while len(self.timerThreads) > 0:
			thread = self.timerThreads.pop()
			thread.Abort()

		self.current_DAQ_thread = 0			# reset the thread counter in case the user wants to start another subrun

	def StartNextThread(self, evt=None):
		if self.current_ET_thread < len(self.DAQthreadStarters):
			self.DAQthreadStarters[self.current_ET_thread]()
			self.current_ET_thread += 1
		else:
			print "Thread count too high"

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
	def __init__(self, process_info, output_window, owner_window, next_thread_delay=0, quit_event=None):
		threading.Thread.__init__(self)
		self.output_window = output_window
		self.owner_window = owner_window
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
				self.owner_window.timerThreads.append(TimerThread(self.next_thread_delay, self.owner_window))

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
			wx.PostEvent(self.owner_window, self.quit_event())
		
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

