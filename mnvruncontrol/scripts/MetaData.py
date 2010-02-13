# Meta Data Module

# some module constants
DESCRIPTION = 0
HASH = 1
CODE = 2
ANY = 3


class MetaData:
	""" 
	Metadata type.  Used to replace the corresponding C++ enumerations.
	It has the cool feature of being able to guess what sort of thing
	(hash, code, description) you want back when you write 'MetaDataInstance[thing]'.
	"""
	
	# now methods.
	def __init__(self, data):
		self.descriptions = []
		self.hashes = []
		self.codes = []
		
		omittedHashes = 0
		omittedCodes = 0
		warned = False
		for entry in data:
			if len(entry) != 3:
				raise ValueError("Metadata entries must be lists or tuples of 3 entries: (description, hash, code).  Length you provided: " + str(len(entry)))
			description = entry[0]
			hashitem = entry[1]
			code = entry[2]
			
			if description == None:
				raise ValueError("A description must be provided for each metadata item.")
			else:
				self.descriptions.append(description)
				
			if hashitem == None and code == None:
				raise ValueError("Either a code or a hash (or both) must be provided for each metadata item.")
			
			if hashitem == None:
				omittedHashes += 1
			if code == None:
				omittedCodes += 1
			
			if omittedHashes > 0 and omittedCodes > 0 and not warned:
				print "Warning: you omitted a code in one entry of this metadata and a hash in another.  Did you really mean to do that?..."
				warned = True
			
			self.hashes.append(hashitem)
			self.codes.append(code)
		
		self.locations = (self.descriptions, self.hashes, self.codes)
	
	def __getitem__(self, key):
		""" 
		The 'operator[]' for this class.
		Intelligently returns the hash/code/description
		corresponding to the key it's given.
		"""
		returntype = ANY
		
		# if you provide more than one argument to the [] operator, it passes them all as a tuple
		if isinstance(key, tuple):
			returntype = key[1]
			key = key[0]
		
		keylocation = None

		for location in self.locations:
#			if location is None:
#				continue
			if key in location:
				keylocation = location
				
		if keylocation is None:
			raise KeyError("Key '" + str(key) + "' is not found in any hash, code, or description.")
		
		if returntype != ANY and returntype in (DESCRIPTION, HASH, CODE):
			return self.locations[returntype][keylocation.index(key)]
		elif returntype != ANY:
			raise ValueError("Invalid return type requested for key '" + str(key) + "'")	
		
		# now we know that the user didn't specify which return type.  do something intelligent.
		if keylocation == self.descriptions:
			if self.codes[keylocation.index(key)] is not None and self.hashes[keylocation.index(key)] is None:
				return self.codes[keylocation.index(key)]
			elif self.codes[keylocation.index(key)] is None and self.hashes[keylocation.index(key)] is not None:
				return self.hashes[keylocation.index(key)]
			else:
				raise KeyError("Description corresponds to metadata with both hashes and keys: must specify return type.")
		else:
			return self.descriptions[keylocation.index(key)]
	
	def __contains__(self, key):
		"""
		This function implements the 'in' operator.
		Allows you to easily check if a description/code/hash is in the metadata
		without having to know which one of the three areas to look in.
		"""
		
		for location in self.locations:
			if key in location:
				return True
		return False
			
	def index(self, key):
		"""
		Replaces the standard Python list function index():
		returns the index of the item in the list that corresponds
		to the key passed.  Raises ValueError if no such key exists.
		"""
		if not key in self:
			raise ValueError("Key not found in this metadata.")
		
		for location in self.locations:
			if key in location:
				return location.index(key)
		
		
		
# need variable "daqStop"

# Format for constructor for MetaData objects:
# ( (description1, hash1, code1),
#   (description2, hash2, code2),
#   ...
#   (descriptionN, hashN, codeN) )
#
# If you want to omit either a hash or a code 
# (you need to have a description and at least one of hash or code every time)
# you should pass None in that position.  e.g.:
# ( (description1, hash1, code1),
#   (description2, None,  code2),
#   (description3, hash3, None ),
#   ...
#   (descriptionN, None,  codeN) )
#
# etc.
#
# Note that if you pass only a hash for one item and only a code for another,
# the program will print out a warning because it assumes you probably didn't mean to do that.
		
