import wx
import sys
import wx.richtext as rt
import commands
import subprocess
import os
import threading
import datetime

ID_START = wx.NewId()

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
		menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")

		# bind the menu event to an event handler
		self.Bind(wx.EVT_MENU, self.OnTimeToClose, id=wx.ID_EXIT)

		# and put the menu on the menubar
		menuBar.Append(menu, "&File")
		self.SetMenuBar(menuBar)

		self.CreateStatusBar()
        

		# Now create the Panel to put the other controls on.
		panel = wx.Panel(self)

		l1 = wx.StaticText(panel, -1, "Run")
		t1 = wx.TextCtrl(panel, -1, "1337", size=(125, -1))
		self.t1 = t1

		l2 = wx.StaticText(panel, -1, "Subrun")
		t2 = wx.TextCtrl(panel, -1, "391", size=(125, -1))
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

		self.startButton = wx.Button(panel, ID_START, "Start DAQ Singleton")
		self.Bind(wx.EVT_BUTTON, self.StartDaqSingleton, self.startButton)
		
		self.stopButton = wx.Button(panel, wx.ID_STOP)
		self.Bind(wx.EVT_BUTTON, self.StopAll, self.stopButton)
		self.stopButton.Disable()		# disabled until the 'start' button is pressed

		space = 6
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
				    self.startButton, (0,0),
				    self.stopButton, (0,0)
				    ])
		border = wx.BoxSizer(wx.VERTICAL)
		border.Add(sizer, 0, wx.ALL, 25)
		panel.SetSizer(border)
		panel.SetAutoLayout(True)
		
		self.threads = []			# ET threads.  
		self.windows = []			# child windows opened by the process.


	def OnTimeToClose(self, evt):
		self.StopAll()

		for window in self.windows:
			window.Close()
		
		self.Close()

	def StartDaqSingleton(self, evt):
		while len(self.threads) > 0:		# if there are any leftover threads from a previous run, remove them
			self.threads.pop()
	
		while len(self.windows) > 0:		# same for extra windows
			window = self.windows.pop()
			window.Close()
			
		self.run     = self.t1.GetValue()
		self.subrun  = self.t2.GetValue()
		self.gates   = self.t3.GetValue()
		self.runMode = self.t4.GetValue()
		self.febs    = self.t5.GetValue()

		now = datetime.datetime.today()
		
		self.ETNAME = 'MN_%08d_%04d_numib_v04_%02d%02d%02d%02d%02d' % (int(self.run), int(self.subrun), now.year, now.month, now.day, now.hour, now.minute)
		#self.ETNAME='testme'
		print self.ETNAME

		self.OUTFL = self.ETNAME + '.dat'
		print self.OUTFL

		self.StartETSys()
		self.StartETMon()
		self.StartEBSvc()

		self.startButton.Disable()
		self.stopButton.Enable()

	def StartETSys(self):

		EVENT_SIZE=2048 
		FRAMES=8
		EVENTS=int(self.gates)*FRAMES*int(self.febs)

		etSysFrame = OutputFrame(self, "ET System")
		etSysFrame.Show(True)
		
		self.windows.append( etSysFrame )
		self.threads.append( ETThread(["/home/jeremy/code/mnvruncontrol/scripts/test.sh"], etSysFrame) )

#		self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v','-f','test','-n',str(EVENTS),'-s',str(EVENT_SIZE)], stdout=PIPE)
#		self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v','-f',str(self.ETNAME),'-n',str(EVENTS),'-s',str(EVENT_SIZE)], stdout=PIPE)
#		self.et_sys = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_start','-v -f ./'+self.ETNAME+' -n '+str(EVENTS)+' -s '+str(EVENT_SIZE)], stdout=PIPE)
#		self.et_sys = Popen(['./start_et_system',str(self.ETNAME),str(self.febs),str(self.gates)], stdout=PIPE)


	def StartETMon(self):
		etMonFrame = OutputFrame(self, "ET Monitor")
		etMonFrame.Show(True)

		self.windows.append( etMonFrame )
		self.threads.append( ETThread(["/home/jeremy/code/mnvruncontrol/scripts/test.sh"], etMonFrame) )		

