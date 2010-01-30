import wx
import sys
import wx.richtext as rt
import commands
import subprocess
import os
import fcntl
import threading
import datetime
import time
import shelve

# some constants for configuration
RUN_SUBRUN_DB_LOCATION = "/work/conditions"
LOGFILE_LOCATION = "/work/data/logs"

ET_SYSTEM_LOCATION = "/work/data/etsys"
RAW_DATA_LOCATION = "/work/data/rawdata"

ID_START = wx.NewId()

#########################################################
#    MyFrame
#########################################################

class MainFrame(wx.Frame):
	"""
	This is MyFrame.  It just shows a few controls on a wxPanel,
	and has a simple menu.
	"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title,
				      pos=(0, 0), size=(600, 400))

		# Create the menubar
		menuBar = wx.MenuBar()

		# and a menu 
		menu = wx.Menu()

		# add an item to the menu, using \tKeyName automatically
		# creates an accelerator, the third param is some help text
		# that will show up in the statusbar
		menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit the run control")

		# bind the menu event to an event handler
		self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

		# and put the menu on the menubar
		menuBar.Append(menu, "&File")
		self.SetMenuBar(menuBar)

		self.statusbar = self.CreateStatusBar(2)
		self.SetStatusWidths([-6, -1])
		self.SetStatusText("STOPPED", 1)
        

		# Now create the Panel to put the other controls on.
		panel = wx.Panel(self)

		runEntryLabel = wx.StaticText(panel, -1, "Run")
		self.runEntry = wx.SpinCtrl(panel, -1, '0', size=(125, -1), min=0, max=100000)
		self.Bind(wx.EVT_SPINCTRL, self.CheckRunNumber, self.runEntry)
		self.runEntry.Disable()

		subrunEntryLabel = wx.StaticText(panel, -1, "Subrun")
		self.subrunEntry = wx.SpinCtrl(panel, -1, '0', size=(125, -1), min=0, max=100000)
		self.subrunEntry.Disable()

		gatesEntryLabel = wx.StaticText(panel, -1, "Gates")
		self.gatesEntry = wx.SpinCtrl(panel, -1, "10", size=(125, -1), min=1, max=10000)

		runModeEntryLabel = wx.StaticText(panel, -1, "Run Mode")
		RunModeChoices = ["One shot", "NuMI", "Cosmics", "Pure light injection", "Mixed beam/pedestal", "Mixed beam/light injection"]
		self.runModeEntry =  wx.Choice(panel, -1, choices=RunModeChoices)


		febsEntryLabel = wx.StaticText(panel, -1, "FEBs")
		self.febsEntry = wx.SpinCtrl(panel, -1, "4", size=(125, -1), min=1, max=10000)

		self.startButton = wx.Button(panel, ID_START, "Start")
		self.Bind(wx.EVT_BUTTON, self.StartDaqSingleton, self.startButton)
		self.startButton.Disable()
		
		self.stopButton = wx.Button(panel, wx.ID_STOP)
		self.Bind(wx.EVT_BUTTON, self.DAQShutdown, self.stopButton)
		self.stopButton.Disable()		# disabled until the 'start' button is pressed

		self.closeAllButton = wx.Button(panel, wx.ID_CLOSE, "Close ET/DAQ windows")
		self.Bind(wx.EVT_BUTTON, self.CloseAllWindows, self.closeAllButton)
		self.closeAllButton.Disable()

		configSizer = wx.GridSizer(5, 2, 10, 10)
 		configSizer.AddMany([ runEntryLabel,      (self.runEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                      subrunEntryLabel,   (self.subrunEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                      gatesEntryLabel,    (self.gatesEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                      runModeEntryLabel,  (self.runModeEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL),
		                      febsEntryLabel,     (self.febsEntry, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL) ])
		configBoxSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Run Configuration"), wx.VERTICAL)
		configBoxSizer.Add(configSizer, 1, wx.EXPAND)

		controlBoxSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Run Control"), wx.VERTICAL)
		controlBoxSizer.AddMany( [ (self.startButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.stopButton, 1, wx.ALIGN_CENTER_HORIZONTAL),
		                           (self.closeAllButton, 1, wx.ALIGN_CENTER_HORIZONTAL) ] )

		topSizer = wx.BoxSizer(wx.HORIZONTAL)
		topSizer.AddMany( [(configBoxSizer, 1, wx.EXPAND | wx.RIGHT, 5), (controlBoxSizer, 1, wx.EXPAND | wx.LEFT, 5)] )

		self.logFileButton = wx.Button(panel, -1, "View most recent log")
		self.Bind(wx.EVT_BUTTON, self.ShowLogFile, self.logFileButton)
		self.logFileButton.Disable()

		logFileViewOldButton = wx.Button(panel, -1, "View older logs...")
		self.Bind(wx.EVT_BUTTON, self.OlderLogFileSelection, logFileViewOldButton)
		
		logBoxSizer = wx.StaticBoxSizer(wx.StaticBox(panel, -1, "Logs"), orient=wx.VERTICAL)
		logBoxSizer.AddMany( [self.logFileButton, logFileViewOldButton] )
		
		globalSizer = wx.BoxSizer(wx.VERTICAL)
		globalSizer.Add(topSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)
		globalSizer.Add(logBoxSizer, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM | wx.TOP | wx.LEFT | wx.RIGHT, border=10)

		panel.SetSizer(globalSizer)
		panel.SetAutoLayout(True)
		self.Layout()
		
		self.ETthreads = []
		self.timerThreads = []
		self.ETthreadStarters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartDAQ]
		self.current_ET_thread = 0			# the next thread to start
		self.windows = []					# child windows opened by the process.
		self.logfilename = "/etc/X11/xorg.conf"

		self.GetNextRunSubrun()
		self.Connect(-1, -1, EVT_THREAD_READY_ID, self.StartNextThread)
		self.Connect(-1, -1, EVT_DAQQUIT_ID, self.DAQShutdown)		# if the DAQ process quits, everything should be stopped.

	def OnTimeToClose(self, evt):
		self.StopAll()

		self.CloseAllWindows()

		self.Close()

	def GetNextRunSubrun(self, evt=None):
		if not os.path.exists(RUN_SUBRUN_DB_LOCATION + "/last_run_subrun.db"):
			errordlg = wx.MessageDialog( None, "The database storing the run/subrun data appears to be missing.  Run/subrun will be set to 1...", "Run/subrun database missing", wx.OK | wx.ICON_WARNING )
			errordlg.ShowModal()

			self.runEntry.SetRange(1, 100000)
			self.runEntry.SetValue(1)
			self.subrunEntry.SetValue(1)
		else:
			d = shelve.open('last_run_subrun.db', 'r')

			if d.has_key('run') and d.has_key('subrun'):
				self.runEntry.SetRange(int(d['run']),100000)
				self.runEntry.SetValue(int(d['run']))
				self.subrunEntry.SetValue(int(d['subrun']))

			else:
				errordlg = wx.MessageDialog( None, "The database storing the run/subrun data appears to be corrupted.  Run/subrun will be set to 1...", "Run/subrun database corrupted", wx.OK | wx.ICON_WARNING )
				errordlg.ShowModal()

				self.runEntry.SetRange(1, 100000)
				self.runEntry.SetValue(1)
				self.subrunEntry.SetValue(1)

			d.close()

		# the minimum subrun allowed for the lowest run.  
		# if the user raises the run number, the subrun will be returned to 1,
		# so if s/he subsequently lowers it again, we need to know what to set the the minimum
		# back to.
		self.minRunSubrun = self.subrunEntry.GetValue()		

		self.runEntry.Enable()
		self.startButton.Enable()
	
	def StoreNextRunSubrun(self):
		db = shelve.open(RUN_SUBRUN_DB_LOCATION + "/last_run_subrun.db")
		db["run"] = self.runEntry.GetValue()
		db["subrun"] = self.subrunEntry.GetValue()
		db.close()
		
	def CheckRunNumber(self, evt=None):
		if self.runEntry.GetValue() < self.runEntry.GetMin():
			self.runEntry.SetValue(self.runEntry.GetMin())
		
		if self.runEntry.GetValue() > self.runEntry.GetMax():
			self.runEntry.SetValue(self.runEntry.GetMax())
		
		if self.runEntry.GetValue() == self.runEntry.GetMin():
			self.subrunEntry.SetValue(self.minRunSubrun)
		else:
			self.subrunEntry.SetValue(1)

	def StartDaqSingleton(self, evt):
		while len(self.ETthreads) > 0:		# if there are any leftover threads from a previous run, remove them
			self.ETthreads.pop()
	
		self.CloseAllWindows()			# same for the windows

		self.runEntry.Disable()
		self.subrunEntry.Disable()
		self.gatesEntry.Disable()
		self.runModeEntry.Disable()
		self.febsEntry.Disable()
			
		self.run     = int(self.runEntry.GetValue())
		self.subrun  = int(self.subrunEntry.GetValue())
		self.gates   = int(self.gatesEntry.GetValue())
		self.runMode = int(self.runModeEntry.GetSelection())
		self.febs    = int(self.febsEntry.GetValue())

		now = datetime.datetime.today()
		
		self.ETNAME = 'MN_%08d_%04d_numib_v04_%02d%02d%02d%02d%02d' % (int(self.run), int(self.subrun), now.year % 100, now.month, now.day, now.hour, now.minute)
		#self.ETNAME='testme'
		#print self.ETNAME

		self.OUTFL = self.ETNAME + '.dat'
		#print self.OUTFL

		self.startButton.Disable()
		self.stopButton.Enable()

		self.SetStatusText("RUNNING", 1)
		self.StartNextThread()			# starts the first thread.  the rest will be started in turn as ThreadReadyEvents are received by this window.

	def StartETSys(self):
		EVENT_SIZE=2048 
		FRAMES=8
		EVENTS=int(self.gates)*FRAMES*int(self.febs)

		etSysFrame = OutputFrame(self, "ET system", window_size=(600,200), window_pos=(600,0))
		etSysFrame.Show(True)
		self.closeAllButton.Enable()

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d" % (os.environ["ET_HOME"], ET_SYSTEM_LOCATION, self.ETNAME, EVENTS, EVENT_SIZE)

		self.windows.append( etSysFrame )
		self.ETthreads.append( ETThread(etsys_command, output_window=etSysFrame, owner_window=self, next_thread_delay=2) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		self.closeAllButton.Enable()
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s" % (os.environ["ET_HOME"], ET_SYSTEM_LOCATION, self.ETNAME)
		self.windows.append( etMonFrame )
		self.ETthreads.append( ETThread(etmon_command, output_window=etMonFrame, owner_window=self, next_thread_delay=2) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)
		self.closeAllButton.Enable()

		eb_command = '%s/bin/event_builder %s/%s %s/%s' % (os.environ['DAQROOT'], ET_SYSTEM_LOCATION, self.ETNAME, RAW_DATA_LOCATION, self.OUTFL)

		self.windows.append( ebSvcFrame )
		self.ETthreads.append( ETThread(eb_command, output_window=ebSvcFrame, owner_window=self, next_thread_delay=15) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		self.closeAllButton.Enable()

		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d" % (os.environ["DAQROOT"], self.ETNAME, self.gates, self.runMode, self.run, self.subrun)

		self.windows.append(daqFrame)
		self.ETthreads.append( ETThread(daq_command, output_window=daqFrame, owner_window=self, quit_event=DAQQuitEvent) )

	def StopAll(self, evt=None):
		while len(self.ETthreads) > 0:
			thread = self.ETthreads.pop()	# pull the threads out of the list one by one.  this way they go out of scope and are garbage collected.
			thread.Abort()
			
		while len(self.timerThreads) > 0:
			thread = self.timerThreads.pop()
			thread.Abort()
			
		self.SetStatusText("STOPPED", 1)

		self.stopButton.Disable()
		self.startButton.Enable()

		self.runEntry.Enable()
		self.gatesEntry.Enable()
		self.runModeEntry.Enable()
		self.febsEntry.Enable()

		self.current_ET_thread = 0			# reset the thread counter in case the user wants to start another subrun

	def StartNextThread(self, evt=None):
		if self.current_ET_thread < len(self.ETthreadStarters):
			self.ETthreadStarters[self.current_ET_thread]()
			self.current_ET_thread += 1
		else:
			print "Thread count too high"
			
	def ShowLogFile(self, evt=None):
		if (self.logfilename):
			logdlg = LogFrame(self, self.logfilename)
			logdlg.Show(True)
		else:
			print "Whoops!  Log file button shouldn't be enabled before log file is available..."

	def OlderLogFileSelection(self, evt=None):
		errordlg = wx.MessageDialog( None, "This feature is not yet implemented.", "Not yet implemented", wx.OK | wx.ICON_WARNING )
		errordlg.ShowModal()


	def CloseAllWindows(self, evt=None):
		while len(self.windows) > 0:		
			window = self.windows.pop()
			
			if window:		# wx guarantees that 'dead' windows will evaluate to False
				window.Destroy()

		self.closeAllButton.Disable()
	
	def DAQShutdown(self, evt=None):
		self.subrunEntry.SetValue(self.subrunEntry.GetValue() + 1)
		self.runEntry.SetRange(self.runEntry.GetValue(), 100000)
		self.StoreNextRunSubrun()
		
		self.logfilename = LOGFILE_LOCATION + "/" + self.ETNAME + ".txt"
		self.logFileButton.Enable()
		
		self.StopAll()
	

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
		#self.textarea.LineBreak()
		#self.textarea.ScrollIntoView(self.textarea.GetLastPosition(), wx.WXK_DOWN)		# scroll down until you can see the last line.
		

#########################################################
#   LogFrame
#########################################################

class LogFrame(wx.Frame):
	def __init__(self, parent, filename):
		wx.Frame.__init__(self, parent, -1, "DAQ log: " + filename, size=(800,600))

		panel = wx.Panel(self)

		textarea = wx.TextCtrl(panel, -1, style = wx.TE_MULTILINE | wx.TE_READONLY)
		textarea.SetEditable(False)

		with open(filename) as f:
			for line in f:
				textarea.AppendText(line)

		
		okButton = wx.Button(panel, wx.ID_OK)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(textarea, 1, wx.EXPAND | wx.ALIGN_TOP)
		sizer.Add(okButton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)
		
		panel.SetSizer(sizer)
		
		self.Bind(wx.EVT_BUTTON, self.CloseOut, okButton)
		
	def CloseOut(self, evt=None):
		self.Close()
	

#########################################################
#   ETThread
#########################################################

class ETThread(threading.Thread):
	""" A thread for an ET/DAQ process. """
	def __init__(self, process_info, output_window, owner_window, next_thread_delay=0, quit_event=None):
		threading.Thread.__init__(self)
		self.output_window = output_window
		self.owner_window = owner_window
		self.command = process_info
		self.next_thread_delay = next_thread_delay
		self.quit_event = quit_event

		self.time_to_quit = False

		self.start()				# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread'''
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
				newdata = self.process.stdout.read(50)	# not every process is careful to spit things out with line breaks, so I can't use readline()

				if len(newdata) > 0:		# shouldn't be a problem since reads are BLOCKING in python, but it's always better to check
					wx.PostEvent(self.output_window, NewDataEvent(newdata))


				if (self.time_to_quit or self.process.returncode != None) and newdata == "":
					break

		print "Process", self.pid, "has quit."
		if self.quit_event:
			wx.PostEvent(self.owner_window, self.quit_event())
		
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
		
		if (self.process.returncode == None):		# it COULD happen that the process has already quit.
			self.process.terminate()		# first, try nicely.

			self.process.poll()
			if (self.process.returncode == None):		# if that doesn't work, kill it the brute force way
				self.process.kill()

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
#   MyApp
#########################################################

class MyApp(wx.App):
	def OnInit(self):
		try:
			temp = os.environ["DAQROOT"]
			temp = os.environ["ET_HOME"]
		except KeyError:
			errordlg = wx.MessageDialog( None, "Your environment appears to be missing the necessary configuration.  Did you source the appropriate setup script(s) before starting the run control?", "Incorrect environment", wx.OK | wx.ICON_ERROR )
			errordlg.ShowModal()
			return False
		else:
			frame = MainFrame(None, "Run Control")
			self.SetTopWindow(frame)
			frame.Show(True)
			return True


#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MyApp(redirect=False)
	app.MainLoop()

