import os
import sys
import re
import argparse

parser = argparse.ArgumentParser(description = "Grep like python utility")
parser.add_argument("pattern", nargs=1, help="The pattern, text or regex, to match")
parser.add_argument("-re", "-regex", action="store_true", help="Treat the given text as a regex string")
parser.add_argument("-r", "-recursive", action="store_true", help="Recursively search all subdirectories")
parser.add_argument("-i", "-ignorecase", action="store_true", help="Match case insensitive")


def dofile(matchfunc):
	def inner(file):
		try:
			inputstream = open(file, 'r')
			lines = inputstream.readlines()
			inputstream.close()
			hasprinted = False
			for i in range(len(lines)):
				if matchfunc(lines[i]):
					if not hasprinted:
						print("\n" + file)
						hasprinted = True
					print(str(i+1) + ":\t" + re.sub("^[\\s]*", "", lines[i]).replace("\n","").replace("\r",""))
		except Exception as e:
			pass
	return inner

def regex(pattern, insensitive):
	compiled = None
	if insensitive:
		compiled = re.compile(pattern, flags=re.IGNORECASE)
	else:
		compiled = re.compile(pattern)
	return dofile(lambda x: compiled.search(x) is not None)
	
def regular(pattern, insensitive):
	return regex(re.escape(pattern), insensitive)

def mapfolder(folder, func):
	names = os.listdir(folder)
	items = [os.path.join(folder,x) for x in names]
	childfolders = [x for x in items if os.path.isdir(x)]
	files = [x for x in items if os.path.isfile(x)]
	for i in childfolders:
		mapfolder(i, func)
	for i in files:
		func(i)
		
def onefolder(folder, func):
	names = os.listdir(folder)
	items = [os.path.join(folder,x) for x in names]
	files = [x for x in items if os.path.isfile(x)]
	for i in files:
		func(i)
		
args = parser.parse_args()
patternmatcher = None
if args.re:
	patternmatcher = regex(args.pattern[0], args.i)
else:
	patternmatcher = regular(args.pattern[0], args.i)

if args.r:
	mapfolder(".", patternmatcher)
else:
	onefolder(".", patternmatcher)
	