#!/usr/bin/env python
# -*- coding: utf_8 -*-

__created__ = "March 17 2015"
__author__ = "Brendan Ashby"
__author_email__ = "brendanevansashby@gmail.com"

"""
::::::::::::::::::::::
: Notes and Thoughts :
::::::::::::::::::::::
>What follows is my stream of conciousness when figuring out this problem.
>I wrote this after I did the JuggleFest problem, so some of the logging
>boilerplate code will be the same.

~~

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
possible combinations. Keep a running total as you traverse (and the nodes 
used) and when you reach a node with no children, record the total. If there
is already a total stored, replace if you are larger. On a tie, don't replace.
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

We are also computing less paths.
5 rows gives 16 paths to check exhaustively. Here, we only check 5.
If this holds, then for the 'triangle.txt' we will only compute 100 paths,
and not the huge number pasted above.

Let me see if I can break my solution:

Using odd number of rows...
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

Try another example:

Using even number of rows...
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
away before seeing the large node. Argh! Didn't work...

More Thoughts:
   
   1              1
  2 3         2       3
 4 5 6  ->  4   5   5   6
7 8 9 10   7 8 8 9 8 9 9 10

Converting to a BST, would create ~633.8 octillion items in the last row
when processing the 'triangle.txt' test file. Nope.

Re-Think It:
I know the issue is when traversing the triangle, whether it is from the
bottom or the top, if you can not see farther than the node in front of you
then you won't be able to properly consider the entire context of the triangle
and you will miss things like the "islands" I created in the above test
triangles. I need a way to present the context of the tree, but within the
local nodes being considered.

Got it. Did a little brainstorming (full disclosure: got some input from
an old college roommate) and realized I should encode the sum of the weights 
from a given node to the bottom leaf node. Then, as you traverse you can
make your decisions based on the entire structure of the triangle.

Example:

	 1
	2 6      (start at 2nd to last row. Take the bigger of the child nodes
   3 8 7      and add its value to the current node. Set the current node
  3 8 4 5     to that value. move up to next row and repeat. Ignore the root.)
 8 7 3 7 3
2 3 3 4 6 7

Becomes....

		  1
	   28  32    
	  21 26 23      
	14 18 15 16   
   11 10 7 11 10
  2  3  3 4  6  7

Now, traverse the tree from the top, choosing the larger node. On a tie, go
left (or right. It doesn't matter. Just be consistent.). Each choice is now
considering the rest of the triangle below that node BECAUSE it's value is 
comprised of the values of all of the child nodes below it that will be 
selected. I love it!

So the answer is:
1 -> 32 -> 26 -> 18 -> 10 -> 3

However, to calculate to "max()" of the triangle. You need to remember these
nodes' original values! So the total would be:

1 -> 6 -> 8 -> 8 -> 7 -> 3 = 33

I also tested it on my earlier test triangles to see if it works there. It
correctly catches the "islands".

Time to code it.
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


# When brushing up on python custom comparison methods I found a great mixin.
# Attribution: Link to Source: http://bit.ly/1Bysb8f
class ComparableMixin(object):
	
	''' A Mixin for adding rich comparison methods to a comparable object '''

	def _compare(self, other, method):
		try:
			return method(self._cmpkey(), other._cmpkey())
		except (AttributeError, TypeError):
			# _cmpkey not implemented, or return different type,
			# so I can't compare with "other".
			return NotImplemented

	def __lt__(self, other):
		return self._compare(other, lambda s,o: s < o)

	def __le__(self, other):
		return self._compare(other, lambda s,o: s <= o)

	def __eq__(self, other):
	   return self._compare(other, lambda s,o: s == o)

	def __ge__(self, other):
		return self._compare(other, lambda s,o: s >= o)

	def __gt__(self, other):
		return self._compare(other, lambda s,o: s > o)

	def __ne__(self, other):
		return self._compare(other, lambda s,o: s != o)
		

class TriangleNode(ComparableMixin):

	''' A class representing a single node in a triangle data structure '''

	def __init__(self, value, parent=None, lchild=None, rchild=None):
		self.value = value
		self.parent = None
		self.lchild = None
		self.rchild = None

	def _cmpkey(self):
		''' [Private] Used in rich comparion operations '''
		return self.value

	def __repr__(self):
		return "<TriangleNode val:%d: Parent:%s, LChild:%s, RChild:%s>" % (
			self.value,
			str(self.parent) if self.parent is None else 'Node:' + 
				str(self.parent.value),
			str(self.lchild) if self.lchild is None else 'Node:' + 
				str(self.lchild.value),
			str(self.rchild) if self.rchild is None else 'Node:' + 
				str(self.rchild.value))


class TriangleSolver(object):

	''' A class that parses and solves max paths in triangle data structs '''

	def __init__(self, inputfile, verbose=False, logging_file=None):
		self.inputfile = inputfile
		self.verbose = verbose
		self.logging_file = logging_file
		self._nodes = []

		# Setup Logging Environment
		if self.logging_file is not None:
			# Attach File Logger
			self._init_file_logging()
		if self.verbose:
			# Attach Console Logger
			self._init_console_logging()

	def parse_input_file(self):
		''' Reads in triangle structure data and construct helper classes '''
		rows = []
		with open(self.inputfile, "r") as f:
			for line in f:
				if len(line.strip()) == 0:  # Ignore blank lines
					continue
				row = line.split()
				rows.append(row)
				for node in row:
					self._nodes.append(TriangleNode(int(node)))

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

	def debug(self):
		''' quick debugging '''
		for j in self.jugglers:
			print j
		for c in self.circuits:
			print c


if __name__ == '__main__':

	def usage_override(name=None):
		return """%(prog)s [-h] [--verbose] [--log [aFilename]] inputfile\n
 _______   _                   _       _____       _                
|__   __| (_)                 | |     / ____|     | |               
   | |_ __ _  __ _ _ __   __ _| | ___| (___   ___ | |_   _____ _ __ 
   | | '__| |/ _` | '_ \ / _` | |/ _ \\\\___ \ / _ \| \ \ / / _ \ '__|
   | | |  | | (_| | | | | (_| | |  __/____) | (_) | |\ V /  __/ |   
   |_|_|  |_|\__,_|_| |_|\__, |_|\___|_____/ \___/|_| \_/ \___|_|   
                          __/ |   v{version} by Brendan Ashby                         
                         |___/                                      
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
