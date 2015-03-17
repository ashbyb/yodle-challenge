#!/usr/bin/env python
# -*- coding: utf_8 -*-

__created__ = "March 17 2015"
__author__ = "Brendan Ashby"
__author_email__ = "brendanevansashby@gmail.com"

"""
Notes and Thoughts:
The assignment is seemingly simple, but some corner cases make it a bit harder.

When you first approach the problem, it seems you just take each node, look at
its child nodes, and choose the larger one. This works for the example 
triangle given to us. See Example:

      1
     1 2
    3 1 2
   3 1 1 2

If you follow the simple "take the larger child process" then you would get
1 -> 2 -> 2 -> 2 = 7 but the answer is 1 -> 1 -> 3 -> 3 = 8.

Possible corner case:
Any given node can be of ANY size. We can not take the risk of ignoring any
node(s) due to some heuristic. For example:

      1
    10 1
   10 1 1
  10 1 1 1
 10 1 1 1 100

Here, you may want to take the left nodes, and get 41, but the answer is 104.

Another possible time-trade off technique would be to take the max() of each
row. Summing these would give the best possible answer for the triangle, but
if any of the nodes are not adjacent to the others then you are out of luck.
Also, if you had items with the same size, then max() will likely (version 
specific) choose the first item as max. This behavior is unpredictable 
for a dict.

One More Consideration:
There may be multiple answers to a triangle. Example:

    1
   1 1
  1 1 1
 1 1 1 1
1 1 1 1 1

"Write a program in a language of your choice to find the maximum total from 
top to bottom [...]". So, if there are multiple answers, then any of those is
the max() for the triangle. i.e. just take the first encountered.

Bottom-Line:
It seems you need an exhaustive approach to be sure of your answer. Try all
possible combinations. Keep running total as you traverse (and the nodes used)
and when you reach a node with no children, record the total. If there is
already a total stored, replace if you are larger. On a tie, don't replace.
When done traversing, current stored total is max.

Total Paths to Traverse:
paths = 2 ^ (rows - 1)

So for the 100 row 'triangle.txt':
There are 2 ^ 99 = 633,825,300,114,114,700,748,351,602,688 paths to check.

Ok, I think I am missing something here. Thinking...

Possible Solution:
Take each row and sort by size. Then we work in reverse. Go through each item
in the last row. Compare in turn to each item in next row up, go with the
first item that is adjacent to current node. Continue until at root.
Example:

    1
   1 3
  1 5 2
 1 6 3 4
7 3 4 5 2

Sort / Reverse:
75432
6341
521
31
1

Compute best path for each node in last row:
7 -> 1 -> 1 -> 1 -> 1 = 11
5 -> 4 -> 2 -> 3 -> 1 = 15
4 -> 6 -> 5 -> 3 -> 1 = 19 (answer)
3 -> 6 -> 5 -> 3 -> 1 = 18
2 -> 4 -> 2 -> 3 -> 1 = 12 

Why this seems to be a solution:
We are skipping some nodes that will never be reached as they are never part
of a complete path.

5 rows gives 16 paths to check exhaustively. Here, we only check 5.
If this holds, then for the 'triangle.txt' we will only compute 100 paths,
and not the huge number pasted above. 

Let me see if I can break my solution:

Odd number of rows...
      1
     2 2
    2 1 2
   2 1 1 2
  2 1 9 1 2
 2 2 1 1 2 2
2 1 1 1 1 1 2
      ^
      This node would find the right answer
      (We assume a tie always selects the left side.)

Try another:

Even number of rows...
         1
        1 1
       1 1 1
      1 1 1 1
     1 1 1 1 1 
    2 1 1 1 1 2
   2 2 1 9 1 2 2  <- assume the 9 is a huge number
  2 2 2 1 1 2 2 2
 2 2 2 2 1 2 2 2 2
1 1 1 1 1 1 1 1 1 1

There is not a middle row to catch the island number. Everything is shunted
away before seeing the large node. Argh!


"""

# "Constants"
VERSION = "0.1.0"

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
        ''' Read in juggler and circuit listing; construct helper classes '''
        with open(self.inputfile, "r") as f:
            for line in f:
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

        # Determine max participants per circuit
        # Told to assume there are no remainders here.
        max_jugglers = len(self.jugglers) / len(self.circuits)
        for circuit in self.circuits:
            circuit.max_jugglers = max_jugglers

    def _init_file_logging(self):
        ''' [Private] Initializes file-based logging if requested at 
        		instantiation '''
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
        ''' [Private] Initializes console-based logging if requested at 
        		instantiation '''
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
                        # If current participant is a weaker match to this
                        # circuit, reassign
                        if participant[1] < cost:
                            reassign.append(participant[0])
                            p.jugglers[idx] = (j, cost)
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
        description="""%(prog)s: A program to schedule Jugglers 
        	to Circuits for Yodle.""",
        epilog="""[Note] If \'--log\' is supplied without an arugment, then a
			default filename (jugglefest_log.txt) is used for logging. When 
			using the default filename, avoid argparse ambiguity by suppling 
			\'--log\' as the last argument (after \'inputfile\').""")
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
        const="jugglefest_log.txt",
        default=None,
        dest="logfile",
        metavar="aFilename",
        help="should I log my actions to a logfile? [default: no]")
    parser.add_argument(
        "inputfile",
        help="a path to a file of jugglers and circuits to be assigned.")
    args = parser.parse_args()

    # Time to Juggle Baby!
    aGloriousJuggleFestScheduler = JuggleFestOmnipotentScheduler(
        args.inputfile,
        verbose=args.verbose,
        logging_file=args.logfile)
