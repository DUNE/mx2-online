# Meta Data Module
		
# need variable "daqStop"
		
SpecialGUI         = {'Depricated':0}

OperatingModes     = {'OneShot'        :0,
                      'Cosmic'         :1,
                      'MixedModePedLI' :2,
                      'MTM'            :3,
                      'MixedModeMTMLI' :4,
                      'MixedModePedMTM':5}

HardwareInitLevels = {'FullHWInit':0,
                      'NoHWInit'  :1}

LILevels           = {'ZeroPE':0,
                      'OnePE' :1,
                      'MaxPE' :2}

DetectorTypes      = {'UnknownDetector'  :0,
                      'PMTTestStand'     :1,
                      'TrackingPrototype':2,
                      'TestBeam'         :4,
                      'MINERvA'          :8}

TriggerTypes       = {'UnknownTrigger'     :0,
                      'Pedestal'           :1,
                      'LightInjection'     :2,
                      'ChargeInjection'    :4,
                      'Cosmic'             :8,
                      'NuMI'               :16,
                      'NuMI_Pedestal'      :32,
                      'NuMI_LightInjection':64}
 
#Special Type Arrays

specGUI   = tuple(sorted(SpecialGUI.values()))
opModes   = tuple(sorted(OperatingModes.values()))
hwLevels  = tuple(sorted(HardwareInitLevels.values()))
liLevels  = tuple(sorted(LILevels.values()))
detTypes  = tuple(sorted(DetectorTypes.values()))
trigTypes = tuple(sorted(TriggerTypes.values()))
        	
#public static readonly DateTime EpochTime = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);

#public static Logger log = new Logger(true);

runMinervaDAQScript    = 'runminervadaq.bat'
dataPath               = '/home/data/'
DAQScriptPath          = '/home/swroot/minerva/MinervaScripts/'
daqConfigDirectoryPath = '/home/data/configurations/daqconfig/'
liConfigDirectoryPath  = '/home/data/configurations/liconfig/'
runLIScript            = 'yattest.bat'

# Run Log (Run Number file counter) & Stop/Go Info
HiddenRunPath = '/zHidden/'
destroyRunLog = False;
silentRunLog  = True;
#public static Logger runlog = new Logger(HiddenRunPath, destroyRunLog, silentRunLog);
#public static Logger stopgolog = new Logger(HiddenRunPath, destroyRunLog, silentRunLog);

