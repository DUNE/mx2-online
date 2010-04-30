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
						
	def daq_start(self, branch, crate, controller_type, mem_slot, gate_slot, adc_slot, tdc_slot, tof_rst_gate_slot, wc_rst_gate_slot, num_events, filepattern, run, subrun, runmode):
		""" Asks the server to start the beamline DAQ. """
		
		request = "mtestbeam_start branch=%d:crate=%d:type=%d:mem_slot=%d:gate_slot=%d:adc_slot=%d:tdc_slot=%d:tof_rst_gate_slot=%d:wc_rst_gate_slot=%d:num_events=%d:run=%d:subrun=%d:runmode=%d:filepattern=%s!" % (branch, crate, controller_type, mem_slot, gate_slot, adc_slot, tdc_slot, tof_rst_gate_slot, wc_rst_gate_slot, num_events, run, subrun, runmode, filepattern)
		#print request
		self.request(request)

	def daq_stop(self):
		""" Asks the server to stop the beamline DAQ. """
		response = self.request("mtestbeam_stop!")
		
		return response == "0"
