ValidRequests = ( "(?P<request>alive)\?",
                  "(?P<request>daq_running)\?",
                  "(?P<request>daq_last_exit)\?",
                  "(?P<request>daq_start) etfile=(?P<etfile>\S+):etport=(?P<etport>\d+):run=(?P<run>\d+):subrun=(?P<subrun>\d+):gates=(?P<gates>\d+):runmode=(?P<runmode>\d+):detector=(?P<detector>\d+):nfebs=(?P<nfebs>\d+):lilevel=(?P<lilevel>\d+):ledgroup=(?P<ledgroup>\d+):hwinitlevel=(?P<hwinitlevel>\d+):identity=(?P<identity>(\w+))!",
                  "(?P<request>daq_stop)!",
                  "(?P<request>sc_setHWconfig) (?P<filename>\S+)!",
                  "(?P<request>sc_voltages)\?" )

