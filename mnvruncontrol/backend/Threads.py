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
import os
import re
import time
import socket
import select
import fcntl
import errno
import subprocess
from Queue import Queue

from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.backend import Events
from mnvruncontrol.backend import ReadoutNode

#########################################################
#   DAQthread
#########################################################

class DAQthread(threading.Thread):
	""" A thread for an ET/DAQ process. """
	def __init__(self, process_info, process_identity, output_window, owner_process, env, next_thread_delay=0, is_essential_service=False):
		threading.Thread.__init__(self)
		self.process_identity = process_identity
		self.output_window = output_window
		self.owner_process = owner_process
		self.environment = env
		self.command = process_info
		self.next_thread_delay = next_thread_delay
		self.is_essential_service = is_essential_service
		self.name = self.command.split()[0] + "Thread"
		self.process = None
		self.daemon = True				# this way the process will end when the main thread does

		self.write_output = True			# if process output should be relayed to the window
		self.time_to_quit = False
		self.issued_quit = False			# has the subprocess been instructed to stop?
		self.have_cleaned_up = False		# have we done a cleanup read of output text yet?

		self.start()					# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread. '''
		self.process = subprocess.Popen(self.command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.environment)
		self.pid = self.process.pid

		if self.next_thread_delay > 0:
			# start a new thread to count down until the next DAQ process can be started.
			self.owner_process.timerThreads.append(TimerThread(self.next_thread_delay, self.owner_process))

		if self.output_window and self.write_output:
			wx.PostEvent(self.output_window, Events.NewDataEvent(data="Started thread with PID " + str(self.pid) + "\n"))	# post a message noting the PID of this thread

		while self.process.poll() is None:
			# no busy-waiting.
			time.sleep(0.1)
			
			# if it's time to quit, the process should be instructed to end.
			# then we'll keep going around this loop until it really does.
			if self.time_to_quit and not self.issued_quit:
				self.process.terminate()
				self.issued_quit = True
			
			newdata = self.read()

			# now post any data from the process to its output window
			if len(newdata) > 0 and self.write_output and self.output_window:		# make sure the window is still open
				wx.PostEvent(self.output_window, Events.NewDataEvent(data=newdata))
					
		# do one final read to clean up anything left in the pipe.
		newdata = self.read(want_cleanup_read = True)
		if self.write_output and self.output_window:
			if len(newdata) > 0:
				wx.PostEvent(self.output_window, Events.NewDataEvent(data=newdata))

			wx.PostEvent(self.output_window, Events.NewDataEvent(data="\n\nThread terminated cleanly."))

		# if this an essential service and it's not being terminated
		# due to some external signal, it's the first thing to quit.
		# the other processes should be stopped, the user should be informed,
		# and the run stopped since further data is expected to be useless.
		# however, if this thread is being watched by the thread watcher,
		# we don't need this event because the thread watcher will issue it
		# when ALL the DAQ threads are done.
		if self.is_essential_service and not self.time_to_quit:
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
			# don't busy-wait.
			time.sleep(0.01)
			
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
		
	def SetRelayOutput(self, dowrite=True):
		''' Sets whether subprocess output should be relayed to the window. '''
		self.write_output = dowrite
	
		
#########################################################
#   SocketThread
#########################################################

