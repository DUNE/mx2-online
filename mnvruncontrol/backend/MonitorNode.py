"""
  MonitorNode.py:
  Module that models an online monitoring node.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Mar.-Apr. 2010
                    
   Address all complaints to the management.
"""

from mnvruncontrol.configuration import SocketRequests

from mnvruncontrol.backend import RemoteNode

class MonitorNode(RemoteNode):
	def __init__(self, name, address):
		RemoteNode.__init__(self, name, address)
		
		self.ValidRequests += SocketRequests.MonitorRequests
						
	def om_start(self, etpattern, etport):
		""" Asks the server to start the OM processes. """
		
		request = "om_start etpattern=%s:etport=%d!" % (etpattern, etport)
		#print request
		self.request(request)

	def om_stop(self):
		""" Asks the server to stop the OM processes. """
		self.request("om_stop!")
