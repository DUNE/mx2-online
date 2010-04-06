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
