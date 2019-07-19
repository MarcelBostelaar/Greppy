from grep import main
import re
tests = [
("-".join(main("grep", isRegex=False, caseInsensitive = False, recursive = False, folder="./test")), '''-./test\\test.txt-1:	grep''')
,("-".join(main("grep", isRegex=False, caseInsensitive = True, recursive = False, folder="./test")), '''-./test\\test.txt-1:	grep-2:	grEP-3:	GREP''')
,("-".join(main("grep", isRegex=False, caseInsensitive = False, recursive = True, folder="./test")), '''-./test\\testmap\\test2.txt-1:	grep--./test\\test.txt-1:	grep''')
,("-".join(main("grep", isRegex=False, caseInsensitive = True, recursive = True, folder="./test")), '''-./test\\testmap\\test2.txt-1:	grep-2:	GRep-3:	GREP--./test\\test.txt-1:	grep-2:	grEP-3:	GREP''')

,("-".join(main("[0-9]+", isRegex=False, caseInsensitive = False, recursive = False, folder="./test")), "")
,("-".join(main("[0-9]+", isRegex=True, caseInsensitive = False, recursive = False, folder="./test")), '''-./test\\test.txt-4:	12345''')
,("-".join(main("[0-9]+", isRegex=True, caseInsensitive = False, recursive = True, folder="./test")), '''-./test\\testmap\\test2.txt-4:	5678--./test\\test.txt-4:	12345''')
,("-".join(main('''[\s]+''', isRegex=True, caseInsensitive = False, recursive = True, folder="./test")), '''-./test\\testmap\\test2.txt-5:	space test''')
,("-".join(main('''[\s]+''', isRegex=False, caseInsensitive = False, recursive = True, folder="./test")), '''-./test\\testmap\\test2.txt-6:	regex_off_test_[\\s]+''')
]

succeeded = True
for i in range(len(tests)):
	if not tests[i][0] == tests[i][1]:
		succeeded = False
		print("Test #" + str(i+1) + " failed")
		print("Expected:")
		print(tests[i][1])
		
		print("Actual:")
		print(tests[i][0])
		print("\n")

if succeeded:
	print("All tests passed")