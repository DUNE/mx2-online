import MetaData

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

class RunInfo(object):

	def __init__(   self,
                        gates      = 0,
                        runMode    = MetaData.RunningModes.descriptions[0],
                        ledLevel   = MetaData.LILevels.descriptions[0],
                        ledGroup   = MetaData.LEDGroups.descriptions[0]):

		self.gates      = gates
		self.runMode    = runMode
		self.ledLevel   = ledLevel
		self.ledGroup   = ledGroup

	def ToString(self):

                dump  = 'Gates                 = %s\n' % self.gates
                dump += 'Run Mode              = %s\n' % self.runMode
                dump += 'LED Level             = %s\n' % self.ledLevel
                dump += 'LED Group             = %s\n' % self.ledGroup
		
		return dump
