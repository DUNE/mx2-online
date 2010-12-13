"""
  ReadoutNode.py:
  Module that models a readout node.
  It handles the socket connection from the client
  (the readout "queen" in Gabe's language) to the readout nodes
  actually attached to hardware (the "soldier" and "worker" nodes)
  as well as taking care of a few other details.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar. 2010
                    
   Address all complaints to the management.
"""

import re
import time
import socket

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import MetaData

class ReadoutNode:
	def __init__(self, name, address):
		self.socket = None
		self.name = name
		self.address = address
		self.port = Defaults.DISPATCHER_PORT
		
	def request(self, request, use_timeout=False):
		is_valid_request = False
		for valid_request in SocketRequests.ValidRequests:
			if re.match(valid_request, request) is not None:
				is_valid_request = True
				break
		
		if not is_valid_request:
			raise ReadoutNodeBadRequestException("Invalid request: '" + request + "'")
		
		tries = 0
		success = False
		while tries < Defaults.MAX_CONNECTION_ATTEMPTS and not success:
			response = ""
			try:
				self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				if use_timeout:
					self.socket.settimeout(Defaults.SOCKET_TIMEOUT)
				self.socket.connect( (self.address, self.port) )
				self.socket.send(request)
				self.socket.shutdown(socket.SHUT_WR)		# notifies the server that I'm done sending stuff

				datalen = -1
				while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire response
					data = self.socket.recv(1024)
					datalen = len(data)
					response += data

				success = True
			except socket.timeout, e:
				time.sleep(Defaults.CONNECTION_ATTEMPT_INTERVAL)		# wait a little to make sure we don't overload the dispatcher
			except socket.error, e:
				print e
			finally:
				self.socket.close()
				
			# an empty response is the sign of a broken connection.
			# (none of the queries will return with a blank response.)
			# we'll want to try again.
			if response == "":
				success = False
				tries += 1
				continue

		if tries >= Defaults.MAX_CONNECTION_ATTEMPTS:
			raise ReadoutNodeNoConnectionException()

		return response
	
	def ping(self):
		""" Requests confirmation from the server that it is indeed alive and well. """
		try:
			response = self.request("alive?", use_timeout=True)
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
	               runMode=MetaData.RunningModes["One shot", MetaData.HASH],
	               detector=MetaData.DetectorTypes["Unknown", MetaData.HASH],
	               numFEBs=114, LIlevel=MetaData.LILevels["Zero PE", MetaData.HASH],
	               LEDgroup=MetaData.LEDGroups["ABCD", MetaData.HASH],
	               HWInit=MetaData.HardwareInitLevels["No HW init", MetaData.HASH]):
		""" Asks the server to start the DAQ process.  Returns True on success,
		    False on failure, and raises an exception if the DAQ is currently running. """
		
		request = "daq_start etfile=%s:etport=%d:run=%d:subrun=%d:gates=%d:runmode=%d:detector=%d:nfebs=%d:lilevel=%d:ledgroup=%d:hwinitlevel=%d:identity=%s!" % (etfile, etport, runNum, subRunNum, numGates, runMode, detector, numFEBs, LIlevel, LEDgroup, HWInit, self.name)
		#print request
		response = self.request(request)
		
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
		response = self.request("daq_stop!")
		
		if response == "0":
			return True
		elif response == "1":
			return False
		elif response == "2":
			raise ReadoutNodeException("The DAQ slave process is not currently running, so it can't be stopped.")
		else:
			raise ReadoutNodeUnexpectedDataException("Unexpected response: " + response)

	def sc_loadHWfile(self, filename):
		""" Asks the server to load the specified hardware configuration file. 
		    Returns 0 on success, 1 on failure, and 2 if the file doesn't exist. """
		response = self.request("sc_setHWconfig '" + filename + "'!")	
		
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

class ReadoutNodeBadRequestException(Exception):
	pass

class ReadoutNodeUnexpectedDataException(Exception):
	pass
	
class ReadoutNodeNoConnectionException(Exception):
	pass
