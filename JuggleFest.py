#!/usr/bin/python
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
VERSION = "0.1.3"

# Python Standard Lib Imports
import os
import sys
import argparse
import logging

# Attach root logger
root_logger = logging.getLogger(__name__)
root_logger.setLevel(logging.DEBUG)
error_formatter = logging.Formatter("%(levelname)s:%(message)s")
error_handler = logging.StreamHandler()
error_handler.setFormatter(error_formatter)
root_logger.addHandler(error_handler)


class JuggleFestEntityBase(object):
	''' A base class for entities in the juggle fest '''
	def __init__(self, number, h, e, p):
		''' initialize base varaibles common across entities '''
		self.num = number
		self.h = h
		self.e = e
		self.p = p

	def dot_product(self, remote):
		''' calculate the dot product between two entities '''
		return (self.h * remote.h) + (self.e * remote.e) + (self.p * remote.p)


class Circuit(JuggleFestEntityBase):
	''' A juggling circuit class '''
	def __init__(self, number, h, e, p, max_jugglers=0):
		JuggleFestEntityBase.__init__(self, number, h, e, p)
		# Default to empty until we can reference the circuit objects (default: []).
		self.jugglers = [] 
		# Prevent adding participants until we know how many we can take (default: 0).
		self.max_jugglers = max_jugglers 

	def __repr__(self):
		return "<Circuit #%d: H:%d, E:%d, P:%d, Max:%d, Jugglers[%d]: %s>" % (
					self.num, 
					self.h, 
					self.e, 
					self.p, 
					self.max_jugglers, 
					len(self.jugglers), 
					', '.join(['J'+str(j[0].num) for j in self.jugglers]))


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
					', '.join(['C'+str(pref.num) for pref in self.preferences]))


class JuggleFestOmnipotentScheduler(object):
	''' Implements Yodle's JuggleFest Challenge '''
	def __init__(self, inputfile, verbose=False, logging_file=None):
		self.inputfile = inputfile
		self.verbose = verbose
		self.logging_file = logging_file
		self.circuits = []
		self.jugglers = []

		# Setup Logging Environment
		if self.logging_file is not None:
			# Attach File Logger
			self._init_file_logging()
		if self.verbose:
		 	# Attach Console Logger
		 	self._init_console_logging()

		# Parse inputfile
		try:
			self.parse_input_file()
		except EnvironmentError:
			root_logger.critical(" Failed to parse inputfile.")
		else:
			# Start juggling
			self.juggle(self.jugglers)
			self.debug()

	def parse_input_file(self):
		''' reads in juggler and circuit input file for analysis, constructs helper classes '''
		with open(self.inputfile, "r") as f:
			for line in f:
				if len(line.strip()) == 0: # Ignore blank lines
					continue
				data = line.split()
				if data[0] == 'C':
					self.circuits.append(Circuit(int(data[1][1:]), int(data[2][2:]), 
										int(data[3][2:]), int(data[4][2:])))
				elif data[0] == 'J':
					# Assumes that circuits all came first. Which I was told I can assume.
					self.jugglers.append(Juggler(int(data[1][1:]), 
										int(data[2][2:]), 
										int(data[3][2:]), 
										int(data[4][2:]), 
										[self.circuits[int(p[1:])] for p in data[5].split(',')]))
		
		# Determine max participants per circuit
		max_jugglers = len(self.jugglers) / len(self.circuits) # Told to assume: No remainders here.
		for circuit in self.circuits:
			circuit.max_jugglers = max_jugglers

	def _init_file_logging(self):
		''' [Private] Initializes file-based logging if requested at instantiation '''
		full_formatter = logging.Formatter("""%(asctime)s:
											%(levelname)s:
											%(module)s.
											%(funcName)s@L
											%(lineno)d:
											%(message)s""")
		file_handler = logging.FileHandler(self.logging_file)
		file_handler.setFormatter(full_formatter)
		root_logger.addHandler(file_handler)
		
	def _init_console_logging(self):
		''' [Private] Initializes console-based logging if requested at instantiation '''
		clean_formatter = logging.Formatter("""%(levelname)s:
											%(module)s.
											%(funcName)s@L
											%(lineno)d:
											%(message)s""")
		console_handler = logging.StreamHandler(stream=sys.stdout)
		console_handler.setFormatter(clean_formatter)
		root_logger.addHandler(console_handler)

	def juggle(self, candidates):
		''' Core execution loop. Assigns jugglers to circuits. '''
		reassign = []
		for j in candidates:
			for p in j.preferences:
				# If there is room, add as participant
				if len(p.jugglers) < p.max_jugglers:
					p.jugglers.append((j, j.dot_product(p)))
					break
				else:
					# If no room, see if better fit
					cost = j.dot_product(p)
					replaced = False
					for idx, participant in enumerate(p.jugglers):
						# If current participant is a weaker match to this circuit, reassign
						if participant[1] < cost:
							reassign.append(participant[0])
							p.jugglers[idx] = (j,cost)
							replaced = True
							break
					if replaced:
						break

		# Recurse, assigning displaced jugglers
		if reassign:
			self.juggle(reassign)

	def debug(self):
		''' quick debugging '''
		for j in self.jugglers:
			print j
		for c in self.circuits:
			print c


if __name__ == '__main__':

	def usage_override(name=None):
		return """%(prog)s [-h] [--verbose] [--log [aFilename]] inputfile\n
      _                   _      ______        _   
     | |                 | |    |  ____|      | |  
     | |_   _  __ _  __ _| | ___| |__ ___  ___| |_ 
 _   | | | | |/ _` |/ _` | |/ _ \  __/ _ \/ __| __|
| |__| | |_| | (_| | (_| | |  __/ | |  __/\__ \ |_ 
 \____/ \__,_|\__, |\__, |_|\___|_|  \___||___/\__|
               __/ | __/ |  v{version}                         
              |___/ |___/                          
		""".format(version=VERSION)

	parser = argparse.ArgumentParser(
				usage=usage_override(), 
				prog=os.path.basename(__file__), 
				description="%(prog)s: A program to schedule Jugglers to Circuits for Yodle.", 
				epilog="""[Note] If \'--log\' is supplied without an arugment, then a 
					default filename (jugglefest_log.txt) is used for logging. When using the 
					default filename, avoid argparse ambiguity by suppling \'--log\' as the last 
					argument (after \'inputfile\').""")
	parser.add_argument("-v", "--verbose", 
				action="store_true", 
				default=False, 
				dest="verbose", 
				help="should I log my actions to console? [default: no]")
	parser.add_argument("-l", "--log", 
				nargs="?", 
				const="jugglefest_log.txt", 
				default=None, 
				dest="logfile", 
				metavar="aFilename", 
				help="should I log my actions to a logfile? [default: no]")
	parser.add_argument("inputfile", 
				help="a path to a file of jugglers and circuits to be assigned.")
	args = parser.parse_args()

	# Time to Juggle Baby!
	aGloriousJuggleFestScheduler = JuggleFestOmnipotentScheduler(
										args.inputfile, 
										verbose=args.verbose, 
										logging_file=args.logfile)
		