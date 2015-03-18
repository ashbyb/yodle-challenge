#!/usr/bin/env python
# -*- coding: utf_8 -*-

__created__ = "March 16 2015"
__author__ = "Brendan Ashby"
__author_email__ = "brendanevansashby@gmail.com"

"""
Notes and Thoughts:
Teams complete juggling circuits (multiple tricks).
  - H : Hand to Eye
  - E : Endurance
  - P : Pizzazz

Quality of match determined by dot product of circuit and juggler's H, E, and P.
  - Bigger is better!

A person can only be on one team.
Each team's circuit is distinct.

Match Jugglers to circuits so they will not want to switch.
  - Switching Criteria:
	 - Prefer the other circuit more (higher dot product)
	 - AND Be a better fit (higher dot product) than another juggler already on the circuit.
This seems to imply:
If the other circuit is a better fit, but all of the jugglers there are themselves a better fit
than the juggler thinking of switching, then he should not switch. Basically, he may be happier
to switch but it will hurt the quality of the performance if he does!

Assume equal distribution of jugglers to circuits.
  - Jugglers will always divide evenly into available circuits.
"""

# "Constants"
VERSION = "0.1.6"

# Python Standard Lib Imports
import os
import sys
import argparse
import logging

# Attach root logger
root_logger = logging.getLogger(__name__)
root_logger.setLevel(logging.DEBUG)

class JuggleFestException(Exception):
	''' Base exception for JuggleFest Module '''
	pass


class FileReadFailure(JuggleFestException):
	''' Failed to read/access the provided file '''
	pass


class FileParseFailure(JuggleFestException):
	''' Failed to parse the provided file '''
	pass


class JuggleFestEntityBase(object):

	''' A base class for abstract entities in the juggle fest '''

	def __init__(self, number, h, e, p):
		''' Initialize base varaibles common across entities '''
		self.num = number
		self.h = h
		self.e = e
		self.p = p

	def dot_product(self, remote):
		''' Calculate the dot product between two entities '''
		return (self.h * remote.h) + (self.e * remote.e) + (self.p * remote.p)


class Circuit(JuggleFestEntityBase):

	''' A juggling circuit class '''

	def __init__(self, number, h, e, p, max_jugglers=0):
		JuggleFestEntityBase.__init__(self, number, h, e, p)
		# Default to empty until we can reference the circuit objects
		self.jugglers = []
		# Prevent adding participants until we know how many we can take
		self.max_jugglers = max_jugglers

	def __repr__(self):
		return "<Circuit #%d: H:%d, E:%d, P:%d, Max:%d, Jugglers[%d]: %s>" % (
			self.num,
			self.h,
			self.e,
			self.p,
			self.max_jugglers,
			len(self.jugglers),
			', '.join(['J' + str(j[0].num) for j in self.jugglers]))


class Juggler(JuggleFestEntityBase):

	''' A juggler class '''

	def __init__(self, number, h, e, p, preferences):
		JuggleFestEntityBase.__init__(self, number, h, e, p)
		self.preferences = preferences

	def __repr__(self):
		return "<Juggler #%d: H:%d, E:%d, P:%d, Prefs[%d]: %s>" % (
			self.num,
			self.h,
			self.e,
			self.p,
			len(self.preferences),
			', '.join(['C' + str(pref.num) for pref in self.preferences]))


