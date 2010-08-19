"""
  ReadoutNode.py:
   Module that models a readout node.
   It wraps the socket connection from the client
   (the readout "queen" in Gabe's language) to the readout nodes
   actually attached to hardware (the "soldier" and "worker" nodes)
   using the RemoteNode base class.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar. 2010
                    
   Address all complaints to the management.
"""

import re

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import MetaData

from mnvruncontrol.backend import RemoteNode

class ReadoutNode(RemoteNode.RemoteNode):
	def __init__(self, name, address):
		RemoteNode.RemoteNode.__init__(self, name, address)
		
		self.ValidRequests += SocketRequests.ReadoutRequests
		self.nodetype = "readout"
		
		self.configured = False
		self.completed = False
		
		self.shutting_down = False
		self.sent_sentinel = False
		
	def daq_checkStatus(self):
		""" Asks the server to check and see if its DAQ process is running. """
		response = self.request("daq_running?")

		if response == "1":
			return True
		elif response == "0":
			return False
		else:
			raise ReadoutNodeUnexpectedDataException("Unexpected response: " + response)
	
	def daq_checkLastExitCode(self):
		""" Asks for the return code from the last DAQ process to run.
		    Returns None if the DAQ hasn't yet been run yet or is still running. """
		response = self.request("daq_last_exit?")
		if response == "NONE":		# DAQ process hasn't been run yet or is still running
			return None
		else:					
			return int(response)
			
	def daq_start( self, etfile, etport, runNum, subRunNum, numGates=10,
	               runMode=MetaData.RunningModes.ONE_SHOT.hash,
	               detector=MetaData.DetectorTypes.UNKNOWN.hash,
	               numFEBs=114, LIlevel=MetaData.LILevels.ZERO_PE.hash,
	               LEDgroup=MetaData.LEDGroups.ABCD.hash,
	               HWInit=MetaData.HardwareInitLevels.NO_HW_INIT.hash ):
		""" Asks the server to start the DAQ process.  Returns True on success,
		    False on failure, and raises an exception if the DAQ is currently running. """
		
		request = "daq_start etfile=%s:etport=%d:run=%d:subrun=%d:gates=%d:runmode=%d:detector=%d:nfebs=%d:lilevel=%d:ledgroup=%d:hwinitlevel=%d!" % (etfile, etport, runNum, subRunNum, numGates, runMode, detector, numFEBs, LIlevel, LEDgroup, HWInit)
		#print request
		try:
			response = self.request(request)
		except RemoteNode.RemoteNodeNoConnectionException:
			raise ReadoutNodeNoConnectionException()		# this is the type of exception DAQMgr is expecting
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise ReadoutNodeException("The DAQ slave process is currently running!  You can't start it again...")
		else:
			raise ReadoutNodeUnexpectedDataException("Unexpected response: " + response)

	def daq_stop(self):
		""" Asks the server to stop the DAQ process.  Returns True on success,
		    False on failure, and raises an exception if no DAQ process
		    is currently running. """
		    
		self.shutting_down = True
		
		try:
			response = self.request("daq_stop!")
		except RemoteNode.RemoteNodeNoConnectionException:
			return False
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise ReadoutNodeNoDAQRunningException("The DAQ slave process is not currently running, so it can't be stopped.")
		else:

	def li_configure(self, li_level, led_groups=None):
		""" Asks the server to configure the light injection system
		    using the specified settings.
		    
		    To disable LI, pass an li_level of ZERO_PE. """
		
		assert (li_level == MetaData.ZERO_PE or led_groups is not None)
		
		if li_level == MetaData.ZERO_PE:
			led_groups = MetaData.LEDGroups.ABCD.hash
		
		response = self.request("li_configure li_level=%d:led_groups=%d" % (li_level, led_groups))
		
		if response == "0":
			return True
		elif response == "1":
			return False
		else:
			raise ReadoutNodeUnexpectedDataException("Unexpected response: " + response)

	def sc_loadHWfile(self, filehash):
		""" Asks the server to load the specified hardware configuration file. 
		    Returns 0 on success, 1 on failure, and 2 if the file doesn't exist. 
		    Note that the return value only indicates receipt of the message and
		    ability to start: it takes a while for the slow control initialization
		    to actually finish.  When it does, the dispatcher sends a message
		    back to the master node. """
		try:
			response = self.request("sc_setHWconfig %d!" % filehash)	
		except RemoteNode.RemoteNodeNoConnectionException:
			raise ReadoutNodeNoConnectionException()		# this is the type of exception DAQMgr is expecting
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise ReadoutNodeException("The specified slow control configuration does not exist.")
		else:
			raise ReadoutNodeUnexpectedDataException("Unexpected response: '%s'" % response)

	def sc_readBoards(self):
		""" Asks the server for a list of the HV information on each of the FEBs.
		    On success, returns a list of dictionaries with the following keys:
	    		    "croc", chain", "board", "voltage_dev", "period"
	    	    On failure, returns None.	"""
		response = self.request("sc_readboards?")
		if response == "NOREAD":
			return None
	
		if response == "NOBOARDS":
			return 0
	
		feb_data = []
		
		lines = response.splitlines()
		pattern = re.compile("^(?P<croc>\d+)-(?P<chain>\d+)-(?P<board>\d+): (?P<hv_dev>-?\d+) (?P<hv_period>\d+)$")
		for line in lines:
			matches = pattern.match(line)
			if matches == None:		# skip any lines that don't make sense... dangerous to fail quietly?
				continue
			
			feb_data.append(matches.groupdict())
		
		return feb_data
		
		
		
class ReadoutNodeException(Exception):
	pass
	
class ReadoutNodeNoDAQRunningException(Exception):
	pass

class ReadoutNodeBadRequestException(Exception):
	pass

class ReadoutNodeUnexpectedDataException(Exception):
	pass
	
class ReadoutNodeNoConnectionException(Exception):
	pass
