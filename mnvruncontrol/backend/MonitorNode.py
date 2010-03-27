"""
  MonitorNode.py:
  Module that models an online monitoring node.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar.-Apr. 2010
                    
   Address all complaints to the management.
"""

import re
import time
import socket

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import MetaData

from mnvruncontrol.backend import RemoteNode

class MonitorNode(RemoteNode):
	def __init__(self, name, address):
		RemoteNode.__init__(self, name, address)
		
		self.ValidRequests += SocketRequests.MonitorRequests
						
	def om_start(self, etfile, etport):
		""" Asks the server to start the OM processes. """
		
		request = "om_start etfile=%s:etport=%d!" % (etfile, etport)
		#print request
		self.request(request)

	def om_stop(self):
		""" Asks the server to stop the OM processes. """
		self.request("om_stop!")
