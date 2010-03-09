"""
  RunControlClientConnection.py:
  Module that handles the socket connection from the client
  (the readout "queen" in Gabe's language) to the readout nodes
  actually attached to hardware (the "soldier" and "worker" nodes).
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb. 2010
                    
   Address all complaints to the management.
"""

import re
import socket

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import MetaData

class RunControlClientConnection:
	def __init__(self, serveraddress):
		self.socket = None
		self.serveraddress = serveraddress
		self.port = Defaults.DISPATCHER_PORT
		
		try:
			self.request("alive?")
		except socket.error:
			raise RunControlClientException("Couldn't connect to the server.  Are you sure you have the right address and that the run control dispatcher has been started on the server?")
		
	def request(self, request):
		is_valid_request = False
		for valid_request in SocketRequests.ValidRequests:
			if re.match(valid_request, request) is not None:
				is_valid_request = True
				break
		
		if not is_valid_request:
			raise RunControlBadRequestException("Invalid request: '" + request + "'")
		
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.socket.settimeout(2)
			self.socket.connect( (self.serveraddress, self.port) )
			self.socket.send(request)
			self.socket.shutdown(socket.SHUT_WR)		# notifies the server that I'm done sending stuff
		except socket.error:
			self.socket.close()
			raise RunControlNoClientConnectionException()
		
		response = ""
		datalen = -1
		while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
			data = self.socket.recv(1024)
			datalen = len(data)
			response += data
		
		self.socket.close()
		
		return response
	
	def ping(self):
		""" Requests confirmation from the server that it is indeed alive and well. """
		try:
			response = self.request("alive?")
		except:
			return False
		
		return len(response) > 0		# if we got ANYTHING back, then it's alive
	
	def daq_checkStatus(self):
		""" Asks the server to check and see if its DAQ process is running. """
		response = self.request("daq_running?")

		if response == "1":
			return True
		elif response == "0":
			return False
		else:
			raise RunControlClientUnexpectedDataException("Unexpected response: " + response)
	
	def daq_checkLastExitCode(self):
		""" Asks for the return code from the last DAQ process to run.
		    Returns None if the DAQ hasn't yet been run yet or is still running. """
		response = self.request("daq_last_exit?")
		if response == "NONE":		# DAQ process hasn't been run yet or is still running
			return None
		else:					
			return int(response)
			
	def daq_start( self, identity, etfile, runNum, subRunNum, numGates=10,
	               runMode=MetaData.RunningModes["One shot", MetaData.HASH],
	               detector=MetaData.DetectorTypes["Unknown", MetaData.HASH],
	               numFEBs=114, LIlevel=MetaData.LILevels["Zero PE", MetaData.HASH],
	               LEDgroup=MetaData.LEDGroups["All", MetaData.HASH],
	               HWInit=MetaData.HardwareInitLevels["No HW init", MetaData.HASH]):
		""" Asks the server to start the DAQ process.  Returns True on success,
		    False on failure, and raises an exception if the DAQ is currently running. """
		
		request = "daq_start etfile=%s:run=%d:subrun=%d:gates=%d:runmode=%d:detector=%d:nfebs=%d:lilevel=%d:ledgroup=%d:hwinitlevel=%d:identity=%s!" % (etfile, runNum, subRunNum, numGates, runMode, detector, numFEBs, LIlevel, LEDgroup, HWInit, identity)
		#print request
		response = self.request(request)
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise RunControlClientException("The DAQ slave process is currently running!  You can't start it again...")
		else:
			raise RunControlClientUnexpectedDataException("Unexpected response: " + response)

	def daq_stop(self):
		""" Asks the server to stop the DAQ process.  Returns True on success,
		    False on failure, and raises an exception if no DAQ process
		    is currently running. """
		response = self.request("daq_stop!")
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise RunControlClientException("The DAQ slave process is not currently running, so it can't be stopped.")
		else:
			raise RunControlClientUnexpectedDataException("Unexpected response: " + response)

	def sc_loadHWfile(self, filename):
		""" Asks the server to load the specified hardware configuration file. 
		    Returns 0 on success, 1 on failure, and 2 if the file doesn't exist. """
		response = self.request("sc_sethw " + filename + "!")	
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise RunControlClientException("The specified slow control configuration does not exist.")
		else:
			raise RunControlClientUnexpectedDataException("Unexpected response: " + response)

	def sc_readVoltages(self):
		""" Asks the server for a list of the voltages on each of the FEBs.
		    On success, returns a list of dictionaries with the following keys:
	    		    "fpga", "croc", chain", "board", "voltage"
	    	    On failure, returns None.	"""
		response = self.request("sc_voltages?")
		if response == "NOREAD" or response == "":
			return None
		
		feb_data = []
		
		lines = response.splitlines()
		for line in lines:
			febdict = {}
			
			board_id, voltage = line.split(": ")
			voltage = float(voltage)
			
			fpga, croc, chain, board = board_id.split("-")
			for item in (fpga, croc, chain, board):
				item = int(item)
			
			febdict["fpga"] = fpga
			febdict["croc"] = croc
			febdict["chain"] = chain
			febdict["board"] = board
			febdict["voltage"] = voltage
			
			feb_data.append(febdict)
		
		return feb_data
		
		
		
class RunControlClientException(Exception):
	pass

class RunControlBadRequestException(Exception):
	pass

class RunControlClientUnexpectedDataException(Exception):
	pass
	
class RunControlNoClientConnectionException(Exception):
	pass
