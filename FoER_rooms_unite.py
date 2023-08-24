import sys
import FoER_rooms_lib


DEFAULT_OUT_FILE='united_rooms.xml'


def print_unite_usage():
	SCRIPT_PATH=sys.argv[0]

	print ( f'FoER random locations rooms uniter by Keirlex v{FoER_rooms_lib.SCRIPT_VERSION}.\n'
			'  Do not use this script for serial locations!\n'
			'  Script will not check input xml file correctness!\n'
			'\nUsage:\n'
			f'\t{SCRIPT_PATH} --help | --version\n'
			f'\t{SCRIPT_PATH} rooms1.xml rooms2.xml [rooms3.xml...] [-o (outfile.xml | -)] [-a] [-f] [-v]\n'
		)

	FoER_rooms_lib.print_usage_args([
		'--help or -h',
		'--version or -V',
		'<files.xml> (at least 2)',
		'--output or -o <file.xml>',
		'--safe-concat or -s',
#		'--use-filename or -f',
		'--dry-run or -d',
		'--quiet or -q',
		'--verbose or -v'
	], [
		'This help.',
		'Print out version of the script.',
		'Files to unite. Lastest room files has higher\npriority,their rooms will rewrite previous with the\nsame names (if no "-s" argument provided).',
		f'Output file to write. If argument set to "-", output\nto stdout. If whole "-o" is omitted, will be used\nname "{DEFAULT_OUT_FILE}".\nNote that output file will be overwritten.',
		'Terminate with message when trying to overwrite\nprevious room. Output file will not be created.',
#		'Use filename as the room name if file contains only\none room.',
		'Stop right before writing (do not output).',
		'Be quiet and do not output anything except errors.',
		'Be verbose and print what is happening.'
	])

TRY_HELP_PARAM=f'\nSee "{sys.argv[0]} --help".'


# unite.py (-h | --help)
# unite.py (-V | --version)
# unite.py -x file.xml -o directory [roomname] # Planned only
# unite.py file1.xml file2.xml [file3.xml...] [--output (outfile.xml | -)] [--append-only] [--use-file-names] [--verbose]
# unite.py file1.xml file2.xml [file3.xml...] [-o (outfile.xml | -)] [-a] [-n] [-v]


argc = len(sys.argv) - 1
argv = sys.argv[ 1: ]

#argvLowered = [ i.lower() for i in argv ]
#argvLowered = map(lower, argv)


# Help/version
#if argc == 1:
#	if argvLowered[0] == '--help' or argvLowered[0] == '-h' or argv[0] == '/?':
#		print_usage()
#		exit()
#	elif argvLowered[0] == '--version' or argvLowered[0] == '-v':
#		exit(SCRIPT_VERSION)


outfilepath = DEFAULT_OUT_FILE # If FoER_rooms_lib.STDOUT_OUT_FILE, output to stdout
saferConcat = False
verbose = False
quiet = False
dryrun = False
onlyScriptInfo = 0 # 0 is no info, 1 is help, 2 is version


roomfiles = []
params = iter(range(len(argv)))

for i in params:
	prm = argv[i]

	if prm == '--help' or prm == '-h':
		onlyScriptInfo=1
		break
	elif prm == '--version' or prm == '-V':
		onlyScriptInfo=2
		break

	if prm == '--safe-concat' or prm == '-s':
		saferConcat=True
	elif prm == '--verbose' or prm == '-v':
		verbose=True
		quiet=False
	elif prm == '--quiet' or prm == '-q':
		quiet=True
		verbose=False
	elif prm == '--outfile' or prm == '-o':
		if i >= len(argv)-1:
			exit('No output file name.')
		else:
			outfilepath=(argv[i+1] if argv[i+1] != '-' else FoER_rooms_lib.STDOUT_OUT_FILE)
			next(params)
	elif prm == '--dry-run' or prm == '-d':
		dryrun = True
	elif prm.startswith('-'):
		exit(f'Unknown parameter "{prm}"' + TRY_HELP_PARAM)
	else:
		try:
			f = open(prm, 'r', encoding='UTF-8')
			roomfiles.append(f)
		except:
			exit(f'Cannot open file "{prm}" for reading.')


# Script info output and exit
if onlyScriptInfo == 1:
	print_unite_usage()
	exit()
elif onlyScriptInfo == 2:
	exit(FoER_rooms_lib.SCRIPT_VERSION)

if len(roomfiles) < 2:
	exit( 'At least 2 room files is required.' + TRY_HELP_PARAM )


rooms = dict()

totalroomCount=0
curroom = str()


for roomfile in roomfiles:
	curroom = ""
	curroomCount=0
	roomfileLines= roomfile.readlines()

	if verbose: print(f'Opened file "{roomfile.name}":')


	for i in range(len(roomfileLines)):
		line1 = roomfileLines[i]
		line = line1.strip() # with removed spaces

		if line.startswith('<land'):
			if FoER_rooms_lib.get_xml_elem(line, 'land', 'serial'):
				exit(f'Tried to unite a serial location {roomfile.name} :/')
		elif line.startswith('<room'):
			xmlline = FoER_rooms_lib.get_xml_elem(line + '</room>', 'room', 'name')
			if not xmlline:
				exit(f'No room name at line {i+1} file {roomfile.name}')

			curroom = xmlline

			if rooms.get(curroom):
				if saferConcat:
					exit(f'Violation of the --safe-concat: tried to rewrite room "{curroom}" with other room from file "{roomfile.name}" at line {i+1}.')
				elif verbose:
					print(f' -Rewriting room "{curroom}"')
			else:
				totalroomCount += 1
				if verbose: print(f' -New room "{curroom}"')

			rooms[curroom] = line1
			curroomCount += 1

		elif line == '</room>':
			rooms[curroom] += line1
			curroom = ""
		elif curroom:
			# Main copy
			rooms[curroom] += line1

	if curroom != "":
		exit(f'Unexpected EoF (no </room> tag) in "{roomfile.name}" while parsing room "{curroom}"')

	if not quiet: print(f'Closed file "{roomfile.name}" with total of {curroomCount} rooms.')

if dryrun:
	if not quiet: print('Stop program before writing: --dry-run.')
	exit()


if verbose: print('Output to ' + (f'file "{outfilepath}"' if outfilepath != FoER_rooms_lib.STDOUT_OUT_FILE else 'stdout') + '...')

with FoER_rooms_lib.write_file_or_stdout(outfilepath) as outfile:
	outfile.write('<all>\n')

	for key in rooms:
		outfile.write(rooms[key])

	outfile.write('</all>')

if not quiet: print(f'Total rooms saved: {totalroomCount}.')

