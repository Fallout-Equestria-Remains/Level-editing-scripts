import sys
import FoER_rooms_lib


DEFAULT_OUT_FILE='cutted_rooms.xml'


def print_unite_usage():
	SCRIPT_PATH=sys.argv[0]

	print ( f'FoER random locations rooms cutter by Keirlex v{FoER_rooms_lib.SCRIPT_VERSION}.\n'
			'  Do not use this script for serial locations!\n'
			'  Script will not check input xml file correctness!\n'
			'\nUsage:\n'
			f'\t{SCRIPT_PATH} --help | --version\n'
			f'\t{SCRIPT_PATH} location.xml roomname1 [roomname2...] [-o (outfile.xml | -)] [-v]\n'
		)

	FoER_rooms_lib.print_usage_args([
		'--help or -h',
		'--version or -V',
		'<location.xml>',
		'<room names>',
		'--output or -o <file.xml>',
#		'--use-filename or -f',
#		'--optional-rooms or -r',
		'--dry-run or -d',
		'--quiet or -q',
		'--verbose or -v'
	], [
		'This help.',
		'Print out version of the script.',
		'Location file to cut rooms. File will be changed',
		'All of these rooms will be cutted from the input file.',
		f'Output file to write. If argument set to "-", output\nto stdout. If whole "-o" is omitted, will be used\nname "{DEFAULT_OUT_FILE}".\nNote that output file will be overwritten.',
#		'Use filename as the room name if file contains only\none room.',
#		'Do not abort when room name not found in the input file.',
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
optionalRooms = False
verbose = False
quiet = False
dryrun = False
onlyScriptInfo = 0 # 0 is no info, 1 is help, 2 is version


roomfile = None
cutRoomNames = []
params = iter(range(len(argv)))

for i in params:
	prm = argv[i]

	if prm == '--help' or prm == '-h':
		onlyScriptInfo=1
		break
	elif prm == '--version' or prm == '-V':
		onlyScriptInfo=2
		break

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
	elif prm == "--optional-rooms" or prm == "-r":
		optionalRooms = True
	elif prm == '--dry-run' or prm == '-d':
		dryrun = True
	elif prm.startswith('-'):
		exit(f'Unknown parameter "{prm}"' + TRY_HELP_PARAM)
	elif roomfile == None:
		try:
			roomfile = open(prm, 'r', encoding='UTF-8')
		except:
			exit(f'Cannot open file "{prm}" for reading.')
	else:
		cutRoomNames += [prm]


# Script info output and exit
if onlyScriptInfo == 1:
	print_unite_usage()
	exit()
elif onlyScriptInfo == 2:
	exit(FoER_rooms_lib.SCRIPT_VERSION)

if roomfile == None:
	exit('No file name to cut.' + TRY_HELP_PARAM)

if len(cutRoomNames) < 1:
	exit('At least 1 room name is required.' + TRY_HELP_PARAM)


rooms = dict()
curroom = ""

roomfileLines= roomfile.readlines()

if verbose: print(f'Opened file "{roomfile.name}".')

for i in range(len(roomfileLines)):
	line1 = roomfileLines[i]
	line = line1.strip() # with removed spaces

	if line.startswith('<land'):
		if FoER_rooms_lib.get_xml_elem(line, 'land', 'serial'):
			exit(f'Tried to cut room from a serial location {roomfile.name} :/')
	elif line.startswith('<room'):
		xmlline = FoER_rooms_lib.get_xml_elem(line + '</room>', 'room', 'name')
		if not xmlline:
			exit(f'No room name at line {i+1} file {roomfile.name}')

		curroom = xmlline
		rooms[curroom] = line1

	elif line == '</room>':
		rooms[curroom] += line1
		curroom = ""
	elif curroom:
		# Main copy
		rooms[curroom] += line1

if curroom != "":
	exit(f'Unexpected EoF (no </room> tag) in "{roomfile.name}" while parsing room "{curroom}"')

if verbose:
	foundlist = ""

	cnt = 0
	for key in rooms:
		if cnt % 5 == 0:
			foundlist += "\n  "
		cnt += 1

		foundlist += f'"{key}" '

	print('Found rooms: ' + foundlist + '\n')


if not dryrun:
	roomfileName = roomfile.name
	roomfile.close()

	try:
		roomfile = open(roomfileName, 'w', encoding='UTF-8')
	except:
		exit(f'Cannot open file "{roomfileName}" for writing.')


if verbose and not dryrun:
	print('Output to ' + (f'file "{outfilepath}"' if outfilepath != FoER_rooms_lib.STDOUT_OUT_FILE else 'stdout') + '...')

totalcutCount=0


def cut_write_room(roomname):
	global totalcutCount

	if key in cutRoomNames:
		if not dryrun: outfile.write(rooms[key])
		totalcutCount += 1
		if verbose: print(f' -Cutted room "{key}".')
	else:
		if not dryrun: roomfile.write(rooms[key])
		if verbose: print(f' -Skipped room "{key}".')


if not dryrun: 
	with FoER_rooms_lib.write_file_or_stdout(outfilepath) as outfile:
		outfile.write('<all>\n')
		roomfile.write('<all>\n')

		for key in rooms:
			cut_write_room(key)

		outfile.write('</all>')
		roomfile.write('</all>')
else:
	for key in rooms:
		cut_write_room(key)

if not quiet:
	inputfileLeftRooms=len(rooms)-totalcutCount

	if dryrun:
		print(f'Do not write because of --dry-run, should be cutted {totalcutCount} rooms and left {inputfileLeftRooms} rooms.')
	else:
		print(f'Cutted {totalcutCount} rooms, in input file left {inputfileLeftRooms} rooms.')
