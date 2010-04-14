"""
  MTestBeamNode.py:
   Module that models the beamline DAQ node at MTest.
   Inherits most of its functionality from RemoteNode.

  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Apr. 2010
                    
   Address all complaints to the management.
"""

from mnvruncontrol.configuration import SocketRequests
from mnvruncontrol.configuration import Configuration

from mnvruncontrol.backend.RemoteNode import RemoteNode

class MTestBeamNode(RemoteNode):
	def __init__(self, name, address, id=None):
		RemoteNode.__init__(self, name, address, id)
		
		self.ValidRequests += SocketRequests.MTestBeamRequests
		self.nodetype = "mtestbeam"
						
	def daq_start(self, filepattern):
		""" Asks the server to start the beamline DAQ. """
		
		request = "mtestbeam_start filepattern=%s!" % filepattern
		#print request
		self.request(request)

	def daq_stop(self):
		""" Asks the server to stop the beamline DAQ. """
		response = self.request("mtestbeam_stop!")
		
		return response == "0"
