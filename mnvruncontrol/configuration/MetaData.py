"""
  MetaData.py:
   Class & objects representing the "metadata" of the MINERvA
   data stream: run modes, LI modes, etc.
  
   Original author: A. Mislivec (mislivec@pas.rochester.edu)
                    Jan. 2010
   
   New object interface: J. Wolcott (jwolcott@fnal.gov)
                         Feb.-Apr. 2010
                    
   Address all complaints to the management.
"""

############################################################################
#
# Note: the actual metadata itself is towards the bottom of this file,
#       after the definition of the MetaData class that's used to store it.
#
############################################################################


# some module constants
DESCRIPTION = 0
HASH = 1
CODE = 2
ANY = 3


class MetaData:
	""" 
	Metadata type.  Used to replace the corresponding C++ enumerations in the old run control software.
	"""
	
	def __init__(self, data):
		self.data = []

		omittedHashes = 0
		omittedCodes = 0
		warned = False
		for entry in data:
			if len(entry) != 4:
				raise ValueError("Metadata entries must be lists or tuples of 4 entries: (identifier, description, hash, code).  Length you provided: " + str(len(entry)))
			identifier = entry[0]
			description = entry[1]
			hashitem = entry[2]
			code = entry[3]
			
			if identifier is None or description is None:
				raise ValueError("An identifier and a description must be provided for each metadata item.")
				
			if hashitem is None and code is None:
				raise ValueError("Either a code or a hash (or both) must be provided for each metadata item.")
			
			if hashitem == None:
				omittedHashes += 1
			if code == None:
				omittedCodes += 1
			
			if omittedHashes > 0 and omittedCodes > 0 and not warned:
				print "Warning: you omitted a code in one entry of this metadata and a hash in another.  Did you really mean to do that?..."
				warned = True
			
			datum = MetaDatum(self, identifier, description, hashitem, code)	
			self.data.append(datum)
			self.__dict__[identifier] = datum

	def __contains__(self, key):
		"""
		This function implements the 'in' operator.
		Allows you to easily check if a description/code/hash is in the metadata.
		"""
		for item in self.data:
			if item == key:
				return True
		
		return False
	
	def __getitem__(self, key):
		""" Returns the MetaDatum instance associated with the key you provide. """
		for item in self.data:
			if item == key:
				return item
				
		raise KeyError("Key '" + str(key) + "' is not found in any hash, code, or description.")
		
	def descriptions(self):
		"""
		Returns a list of the descriptions of the items in this particular MetaData.
		Handy if you need an ordered list of them (for a selection drop-down list, for example).
		"""
		return [item.description for item in self.data]

	def hashes(self):
		""" Same as descriptions() except returns hashes instead. """
		return [item.hash for item in self.data]

	def codes(self):
		""" Same as descriptions() except returns codes instead. """
		return [item.code for item in self.data]

	def get(self, key, returntype):
		"""
		Intelligently returns the hash/code/description
		corresponding to the key it's given.  Looks in
		the specified location (or all if given ANY).
		"""
		
		datum = self[key]

		getters = { DESCRIPTION: datum.description, HASH: datum.hash, CODE: datum.code }
		
		if returntype in getters:
			return getters[returntype]
		else:
			raise ValueError("Invalid return type requested for key '" + str(key) + "'")	


		# I've given up on the 'smart' type guessing as being useful.
		# it's left here in case somebody in the future thinks it's relevant. 
				