class JuggleFestOmnipotentScheduler(object):

	''' Implements Yodle's JuggleFest Challenge '''

	def __init__(self, input_file, verbose=False, logging_file=None, output_file=None):
		self.input_file = input_file
		self.verbose = verbose
		self.logging_file = logging_file
		self.output_file = output_file
		self.circuits = []
		self.jugglers = []

		# Setup Logging Environment
		if self.logging_file is not None:
			# Attach File Logger
			self._init_file_logging()
		if self.verbose:
			# Attach Console Logger
			self._init_console_logging()
		else:
			# Use a base logger
			error_formatter = logging.Formatter("%(levelname)s:%(message)s")
			error_handler = logging.StreamHandler()
			error_handler.setFormatter(error_formatter)
			error_handler.setLevel(logging.ERROR)
			root_logger.addHandler(error_handler)

		# Vocalize
		root_logger.debug("JuggleFest v%s by Brendan Ashby, has loaded." % VERSION)
		root_logger.debug("Logging to File: %s. Verbose Logging to Console: %s."
			% (self.logging_file is not None, self.verbose))

	def parse_input_file(self):
		''' Read in juggler and circuit listing; construct helper classes '''
		try:
			with open(self.input_file, "r") as f:
				for line in f:
					try:
						if len(line.strip()) == 0:  # Ignore blank lines
							continue
						data = line.split()
						if data[0] == 'C':
							self.circuits.append(
								Circuit(
									int(data[1][1:]),
									int(data[2][2:]),
									int(data[3][2:]),
									int(data[4][2:])))
							root_logger.debug("Created Circuit: %s" % 
								(self.circuits[-1]))
						elif data[0] == 'J':
							# Assumes that circuits all came first.
							# Which I was told I can assume.
							self.jugglers.append(
								Juggler(
									int(data[1][1:]), 
									int(data[2][2:]), 
									int(data[3][2:]), 
									int(data[4][2:]), 
									[self.circuits[int(p[1:])] for p in 
										data[5].split(',')]))
							root_logger.debug("Created Juggler: %s" % 
								(self.jugglers[-1]))
					except IndexError:
						root_logger.error("Error parsing line in inputfile: %s"
							% line)
						raise FileParseFailure()
		except IOError:
			root_logger.error("Failed to open the inputfile.")
			raise FileReadFailure()

		# Alert of parsing status
		root_logger.debug("%d circuits and %d jugglers parsed from inputfile."
			% (len(self.circuits), len(self.jugglers)))

		# Determine max participants per circuit
		# Told to assume there are no remainders here.
		if len(self.circuits) != 0:
			max_jugglers = len(self.jugglers) / len(self.circuits)
			root_logger.debug("Max jugglers per circuit set to %d." % 
				max_jugglers)
			for circuit in self.circuits:
				circuit.max_jugglers = max_jugglers

	def _init_file_logging(self):
		''' [Private] Initializes file-based logging if requested at 
				instantiation '''
		fmt = ("%(asctime)s:%(levelname)s:%(module)s.%(funcName)s@L"
			"%(lineno)d:%(message)s")
		full_formatter = logging.Formatter(fmt)
		file_handler = logging.FileHandler(self.logging_file)
		file_handler.setFormatter(full_formatter)
		root_logger.addHandler(file_handler)

	def _init_console_logging(self):
		''' [Private] Initializes console-based logging if requested at 
				instantiation '''
		fmt = "%(levelname)s:%(module)s.%(funcName)s@L%(lineno)d:%(message)s"
		clean_formatter = logging.Formatter(fmt)
		console_handler = logging.StreamHandler(stream=sys.stdout)
		console_handler.setFormatter(clean_formatter)
		console_handler.setLevel(logging.DEBUG)
		root_logger.addHandler(console_handler)

	def juggle(self, candidates=None):
		''' Core execution loop. Assigns jugglers to circuits. '''
		if candidates is None:
			candidates = self.jugglers
		
		# Juggle Loop
		reassign = []
		for j in candidates:
			for p in j.preferences:
				fit = j.dot_product(p)
				# If there is room, add as participant
				if len(p.jugglers) < p.max_jugglers:
					p.jugglers.append((j, fit))
					root_logger.debug("Assigned J%d to C%d with fit %d." % 
						(j.num, p.num, fit))
					break
				else:
					# If no room, see if better fit
					replaced = False
					for idx, participant in enumerate(p.jugglers):
						# If current participant is a weaker match to this
						# circuit, reassign
						if participant[1] < fit:
							reassign.append(participant[0])
							p.jugglers[idx] = (j, fit)
							replaced = True
							root_logger.debug(("Assigned J%d to C%d with " 
								"fit %d. Displaced J%d.") % 
								(j.num, p.num, fit, participant[0].num))
							break
					if replaced:
						break

		# Recurse, assigning displaced jugglers
		if reassign:
			root_logger.debug("I have %d displaced juggler(s) to reassign." % 
				len(reassign))
			self.juggle(candidates=reassign)

	def output_answer(self):
		''' outputs answer to JuggleFest challenge '''
		pass



if __name__ == '__main__':

	def usage_override(name=None):
		return """%(prog)s [-h] [-v] [-l [logfile]] inputfile outputfile\n
           _                   _      ______        _
          | |                 | |    |  ____|      | |
          | |_   _  __ _  __ _| | ___| |__ ___  ___| |_
      _   | | | | |/ _` |/ _` | |/ _ \  __/ _ \/ __| __|
     | |__| | |_| | (_| | (_| | |  __/ | |  __/\__ \ |_
      \____/ \__,_|\__, |\__, |_|\___|_|  \___||___/\__|
                    __/ | __/ |  v{version} by Brendan Ashby
                   |___/ |___/
		""".format(version=VERSION)

	parser = argparse.ArgumentParser(
		usage=usage_override(),
		prog=os.path.basename(__file__),
		description="""%(prog)s: A program to schedule Jugglers 
			to Circuits for Yodle.""",
		epilog="""[Note] If \'--log\' is supplied without an arugment, then a
			default filename (jugglefest.log) is used for logging. When 
			using the default filename, avoid argparse ambiguity by suppling 
			\'--log\' as the last argument (after \'outputfile\').""")
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		default=False,
		dest="verbose",
		help="should I log my actions to console? [default: no]")
	parser.add_argument(
		"-l",
		"--log",
		nargs="?",
		const="jugglefest.log",
		default=None,
		dest="logfile",
		metavar="logfile",
		help="should I log my actions to a logfile? [default: no]")
	parser.add_argument(
		"inputfile",
		help="a path to a file of jugglers and circuits to be assigned.")
	parser.add_argument(
		"outputfile",
		help=("a filename to write the output (the computed optimal circuits)"
			" of '%(prog)s' to."))

	# Parse Arguments
	args = parser.parse_args()

	# Time to Juggle Baby!
	aGloriousJuggleFestScheduler = JuggleFestOmnipotentScheduler(
		args.inputfile,
		verbose=args.verbose,
		logging_file=args.logfile,
		output_file=args.outputfile)
	
	# Parse inputfile
	try:
		aGloriousJuggleFestScheduler.parse_input_file()
	except JuggleFestException:
		root_logger.error(" A problem was encountered while processing inputfile.")
	else:
		# Start juggling
		aGloriousJuggleFestScheduler.juggle()
		# Output answer
		aGloriousJuggleFestScheduler.output_answer()
