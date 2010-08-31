"""
  MonitorDispatcher.py:
  Listener service that runs on an online monitoring node.
  It handles starting and stopping of the OM processes
  based on information it receives from the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar.-Apr. 2010
                    August 2010
                    
   Address all complaints to the management.
"""

import subprocess
import threading
import signal
import shutil
import fcntl
import time
import sys
import os
import socket
import logging
import logging.handlers

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend import Dispatcher
from mnvruncontrol.backend import MailTools

class MonitorDispatcher(Dispatcher.Dispatcher):
	"""
	Online monitor node dispatcher.  Starts and stops the OM processes
	based on instructions received from the run control.
	"""
	def __init__(self):
		Dispatcher.Dispatcher.__init__(self)
	
		# Dispatcher() maintains a central logger.
		# We want a file output, so we'll set that up here.
		self.filehandler = logging.handlers.RotatingFileHandler(Configuration.params["Monitoring nodes"]["om_logfileName"], maxBytes=204800, backupCount=5)
		self.filehandler.setLevel(logging.INFO)
		self.filehandler.setFormatter(self.formatter)		# self.formatter is set up in the Dispatcher superclass
		self.logger.addHandler(self.filehandler)

		# we need to specify what requests we know how to handle.
		self.valid_requests += SocketRequests.MonitorRequests
		self.handlers.update( { "om_start" : self.om_start,
		                        "om_stop"  : self.om_stop } )

		# need to shut down the subprocesses...
		self.cleanup_methods += [self.om_stop]
		                        
		self.pidfilename = Configuration.params["Monitoring nodes"]["om_PIDfileLocation"]
		                   
		self.om_eb_thread = None
		self.om_Gaudi_thread = None
		
		self.etpattern = None
		self.evbfile = None
			

	def om_start(self, matches, show_details, **kwargs):
		""" Starts the online monitoring services as subprocesses.  First checks
		    to make sure it's not already running, and if it is, does nothing.

		    Returns 0 on success and 1 on failure.  """
		    
		if show_details:
			self.logger.info("Client wants to start the OM processes.")

		# first clear up any old event builder processes.
		if self.om_eb_thread and self.om_eb_thread.is_alive() is None:
			self.om_eb_thread.terminate()
			self.om_eb_thread.join()
		
		self.etpattern = matches.group("etpattern")
		self.evbfile = "%s/%s_RawData.dat" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		self.raweventfile = "%s/%s_RawEvent.root" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		
		
		try:
			self.om_start_eb(etfile="%s_RawData" % matches.group("etpattern"), etport=matches.group("etport"))
			return "0"
		except Exception, excpt:
			self.logger.error("   ==> The event builder process can't be started!")
			self.logger.error("   ==> Error message: '%s'", excpt)
			return "1"
	
	def om_start_eb(self, etfile, etport):
		""" Start the event builder process. """
		executable = ( "%s/bin/event_builder %s/%s %s %s %d" % (environment["DAQROOT"], Configuration.params["Master node"]["etSystemFileLocation"], etfile, self.evbfile, etport, os.getpid()) ) 
		self.logger.info("   event_builder command:")
		self.logger.info("      '%s'", executable)
		
		signal.signal(signal.SIGUSR1, self.om_start_Gaudi)
		self.om_eb_thread = OMThread(executable, "eventbuilder")
	
	def om_start_Gaudi(self, signum=None, sigframe=None):
		""" Start the Gaudi process. """
		# first clear the signal handler so an accidental call wouldn't restart the service.
		signal.signal(signal.SIGUSR1, signal.SIG_IGN)

		# let the main RC know that the event builder is done starting up
		self.queue.put(Dispatcher.Message("om_ready", Dispatcher.MASTER))

		try:
			# replace the options files so that we get the new event builder output.
			with open(Configuration.params["Monitoring nodes"]["om_GaudiOutputOptionsFile"], "w") as optsfile:
				path = Configuration.params["Monitoring nodes"]["om_DSTTargetPath"]
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

			with open(Configuration.params["Monitoring nodes"]["om_GaudiInputOptionsFile"], "w") as optsfile:
				optsfile.write("BuildRawEventAlg.InputFileName   = \"%s\" ;\n" % self.evbfile)
			
			# if the Gaudi (monitoring) thread is still running, it needs to be stopped.
			if self.om_Gaudi_thread is not None and self.om_Gaudi_thread.is_alive():
				self.om_Gaudi_thread.process.terminate()
				self.om_Gaudi_thread.join()

			# now start a new copy of each of the Gaudi jobs.
			gaudi_processes = ( { "processname": "monitoring",
				                 "executable" : "%s/%s/MinervaNearline.exe %s/options/NearlineCurrent.opts" % (os.environ["DAQRECVROOT"], os.environ["CMTCONFIG"], os.environ["DAQRECVROOT"]) },
				               { "processname": "dst",
				                 "executable" : "%s/%s/MinervaNearline.exe %s/options/Nearline.opts" % (os.environ["DAQRECVROOT"], os.environ["CMTCONFIG"], os.environ["DAQRECVROOT"]) } )

			for process in gaudi_processes:
				# we will only keep track of the monitoring thread, because this one
				# is the one that will be replaced.
				# the others will continue to run, but we'll have no handle for them
				# (which is intentional, so that they run unmolested until they finish).
				# of course, if this thread is killed, they might go with it, but that
				# depends on whether or not they fork first.  (i can't remember.)
				thread = OMThread(process["executable"], "gaudi_%s" % process["processname"], persistent=(process["processname"] == "dst"))
				if process["processname"] == "monitoring":
					self.om_Gaudi_thread = thread

				self.logger.info("   Starting a copy of MinervaNearline.exe using the following command:\n%s", process["executable"])
			
				# want to record the PID.  wait until it's ready.
				while thread.pid is None:
					time.sleep(0.01)
					pass
				
				self.logger.info("     ==> process id: %d" % thread.pid)
		except:
			self.logger.exception("  Error starting the Gaudi processes!:")
	
	def om_stop(self, matches=None, show_details=True, **kwargs):
		""" Stops the online monitor processes.  Only really needed
		    if the dispatcher is going to be stopped since the om_start()
		    method closes any open threads before proceeding. 
		    
		    Returns 0 on success and 1 on failure. """
		    
		if show_details:
			self.logger.info("Client wants to stop the OM processes.")
		
		errors = False
		if self.om_eb_thread and self.om_eb_thread.is_alive():
			if show_details:
				self.logger.info("   ==> Attempting to stop the event builder thread.")
			try:
				self.om_eb_thread.process.terminate()
				self.om_eb_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
			except Exception, excpt:
				self.logger.error("   ==> event builder process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				errors = True

		if self.om_Gaudi_thread and self.om_Gaudi_thread.is_alive():
			if show_details:
				self.logger.info("   ==> Attempting to stop the Gaudi (monitoring) thread.")
			try:
				self.om_Gaudi_thread.process.terminate()
				self.om_Gaudi_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
			except Exception, excpt:
				self.logger.error("   ==> Gaudi process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				errors = True

		if show_details and not errors:
			self.logger.info("   ==> Stopped successfully.")
		
		return "0" if not errors else "1"
		

#########################
# OMThread              #
#########################
class OMThread(threading.Thread):
	""" OM processes need to be run in a separate thread
	    so that we know if they finish. """
	def __init__(self, command, processname, persistent=False):
		threading.Thread.__init__(self)
		
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
			filename = "%s/%s.%d.log" % (Configuration.params["Monitoring nodes"]["om_logfileLocation"], self.processname, i)
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

					self.process = subprocess.Popen(self.command.split(), shell=False, env=os.environ, stdout=fileobj.fileno(), stderr=subprocess.STDOUT)
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
		# NOTIFY_ADDRESSES configuration parameter with the
		# log file.
		if error is not None or timediff < Configuration.params["Monitoring nodes"]["om_DSTminJobTime"]:
			subject = "MINERvA near-online automatic DST production warning"
			if error:
				messagebody = "There was an error during automatic DST processing.  The error message is:\n\n%s\n\n" % str(error)
			else:
				messagebody = "An automatically-produced DST on the near-online system finished in less than the specified time interval (%i s)." % Configuration.params["Monitoring nodes"]["om_DSTminJobTime"]
			messagebody += "\nPlease see that attached log file for further information."
			
			sender = "%s@%s" % (os.environ["LOGNAME"], socket.getfqdn())

			MailTools.sendMail(fro=sender, to=Configuration.params["General"]["notify_addresses"], subject=subject, text=messagebody, files=[filename,])
		
                        
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
	try:
		environment["DAQROOT"] = os.environ["DAQROOT"]
		environment["ET_HOME"] = os.environ["ET_HOME"]
		environment["ET_LIBROOT"] = os.environ["ET_LIBROOT"]
		environment["CAEN_DIR"] = os.environ["CAEN_DIR"]
		environment["LD_LIBRARY_PATH"] = os.environ["LD_LIBRARY_PATH"]
	except KeyError:
		sys.stderr.write("Your environment is not properly configured.  You must run the 'setupdaqenv.sh' script before launching the dispatcher.\n")
		sys.exit(1)

	dispatcher = MonitorDispatcher()
	dispatcher.bootstrap()
	
	sys.exit(0)
	
else:
	raise RuntimeError("This module is not designed to be imported!")
