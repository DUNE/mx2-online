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

ID_START = wx.NewId()

#########################################################
#    MyFrame
#########################################################

class MyFrame(wx.Frame):
	"""
	This is MyFrame.  It just shows a few controls on a wxPanel,
	and has a simple menu.
	"""
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title,
				      pos=(0, 0), size=(600, 600))

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

		l1 = wx.StaticText(panel, -1, "Run")
                t1 = wx.SpinCtrl(panel, -1, '0', size=(125, -1), min=0, max=100000)
                t1.Disable()
		self.t1 = t1

		l2 = wx.StaticText(panel, -1, "Subrun")
                t2 = wx.SpinCtrl(panel, -1, '0', size=(125, -1), min=0, max=100000)
                t2.Disable()
		self.t2 = t2

		l3 = wx.StaticText(panel, -1, "Gates")
		t3 = wx.TextCtrl(panel, -1, "10", size=(125, -1))
		self.t3 = t3

		l4 = wx.StaticText(panel, -1, "Run Mode")
		t4 = wx.TextCtrl(panel, -1, "0", size=(125, -1))
		self.t4 = t4

		l5 = wx.StaticText(panel, -1, "FEBs")
		t5 = wx.TextCtrl(panel, -1, "4", size=(125, -1))
		self.t5 = t5

                self.getLastButton = wx.Button(panel, -1, 'Get Last Run/Subrun')
                self.Bind(wx.EVT_BUTTON, self.GetLastRunSubrun, self.getLastButton)

		self.startButton = wx.Button(panel, ID_START, "Start DAQ Singleton")
		self.Bind(wx.EVT_BUTTON, self.StartDaqSingleton, self.startButton)
		self.startButton.Disable()
		
		self.stopButton = wx.Button(panel, wx.ID_STOP)
		self.Bind(wx.EVT_BUTTON, self.StopAll, self.stopButton)
		self.stopButton.Disable()		# disabled until the 'start' button is pressed

		self.closeAllButton = wx.Button(panel, wx.ID_CLOSE, "Close windows")
		self.Bind(wx.EVT_BUTTON, self.CloseAllWindows, self.closeAllButton)
		self.closeAllButton.Disable()

		space = 10
		#bsizer = wx.BoxSizer(wx.VERTICAL)
		#bsizer.Add(b, 0, wx.GROW|wx.ALL, space)
		#bsizer.Add(b2, 0, wx.GROW|wx.ALL, space)
		#bsizer.Add(b3, 0, wx.GROW|wx.ALL, space)

		sizer = wx.FlexGridSizer(cols=2, hgap=space, vgap=space)
		sizer.AddMany([ l1, t1,
				    l2, t2,
				    l3, t3,
				    l4, t4,
				    l5, t5,  
				    self.getLastButton, (0,0),
				    self.startButton, (0,0),
				    self.stopButton, self.closeAllButton
				    ])
		border = wx.BoxSizer(wx.VERTICAL)
		border.Add(sizer, 0, wx.ALL, 25)
		panel.SetSizer(border)
		panel.SetAutoLayout(True)
		
		self.threads = []			# ET threads.
		self.thread_starters = [self.StartETSys, self.StartETMon, self.StartEBSvc, self.StartDAQ]
		self.current_thread = 0			# the next thread to start
		self.windows = []			# child windows opened by the process.

		self.Connect(-1, -1, EVT_THREAD_READY_ID, self.StartNextThread)
		self.Connect(-1, -1, EVT_DAQQUIT_ID, self.StopAll)		# if the DAQ process quits, everything should be stopped.

	def OnTimeToClose(self, evt):
		self.StopAll()

		self.CloseAllWindows()

		self.Close()

        def GetLastRunSubrun(self, evt=None):

            if not os.path.exists('last_run_subrun.db'):

                print 'File \'last_run_subrun.db\' does not exist'

            else:

                d = shelve.open('last_run_subrun.db', 'r')

                if d.has_key('run') and d.has_key('subrun'):

                    self.t1.SetRange(int(d['run']),100000)
                    self.t1.SetValue(int(d['run']))
                    self.t2.SetValue(int(d['subrun']))

                    self.t1.Enable()
                    self.getLastButton.Disable()
                    self.startButton.Enable()

                else:

                    print '\'last_run_subrun.db\' does not contain run & subrun'

                d.close()

	def StartDaqSingleton(self, evt):
		while len(self.threads) > 0:		# if there are any leftover threads from a previous run, remove them
			self.threads.pop()
	
		self.CloseAllWindows()			# same for the windows

                self.t1.Disable()
                self.t2.Disable()
                self.t3.Disable()
                self.t4.Disable()
                self.t5.Disable()
			
		self.run     = int(self.t1.GetValue())
		self.subrun  = int(self.t2.GetValue())
		self.gates   = int(self.t3.GetValue())
		self.runMode = int(self.t4.GetValue())
		self.febs    = int(self.t5.GetValue())

		now = datetime.datetime.today()
		
		self.ETNAME = 'MN_%08d_%04d_numib_v04_%02d%02d%02d%02d%02d' % (int(self.run), int(self.subrun), now.year % 100, now.month, now.day, now.hour, now.minute)
		#self.ETNAME='testme'
		#print self.ETNAME

		self.OUTFL = self.ETNAME + '.dat'
		#print self.OUTFL

		self.etSysLocation = "/work/data/etsys"
		self.rawDataLocation = "/work/data/rawdata"

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

		etsys_command = "%s/Linux-x86_64-64/bin/et_start -v -f %s/%s -n %d -s %d" % (os.environ["ET_HOME"], self.etSysLocation, self.ETNAME, EVENTS, EVENT_SIZE)

		self.windows.append( etSysFrame )
		self.threads.append( ETThread(etsys_command, output_window=etSysFrame, owner_window=self, next_thread_delay=2) ) 

	def StartETMon(self):
		etMonFrame = OutputFrame(self, "ET monitor", window_size=(600,600), window_pos=(600,200))
		etMonFrame.Show(True)
		self.closeAllButton.Enable()
		
		etmon_command = "%s/Linux-x86_64-64/bin/et_monitor -f %s/%s" % (os.environ["ET_HOME"], self.etSysLocation, self.ETNAME)
		self.windows.append( etMonFrame )
		self.threads.append( ETThread(etmon_command, output_window=etMonFrame, owner_window=self, next_thread_delay=2) )

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self, "Event builder service", window_size=(600,200), window_pos=(1200,0))
		ebSvcFrame.Show(True)
		self.closeAllButton.Enable()

		eb_command = '%s/bin/event_builder %s/%s %s/%s' % (os.environ['DAQROOT'], self.etSysLocation, self.ETNAME, self.rawDataLocation, self.OUTFL)

		self.windows.append( ebSvcFrame )
		self.threads.append( ETThread(eb_command, output_window=ebSvcFrame, owner_window=self, next_thread_delay=15) )	

	def StartDAQ(self):
		daqFrame = OutputFrame(self, "THE DAQ", window_size=(600,600), window_pos=(1200,200))
		daqFrame.Show(True)
		self.closeAllButton.Enable()

		daq_command = "%s/bin/minervadaq -et %s -g %d -m %d -r %d -s %d" % (os.environ["DAQROOT"], self.ETNAME, self.gates, self.runMode, self.run, self.subrun)

		self.windows.append(daqFrame)
		self.threads.append( ETThread(daq_command, output_window=daqFrame, owner_window=self, quit_event=DAQQuitEvent) )

	def StopAll(self, evt=None):
		while len(self.threads) > 0:
			thread = self.threads.pop()	# pull the threads out of the list one by one.  this way they go out of scope and are garbage collected.
			thread.Abort()
			
		self.SetStatusText("STOPPED", 1)

		self.stopButton.Disable()
		self.startButton.Enable()

                self.t1.Enable()
                self.t3.Enable()
                self.t4.Enable()
                self.t5.Enable()

		self.current_thread = 0			# reset the thread counter in case the user wants to start another subrun

	def StartNextThread(self, evt=None):
		if self.current_thread < len(self.thread_starters):
			self.thread_starters[self.current_thread]()
			self.current_thread += 1

	def CloseAllWindows(self, evt=None):
		while len(self.windows) > 0:		
			window = self.windows.pop()
			
			if window:		# wx guarantees that 'dead' windows will evaluate to False
				window.Destroy()

		self.closeAllButton.Disable()

		