SpecialGUI		= MetaData( tuple([("Deprecated", 0, None)]) )

HardwareInitLevels	= MetaData(( ("Full HW init", 0, None),
				             ("No HW init",   1, None) ))
				             
LILevels			= MetaData(( ("Zero PE", 0, None),
				             ("One PE",  1, None),
				             ("Max PE",  2, None) ))

LEDGroups			= MetaData(( ("All" ,   2**3,    "0"),
				             (" BCD",   2**4,    "a"),
				             ("A CD",   2**5,    "b"),
				             ("  CD",   2**6,    "c"),
				             ("AB D",   2**7,    "d"),
				             (" B D",   2**8,    "e"),
				             ("A  D",   2**9,    "f"),
				             ("   D",   2**10,   "g"),
				             (""    ,   2**11,   "h"),
				             (" BC ",   2**12,   "i"),
				             ("A C ",   2**13,   "j"),
				             ("  C ",   2**14,   "k"),
				             ("AB  ",   2**15,   "l"),
				             (" B  ",   2**16,   "m"),
				             ("A   ",   2**17,   "n"),
				             (""    ,   2**18,   "o"),
				             (""    ,   2**19,   "p"),
				             (" BCD",   2**20,   "q"),
				             ("A CD",   2**21,   "r"),
				             ("  CD",   2**22,   "s"),
				             ("AB D",   2**23,   "t"),
				             (" B D",   2**24,   "u") ))

# these are a couple of very useful translator functions
# (they convert LED group strings like "ABD" to the appropriate code, e.g., "d",
#  and back.)
def LIgroupCodeToLEDgroups(LEDgroupcode):
	LEDcodes = "0abcdefghijklmnopqrstuv"
	pos = LEDcodes.index(LEDgroupcode.lower())
	
	LIgroup = ""
	
	if LEDgroupcode / 8 == 0:
		LIgroup += "D"
	LEDgroupcode %= 8
	if LEDgroupcode / 4 == 0:
		LIgroup += "C"
	LEDgroupcode %= 4
	if LEDgroupcode / 2 == 0:
		LIgroup += "B"
	LEDgroupcode %= 2
	if LEDgroupcode == 1:
		LIgroup += "A"
		
	return LIgroup

def LEDgroupsToLIgroupCode(LEDgroup):
	LEDcodes = "0abcdefghijklmnopqrstuv"
	
	LEDgroup = LEDgroup.upper()
	
	hasA = 'A' in LEDgroup
	hasB = 'B' in LEDgroup
	hasC = 'C' in LEDgroup
	hasD = 'D' in LEDgroup
	
	inverseAddress = hasA + 2*hasB + 4*hasC + 8*hasD
	return LEDcodes[15 - inverseAddress]

LEDGroups.LIgroupCodeToLEDgroups = LIgroupCodeToLEDgroups
LEDGroups.LEDgroupsToLIgroupCode = LEDgroupsToLIgroupCode


DetectorTypes		= MetaData(( ("Unknown",            0,  "UN"),
				             ("PMT test stand",     1,  "FT"),
				             ("Tracking prototype", 2,  "TP"),
				             ("Test beam",          4,  "TB"),
				             ("Frozen",             8,  "MN"),
				             ("Upstream",           16, "US"),
				             ("Full MINERvA",       32, "MV") ))

RunningModes		= MetaData(( ("One shot",            0, "pdstl"),
				             ("NuMI beam",           1, "numib"),
				             ("Cosmics",             2, "cosmc"),
				             ("Light injection",     3, "linjc"),
				             ("Mixed beam/pedestal", 4, "numip"),
				             ("Mixed beam/LI",       5, "numil") ))

        	
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

