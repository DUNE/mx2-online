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
import time
import sys
import os
import logging
import logging.handlers

from mnvruncontrol.configuration import MetaData
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
		                        
		self.pidfilename = Configuration.params["Monitoring nodes"]["om_PIDfileLocation"]
		                   
		self.om_eb_thread = None
		self.om_Gaudi_thread = None
		
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
			
		self.evbfile = "%s/%s_RawData.dat" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], matches.group("etpattern") )
		self.raweventfile = "%s/%s_RawEvent.dat" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], matches.group("etpattern") )
		self.rawhistosfile = "%s/%s_RawHistos.dat" % ( Configuration.params["Monitoring nodes"]["om_rawdataLocation"], matches.group("etpattern") )
		
		try:
			self.om_start_eb(etfile="%s_RawData" % matches.group("etpattern"), etport=matches.group("etport"))
		except Exception, excpt:
			self.logger.error("   ==> The event builder process can't be started!")
			self.logger.error("   ==> Error message: '" + str(excpt) + "'")
		
		return "0"		# the run control doesn't care whether this has started correctly.
	
	def om_start_eb(self, etfile, etport):
		""" Start the event builder process. """
		executable = ( "%s/bin/event_builder %s/%s %s %s %d" % (environment["DAQROOT"], Configuration.params["Front end"]["etSystemFileLocation"], etfile, self.evbfile, etport, os.getpid()) ) 
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
			optsfile.write("BuildRawEventAlg.InputFileName   = \"%s\";" % self.evbfile)
			optsfile.write("Event.Output = \"DATAFILE='PFN:%s' TYP='POOL_ROOTTREE' OPT='RECREATE'\";" % self.raweventfile)
			optsfile.write("HistogramPersistencySvc.Outputfile = \"%s\";" % self.rawhistosfile)
		
		# if the Gaudi thread is still running, just have DIM stop and restart it.
		if self.om_Gaudi_thread is not None and self.om_Gaudi_thread.is_alive():
			subprocess.call("dim_send_command.exe NEARONLINE stop", shell=True)
			subprocess.call("dim_send_command.exe NEARONLINE start", shell=True)
		# otherwise, start it fresh.
		else:
			executable = ("$DAQRECVROOT/$CMTCONFIG/OnlineMonitor.exe $GAUDIONLINEROOT/$CMTCONFIG/libGaudiOnline.so OnlineTask -tasktype=LHCb::Class2Task -main=$GAUDIONLINEROOT/options/Main.opts -opt=$DAQRECVROOT/options/Nearonline.opts -auto")
			self.om_Gaudi_thread = OMThread(executable, "gaudi")

			self.logger.info("   OnlineMonitor command:")
			self.logger.info("      '" + executable + "'...")
	
	def om_stop(self, matches, show_details, **kwargs):
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
				self.om_Gaudi_thread.daq_process.terminate()
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
	def __init__(self, command, processname):
		threading.Thread.__init__(self)
		
		self.process = None
		self.command = command
		self.processname = processname
		
		self.start()		# inherited from threading.Thread.  starts run() in a separate thread.
		
	def run(self):
		# unfortunately we need to run these through the shell so they get all the right environment
		# variables from this process's parent environment.
		self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		self.pid = self.process.pid		# less typing.

		stdout, stderr = self.process.communicate()
		
		filename = "%s/%s.log" % (Configuration.params["Monitoring nodes"]["om_logfileLocation"], self.processname)
		# dump the output of the process to a file so that crashes can be investigated.
		# we only keep one copy because it will be rare that anyone is interested.
		try:
			with open(filename, "w") as logfile:
				logfile.write(stdout)
		except OSError:
			self.owner_process.logger.exception("OM process log file error:")
			self.owner_process.logger.error("   ==> log file information will be discarded.")

		self.returncode = self.process.returncode
		
                        
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
