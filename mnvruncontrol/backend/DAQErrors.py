"""
  DAQErrors.py:
  Errors used by the DataAcquisitionManager.
  
  They are abstracted here so they can be properly
  unpickled when sent via a PostOffice Message.
  (It just works better when they're in their
  own module.)
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Nov. 2010
                    
   Address all complaints to the management.
"""

class AlertError(Exception):
	pass

class ConfigurationError(Exception):
	pass
	
class FileError(Exception):
	pass
	
class NodeError(Exception):
	pass
	
class RunError(Exception):
	pass
