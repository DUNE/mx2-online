"""
   Threads.py:
   Some custom threads that are used in the main
   run control.  Extracted here to prevent clutter
   in the main files.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Mar. 2010
                    
   Address all complaints to the management.
"""

import os
import re
import time
import socket
import select
import fcntl
import errno
import logging
import subprocess
import threading
from Queue import Queue

# since both frontend and backend objects import
# the Threads module, if wx is not available,
# we won't panic.
try:
	import wx
	from mnvruncontrol.backend import Events
except ImportError:
	pass


from mnvruncontrol.configuration import Configuration
from mnvruncontrol.configuration import Logging
from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import Alert

#########################################################
#   DAQthread
#########################################################

class DAQthread(threading.Thread):
	""" A thread for an ET/DAQ process. """
	def __init__(self, process_info, process_identity, postoffice, env, is_essential_service=False):
		threading.Thread.__init__(self)
		self.process_identity = process_identity
		self.postoffice = postoffice
		self.environment = env
		self.command = process_info
		self.is_essential_service = is_essential_service
		self.name = self.command.split()[0] + "Thread"
		self.process = None
		self.daemon = True				# this way the process will end when the main thread does

		self.relay_output = False		# if process output should be relayed to the front end
		self.output_history = ""
		self.time_to_quit = False
		self.issued_quit = False			# has the subprocess been instructed to stop?

		self.start()					# starts the run() function in a separate thread.  (inherited from threading.Thread)
	
	def run(self):
		''' The stuff to do while this thread is going.  Overridden from threading.Thread. '''
		self.process = subprocess.Popen(self.command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=self.environment)
		self.pid = self.process.pid

		while self.process.poll() is None:
			# no busy-waiting.
			time.sleep(0.1)
			
			# if it's time to quit, the process should be instructed to end.
			# then we'll keep going around this loop until it really does.
			if self.time_to_quit and not self.issued_quit:
				self.process.terminate()
				self.issued_quit = True
			
			newdata = self.read()

			# push any data to the frontend if it wants it
			if len(newdata) > 0 and self.relay_output:
				 self.postoffice.Send(PostOffice.Message(subject="frontend_info", update="process_data", data=newdata))
				 
			self.output_history += newdata
			self.output_history = self.output_history[-2000:]	# trim to 2000 characters
					
		# do one final read to clean up anything left in the pipe.
		newdata = self.read()
		if self.relay_output:
			if len(newdata) > 0:
				self.postoffice.Send(PostOffice.Message(subject="frontend_info", update="process_data", data=newdata))

		self.output_history += newdata
		self.output_history = self.output_history[-2000:]	# trim to 2000 characters

		# if this an essential service and it's not being terminated
		# due to some external signal, it's the first thing to quit.
		# the other processes should be stopped, the user should be informed,
		# and the run stopped since further data is expected to be useless.
		# this is only expected to really be a problem if it exits with a
		# non-zero return value, however.
		if self.is_essential_service and not self.time_to_quit and self.process.returncode != 0:
			self.postoffice.Send( PostOffice.Message(subject="mgr_internal", event="series_end", early_abort=True, lost_process=self.process_identity, output_history=self.output_history) )
			
			
	def read(self, want_cleanup_read = False):
		""" Read out the data from the process.  This method attempts
		    to be intelligent about its reads from stdout: it
		    is non-blocking (won't lock up if there's nothing there). """
		    
		#	We use select() (again from the UNIX library) to check that
		#	there actually IS something in the buffer before we try to read.
		#	If we didn't do that, the thread would lock up until the specified
		#	number of characters was read out.

		do_cleanup_read = want_cleanup_read and not self.have_cleaned_up
		if do_cleanup_read:
			self.have_cleaned_up = True
		
		data = ""
		length_read = -1
		while length_read != 0 and not self.time_to_quit:
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
				length_read = len(newdata)
			except OSError:		# if the pipe is closed mid-read
				break
			
			data += newdata
		
		return data
	
	def Abort(self):
		''' When the Stop button is pressed, we gotta quit! '''
		self.time_to_quit = True
		
#########################################################
#   WorkerThread
#########################################################

class WorkerThread(threading.Thread):
	""" A special thread that's designed to 
	    perform run control functionality on behalf
	    of the message handlers (so that we don't
	    tie up the message handler thread). """
	def __init__(self):
		threading.Thread.__init__(self)
		
		self.queue = Queue()
		self.time_to_quit = False
		
		self.start()
	
	def run(self):
		""" The worker thread loop.
		
		    Use this thread by putting a dictionary of the form
		     { "method": <function object>,
		       "args":   <non-keyword arguments as a list>,
		       "kwargs": <keyword arguments as a dictionary> }
		    into the WorkerThread's queue.   The method will
		    then execute the function with these arguments."""
		    
		while True:
			method_info = self.queue.get()
			
			# this is how the main thread signals us to quit
			if method_info == "QUIT":
				break
			
			# call the specified method with the specified non-keyword and keyword arguments
			args = [] if "args" not in method_info else method_info["args"]
			kwargs = {} if "kwargs" not in method_info else method_info["kwargs"]
