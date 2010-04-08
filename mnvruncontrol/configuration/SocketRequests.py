"""
  SocketRequests.py:
   The requests that are considered "valid" by the
   dispatchers.  They are encoded in regular expression
   form (see the Python regular expression documentation,
       http://docs.python.org/library/re.html,
   and the references contained therein if you are 
   unfamiliar with it.)
     
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

GlobalRequests =  [ "(?P<request>alive)\?",
                    "(?P<request>get_lock) (?P<identity>\S+)!",
                    "(?P<request>release_lock)!" ]

ReadoutRequests = [ "(?P<request>daq_running)\?",
                    "(?P<request>daq_last_exit)\?",
                    "(?P<request>daq_start) etfile=(?P<etfile>\S+):etport=(?P<etport>\d+):run=(?P<run>\d+):subrun=(?P<subrun>\d+):gates=(?P<gates>\d+):runmode=(?P<runmode>\d+):detector=(?P<detector>\d+):nfebs=(?P<nfebs>\d+):lilevel=(?P<lilevel>\d+):ledgroup=(?P<ledgroup>\d+):hwinitlevel=(?P<hwinitlevel>\d+)!",
                    "(?P<request>daq_stop)!",
                    "(?P<request>sc_setHWconfig) (?P<hwconfig>\d+)!",
                    "(?P<request>sc_readboards)\?" ]

MonitorRequests = [ "(?P<request>om_start) etpattern=(?P<etpattern>\S+):etport=(?P<etport>\d+)!",
                    "(?P<request>om_stop)!",
                    "(?P<request>om_alive)\?" ]
                    
Notification = "FOR:(?P<addressee>[\d\w\-]+) FROM:(?P<sender>\S+) MSG:(?P<message>.*)"