#		#self.et_mon = Popen(['$ET_HOME/Linux-x86_64-64/bin/et_monitor','-f',str(self.ETNAME)], stdout=PIPE)
#		#self.etMonFrame.rtc.WriteText(self.et_mon.communicate()[0])

#		script_string = '%s/runthedaq/start_et_monitor' % os.environ['DAQROOT']
#		print script_string
#		subprocess.Popen(['xterm','-geometry','88x60+890+1','-e',str(script_string),str(self.ETNAME)])

	def StartEBSvc(self):
		ebSvcFrame = OutputFrame(self, "EB Service")
		ebSvcFrame.Show(True)

		self.windows.append( ebSvcFrame )
		self.threads.append( ETThread(["/home/jeremy/code/mnvruncontrol/scripts/test.sh"], ebSvcFrame) )		

#		script_string = '%s/runthedaq/start_eb_service' % os.environ['DAQROOT']
#		print script_string
#		subprocess.Popen(['xterm','-geometry','88x28+380+421','-e',str(script_string),str(self.ETNAME),str(self.OUTFL)])

	def StopAll(self, evt):
		while len(self.threads) > 0:
			thread = self.threads.pop()	# pull the threads out of the list one by one.  this way they go out of scope and are garbage collected.
			thread.Abort()
			
		self.stopButton.Disable()
		self.startButton.Enable()

		while len(self.windows) > 0:		# remove windows from the list and close them.
			window = self.windows.pop()
			window.Close()

class OutputFrame(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, -1, title, size=(400,300)) #, style = wx.VSCROLL | wx.SIMPLE_BORDER)
		self.textarea = rt.RichTextCtrl(self, -1, style = rt.RE_CENTER_CARET)
		self.textarea.SetEditable(False)

		self.Connect(-1, -1, EVT_NEWDATA_ID, self.OnNewData)
		
	def OnNewData(self, data_event):
		self.textarea.AppendText(data_event.data)
		self.textarea.LineBreak()
		self.textarea.ScrollIntoView(self.textarea.GetLastPosition(), wx.WXK_DOWN)		# scroll down until you can see the last line.
		

class ETThread(threading.Thread):
	""" A thread for an ET process. """
	def __init__(self, process_info, parent_window):
		threading.Thread.__init__(self)
		self.parent_window = parent_window
		self.process = subprocess.Popen(process_info, stdout=subprocess.PIPE)
		self.pid = self.process.pid

		self.time_to_quit = False

		wx.PostEvent(self.parent_window, NewDataEvent("Started thread with PID " + str(self.pid)))	# post a message noting the PID of this thread
		
		self.start()				# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread'''
		while (self.process.returncode == None):
			self.process.poll()		# check if the process is still alive
			
			newdata = self.process.stdout.readline()
			if (self.time_to_quit == False):
				wx.PostEvent(self.parent_window, NewDataEvent(newdata[0:-1]))	# strip off the EOL character
			else:
				break
		
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
		
		if (self.process.returncode == None):		# it COULD happen that the process has already quit.
			self.process.terminate()		# first, try nicely.

			self.process.poll()
			if (self.process.returncode == None):		# if that doesn't work, kill it the brute force way
				self.process.kill()

EVT_NEWDATA_ID = wx.NewId()
class NewDataEvent(wx.PyEvent):
	""" An event to carry data between the threaded processes and the windows built to display their output. """
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.data = data	
		self.SetEventType(EVT_NEWDATA_ID)

class MyApp(wx.App):
	def OnInit(self):
		frame = MyFrame(None, "Run Control")
		
		self.SetTopWindow(frame)

		frame.Show(True)
		return True

if __name__ == '__main__':		# make sure that this file isn't being included somewhere else
	app = MyApp(redirect=True)
	app.MainLoop()

