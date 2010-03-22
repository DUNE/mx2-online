"""
   Threads.py:
   Some custom threads that are used in the main
   run control.  Extracted here to prevent clutter
   in the main files.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import threading
import wx
import socket
import select
import fcntl
import errno
import subprocess

from mnvruncontrol.backend import Events
from mnvruncontrol.backend import ReadoutNode

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