#		# now we know that the user didn't specify which return type.  do something intelligent.
#		if keylocation == self.descriptions:
#			if self.codes[keylocation.index(key)] is not None and self.hashes[keylocation.index(key)] is None:
#				return self.codes[keylocation.index(key)]
#			elif self.codes[keylocation.index(key)] is None and self.hashes[keylocation.index(key)] is not None:
#				return self.hashes[keylocation.index(key)]
#			else:
#				raise KeyError("Description you provided corresponds to metadata with both hashes and keys: must specify return type.")
#		else:
#			return self.descriptions[keylocation.index(key)]
			
	def code(self, key):
		""" Uses get() to get the code you want. """
		return self.get(key, CODE)

	def hash(self, key):
		""" Uses get() to get the hash you want. """
		return self.get(key, HASH)
	
	def description(self, key):
		""" Uses get() to get the description you want. """
		return self.get(key, DESCRIPTION)
	
	def item(self, index, returntype=None):
		"""
		Allows you to get information based on the position in the array.
		It's sort of the inverse of index() below.
		Useful if you have a list box or something similar where you provided
		one of the lists (descriptions, hashes, codes) as input and the indexing
		by position is maintained when you are figuring out what is selected.
		"""
		if index >= 0 and index < len(self.data):
			datum = self.data[index]
			getters = { DESCRIPTION: datum.description, HASH: datum.hash, CODE: datum.code }
			if returntype is None:
				return datum	
			elif returntype in getters:
				return getters[returntype]
			else:
				raise ValueError("Invalid returntype specified: '" + str(returntype) + "'...")
		else:
			raise ValueError("Invalid index specified: '" + str(index) + "'...")
			
	def index(self, key):
		"""
		Replaces the standard Python list function index():
		returns the index of the item in the list that corresponds
		to the key passed.  Raises ValueError if no such key exists.
		"""
		if not key in self:
			raise ValueError("Key '%s' not found in this metadata." % key)
		else:
			for i in range(len(self.data)):
				if key == self.data[i]:
					return i
				
class MetaDatum:
	""" Wraps a particular piece of MetaData information. """
	def __init__(self, parent, identifier, description, itemhash=None, code=None):
		if code is None and itemhash is None:
			raise ValueError("Either a code or a hash (or both) must be provided for each MetaDatum.")
		
		self.parent = parent
		self.identifier = identifier
		self.description = description
		self.code = code
		self.hash = itemhash
	
	def __eq__(self, other):
		# if other has ANY of the same attributes, we should judge equality based on that.
		if hasattr(other, "identifier") or hasattr(other, "description") or hasattr(other, "code") or hasattr(other, "hash"):
			try:
				return other.identifier == self.identifier and other.description == self.description and other.code == self.code and other.hash == self.hash
			except KeyError:
				return False

		# otherwise, it's probably a simple type.
		if other == self.identifier or other == self.description or other == self.code or other == self.hash:
			return True
		
		
		return False

	def __repr__(self):
		return self.description

	def index(self):
		return self.parent.index(self)
	
########################################################################################################
#
#   Now the actual metadata.
#		
# Format for constructor for MetaData objects:
# ( (IDENTIFIER1, description1, hash1, code1),
#   (IDENTIFIER2, description2, hash2, code2),
#   ...
#   (IDENTIFIERN, descriptionN, hashN, codeN) )
#
# If you want to omit either a hash or a code 
# (you need to have a description and at least one of hash or code every time)
# you should pass None in that position.  e.g.:
# ( (IDENTIFIER1, description1, hash1, code1),
#   (IDENTIFIER2, description2, None,  code2),
#   (IDENTIFIER3, description3, hash3, None ),
#   ...
#   (IDENTIFIERN, descriptionN, None,  codeN) )
#
# etc.
#
# Note that if you pass only a hash for one item and only a code for another in the same metadata object,
# the program will print out a warning because it assumes you probably didn't mean to do that.
#
########################################################################################################
		
HardwareConfigurations = MetaData(( ("NOFILE",     "Current state",          0, "[no HW file -- current configuration]"),
                                    ("BEAM",       "Beam settings",          1, "SCBeamFile"),
                                    ("LI",         "LI settings",            2, "SCLIFile"),
                                    ("LI_DISCRIM", "LI with discriminators", 3, "SCLIDiscriminatorsFile") ))
                                    
HardwareInitLevels	= MetaData(( ("NO_HW_INIT",   "No HW init",   0, None),
				             ("FULL_HW_INIT", "Full HW init", 1, None) ))
				             
LILevels			= MetaData(( ("ZERO_PE", "Zero PE", 0, None),
				             ("ONE_PE",  "One PE",  1, None),
				             ("MAX_PE",  "Max PE",  2, None) ))