#			print "args:", args
#			print "kwargs:", kwargs
#			print "Calling method %s..." % method_info["method"]

			# functions being run using this thread
			# can raise a StopWorkingException if they
			# need a quick way out.  we need to trap it
			# here so that it doesn't propagate further up.
			try:
				method_info["method"](*args, **kwargs)
			except StopWorkingException:
				pass
		
#########################################################
#   AlertThread
#########################################################

# the interval time is configurable,
# though nobody will probably ever
# want to tune it.
PULSE_INTERVAL = 0.25		# in seconds

class AlertThread(threading.Thread):
	""" A custom thread dedicated to keeping the user
	    up-to-date on what's going on in the run control.
	    
	    It's currently used for two purposes:
	      (a) to manage incoming Alerts, which require
	          recurring notifications to the frontend
	      (b) to send events to the frontend when the
	          progress gauge is in "indeterminate" mode
	          ('pulse' events need to be sent at regular
	          intervals to get motion from the little bar). """
	          
	def __init__(self, parent_app):
		threading.Thread.__init__(self)
		self._parent_app = parent_app
		self.daemon = True

		# user-accessible parameters.
		self.do_pulse = False		# should we be sending 'pulse' events?
		self.time_to_quit = False

		self._logger = logging.getLogger("Frontend")

		
		self._alerts = []
		self._current_alert = None
		
		self._alert_lock = threading.Lock()
		
		self._last_bell = 0
		self._last_blink = 0
		self._last_pulse = 0
		
		self.start()

	def run(self):
		lastupdate = 0
		while not self.time_to_quit:
			# don't busy-wait!
			time.sleep(0.1)

			# if the place to send the alert no longer exists, then this thread is pointless.
			if not self._parent_app:
				return

			# if there's nothing to do, just keep looping.
			if self._current_alert is None \
			   and len(self._alerts) == 0 \
			   and not self.do_pulse:
				continue

			# however, if there's a message waiting, we have things to do now
			if self._current_alert is None and len(self._alerts) > 0:
				with self._alert_lock:
					self._current_alert = self._alerts.pop(0)
					
					if Configuration.params["Front end"]["bellInterval"] > 0:
						self._last_bell = time.time()
						bell = True
					else:
						bell = False

					if Configuration.params["Front end"]["blinkInterval"] > 0:
						self._last_blink = time.time()
						blink = True
					else:
						blink = False
					self._last_blink = time.time()
					
					wx.PostEvent( self._parent_app, Events.AlertEvent(alert=self._current_alert, bell=bell, blink=blink) )
					
			# and if there's a current message,
			# we need to make sure that bells and blinks
			# are done at the correct intervals
			if self._current_alert is not None:
				bell = False
				blink = False
				if Configuration.params["Front end"]["bellInterval"] > 0 and \
				   time.time() - self._last_bell > Configuration.params["Front end"]["bellInterval"]:
					bell = True
					self._last_bell = time.time()
				elif Configuration.params["Front end"]["blinkInterval"] and \
				     time.time() - self._last_blink > Configuration.params["Front end"]["blinkInterval"]:
					blink = True
					self._last_blink = time.time()
				
				if bell or blink:
					wx.PostEvent( self._parent_app, Events.AlertEvent(alert=self._current_alert, bell=bell, blink=blink) )

			# if we want 'pulses', we should do that now.
			if self.do_pulse and time.time() - self._last_pulse > PULSE_INTERVAL:
				wx.PostEvent( self._parent_app, Events.UpdateProgressEvent(progress=(0,0)) )
				
				self._last_pulse = time.time()

	def AcknowledgeAlert(self, alert_id, send_acknowledgment=True):
		""" Dismisses an alert and (optionally) sends
		    notification to the manager. """
		
		self._logger.debug("Alert %s acknowleged.", alert_id)
		
		alert = None
		
		with self._alert_lock:
			if self._current_alert == alert_id:
				alert = self._current_alert
				self._current_alert = None
			
			if alert in self._alerts:
				alert = self._alerts.pop(self._alerts.index(alert_id))
				
		if alert is not None and alert.is_manager_alert and send_acknowledgment:
			self._logger.debug("Sending manager acknowledgement.")
			self._parent_app.postoffice.Send( PostOffice.Message(subject="mgr_directive", directive="alert_acknowledge", alert_id=alert.id, client_id=self._parent_app.id) )
		
	def NewAlert(self, alert):
		""" Adds a new alert to the stack. """

		# don't accept poorly-formed alerts
		assert hasattr(alert, "notice") and hasattr(alert, "severity")
		
		with self._alert_lock:
			# don't add the same alert twice.
			if alert in self._alerts or alert == self._current_alert:
				return
			else:
				self._logger.debug("New alert (id: %s).", alert.id)
			
			self._alerts.append(alert)

		prefix = "(from DAQ manager) " if (hasattr(alert, "is_manager_alert") and alert.is_manager_alert) else ""
		log_method = { Alert.WARNING: self._logger.warning,
		               Alert.ERROR:   self._logger.error }
		log_method[alert.severity](prefix + alert.notice)
			
	def Abort(self):
		self.time_to_quit = True


#########################################################
#   Internal Utilities
#########################################################

class StopWorkingException(Exception):
	""" Raise one of these within a function being run by
	    the worker thread if you want to stop working immediately.  """
	pass
