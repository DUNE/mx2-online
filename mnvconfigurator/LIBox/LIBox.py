#!/usr/bin/python
"""
MINERvA light injection system manager.
Adapted from the original (C#) script by J. Meyer
  by J. Wolcott (jwolcott@fnal.gov), 02/2010

Address all complaints to the management.
"""

import serial
import time
import re
import sys

# for testing purposes.
LIBOX_WAIT_FOR_RESPONSE = True

# configuration for the serial port.
# these probably will never need to be changed.
LIBOX_SERIAL_PORT_DEVICE         = "/dev/ttyS0"
LIBOX_SERIAL_PORT_BAUD           = 9600
LIBOX_SERIAL_PORT_PARITY         = serial.PARITY_NONE
LIBOX_SERIAL_PORT_SW_FLOWCONTROL = False
LIBOX_SERIAL_PORT_HW_FLOWCONTROL = True
LIBOX_SERIAL_PORT_DATA_BITS      = serial.EIGHTBITS
LIBOX_SERIAL_PORT_STOP_BITS      = serial.STOPBITS_ONE

class LIBox:
	""" Control class for the LI box. """
	def __init__(self, pulse_height = 12.07, pulse_width = 7, LED_groups = "ABCD", trigger_internal = False, trigger_rate = None):
		self.pulse_height     = pulse_height
		self.pulse_width      = pulse_width
		self.LED_groups       = LED_groups
		self.trigger_internal = trigger_internal
		self.trigger_rate     = trigger_rate
		
		self.command_stack = []
		
		self.initialized = False
		
		self.command_log = []
		
		# the following are the commands that are ok (in regular expression form).
		# this is probably not strictly necessary since 
		# I can't imagine a user ever setting the commands by hand,
		# but it's usually better to be safe anyway.
		self.permitted_commands = ( "_X" , "aA", "aE[0a-vA-V]", "aB[0-3]", "aC[\da-fA-F]_[\da-fA-F]", "aO", "aD[0-7]", "aQ", "aK", "aH[\da-fA-F]{2}", "aI[\da-fA-F]{2}" )

		# this will throw an exception if the port's not properly configured.
		# that's ok -- it needs to be fixed in that case!
		# (the 'timeout' parameter is how long the process will wait for a read, in seconds.)
		self.port = serial.Serial( port     = LIBOX_SERIAL_PORT_DEVICE,
		                           baudrate = LIBOX_SERIAL_PORT_BAUD,
		                           bytesize = LIBOX_SERIAL_PORT_DATA_BITS,
		                           parity   = LIBOX_SERIAL_PORT_PARITY,
		                           stopbits = LIBOX_SERIAL_PORT_STOP_BITS,
		                           xonxoff  = LIBOX_SERIAL_PORT_SW_FLOWCONTROL,
		                           rtscts   = LIBOX_SERIAL_PORT_HW_FLOWCONTROL,
		                           timeout  = 0.1 )

		self.port.writeTimeout = 0.1
		
#		try:
#			self.port.read(1)
#		except serial.SerialException:
#			raise LIBoxException("The LI box does not seem to be connected.  Check the settings and the cable connection.")
		
	def reset(self):
		self.command_stack = ["_X"]
		self.communicate()
	
	def initialize(self):
		self.command_stack = ["_X", "aA"]
		self.communicate()

		self.initialized = True
	
	def communicate(self):
		""" Sends the commands in the command stack to the LI box. """
		self.check_commands()
		
		for command in self.command_stack:
			self.command_log.append(command)		# store this in a log for later review.
			try:
