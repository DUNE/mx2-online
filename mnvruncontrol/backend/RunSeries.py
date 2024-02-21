"""
  RunSeries.py:
   Objects modelling a collection of runs of similar configuration
   (known elsewhere as a "run series").
  
   Original author: A. Mislivec (mislivec@pas.rochester.edu)
					Feb. 2010
					
   Address all complaints to the management.
"""
from mnvruncontrol.configuration import MetaData

class RunSeries:
	
	def __init__(self):
		self.Runs = []

	def FirstRun(self):
		try:
			return self.Runs[0]
		except:
			print('RunSeries: Could not retrieve first run.  Runs container may be empty')

	def GetRun(self, index):
		try:
			return self.Runs[index]
		except:
			print('RunSeries: Could not retrieve run.  Runs container may be empty')

	def SetRun(self, index, runInfo):
		if type(runInfo) != RunInfo:
			print('RunSeries: Second parameter must be an instance of the RunInfo class')
			return
		try:
			self.Runs[index] = runInfo
		except:
			print('RunSeries: Invalid index to Runs container')

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
						runMode    = MetaData.RunningModes.ONE_SHOT.hash,
						hwcfg      = MetaData.HardwareConfigurations.NOFILE.hash,
						ledLevel   = MetaData.LILevels.ZERO_PE.hash,
						ledGroup   = MetaData.LEDGroups.ABCD.hash ):

		self.gates      = gates
		self.runMode    = runMode
		self.hwConfig   = hwcfg
		self.ledLevel   = ledLevel
		self.ledGroup   = ledGroup

	def ToString(self):

		dump  = 'Run Mode               = %s\n' % MetaData.RunningModes.description(self.runMode)
		dump += 'Gates                  = %d\n' % self.gates
		dump += 'Hardware configuration = %s\n' % MetaData.HardwareConfigurations.description(self.hwConfig)
		dump += 'LED Level              = %s\n' % self.ledLevel if self.ledLevel not in MetaData.LILevels else MetaData.LILevels.description(self.ledLevel)
		dump += 'LED Group              = %s\n' % self.ledGroup if self.ledGroup not in MetaData.LEDGroups else MetaData.LEDGroups.description(self.ledGroup)
		
		return dump
