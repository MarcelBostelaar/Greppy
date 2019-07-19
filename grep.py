import os
import sys
import re

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

def regex(pattern):
	return dofile(lambda x: re.search(pattern, x) is not None)
	
def regular(pattern):
	return dofile(lambda x: pattern in x)

def mapfolder(folder, func):
	names = os.listdir(folder)
	items = [os.path.join(folder,x) for x in names]
	childfolders = [x for x in items if os.path.isdir(x)]
	files = [x for x in items if os.path.isfile(x)]
	for i in childfolders:
		mapfolder(i, func)
	for i in files:
		func(i)
		
if len(sys.argv) == 2:
	pattern = sys.argv[1]
	mapfolder(".", regular(pattern))
elif len(sys.argv) == 3 and sys.argv[1] == "-re":
	pattern = sys.argv[2]
	mapfolder(".", regex(pattern))
else:
	print("Wrong usage:")
	print("grep.py \"some text\"")
	print("grep.py -re \"some regex pattern\"")