LEDGroups			= MetaData(( ("ABCD",            "ABCD",  2**3,    "0"),
				             ("BCD",             "BCD",   2**4,    "a"),
				             ("ACD",             "ACD",   2**5,    "b"),
				             ("CD",              "CD",    2**6,    "c"),
				             ("ABD",             "ABD",   2**7,    "d"),
				             ("BD",              "BD",    2**8,    "e"),
				             ("AD",              "AD",    2**9,    "f"),
				             ("D",               "D",     2**10,   "g"),
				             ("NOT_IMPLEMENTED", "" ,     2**11,   "h"),
				             ("BC",              "BC",    2**12,   "i"),
				             ("AC",              "AC",    2**13,   "j"),
				             ("C",               "C",     2**14,   "k"),
				             ("AB",              "AB",    2**15,   "l"),
				             ("B",               "B",     2**16,   "m"),
				             ("A",               "A",     2**17,   "n") ))
				             
# These are technically supported by the LI box but are redundant
#				             ("",      2**18,   "o"),
#				             ("",      2**19,   "p"),
#				             ("BCD",   2**20,   "q"),
#				             ("ACD",   2**21,   "r"),
#				             ("CD",    2**22,   "s"),
#				             ("ABD",   2**23,   "t"),
#				             ("BD",    2**24,   "u") ))


DetectorTypes		= MetaData(( ("UNKNOWN",        "Unknown",            0,  "UN"),
				             ("PMT_TEST_STAND", "PMT test stand",     1,  "FT"),
				             ("TP",             "Tracking prototype", 2,  "TP"),
				             ("TEST_BEAM",      "Test beam",          4,  "TB"),
				             ("FROZEN",         "Frozen",             8,  "MN"),
				             ("UPSTREAM",       "Upstream",           16, "US"),
				             ("MINERVA",        "Full MINERvA",       32, "MV") ))

RunningModes		= MetaData(( ("ONE_SHOT",       "One shot",             0, "pdstl"),
				             ("NUMI",           "NuMI beam",            1, "numib"),
				             ("COSMICS",        "Cosmics",              2, "cosmc"),
				             ("LI",             "Light injection",      3, "linjc"),
				             ("MIXED_NUMI_PED", "Mixed beam/pedestal",  4, "numip"),
				             ("MIXED_NUMI_LI",  "Mixed beam/LI",        5, "numil"),
				             ("TB_BEAM_MUON",   "Test beam with muons", 6, "bmuon"),
				             ("TB_BEAM_ONLY",   "Test beam, beam only", 7, "bonly") ))

RunSeriesTypes          = MetaData(( ("BEAM",           "Beam",                0, "beam_series.db"),
				                 ("PEDESTAL",       "Pedestal",            1, "pedestal_series.db"),
				                 ("LI_MAX_PE",      "LI Max PE",           2, "li_max_pe_series.db"),
				                 ("LI_ONE_PE",      "LI One PE",           3, "li_one_pe_series.db"),
				                 ("MIXED_BEAM_PED", "Mixed Beam-Pedestal", 4, "mix_beam_ped_series.db"),
				                 ("MIXED_BEAM_LI",  "Mixed Beam-LI",       5, "mix_beam_li_series.db"),
				                 ("CUSTOM",         "Custom Series",       6, "custom_series.db") ))
				                 
TriggerTypes       = MetaData(( ("UNKNOWN",   "Unknown",          0,   None),
                                ("PEDESTAL",  "Pedestal",         1,   None),
                                ("LINJC",     "Light injection",  2,   None),
                                ("CHINJ",     "Charge injection", 4,   None),
                                ("COSMC",     "Cosmic",            8,  None),
                                ("NUMI",      "NuMI",             16,  None),
                                ("MUON",      "Test beam muon",   32,  None),
                                ("TBEAM",     "Test beam",        64,  None),
                                ("MC",        "Monte Carlo",      128, None)  ))
      	
# these are a couple of very useful translator functions
# (they convert LED group strings like "ABD" to the appropriate code, e.g., "d",
#  and back.)
def LIgroupCodeToLEDgroups(LEDgroupcode):
	LEDcodes = "0abcdefghijklmnopqrstuv"
	pos = LEDcodes.index(LEDgroupcode.lower())
#	print "Pos is: ", pos
	
	LIgroup = ""
	
	if pos / 8 > 0:
		LIgroup += "D"
	pos %= 8
	if pos / 4 > 0:
		LIgroup += "C"
	pos %= 4
	if pos / 2 > 0:
		LIgroup += "B"
	pos %= 2
	if pos == 1:
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


