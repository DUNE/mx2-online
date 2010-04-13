"""
  SortTools.py:
   A few sorting methods used by the run control.
   
   Extracted here to eliminate some clutter in the main file.
  
   Original author: J. Wolcott (jwolcott@fnal.gov)
                    Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

import re
import time

from mnvruncontrol.configuration import Defaults
from mnvruncontrol.configuration import MetaData

def parseLogfileName(filename):
	matches = re.match(Defaults.LOGFILE_NAME_PATTERN, filename)
	
	if matches is None:
		return None
	
	fileinfo = {}
	fileinfo["run"]    = matches.group("run").lstrip('0')
	fileinfo["subrun"] = matches.group("subrun").lstrip('0')
	fileinfo["date"]   = matches.group("month") + "/" + matches.group("day") + "/20" + matches.group("year")
	fileinfo["time"]   = matches.group("hour") + ":" + matches.group("minute")

	if matches.group("type") in MetaData.RunningModes:
		fileinfo["type"] = MetaData.RunningModes.description(matches.group("type"))
	else:
		return None

	if matches.group("detector") in MetaData.DetectorTypes:
		fileinfo["detector"] = MetaData.DetectorTypes.description(matches.group("detector"))
	else:
		return None
	
	fileinfo["controller"] = matches.group("controller")

	return fileinfo

def SortLogData(fileinfo1, fileinfo2):
	f1 = int(fileinfo1["run"])*10000 + int(fileinfo1["subrun"])		# run * 10000 + subrun
	f2 = int(fileinfo2["run"])*10000 + int(fileinfo2["subrun"])
	
	if f1 == f2:
		t1 = time.strptime("2010 " + fileinfo1["time"], "%Y %H:%M")		# need to include a year because otherwise the 'mktime' below overflows.  which year it is is irrelevant (all we need is a difference anyway).
		t2 = time.strptime("2010 " + fileinfo2["time"], "%Y %H:%M")
		
		timediff = time.mktime(t1) - time.mktime(t2)
		if timediff == 0:		# this should never happen.
			return 1 if fileinfo1["controller"] > fileinfo2["controller"] else -1
		else:
			return 1 if timediff > 0 else -1
	else:
		return 1 if f1 > f2 else -1
		
def SortLogFiles(file1, file2):
	pattern = re.compile(Defaults.LOGFILE_NAME_PATTERN)
	
	matchdata1 = pattern.match(file1)
	matchdata2 = pattern.match(file2)
	
	if not matchdata1 or not matchdata2:		# maybe the files don't match the pattern.
		return 0
	
	if matchdata1.group("run") == matchdata2.group("run"):
		if matchdata1.group("subrun") == matchdata2.group("subrun"):		# shouldn't ever have same run/subrun combination
			if matchdata1.group("hour") == matchdata2.group("hour"):
				if matchdata1.group("minute") == matchdata2.group("minute"):
					if matchdata1.group("controller") == matchdata2.group("controller"):
						print "Run/subrun pair equal! : (", matchdata1.group("run"), ",", matchdata1.group("subrun"), ") == (", matchdata2.group("run"), ",", matchdata2.group("subrun"), ")!"
						print "Files: '" + file1 + "', '" + file2 + "'"
						print "Log sorting problem."
						sys.exit(1)
					else:
						return 1 if matchdata1.group("controller") > matchdata2.group("controller") else -1
				else:
					return 1 if matchdata1.group("minute") > matchdata2.group("minute") else -1
			else:
				return 1 if matchdata1.group("hour") > matchdata2.group("hour") else -1
		else:
			return 1 if matchdata1.group("subrun") > matchdata2.group("subrun") else -1
	else:
		return 1 if matchdata1.group("run") > matchdata2.group("run") else -1

