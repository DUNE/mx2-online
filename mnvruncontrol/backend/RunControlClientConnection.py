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

class RunControlClientConnection:
	def __init__(self, serveraddress):
		self.socket = None
		self.serveraddress = serveraddress
		
		try:
			self.request("alive?")
		except:
			raise RunControlClientException("The server does not appear to be responding.  Are you sure you have the right address and that the run control dispatcher has been started on the server?")
		
	def request(self, request):
		request = request.lower()
		
		is_valid_request = False
		for valid_request in SocketRequests.ValidRequests:
			if re.match(valid_request, request) is not None:
				is_valid_request = True
				break
		
		if not is_valid_request:
			raise RunControlClientException("Invalid request: '" + request + "'")
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.bind( (self.serveraddress, Defaults.DISPATCHER_PORT) )
		self.socket.send(request)
		self.socket.shutdown(socket.SHUT_WR)		# notifies the server that I'm done sending stuff
		
		response = ""
		datalen = -1
		while datalen != 0:		# when the socket closes (a receive of 0 bytes) we assume we have the entire request
			data = client_socket.recv(1024)
			datalen = len(data)
			response += data
		
		requestname = matches.group("request")
		if requestname == "alive":
			return len(response) > 0			# if we got ANYTHING back, then it's alive
		elif requestname == "daq_running":
			if response == "1":			# "1" if it's running, "0" if not
				return True
			elif response == "0":
				return False
			else:
				raise RunControlClientUnexpectedDataException()
		elif requestname == "daq_last_exit":
			if 
			return int(response)
		
class RunControlClientException(Exception):
	pass

class RunControlClientUnexpectedDataException(Exception):
	pass