#########################################################
#   OutputFrame
#########################################################

class OutputFrame(wx.Frame):
	def __init__(self, parent, title, window_size=(400,300), window_pos=None):
		if window_pos:
			wx.Frame.__init__(self, parent, -1, title, size=window_size)
		else:
			wx.Frame.__init__(self, parent, -1, title, size=window_size, pos=window_pos)
		self.textarea = rt.RichTextCtrl(self, -1)
		self.textarea.SetEditable(False)

		self.Connect(-1, -1, EVT_NEWDATA_ID, self.OnNewData)
		
	def OnNewData(self, data_event):
		self.textarea.AppendText(data_event.data)
		#self.textarea.LineBreak()
		#self.textarea.ScrollIntoView(self.textarea.GetLastPosition(), wx.WXK_DOWN)		# scroll down until you can see the last line.
		
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
				timer = TimerThread(self.next_thread_delay, self.owner_window)	

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
		self.start()

	def run(self):
		time.sleep(self.time)

		if (self.postback_window):		# make sure the user didn't close the window while we were waiting
			wx.PostEvent(self.postback_window, ThreadReadyEvent())

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
		frame = MyFrame(None, "Run Control")
		
		self.SetTopWindow(frame)

		frame.Show(True)
		return True


#########################################################
#   Main execution
#########################################################


if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MyApp(redirect=False)
	app.MainLoop()

