import os
import sys
import re
import argparse

flatten = lambda l: [item for sublist in l for item in sublist]

def removelinebreak(text):
	return text.replace("\n","").replace("\r","")

def dofile(matchfunc):
	def inner(file):
		total = []
		try:
			inputstream = open(file, 'r')
			lines = inputstream.readlines()
			inputstream.close()
			lines = [removelinebreak(x) for x in lines]
			hasprinted = False
			for i in range(len(lines)):
				if matchfunc(lines[i]):
					if not hasprinted:
						total += [""]
						total += [file]
						hasprinted = True
					total += [str(i+1) + ":\t" + re.sub("^[\\s]*", "", lines[i])]
		except Exception as e:
			return []
		return total
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
	childfolderresults = flatten([mapfolder(x, func) for x in childfolders])
	fileresults = flatten([func(x) for x in files])
	return childfolderresults + fileresults
		
def onefolder(folder, func):
	names = os.listdir(folder)
	items = [os.path.join(folder,x) for x in names]
	files = [x for x in items if os.path.isfile(x)]
	return flatten([func(x) for x in files])

'''Takes a pattern and several options and returns a list of strings that represent the result'''
def main(pattern, isRegex=False, caseInsensitive = False, recursive = False, folder="."):
	patternmatcher = None
	if isRegex:
		patternmatcher = regex(pattern, caseInsensitive)
	else:
		patternmatcher = regular(pattern, caseInsensitive)	
		
	if recursive:
		return mapfolder(folder, patternmatcher)
	else:
		return onefolder(folder, patternmatcher)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Grep like python utility")
	parser.add_argument("pattern", nargs="?", help="The pattern, text or regex, to match")
	parser.add_argument("-re", "-regex", action="store_true", help="Treat the given text as a regex string")
	parser.add_argument("-r", "-recursive", action="store_true", help="Recursively search all subdirectories")
	parser.add_argument("-i", "-ignorecase", action="store_true", help="Match case insensitive")
	parser.add_argument("-f", "-folder", default=".", help="Folder to search in (default: current directory)")
	parser.add_argument("--h", "-help", "--help", action="help", help="Show help page")

	args = parser.parse_args()
	if args.pattern is None:
		print("Error: pattern is required.")
		parser.print_help()
		sys.exit(0)

	if args.pattern == "":
		print("Warning: empty pattern is not allowed.")
		parser.print_help()
		sys.exit(1)

	if args.pattern.strip() == "":
		confirmation = input("Pattern is whitespace-only. Continue? [y/N]: ").strip().lower()
		if confirmation not in ["y", "yes"]:
			print("Search cancelled.")
			parser.print_help()
			sys.exit(1)
	
	if args.pattern == "help":
		confirmation = input("Show help? Press enter/no to search for the pattern 'help'. [y/N]: ").strip().lower()
		if confirmation in ["y", "yes"]:
			parser.print_help()
			sys.exit(0)

	result = main(args.pattern, isRegex=args.re, caseInsensitive=args.i, recursive=args.r, folder=args.folder)
	print("\n".join(result))
	