class SocketThread(threading.Thread):
	""" A thread that keeps open a socket to listen for
	    the "done" signal from all readout nodes. """
	def __init__(self, logger):
		threading.Thread.__init__(self)
		
		self.logger = logger		# loggers are thread-safe!

		self.name = "SocketThread"
		self.time_to_quit = False
		
		self.subscriptions = []

		self.daemon = True
		
		# set up the socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		# TCP/IP (only IPv4)
		# allowed to be rebound before a TIME_WAIT, LAST_ACK, or FIN_WAIT state expires
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	
		try:
			self.socket.bind(("", Configuration.params["Socket setup"]["masterPort"]))		# allow any incoming connections on the right port number
		except socket.error:
			raise SocketAlreadyBoundException

		self.socket.setblocking(0)			# we want to be able to update the display, so we can't wait on a connection
		self.socket.listen(3)				# we might have more than one node contact us simultaneously, so allow multiple backlogged connections

		self.start()
	
	def run(self):
		lastupdate = 0
		while not self.time_to_quit:
			# this loop is a busy-wait-style loop.
			# we sleep so that we bring the CPU usage
			# down to a negligible level.
			time.sleep(0.01)
			
			if select is not None and select.select([self.socket], [], [], 0)[0]:		# the first part is to ensure that we don't get messed up when shutting things down
				client_socket, client_address = self.socket.accept()

				request = ""
				datalen = -1
				while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
					data = client_socket.recv(1024)
					datalen = len(data)
					request += data
				
				self.DispatchMessage(request)
				
			if len(self.subscriptions) > 0 and time.time() - lastupdate > 0.25:			# some throttling to make sure we don't overload the event dispatcher
				lastupdate = time.time()
				
				# issue an event to any callback objects waiting on updates.
				# note that we will only issue ONE message per cycle per callback
				# (otherwise we could overload the event dispatcher)
				# so whoever's first on the subscription list will be the lucky one.
				callbacks_notified = []
				for subscription in self.subscriptions:		# loops on lists are thread-safe.
					if subscription.waiting and subscription.notice is not None and subscription.callback not in callbacks_notified:
						wx.PostEvent(subscription.callback, Events.UpdateProgressEvent( text=subscription.notice, progress=(0,0)) )
						callbacks_notified.append(subscription.callback)
#					else:
#						print "(%d, %d, %d)" % (subscription.waiting, subscription.notice is not None, subscription.callback not in callbacks_notified)
		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()
					
	def Subscribe(self, addressee, node_name, message, callback, waiting=False, notice=None):
		""" Clients should use this method to book a subscription
		    for messages from the readout nodes. """
		subscription = SocketSubscription(addressee, node_name, message, callback, waiting, notice)
		if subscription not in self.subscriptions:
			self.subscriptions.append(subscription)		# append() is thread-safe.
			self.logger.debug("New socket message subscription: (addressee, node name, message)\n(%s, %s, %s)" % (addressee, node_name, message))
		else:
			self.logger.warning("Not adding duplicate socket message subscription: (addressee, node name, message)\n(%s, %s, %s)" % (addressee, node_name, message))
			
	def Unsubscribe(self, addressee, node_name, message, callback):
		""" Cancel a subscription previously booked using Subscribe(). """
		subscription = SocketSubscription(addressee, node_name, message, callback)
		if subscription in self.subscriptions:
			self.subscriptions.remove(subscription)		# remove() is thread-safe.
			self.logger.debug("Released socket subscription: (addressee, node name, message)\n(%s, %s, %s)" % (addressee, node_name, message))
	
	def UnsubscribeAll(self, addressee):
		""" Unsubscribe all messages intended for a certain host. """
		# I'm worried about making a copy and only sending non-removed items to it,
		# then replacing the original with the copy.  I suspect that's not a thread-safe way to handle it
		# (what if another thread is trying to update the list simultaneously?  
		#  whose list is the one we get in the end?)
		# Hence the less efficient but definitely thread-safe solution below.
		while True:
			list_changed = False
			
			# loop through the subscriptions until we find one that matches.
			# remove that one.  then start over to make sure we don't miss any.
			for subscription in self.subscriptions:
				if subscription.recipient == addressee:
					self.subscriptions.remove(subscription)		# remove() is thread-safe.
					self.logger.debug("Released socket subscription: (addressee, node name, message)\n(%s, %s, %s)" % (subscription.recipient, subscription.node_name, subscription.message))
					list_changed = True
					break

			if not list_changed:
				break
