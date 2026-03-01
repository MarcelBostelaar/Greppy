import os
import sys
import re
import argparse

def clear_console():
	os.system('cls' if os.name == 'nt' else 'clear')

	
def printEscaped(text, end="\n"):
	print(text.encode("unicode_escape").decode(), end=end)

def printColored(text, end="\n"):
	reset_code = "\033[0m"
	green_code = "\033[1;32m"
	text = text.encode("unicode_escape").decode()
	print(green_code + text + reset_code, end=end)

class MatchResult:
	def __init__(self, filepath, relative_start, relative_end, lines):
		self.filepath = filepath
		self.relative_start = relative_start
		self.relative_end = relative_end
		self.lines = lines

	def print(self):
		print(self.filepath)
		index = 0
		for line in self.lines:
			line_length = line["end"] - line["start"]
			# Line is after the match, skip rest of the lines
			if index > self.relative_end:
				break
			# Line is before the match, skip it
			if index + line_length <= self.relative_start:
				index += line_length
				continue
			print(str(line["line_number"]) + ":\t", end="")
			#Line is fully within the match
			if index >= self.relative_start and index < self.relative_end:
				printColored(line["text"])
			#start
			elif index < self.relative_start and index + line_length > self.relative_end:
				# The line is fully within the match
				start_segment = line["text"][:self.relative_start - index]
				middle_segment = line["text"][self.relative_start - index:self.relative_end - index + 1]
				end_segment = line["text"][self.relative_end - index + 1:]
				printEscaped(start_segment, end="")
				printColored(middle_segment, end="")
				printEscaped(end_segment)
			# The line is partially within the match, but the match ends in a later line
			elif index < self.relative_start:
				start_segment = line["text"][:self.relative_start - index]
				end_segment = line["text"][self.relative_start - index:]
				printEscaped(start_segment, end="")
				printColored(end_segment)
			# The line is partially within the match, but the match starts in an earlier line
			else:
				start_segment = line["text"][:self.relative_end - index + 1]
				end_segment = line["text"][self.relative_end - index + 1:]
				printColored(start_segment, end="")
				printEscaped(end_segment)
			index += line_length
		print()

class LineSpanIndex:
	def __init__(self, filepath, file_text):
		self.filepath = filepath
		self.line_spans = []
		char_index = 0
		lines = file_text.splitlines(True)

		if len(lines) == 0:
			self.line_spans = [{"line_number": 1, "start": 0, "end": 0, "text": ""}]
			return

		for line_number, line_text in enumerate(lines, start=1):
			start_index = char_index
			end_index = start_index + len(line_text)
			self.line_spans += [{
				"line_number": line_number,
				"start": start_index,
				"end": end_index,
				"text": line_text
			}]
			char_index = end_index

	def _span_index_for_position(self, position):
		if len(self.line_spans) == 1:
			return 0

		left = 0
		right = len(self.line_spans) - 1

		# Binary search to find the line span that contains the given position
		while left <= right:
			middle = (left + right) // 2
			line_span = self.line_spans[middle]
			if position < line_span["start"]:
				right = middle - 1
			elif position > line_span["end"]:
				left = middle + 1
			else:
				return middle

		raise ValueError("Position " + str(position) + " is out of bounds for the given file text")

	def get_match_result(self, start_index, end_index):
		"""Arguments:
		- start_index: The start index of the match
		- end_index: The end index of the match, inclusive
		"""
		if len(self.line_spans) == 0:
			return []

		if end_index < start_index:
			raise ValueError("end_index must be greater than or equal to start_index")

		first_index = self._span_index_for_position(start_index)
		last_index = self._span_index_for_position(end_index + 1)

		matching_lines = self.line_spans[first_index:last_index + 1]

		relative_start = start_index - matching_lines[0]["start"]
		relative_end = end_index - matching_lines[0]["start"]

		return MatchResult(self.filepath, relative_start, relative_end, matching_lines)

def dofile_regular(file_path, pattern, insensitive=False):
	pattern = re.escape(pattern)
	return dofile_regex(file_path, pattern, insensitive)

def dofile_regex(file_path, pattern, insensitive=False, unify_linebreaks_to_slashn=False):
	flags = re.DOTALL
	if insensitive:
		flags = flags | re.IGNORECASE

	compiled = re.compile(pattern, flags=flags)

	
	try:
		with open(file_path, 'rb') as inputstream:
			data = inputstream.read()
			file_text = data.decode("utf-8")
	except UnicodeDecodeError as e:
		#Not a text file. Skip it.
		return []

	if unify_linebreaks_to_slashn:
		file_text = file_text.replace("\r\n", "\n").replace("\r", "\n")

	line_span_index = LineSpanIndex(file_path, file_text)
	matches = []

	matches = [line_span_index.get_match_result(match.start(), match.end() - 1) for match in compiled.finditer(file_text)]
	return matches

def get_file_paths(folder, recursive=False):
	if recursive:
		paths = []
		for root, _, files in os.walk(folder):
			paths += [os.path.join(root, file_name) for file_name in files]
		return paths

	names = os.listdir(folder)
	items = [os.path.join(folder, x) for x in names]
	return [x for x in items if os.path.isfile(x)]

def execute_files(file_paths, pattern, isRegex=False, caseInsensitive=False, base_folder=".", unify_linebreaks_to_slashn=True):
	total_files = len(file_paths)
	all_results = []

	for index, file_path in enumerate(file_paths, start=1):
		if isRegex:
			matches_for_file = dofile_regex(file_path, pattern, caseInsensitive, unify_linebreaks_to_slashn=unify_linebreaks_to_slashn)
		else:
			matches_for_file = dofile_regular(file_path, pattern, caseInsensitive)

		if(not (index % 1000 == 0)):
			continue
		match_count = len(matches_for_file)

		relative_path = os.path.relpath(file_path, start=base_folder)
		text = "\033[2J\033[H" # Clear console and move cursor to top left
		text += (str(index) + "/" + str(total_files)) + "\n"
		text += ("matches: " + str(match_count)) + "\n"
		text += (relative_path)
		print(text)

		all_results += matches_for_file

	return all_results

'''Takes a pattern and several options and returns a list of strings that represent the result'''
def main(pattern, isRegex=False, caseInsensitive = False, recursive = False, folder=".", unify_linebreaks_to_slashn=True):
	if os.name == 'nt':
		os.system('color')
	file_paths = get_file_paths(folder, recursive)
	return execute_files(file_paths, pattern, isRegex, caseInsensitive, folder, unify_linebreaks_to_slashn=unify_linebreaks_to_slashn)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Grep like python utility")
	parser.add_argument("pattern", nargs="?", help="The pattern, text or regex, to match")
	parser.add_argument("-re", "-regex", action="store_true", help="Treat the given text as a regex string")
	parser.add_argument("-tlb", "-true-linebreaks", action="store_false", help="Prevents unification of linebreaks to Unix style (\\n) before matching, keeping the true linebreak characters. Linebreaks are unified by default. Only applies to regex mode.")
	parser.add_argument("-r", "-recursive", action="store_true", help="Recursively search all subdirectories")
	parser.add_argument("-i", "-ignorecase", action="store_true", help="Match case insensitive")
	parser.add_argument("-f", "-folder", default=".", help="Folder to search in (default: current directory)")
	parser.add_argument("--h", "-help", action="help", help="Show help page")

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

	result = main(args.pattern, isRegex=args.re, caseInsensitive=args.i, recursive=args.r, folder=args.f, unify_linebreaks_to_slashn=args.tlb)
	clear_console()
	print(args.pattern)
	print("Total matches: " + str(len(result)))
	for match in result:
		match.print()
	