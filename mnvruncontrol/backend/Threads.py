"""
  Package: mnvruncontrol
   The MINERvA run control
   
  File: Threads.py
  
  Notes:
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
import shlex
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
		# note that shlex.split doesn't understand Unicode...
		self.process = subprocess.Popen(shlex.split(str(self.command)),
			close_fds=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			env=self.environment)
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
#		print "last read!"
		newdata = self.read()
		if self.relay_output:
			if len(newdata) > 0:
				self.postoffice.Send(PostOffice.Message(subject="frontend_info", update="process_data", data=newdata))

		self.output_history += newdata
		identity = self.process_identity.lower().replace(" ", "")
		fname = os.path.join(Configuration.params["mstr_logfileLocation"], "%s.log" % identity)
		print "Writing log for process '%s' to file: %s" % (self.process_identity, fname)
		try:
			with open(fname, "w") as outf:
				outf.write(self.output_history)
		except Exception as e:
			print e
			
		self.output_history = self.output_history[-2000:]	# trim to 2000 characters

		# if this an essential service and it's not being terminated
		# due to some external signal, it's the first thing to quit.
		# the other processes should be stopped, the user should be informed,
		# and the run stopped since further data is expected to be useless.
		# this is only expected to really be a problem if it exits with a
		# non-zero return value, however.
		if self.is_essential_service and not self.time_to_quit and self.process.returncode != 0:
			self.postoffice.Send( PostOffice.Message(subject="mgr_internal", event="series_end", early_abort=True, lost_process=self.process_identity, output_history=self.output_history) )
#		else:
#			print "Process '%s' ended.\n"
			
			
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
		
#		print "from process '%s': %s" % (self.process_identity, data)
		
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
	def __init__(self, logger=None):
		""" Constructor.
		
		    If you pass a Python logger object (see the
		    documentation for the 'logging' module) as
		    the 'logger' parameter, the worker will
		    send announcements immediately before and
		    after running each work function.  This can
		    help to pin down thread deadlocks. """

		threading.Thread.__init__(self)
		
		self.queue = Queue()
		self.time_to_quit = False
		self._logger = logger
		
		self.start()
	
	def run(self):
		""" The worker thread loop.
		
		    Use this thread by putting a dictionary of the form
		     { "method": <function object>,
		       "args":   <non-keyword arguments as a list>,
		       "kwargs": <keyword arguments as a dictionary> }
		    into its queue.   The worker will then execute
		    the function with these arguments. """
		    
		    
		while True:
			method_info = self.queue.get()
			
			# this is how the main thread signals us to quit
			if isinstance(method_info, StopWorkingException):
				if self._logger is not None:
					self._logger.debug("Worker thread instructed to quit...")
				break
			
			# call the specified method with the specified non-keyword and keyword arguments
			args = [] if "args" not in method_info else method_info["args"]
			kwargs = {} if "kwargs" not in method_info else method_info["kwargs"]

			if self._logger is not None:
				self._logger.debug("Worker thread is about to go to work using the following items:\n  Function: %s\n  args:     %s\n  kwargs:   %s", method_info["method"], args, kwargs)

			# functions being run using this thread
			# can raise a StopWorkingException if they
			# need a quick way out.  we need to trap it
			# here so that it doesn't propagate further up.
			try:
				method_info["method"](*args, **kwargs)
			except StopWorkingException:
				pass
			
			if self._logger is not None:
				self._logger.debug("Worker thread returned from work function: %s", method_info["method"])
		
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
	    
	    It's currently used for three purposes:
	      (a) to manage incoming Alerts, which require
	          recurring notifications to the frontend
	      (b) to send events to the frontend when the
	          progress gauge is in "indeterminate" mode
	          ('pulse' events need to be sent at regular
	          intervals to get motion from the little bar).
	      (c) check how long it's been since the last trigger
	          notification was received.  If it has been
	          longer than the interval specified in the
	          Configuration, an alert is generated to make
	          sure that the shifter is paying attention. """
	          
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
		self._last_trigger_status_update = 0
		
		self._last_trigger = None
		self._trigger_alert_id = None
		
		self.start()

	def run(self):
		lastupdate = 0
		while not self.time_to_quit:
			# don't busy-wait!
			time.sleep(0.1)

			# if the place to send the alert no longer exists, then this thread is pointless.
			if not self._parent_app:
				return
				
			# check if we should be creating a "no triggers" alert
			# (only if the config says to do it,
			#  the appropriate amount of time has elapsed,
			#  and we haven't already created one)
			trigger_interval = None if self._last_trigger is None else (time.time() - self._last_trigger)
			trigger_interval_min = None if trigger_interval is None else int(trigger_interval/60.)
			if Configuration.params["frnt_maxTriggerInterval"] > 0 \
			   and self._last_trigger is not None \
			   and self._parent_app.in_control \
			   and trigger_interval_min > Configuration.params["frnt_maxTriggerInterval"] \
			   and self._trigger_alert_id is None:
				alert = Alert.Alert(
					notice="No triggers have been received for the last %d minutes.  Is this what you're expecting?  (Is the beam down?)" % trigger_interval_min,
					severity=Alert.WARNING
				)
				self._trigger_alert_id = alert.id
				self.NewAlert(alert)
			
			# the background of the "last trigger" status area
			# is meant to reflect the run control's best knowledge
			# of how recent the last trigger was:
			#  - "ok" if none of the following conditions are met
			#  - "warning" if it's been longer than a configurable number of seconds
			#    but the full-screen trigger warning hasn't been sounded yet
			#  - "alarm" if the trigger warning is in effect
			if self._parent_app.daq and time.time() - self._last_trigger_status_update > Configuration.params["frnt_blinkInterval"]:
				level = None
				if Configuration.params["frnt_triggerWarningInterval"] is not None:
					if self._trigger_alert_id is not None:
						level = Alert.ERROR
					elif trigger_interval is None or trigger_interval > Configuration.params["frnt_triggerWarningInterval"]:
						level = Alert.WARNING
				
				# criteria:
				#  - always propagate 'warning' or 'error' messages
				#  - send an update if none has yet been sent
				#  - send an update if a trigger has happened more recently than the last update.
				if level is not None \
				  or self._last_trigger_status_update is None \
				  or self._last_trigger > self._last_trigger_status_update:
					wx.PostEvent(
						self._parent_app,
						Events.TriggerStatusEvent(warning_level=level)
					)
					self._last_trigger_status_update = time.time()

			# if there's nothing to do, just keep looping.
			if self._current_alert is None \
			   and len(self._alerts) == 0 \
			   and not self.do_pulse:
				continue

			# however, if there's a message waiting, we have things to do now
			if self._current_alert is None and len(self._alerts) > 0:
				with self._alert_lock:
					self._current_alert = self._alerts.pop(0)
					
					if Configuration.params["frnt_bellInterval"] > 0:
						self._last_bell = time.time()
						bell = True
					else:
						bell = False

					if Configuration.params["frnt_blinkInterval"] > 0:
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
				if Configuration.params["frnt_bellInterval"] > 0 and \
				   time.time() - self._last_bell > Configuration.params["frnt_bellInterval"]:
					bell = True
					self._last_bell = time.time()
				elif Configuration.params["frnt_blinkInterval"] and \
				     time.time() - self._last_blink > Configuration.params["frnt_blinkInterval"]:
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
	
	def DropManagerAlerts(self):
		""" When a client disconnects from the DAQ,
		    all the alerts that came from the DAQ manager
		    are no longer relevant.  They should be
		    summarily dismissed (they will be re-sent by
		    the manager if this client should re-connect). """
		
		# be careful.  don't want to call AcknowledgeAlert
		# within the loop because it would modify the the
		# list of alerts and might cause us to skip some...
		alerts_to_remove = []
		for alert in self._alerts:
			if alert.is_manager_alert:
				alerts_to_remove.append(alert.id)
		
		for alert_id in alerts_to_remove:
			self.AcknowledgeAlert(alert_id)
		
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
		
	def TriggerUpdate(self, turn_off=False):
		""" Method used to declare a trigger update. """

		if self._trigger_alert_id is not None:
			self.AcknowledgeAlert(self._trigger_alert_id)

		if turn_off:
			self._last_trigger = None
		else:
			self._last_trigger = time.time()
			self._trigger_alert_id = None
			
	def Abort(self):
		self.time_to_quit = True


#########################################################
#   Internal Utilities
#########################################################

class StopWorkingException(Exception):
	""" Raise one of these within a function being run by
	    the worker thread if you want to stop working immediately.  """
	pass