#				print "Writing command '" + command + "'..."
				self.port.write(command + "\n")
			except serial.SerialTimeoutException:
				raise LIBoxException("The LI box isn't responding.  Are you sure you have the correct port setting and that the LI box is on?")

			if LIBOX_WAIT_FOR_RESPONSE:
				char = self.port.read(1)
			
				if char != "K":
					raise LIBoxException("The LI box didn't respond affirmatively to the command: '" + command + "'.")
			
			time.sleep(0.01)
		
		self.command_stack = []
			
	def check_commands(self):
		for command in self.command_stack:
			command_ok = False
			for permitted_command in self.permitted_commands:
				if re.match("^" + permitted_command + "$", command):
					command_ok = True
					break
			
			if command_ok == False:
				raise LIBoxException("Command '" + command + "' is invalid and cannot be sent to the LI box.")
				
	def write_configuration(self):
		""" Builds a stack of commands based on this object's parameters, then calls communicate(). """
		
		self.command_stack = []
		
		if not self.initialized:
			self.initialize()
		
		# first, LED group.
		self.LED_groups = self.LED_groups.upper()
		self.LED_groups = self.LED_groups.replace(" ", "")
		
		if not re.match("[a-dA-D]{1,4}", self.LED_groups):
			raise LIBoxException("LED groups to use must be some combination of 'A', 'B', 'C', 'D'.")

		# the following wizardry is brought to you by the magic that powers the LI box.
		# trust me -- it works.
		inverseAddress = 0
		pos = 0
		LEDcodes = "0abcdefghijklmnopqrstuv";
		for char in "ABCD":
			inverseAddress += self.LED_groups.count(char) * 2 ** (pos)
			pos += 1
		LEDcode = LEDcodes[15 - inverseAddress];

		self.command_stack.append("aE" + LEDcode)
		
		
		# pulse height (in volts) next.
		# allowed values are 4.05-12.07.
		if self.pulse_height < 4.05 or self.pulse_height > 12.07:
			raise LIBoxException("LI pulse height must be between 4.05 and 12.07 volts (inclusive).")
		
		highBit = int( (self.pulse_height - 4.0429) / 2.01 )

		lowBit  = int( (self.pulse_height - highBit * 2.01 - 4.0429) / .00783 )
		lowBit1 = lowBit / 16;		# note: INTEGER division.
		lowBit2 = lowBit % 16;

		highBit = "%x" % highBit
		self.command_stack.append("aB" + highBit)

		lowBit1 = "%x" % lowBit1
		lowBit2 = "%x" % lowBit2
		self.command_stack.append("aC" + lowBit1 + "_" + lowBit2)
		
		# must always follow "aB" and "aC" with "aO"...
		self.command_stack.append("aO")
		
		# pulse width: 0-7.  (roughly 20-35 ns)
		if self.pulse_width < 0 or self.pulse_width > 7:
			raise LIBoxException("LI pulse width must be in the range 0-7 (inclusive).")
		self.command_stack.append("aD" + str(self.pulse_width))
		
		# now the triggering.
		if (self.trigger_internal):
			if self.trigger_rate == None:
				raise LIBoxException("If you intend to use internal triggering, you must manually set the trigger rate.")
				
			self.command_stack.append("aK")

			self.trigger_rate = int(self.trigger_rate, 16)		# no decimals.  need it in hexadecimal, too.
			if self.trigger_rate < 0 or self.trigger_rate > 0xffff:
				raise LIBoxException("Internal trigger rate must be between 0 and FFFF (hex).")
			
			trigger_rate = self.trigger_rate
			
			highNum1 = trigger_rate / 0x1000
			highNum2 = (trigger_rate - highNum1 * 0x1000) / 0x100
			trigger_rate -= highNum1 * 0x1000 + highNum2 * 0x100
			
			highNum1 = "%x" % highNum1
			highNum2 = "%x" % highNum2
			self.command_stack.append("aH" + highNum1 + highNum2)
			
			lowNum1 = trigger_rate / 0x10
			lowNum2 = trigger_rate - lowNum1 * 0x10
			lowNum1 = "%x" % lowNum1
			lowNum2 = "%x" % lowNum2
			self.command_stack.append("aI" + lowNum1 + lowNum2)
		else:
			self.command_stack.append("aQ")
		
		self.communicate()
			

class LIBoxException(Exception):
	pass

#####################################################################################

# if this is the main module, we'll do some command-line processing
if __name__ == "__main__":
	import optparse
	
	parser = optparse.OptionParser(usage="usage: %prog [options] command\n  where 'command' is 'initialize', 'reset', or 'configure'")
	parser.add_option("-p", "--pulse-height", dest="pulse_height", help="Set the pulse height (volts).  Valid values: 4.05-12.07.  Default: %default.", default=12.07, type="float")
	parser.add_option("-w", "--pulse-width", dest="pulse_width", help="Set the pulse width.  Valid values: 0-7 (roughly corresponding to 20-35 ns).  Default: %default.", default=7, type="int")
	parser.add_option("-l", "--led-groups", dest="led_groups", help="Set the LED groups that will fire.  Valid values: some combination of 'A', 'B', 'C', 'D'.  Default: %default.", default="ABCD")
	parser.add_option("-i", "--trigger-internal", dest="trigger_internal", action="store_true", help="Use internal triggering for the LI pulses instead of the usual external trigger from the pulser.  (You should also set -r if you use this option.)  Default: %default", default=False)
	parser.add_option("-r", "--trigger-rate", dest="trigger_rate", help="Set the triggering rate for internal triggering.  (You should only use this option in conjunction with -i.)  Valid values: 0-FFFF (hex).  Default: None.", default=None)
	
	(options, commands) = parser.parse_args()
	
	if len(commands) != 1 or not(commands[0].lower() in ("initialize", "reset", "configure")):
		parser.print_help()
		sys.exit(0)

	command = commands[0].lower()
	
#	print options
	
	if command == "initialize":
		box = LIBox()
		box.initialize()
	elif command == "reset":
		box = LIBox()
		box.reset()
	else:
		box = LIBox(options.pulse_height, options.pulse_width, options.led_groups, options.trigger_internal, options.trigger_rate)
		box.write_configuration()
		
	sys.exit(0)
