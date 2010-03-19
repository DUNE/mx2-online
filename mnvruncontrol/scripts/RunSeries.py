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

	def __init__(   self,
			run        = 1,
                        subrun     = 1,
                        gates      = 0,
                        runLength  = 0,
                        runMode    = "Null",
                        detector   = "Null",
                        febs       = 1,
                        ledLevel   = "Off",
                        ledGroup   = "None",
			configFile = "",
			etFile     = ""):

		self.run        = run
		self.subrun     = subrun
		self.gates      = gates
		self.runLength  = runLength
		self.runMode    = runMode
		self.detector   = detector
		self.febs       = febs
		self.ledLevel   = ledLevel
		self.ledGroup   = ledGroup
                self.configFile = configFile
                self.etFile     = etFile

	"""
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
	"""        

	def ToString(self):

                dump  = 'Run Number            = %s\n' % self.run
                dump += 'SubRun Number         = %s\n' % self.subrun
                dump += 'Gates                 = %s\n' % self.gates
                dump += 'Run Length (s)        = %s\n' % self.runLength
                dump += 'Run Mode              = %s\n' % self.runMode
                dump += 'Detector              = %s\n' % self.detector
                dump += 'FEBs                  = %s\n' % self.febs
                dump += 'LED Level             = %s\n' % self.ledLevel
                dump += 'LED Group             = %s\n' % self.ledGroup
                dump += 'Config File           = %s\n' % self.configFile
                dump += 'ET File               = %s\n' % self.etFile
		
		return dump
