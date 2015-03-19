import argparse
import random

# Seed
random.seed()

parser = argparse.ArgumentParser(prog="Triangle Gen", description="Generate triangles for testing")
parser.add_argument("rows", type=int, help="create a triangle with this many rows.")
parser.add_argument("outfile", help="filename to write output of generated triangle to")

args = parser.parse_args()

# open file for writing
with open(args.outfile, 'w+') as f:
	for row in range(args.rows + 1):
		for node in range(row):
			f.write(str(random.randint(1, 100)) + ' ')
		f.write('\n') 