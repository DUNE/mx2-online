"""
  MonitorDispatcher.py:
  Listener service that runs on an online monitoring node.
  It handles starting and stopping of the OM processes
  based on information it receives from the run control.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar.-Apr. 2010
                    
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
import logging
import logging.handlers

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.Dispatcher import Dispatcher

class MonitorDispatcher(Dispatcher):
	"""
	Online monitor node dispatcher.  Starts and stops the OM processes
	based on instructions received from the run control.
	"""
	def __init__(self):
		Dispatcher.__init__(self)
	
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
		self.last_etpattern = None
		self.evbfile = None
			

	def om_start(self, matches, show_details, **kwargs):
		""" Starts the online monitoring services as subprocesses.  First checks
		    to make sure it's not already running, and if it is, does nothing.

		    Returns 0 since the run control doesn't actually care if 
		    the processes are started correctly.  """
		    
		if show_details:
			self.logger.info("Client wants to start the OM processes.")

		# first clear up any old event builder processes.
		if self.om_eb_thread and self.om_eb_thread.is_alive() is None:
			self.om_eb_thread.terminate()
			self.om_eb_thread.join()
		
		# save the old etpattern if there is one--
		# we'll need it to tell the last Gaudi DST job to finish properly
		if self.etpattern is not None:
			self.last_etpattern = self.etpattern
			
		self.etpattern = matches.group("etpattern")
		self.evbfile = "%s/%s_RawData.dat" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		self.raweventfile = "%s/%s_RawEvent.root" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		self.rawhistosfile = "%s/%s_RawHistos.root" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		self.dstfile = "%s/%s_DST.root" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], self.etpattern )
		
		try:
			self.om_start_eb(etfile="%s_RawData" % matches.group("etpattern"), etport=matches.group("etport"))
		except Exception, excpt:
			self.logger.error("   ==> The event builder process can't be started!")
			self.logger.error("   ==> Error message: '" + str(excpt) + "'")
		
		return "0"		# the run control doesn't care whether this has started correctly.
	
	def om_start_eb(self, etfile, etport):
		""" Start the event builder process. """
		executable = ( "%s/bin/event_builder %s/%s %s %s %d" % (environment["DAQROOT"], Configuration.params["Master node"]["etSystemFileLocation"], etfile, self.evbfile, etport, os.getpid()) ) 
		self.logger.info("   event_builder command:")
		self.logger.info("      '" + executable + "'...")
		signal.signal(signal.SIGUSR1, self.om_start_Gaudi)
		self.om_eb_thread = OMThread(executable, "eventbuilder")
	
	def om_start_Gaudi(self, signum=None, sigframe=None):
		""" Start the Gaudi process. """
		# first clear the signal handler so an accidental call wouldn't restart the service.
		signal.signal(signal.SIGUSR1, signal.SIG_IGN)
		
		# replace the options file so that we get the new event builder output.
		with open(Configuration.params["Monitoring nodes"]["om_GaudiOptionsFile"], "w") as optsfile:
			optsfile.write("BuildRawEventAlg.InputFileName   = { \"%s\" };\n" % self.evbfile)
			optsfile.write("Event.Output = \"DATAFILE='PFN:%s' TYP='POOL_ROOTTREE' OPT='RECREATE'\";\n" % self.raweventfile)
			optsfile.write("HistogramPersistencySvc.Outputfile = \"%s\";\n" % self.rawhistosfile)
			optsfile.write("NTupleSvc.Output  = { \"FILE1 DATAFILE='%s' OPT='NEW' TYP='ROOT'\" };\n" % self.dstfile)
		
		# if the Gaudi thread is still running, it needs to be stopped.
		# the DIM command is supposed to help it shut down cleanly.  
		if self.om_Gaudi_thread is not None and self.om_Gaudi_thread.is_alive():
			subprocess.call("dim_send_command.exe NEARONLINE stop", shell=True)
			subprocess.call("dim_send_command.exe NEARONLINE_%s stop" % self.last_etpattern, shell=True)
	
			self.om_Gaudi_thread.process.terminate()
			self.om_Gaudi_thread.join()

		# now start a new copy of each of the Gaudi jobs.
		gaudi_processes = ( {"utgid": "NEARONLINE", "processname": "presenter", "optionsfile": "NearonlinePresenter.opts"}, 
		                    {"utgid": "NEARONLINE_%s" % self.etpattern, "processname": "dst", "optionsfile": "NearonlineDST.opts"} )
		for process in gaudi_processes:
			executable = "$DAQRECVROOT/$CMTCONFIG/OnlineMonitor.exe $GAUDIONLINEROOT/$CMTCONFIG/libGaudiOnline.so OnlineTask -tasktype=LHCb::Class2Task -main=$GAUDIONLINEROOT/options/Main.opts -opt=$DAQRECVROOT/options/%s -auto" % process["optionsfile"]
			
			# we will only keep track of the presenter thread, because this one
			# is the one that will be replaced (needs to have the same UTGID so
			# that the Presenter can find it properly).
			# the others will continue to run, but we'll have no handle for them
			# (which is intentional, so that they run unmolested until they finish).
			thread = OMThread(executable, "gaudi_%s" % process["processname"], process["utgid"], persistent=(process["processname"] == "dst"))
			if process["processname"] == "presenter":
				self.om_Gaudi_thread = thread
			elif process["processname"] == "dst":
				thread.dstfile = self.dstfile

			self.logger.info("   Starting a copy of OnlineMonitor using the following command:\n%s", executable)
	
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
				self.logger.info("   ==> Attempting to stop the Gaudi thread.")
			try:
				# both Gaudi jobs need a DIM "stop" command,
				# but only the Presenter one will be forcibly terminated.
				subprocess.call("dim_send_command.exe NEARONLINE stop", shell=True)
				subprocess.call("dim_send_command.exe NEARONLINE_%s stop" % self.etpattern, shell=True)
				self.om_Gaudi_thread.process.terminate()
				self.om_Gaudi_thread.join()		# 'merges' this thread with the other one so that we wait until it's done.
			except Exception, excpt:
				self.logger.error("   ==> Gaudi process couldn't be stopped!")
				self.logger.exception("   ==> Error message:")
				errors = True

		if show_details:
			self.logger.info("   ==> Stopped successfully.")
		
		return "0" if not errors else "1"
		

#########################
# OMThread             #
#########################
class OMThread(threading.Thread):
	""" OM processes need to be run in a separate thread
	    so that we know if they finish. """
	def __init__(self, command, processname, utgid="", persistent=False):
		threading.Thread.__init__(self)
		
		self.process = None
		self.command = "UTGID=%s %s" % (utgid, command)
		self.utgid = utgid
		self.processname = processname
		self.persistent = persistent		# if this thread is supposed to run until it finishes
		
		self.dstfile = None				# overridden as necessary by the parent process.
		
		self.daemon = True
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		# redirect any output to a log file
		i = 1
		while True:
			filename = "%s/%s.%d.log" % (Configuration.params["Monitoring nodes"]["om_logfileLocation"], self.processname, i)
			with open(filename, "w") as fileobj:
				# try to get a lock on the log file.
				# this ensures we don't write to the same one via
				# two different processes.
				try:
					fcntl.flock(fileobj.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
				# if the file is already locked, we'll try a new filename.
				except IOError:
					i += 1
					continue
				
				try:
					# the subprocesses need access to a bunch of environment
					# variables from this process's startup environment:
					# hence the 'shell=True'.  don't remove that.
					self.process = subprocess.Popen(self.command, shell=True, stdout=fileobj.fileno(), stderr=subprocess.STDOUT)
					self.pid = self.process.pid		# less typing.

					# now wait until the process finishes.
					# we need to check up on it via DIM every so often...
					# (it doesn't quit all the way out unless killed
					#  or sent an "unload" command via DIM) 
					lastcheck = time.time()
					while self.process.poll() is None:
						# no busy-waiting.
						time.sleep(0.25)
						
						# check every 60 seconds.
						if time.time() - lastcheck > 60 and self.persistent:
							lastcheck = time.time()
							dimcmd = subprocess.Popen("dim_get_service.exe %s/status" % self.utgid, shell=True, stdout=subprocess.PIPE)
							stdout, stderr = dimcmd.communicate()
							
#							print stdout
							
							# the DIM response includes the word "RUNNING" if
							# the process is still going, and "READY" instead
							# if it's done and waiting.
							if "READY" in stdout:
								self.process.terminate()
					self.returncode = self.process.returncode
				# we want to release the lock no matter what happens!
				finally:
					fcntl.flock(fileobj.fileno(), fcntl.LOCK_UN)
				
				break
		
		# copy the DST to its target location.
		if self.persistent and self.dstfile:
			shutil.copy2(self.dstfile, Configuration.params["Monitoring nodes"]["om_DSTTargetPath"])
                        
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
