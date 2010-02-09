import MetaData
import datetime

class RunSeries:
	
        def __init__(self):
		self.Runs = list()

	def FirstRun(self):
	        try:
			return self.Runs[0]
        	except:
			print 'RunSeries: Could not retrieve first run.  Runs container may be empty'

	def AppendToRunList(self,runInfo):     
		self.Runs.append(runInfo)
	
        def ClearRunList(self):
		self.Runs = []

	def Show(self):
		infoAllRuns = ''
		for runInfo in self.Runs:
			infoAllRuns += runInfo.ToString() + '\n'
		return infoAllRuns

# Each run is characterized by the following elements:
#       sequence # -> a value that establishes the ordering of a group of subruns (internal)
#       type -> the kind of run to be taken
#       run number -> the run number
#       DAQ config -> the name of the xml file the Configurator should apply
#       LI config -> the name of the file the YAT should execute for the LI box
#       Time -> length of a run in seconds
#       # of Events -> number of events in the subrun
#       file base -> name of output file
#       hw init level -> does the DAQ do any hardware inits?
#       operating mode -> run mode for CRIM, redunant with run type?
#       crocList -> set of static crocs to read out (0 is dynamic look up)
# During a run series, the DAQ will step through a list of subruns, all with the 
# same *run* number, according to the parameters specified in this object.  If 
# both time and number of events are specified, the DAQ should stop its run when 
# the earliest of the two conditions are reached.

class RunInfo(object):

	def __init__(self,
		     detector          = MetaData.DetectorTypes['UnknownDetector'],
		     sequenceNumber    = 0,
		     runType           = MetaData.TriggerTypes['UnknownTrigger'],
		     runNumber         = 0,
		     subRunNumber      = 0,
            	     daqConfigFile     = 'daqConfig', # No reasonable default? -> SlowControl xml
                     liConfigFile      = 'liConfig', # No reasonable default? -> LI Box config
                     runTimeLength     = 60, # seconds
                     numberOfEvents    = 0, # events
                     fileBase          = 'Run0',
                     hwInitLevel       = MetaData.HardwareInitLevels['NoHWInit'], # no init
                     operatingMode     = MetaData.OperatingModes['OneShot'], # default mode right now is oneShot
                     version           = 1,
                     liLevel           = 0,
                     liEnabled         = False,
                     detectorConfig    = 0,
                     pulserEventPeriod = 10,
                     pulserHeight      = 4.05,
                     ledtoprow         = 1,
                     ledbotrow         = 0,
                     crocList          = 0):

		self.detector          = detector
		self.sequenceNumber    = sequenceNumber
		self.runType           = runType
		self.runNumber         = runNumber
		self.subRunNumber      = subRunNumber
		self.daqConfigFile     = daqConfigFile
		self.liConfigFile      = liConfigFile
		self.runTimeLength     = runTimeLength
		self.numberOfEvents    = numberOfEvents
		self.fileBase          = fileBase
		self.hwInitLevel       = hwInitLevel
		self.operatingMode     = operatingMode
		self.version           = version
		self.liLevel           = liLevel
		self.liEnabled         = liEnabled
		self.detectorConfig    = detectorConfig
		self.pulserEventPeriod = pulserEventPeriod
		self.pulserHeight      = pulserHeight
		self.ledtoprow         = ledtoprow
		self.ledbotrow         = ledbotrow
		self.crocList          = crocList

	def BuildFileBase(self):
        
		det = 'UN' # Default: 'UN' denotes unknown detector type
                if self.detector == MetaData.DetectorTypes['TrackingPrototype']:
			det = 'TP'
                elif self.detector == MetaData.DetectorTypes['TestBeam']:
			det = 'TB'
                elif self.detector == MetaData.DetectorTypes['PMTTestStand']:
			det = 'FT'
                elif self.detector == MetaData.DetectorTypes['MINERvA']:
			det = 'MN'

		trig = 'unknown'		
		if self.runType ==  MetaData.TriggerTypes['Pedestal']:
			trig = 'pdstl'
                elif self.runType == MetaData.TriggerTypes['LightInjection']:
			trig = 'linjc'
		elif self.runType == MetaData.TriggerTypes['ChargeInjection']:
			trig = 'chinj'
                elif self.runType == MetaData.TriggerTypes['Cosmic']:
			trig = 'cosmc'
                elif self.runType == MetaData.TriggerTypes['NuMI']:
			trig = 'numib'
		elif self.runType == MetaData.TriggerTypes['NuMI_Pedestal']:
			trig = 'numip'
		elif self.runType == MetaData.TriggerTypes['NuMI_LightInjection']:
			trig = 'numil'
                elif self.runType == MetaData.TriggerTypes['UnknownTrigger']:
			trig = 'unkwn'
		
		now = datetime.datetime.utcnow()

                self.filebase = '%s_%08d_%04d_%s_v04_%02d%02d%02d%02d%02d' % (det,
									      int(self.runNumber),
									      int(self.subRunNumber),
									      trig,
									      now.year % 100,
									      now.month,
									      now.day,
									      now.hour,
									      now.minute)
        
	def ToString(self):

                dump  = 'Detector              = %s\n' % self.detector
                dump += 'Sequence Number       = %s\n' % self.sequenceNumber
                dump += 'Run Type              = %s\n' % self.runType
                dump += 'Run Number            = %s\n' % self.runNumber
                dump += 'SubRun Number         = %s\n' % self.subRunNumber
                dump += 'DAQ Config File       = %s\n' % self.daqConfigFile
                dump += 'LI Config File        = %s\n' % self.liConfigFile
                dump += 'Run Time (s)          = %s\n' % self.runTimeLength
                dump += 'Num. of Events        = %s\n' % self.numberOfEvents
                dump += 'HW Init Level         = %s\n' % self.hwInitLevel
                dump += 'Operating Mode        = %s\n' % self.operatingMode
                dump += 'DAQ Version           = %s\n' % self.version
                dump += 'LI Level              = %s\n' % self.liLevel
                dump += 'LI Enabled            = %s\n' % self.liEnabled
                dump += 'Config. Code          = %s\n' % self.detectorConfig
                dump += 'Pulser Event Period   = %s\n' % self.pulserEventPeriod
                dump += 'Pulser Height         = %s\n' % self.pulserHeight
                dump += 'Pulser Code (Top Row) = %s\n' % self.ledtoprow
                dump += 'Pulser Code (Bot Row) = %s\n' % self.ledbotrow
                dump += 'CROC List Code        = %s\n' % self.crocList
		
		return dump
