from mnvruncontrol.configuration import MetaData

class RunSeries:
	
        def __init__(self):
		self.Runs = list()

	def FirstRun(self):
	        try:
			return self.Runs[0]
        	except:
			print 'RunSeries: Could not retrieve first run.  Runs container may be empty'

	def GetRun(self, index):
                try:
                        return self.Runs[index]
                except:
                        print 'RunSeries: Could not retrieve run.  Runs container may be empty'

	def SetRun(self, index, runInfo):
		if type(runInfo) != RunInfo:
			print 'RunSeries: Second parameter must be an instance of the RunInfo class'
			return
		try:
			self.Runs[index] = runInfo
		except:
			print 'RunSeries: Invalid index to Runs container'

	def AppendRun(self,runInfo):     
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
                        runMode    = MetaData.RunningModes.item(0,MetaData.HASH),
                        ledLevel   = MetaData.LILevels.item(0,MetaData.HASH),
                        ledGroup   = MetaData.LEDGroups.item(0,MetaData.HASH)):

		self.gates      = gates
		self.runMode    = runMode
		self.ledLevel   = ledLevel
		self.ledGroup   = ledGroup

	def ToString(self):

                dump  = 'Run Mode              = %s\n' % MetaData.RunningModes[self.runMode,MetaData.DESCRIPTION]
		dump += 'Gates                 = %s\n' % self.gates
                dump += 'LED Level             = %s\n' % MetaData.LILevels[self.ledLevel,MetaData.DESCRIPTION]
                dump += 'LED Group             = %s\n' % MetaData.LEDGroups[self.ledGroup,MetaData.DESCRIPTION]
		
		return dump
