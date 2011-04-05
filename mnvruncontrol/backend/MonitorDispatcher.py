"""
  MonitorDispatcher.py:
   Listener service that runs on an online monitoring node.
   It handles starting and stopping of the OM processes
   based on information it receives from the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    July-Aug. 2010
                    
   Address all complaints to the management.
"""

import subprocess
import threading
import signal
import shutil
import shlex
import fcntl
import time
import sys
import os
import os.path
import socket
import logging

import mnvruncontrol.configuration.Logging

from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.Dispatcher import Dispatcher
from mnvruncontrol.backend import PostOffice
from mnvruncontrol.backend import MailTools

class MonitorDispatcher(Dispatcher):
	"""
	Online monitor node dispatcher.  Starts and stops the OM processes
	based on instructions received from the run control.
	"""
	def __init__(self):
		Dispatcher.__init__(self)
	
		self.logger = logging.getLogger("Dispatcher.OM")

		# need to shut down the subprocesses...
		self.cleanup_methods += [self.om_stop]
		                        
		self.pidfilename = Configuration.params["mon_PIDfile"]
		                   
		self.om_eb_thread = None
		self.om_Gaudi_thread = None
		
		self.etpattern = None
		self.evbfile = None
		
		self.use_condor = Configuration.params["mon_useCondor"]
		
		# has the "OM ready" signal been sent to the
		# DAQ manager for this subrun?
		self.signalled_ready = False
		
		# this is how we know to start the second part
		# of the nearline system, which needs to wait
		# until the event builder has set up: the EB
		# signals this process.  we have to set the
		# signal handler up here (instead of only when
		# starting the EB) because Python's 'signal'
		# module refuses to do anything anywhere
		# except in the main thread.
		signal.signal(signal.SIGUSR1, self.om_start_Gaudi)
		
	def BookSubscriptions(self):
		""" Overrides Dispatcher's BookSubscriptions()
		    to do something useful here. """
	
		# we need to know when the DAQ manager goes up or down,
		# as well as when the OM system on this node is supposed
		# to start or stop
		handlers = { PostOffice.Subscription(subject="mgr_status", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.DAQMgrStatusHandler,
			        PostOffice.Subscription(subject="om_directive", action=PostOffice.Subscription.DELIVER, delivery_address=self) : self.OMDirectiveHandler }
	
		for subscription in handlers:
			self.postoffice.AddSubscription(subscription)
			self.AddHandler(subscription, handlers[subscription])

	def CheckCondor(self):
		""" Checks to see if it appears Condor is available
		    and accepting jobs. """
		
		# don't do anything if we don't want to use Condor.
		if not Configuration.params["mon_useCondor"]:
			return
		
		# local variable that will be compared with self.use_condor in a minute
		use_condor = True

		# first ask Condor for names and statuses of its slots.
		condor_command = "condor_status -format \"%s \" Name -format \"%s\\n\" State"
		p = subprocess.Popen(condor_command, shell=True, stdout=subprocess.PIPE)
		status_text = p.stdout.read()
		return_code = p.wait()
		available_slots = status_text.count("Unclaimed")
		
		self.logger.info("Condor reports the following status:\n====================================\n%s", status_text)
		
		# in case we need to send mail below
		sender = "%s@%s" % (os.environ["LOGNAME"], socket.getfqdn())
		subject = None
		messagebody = None
		
		if return_code != 0:
			self.logger.warning("Condor status query returned non-zero exit code (code: %d)!  Falling back to unmonitored job submission...", return_code)
			self.logger.warning("Condor query command was: %s\n", condor_command)

			use_condor = False

			subject = "MINERvA near-online Condor error"
			messagebody = "There was an error attempting to query the mnvnearline* Condor queue status:\n\n'condor_status' returned with exit code: %d\n\nThe output from the condor_status query was: '%s'" % (return_code, status_text)
		elif available_slots == 0:
			self.logger.warning("Condor slots are all full!  This job will be queued for processing when a slot becomes available...")

			# job status == 1 is an "idle" job.
			condor_command = "condor_q -constraint \"JobStatus == 1\" -format \"%d \" JobStatus"
			p = subprocess.Popen(condor_command, shell=True, stdout=subprocess.PIPE)
			status_text = p.stdout.read()
			p.wait()
			idle_job_count = len(status_text.split(" "))
			
			# only start sending mail when the threshold is crossed.
			# maybe the user is ok with a job or two in the backlog.
			self.logger.info("Idle Condor jobs: %d", idle_job_count)
			if idle_job_count >= Configuration.params["mon_maxCondorBacklog"]:
				condor_command = "condor_q"
				p = subprocess.Popen(condor_command, shell=True, stdout=subprocess.PIPE)
				status_text = p.stdout.read()
				p.wait()

				subject = "MINERvA near-online Condor queue is full"
				messagebody = "The Condor queue on mnvnearline* is full.  The queue currently looks like:\n%s" % status_text
		
		# if Condor has gone down, send a notification
		if not use_condor and self.use_condor:
			messagebody += "\n\nInteractive job submission will be used until Condor reports it is accessible and functioning."
		# and similarly, if it just came back up, ditto
		elif use_condor and not self.use_condor:
			subject = "MINERvA near-online Condor is back up"
			messagebody = "The mnvnearline* Condor queue has returned to normal working order." 			

		if subject is not None and messagebody is not None:
			self.logger.info("Sending mail to notification addresses.")
			MailTools.sendMail(fro=sender, to=Configuration.params["gen_notifyAddresses"], subject=subject, text=messagebody)

		self.use_condor = use_condor

	def DAQMgrStatusHandler(self, message):
		""" Method to respond to changes in status of the
		    DAQ manager (books subscriptions, etc.). """

		self.DAQMgrStatusUpdate(message, ["om_directive",])		    
	
	def OMDirectiveHandler(self, message):
		""" Handles incoming directives for the online monitoring system. """
		
		if not ( hasattr(message, "directive") and hasattr(message, "mgr_id") ):
			self.logger.info("OM directive message is improperly formatted.  Ignoring...")
			return
		
		response = message.ResponseMessage()
		if message.mgr_id in self.identities:
			response.sender = self.identities[message.mgr_id]
		
		status = True
		if not self.ClientAllowed(message.mgr_id):
			response.subject = "not_allowed"
		else:
			if message.directive == "start":
				if not (hasattr(message, "et_pattern") and hasattr(message, "et_port")):
					status = None
				else:
					status = self.om_start(message.et_pattern, message.et_port)
			
			elif message.directive == "stop":
				status = self.om_stop()
		
			if status is None:
				response.subject = "invalid_request"
			else:
				response.subject = "request_response"
				response.success = status
		self.postoffice.Send(response)

	def om_start(self, etpattern, etport):
		""" Starts the online monitoring services as subprocesses.  First checks
		    to make sure it's not already running, and if it is, does nothing. """
		    
		self.logger.info("Manager wants to start the OM processes.")
		
		self.signalled_ready = False

		# first clear up any old event builder processes.
		if self.om_eb_thread and self.om_eb_thread.is_alive() is None:
			self.om_eb_thread.terminate()
			self.om_eb_thread.join()
		
		self.etpattern = etpattern
		self.evbfile = "%s/%s_RawData.dat" % ( Configuration.params["mon_rawdataLocation"], self.etpattern )
		self.raweventfile = "%s/%s_RawEvent.root" % ( Configuration.params["mon_rawdataLocation"], self.etpattern )
		
		
		try:
			self.om_start_eb(etfile="%s_RawData" % etpattern, etport=etport)
		except Exception as excpt:
			self.logger.error("   ==> The event builder process can't be started!")
			self.logger.error("   ==> Error message: '%s'", excpt)
			return False
		
		return True
	
	def om_start_eb(self, etfile, etport):
		""" Start the event builder process. """
		executable = ( "%s/bin/event_builder %s/%s %s %s %d" % (environment["DAQROOT"], Configuration.params["mstr_etSystemFileLocation"], etfile, self.evbfile, etport, os.getpid()) ) 
		self.logger.info("   event_builder command:\n      '%s'...", executable)
		
		self.om_eb_thread = OMThread(self, executable, "eventbuilder")
	
	def om_start_Gaudi(self, signum=None, sigframe=None):
		""" Start the Gaudi processes. """
		# let the DAQ manager know that the event builder
		# is done setting up
		message = PostOffice.Message(subject="om_status", state="om_ready", sender=self.identities[self.lock_id])
		self.postoffice.Send(message)
		
		self.signalled_ready = True
		
		self.CheckCondor()
		
		try:
			# replace the options file so that we get the new event builder output.
			with open(Configuration.params["mon_GaudiOutputOptionsFile"], "w") as optsfile:
				path = Configuration.params["mon_DSTTargetPath"]
				optsfile.write("HistogramSaver.Outputfile = \"%s/%s_Histos.root\";\n" % (path, self.etpattern ) )

				dstfiles = []
				for dsttype in ("linjc", "numib"):
					prefix = "Linjc" if dsttype == "linjc" else ""
					dstfiles.append( { "DSTWriter": dsttype.capitalize(), "filename": "%s/%s_%sDST.root" % (path, self.etpattern, prefix) } )

				for dstinfo in dstfiles:
					optsfile.write("%sDSTWriter.OutputFile = \"%s\";\n" % (dstinfo["DSTWriter"], dstinfo["filename"]) )
				
				optsfile.write( "MaxPEGainAlg.OutfileName = \"%s/%s_gain_table.dat\";\n" % (path, self.etpattern) )
				optsfile.write( "MaxPEGainAlg.ProblemChannelFileName = \"%s/%s_problemchannels.dat\";\n" % (path, self.etpattern) )
				optsfile.write( "MaxPEGainAlg.HVFileName = \"%s/%s_tunedHVs.dat\";\n" % (path, self.etpattern) )

			with open(Configuration.params["mon_GaudiInputOptionsFile"], "w") as optsfile:
				optsfile.write("BuildRawEventAlg.InputFileName   = \"%s\" ;\n" % self.evbfile)
			
			# if the Gaudi (monitoring) thread is still running, it needs to be stopped.
			if self.om_Gaudi_thread is not None and self.om_Gaudi_thread.is_alive():
				self.logger.info(" ... stopping previous monitoring thread...")
				self.om_Gaudi_thread.process.terminate()
				self.om_Gaudi_thread.join()
				self.logger.info(" ... done.")

			# now start a new copy of each of the Gaudi jobs.
			gaudi_processes = ( { "processname": "monitoring",
				                 "executable" : "%s/%s/MinervaNearline.exe %s/options/NearlineCurrent.opts" % (os.environ["DAQRECVROOT"], os.environ["CMTCONFIG"], os.environ["DAQRECVROOT"]),
				                 "run"        : Configuration.params["mon_runCurrentJob"] },
				               { "processname": "dst",
				                 "executable" : "%s/%s/MinervaNearline.exe %s/options/Nearline.opts" % (os.environ["DAQRECVROOT"], os.environ["CMTCONFIG"], os.environ["DAQRECVROOT"]),
				                 "run"        : Configuration.params["mon_runDSTjobs"] } )

			for process in gaudi_processes:
				# we will only keep track of the monitoring thread, because this one
				# is the one that will be replaced.
				# 
				# if we're using Condor, the others will be submitted as jobs via minerva_jobsub.
				# that will be the last that we ever see of them here.
				# otherwise, they'll run 'interactively' in the background,
				# but we won't keep a handle for them (not assign to a variable)
				# so that they run unmolested until they finish.
				# of course, if this thread is killed, they might go with it, but that
				# depends on whether or not they fork first.  (i don't think they do.)
			
				# user can configure not to run either of the types of Gaudi job
				if not process["run"]:
					continue
					
				interactive = process["processname"] == "monitoring" or (process["processname"] == "dst" and not self.use_condor)
				
				if interactive:
					thread = OMThread(self, process["executable"], "gaudi_%s" % process["processname"], persistent=(process["processname"] == "dst"))
					if process["processname"] == "monitoring":
						self.om_Gaudi_thread = thread

					self.logger.info("  Starting a copy of MinervaNearline.exe with the following command:\n%s", process["executable"])
			
					# want to record the PID.  wait until it's ready.
					while thread.pid is None:
						time.sleep(0.01)
						pass
				
					self.logger.info("     ==> process id: %d" % thread.pid)
				else:
					fmt = { "host":        Configuration.params["mon_condorHost"],
					        "notify":      ",".join(Configuration.params["gen_notifyAddresses"]),
					        "release":     os.environ["MINERVA_RELEASE"],
					        "siteroot":    os.environ["MYSITEROOT"],
					        "daqrecvroot": os.environ["DAQRECVROOT"],
					        "executable":  process["executable"] }
					executable = "minerva_jobsub -l \"notify_user = %(notify)s\" -submit_host %(host)s -r %(release)s -i %(siteroot)s -t %(daqrecvroot)s -q %(executable)s" % fmt
					self.logger.info("  Submitting a Condor job using the following command:\n%s", executable)
					return_code = subprocess.call(executable, shell=True)
					
					if return_code != 0:
						self.logger.warning("Condor submission exited with non-zero return code: %d.  This job was probably not submitted!" % return_code)
						
						sender = "%s@%s" % (os.environ["LOGNAME"], socket.getfqdn())
						subject = "MINERvA near-online Condor submission problem"
						messagebody = "A job submission to the mnvnearline* Condor queue returned a non-zero exit code: %d." % return_code
						messagebody += "The command was:\n%s" % executable 			
						MailTools.sendMail(fro=sender, to=Configuration.params["gen_notifyAddresses"], subject=subject, text=messagebody)
					else:
						self.logger.info("  ... submitted successfully.")
					
		except Exception:
			self.logger.exception("  Error starting the Gaudi processes!:")
	
	def om_stop(self, matches=None, show_details=True, **kwargs):
		""" Stops the online monitor processes.  Only really needed
		    if the dispatcher is going to be stopped since the om_start()
		    method closes any open threads before proceeding. """
		    
		self.logger.info("Client wants to stop the OM processes.")
		
		errors = False
		if self.om_eb_thread and self.om_eb_thread.is_alive():
			self.logger.info("   ==> Attempting to stop the event builder thread.")
			try:
				self.om_eb_thread.process.terminate()
				self.om_eb_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
			except Exception, excpt:
				self.logger.error("   ==> event builder process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				errors = True

		if self.om_Gaudi_thread and self.om_Gaudi_thread.is_alive():
			self.logger.info("   ==> Attempting to stop the Gaudi thread.")
			try:
				self.om_Gaudi_thread.process.terminate()
				self.om_Gaudi_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
			except Exception, excpt:
				self.logger.error("   ==> Gaudi process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				errors = True

		if not errors:
			self.logger.info("   ==> Stopped successfully.")
		
		return True if not errors else False
		

#########################
# OMThread              #
#########################
class OMThread(threading.Thread):
	""" OM processes need to be run in a separate thread
	    so that we know if they finish. """
	def __init__(self, parent, command, processname, persistent=False):
		threading.Thread.__init__(self)
		
		self.parent = parent
		self.process = None
		self.pid = None
		self.command = command
		self.processname = processname
		self.persistent = persistent		# if this thread is supposed to run until it finishes
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		# redirect any output to a log file
		i = 1
		error = None
		timediff = 0
		while True:
			filename = "%s/%s.%d.log" % (Configuration.params["mon_logfileLocation"], self.processname, i)
			# open the file in append mode so that if it's locked,
			# we don't erase the whole thing when opening it
			with open(filename, "a") as fileobj:
				# try to get a lock on the log file.
				# this ensures we don't write to the same one via
				# two different processes.
				try:
					fcntl.flock(fileobj, fcntl.LOCK_EX | fcntl.LOCK_NB)
				# if the file is already locked, we'll try a new filename.
				except IOError:
					i += 1
					continue
				
				# if we successfully locked the file, we need to start at its beginning.
				fileobj.truncate(0)
				
				try:
					starttime = time.time()

					self.process = subprocess.Popen(shlex.split(self.command),
						shell=False,
						close_fds=True,
						env=os.environ,
						stdout=fileobj.fileno(),
						stderr=subprocess.STDOUT)
					self.pid = self.process.pid		# less typing.

					# now wait until it finishes.
					self.returncode = self.process.wait()

					# calculate how long the job took.
					# if it was too short, we'll email the notify addresses below.
					timediff = time.time() - starttime
				except Exception as e:
					error = e
				# we want to release the lock no matter what happens!
				finally:
					fcntl.flock(fileobj, fcntl.LOCK_UN)
				
				break
		
		# if an error happened, or if the job was too short,
		# send an e-mail to the addresses listed in the
		# gen_notifyAddresses configuration parameter with the
		# log file.
		if error is not None or timediff < Configuration.params["mon_DSTminJobTime"]:
			subject = "MINERvA near-online automatic DST production warning"
			if error:
				messagebody = "There was an error during automatic DST processing.  The error message is:\n\n%s\n\n" % str(error)
			else:
				messagebody = "An automatically-produced DST on the near-online system finished in less than the specified time interval (%i s)." % Configuration.params["mon_DSTminJobTime"]
			messagebody += "\nPlease see that attached log file for further information."
			
			sender = "%s@%s" % (os.environ["LOGNAME"], socket.getfqdn())

			MailTools.sendMail(fro=sender, to=Configuration.params["gen_notifyAddresses"], subject=subject, text=messagebody, files=[filename,])
			
			# inform the DAQ manager if necessary.
			if not self.parent.signalled_ready:
				msg = PostOffice.Message(subject="om_status", state="om_error", sender=self.parent.identities[self.parent.lock_id], error="Process '%s' quit early." % self.processname)
				self.parent.postoffice.Send(msg)
		
                        
####################################################################
####################################################################
"""
  This module should probably never be imported elsewhere.
  It's designed to run directly as a background process that handles
  incoming requests for the online monitoring system.
  
  If it IS running as a stand-alone, it will need to daemonize
  and begin listening on the specified port (both of which are
  taken care of by the Dispatcher superclass's method bootstrap()).
  
  Otherwise this implementation will bail with an error.
"""
if __name__ == "__main__":
	environment = {}
	var_list = [ "DAQROOT", "ET_HOME", "ET_LIBROOT", "CAEN_DIR",
	             "DAQRECVROOT", "CMTCONFIG", "MINERVA_RELEASE",
	             "MYSITEROOT", "LD_LIBRARY_PATH" ]

	if Configuration.params["mon_useCondor"]:
		var_list += ["CONDOR_TMP", "CONDOR_EXEC"]
		
	for var in var_list:
		try:
			environment[var] = os.environ[var]
		except KeyError:
			sys.stderr.write("Your environment is not properly configured.  Missing variable: %s\n\n" % var)
			sys.stderr.write("You must source the 'setupdaqenv.sh', 'setup.minerva.condor.sh' (if using Condor),\n")
			sys.stderr.write("general MINERvA analysis framework, and DaqRecv package setup scripts\n")
			sys.stderr.write("before launching this dispatcher.\n")
			sys.exit(1)

	dispatcher = MonitorDispatcher()
	dispatcher.Bootstrap()

	sys.exit(0)
	
else:
	raise RuntimeError("This module is not designed to be imported!")