#			else:
#				print "Subscription didn't match: %s, %s" % (str(subscription), addressee)
		
			
	def DispatchMessage(self, message):
		""" Checks if this message matches any subscriptions, and if so,
		    issues an event to the callback object. """
		matches = re.match(SocketRequests.Notification, message)
		if matches is None:
			self.logger.debug("Received garbled message:\n%s" % message)
			self.logger.debug("Ignoring.")
			return
		else:
			self.logger.debug("Received message:")
			self.logger.debug(message)
		
		matched = False
		
		# we only match based on the BASE part of the text (anything before the first space).
		# anything after that is considered "data" that goes with the message.
		message = matches.group("message").partition(" ")[0]
		data = matches.group("message").partition(" ")[2]
		for subscription in self.subscriptions:
			if     matches.group("addressee") == subscription.recipient \
			   and matches.group("sender") == subscription.node_name \
			   and message == subscription.message:
				matched = True
				
				wx.PostEvent( subscription.callback, Events.SocketReceiptEvent(addressee=matches.group("addressee"), sender=matches.group("sender"), message=message, data=data) )
				self.logger.debug("Message matched subscription.  Delivered.")
#			else:
#				print "(%d, %d, %d)" % (matches.group("addressee") == str(subscription.recipient), matches.group("sender") == subscription.node_name, matches.group("message") == subscription.message)
#				print "no match."
		
		if not matched:
			self.logger.debug("Message didn't match any subscriptions.  Discarding.")
		
	def Abort(self):
		self.time_to_quit = True

class SocketSubscription:
	""" A simple class to model socket subscriptions. """
	def __init__(self, recipient, node_name, message, callback, waiting=False, notice=None):
		self.recipient = str(recipient)
		self.node_name = str(node_name)
		self.message = str(message)
		self.callback = callback
		self.waiting = waiting
		self.notice = notice
	
	def __eq__(self, other):
		try:
			# note that this scheme means subscriptions are equivalent
			# if the BASE part of their message (before any spaces) match.
			# anything after that is irrelevant and not used in comparison
			# (it's assumed to be some kind of variable data).
			return (self.recipient == other.recipient and self.node_name == other.node_name and self.callback == other.callback and self.message.partition(" ")[0] == other.message.partition(" ")[0])
		except AttributeError:		# if other doesn't have one of these properties, it can't be equal!
			return False
			
	def __repr__(self):
		return "(%s, %s, %s)" % (self.recipient, self.node_name, self.message)

class SocketAlreadyBoundException(Exception):
	pass


#########################################################
#   AlertThread
#########################################################

class AlertThread(threading.Thread):
	def __init__(self, postback_window):
		threading.Thread.__init__(self)
		self.postback_window = postback_window
		self.time_to_quit = False
		self.daemon = True

		self.messages = Queue()
		self.current_message = None
		self.current_message_displayed = False
		
		self.start()

	def run(self):
		lastupdate = 0
		while not self.time_to_quit:
			# don't busy-wait!
			time.sleep(0.1)

			# if the place to send the alert no longer exists, then this thread is pointless.
			if not self.postback_window:
				return

			# if there's nothing to do, just keep looping.
			if self.current_message is None and self.messages.empty():
				continue

			# however, if there's a message waiting, we have things to do now
			if self.current_message is None:
				self.current_message = self.messages.get_nowait()
				lastupdate = 0

			# update at the specified interval.
			# high-priority messages need events every interval;
			# lower-priority ones only need the initial push.
			if (self.current_message.priority == AlertMessage.HIGH_PRIORITY or not self.current_message_displayed) and time.time() - lastupdate > Configuration.params["Front end"]["notificationInterval"]:
				lastupdate = time.time()
				wx.PostEvent(self.postback_window, Events.NotifyEvent(priority=self.current_message.priority, messageheader=self.current_message.title, messagebody=self.current_message.text))
				self.current_message_displayed = True

	def acknowledge(self):
		""" Dismisses the current alert. """
		self.current_message = None
		self.current_message_displayed = False
		
			
	def Abort(self):
		self.time_to_quit = True

class AlertMessage:
	HIGH_PRIORITY = 2
	NORMAL_PRIORITY = 1
	LOW_PRIORITY = 0
	def __init__(self, title=None, text=None, priority=NORMAL_PRIORITY):
		if title is None and text is None:
			raise ValueError("Title and text cannot both be blank.")

		self.title = title
		self.text = text
		self.priority = priority

		

