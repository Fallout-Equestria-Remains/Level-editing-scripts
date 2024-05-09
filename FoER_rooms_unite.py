import libfoerrooms as FoER
from libfoerrooms import msgexit as exit
import sys
import argparse


DEFAULT_OUT_FILE="outrooms_united.xml"


argparser = argparse.ArgumentParser(
	usage='''
  %(prog)s file1.xml file2.xml [file3.xml ...] [-o OUTFILE] [-afsSv]
  %(prog)s --help|--version''',
	description=f'FoER locations room uniter v{FoER.SCRIPT_VERSION}. (c) Keirlex'
)

argparser.add_argument('filenames', nargs='*', metavar='file1.xml file2.xml [file3.xml ...]', help='Files to unite. Lastest room files has higher priority, their rooms will rewrite previous with the same names (if no "-a" argument provided).')
argparser.add_argument('-o', '--output', dest='outfile', default=DEFAULT_OUT_FILE, help=f'Output file to write. If name set to "-", output to stdout. If whole "-o" is omitted, will be used name "{DEFAULT_OUT_FILE}". Note that output file will be overwritten!')
argparser.add_argument('-a', '--append-only', '--safe-concat', dest='safeconcat', default=False, action='store_true', help='Terminate with message when trying to overwrite some previous room. Output file will not be created or updated.')
argparser.add_argument('-s', '--sort', action='store_const', default=0, const=1, dest='sortmode', help='Sort output by room names like in the default level editor.')
argparser.add_argument('-S', '--sort-abc', action='store_const', default=0, const=2, dest='sortmode', help='Sort output by room names in lexicographic order.')
argparser.add_argument('-v', '--verbose', action='store_true', help='Be verbose and print more info (including processed room names).')
argparser.add_argument('-V', '--version', action='version', version=f'{FoER.SCRIPT_VERSION}', help='Print out version of the script and exit.')
TRY_HELP_PARAM=f'\nSee "{sys.argv[0]} --help" for usage.'


args = argparser.parse_args()

if len(args.filenames) < 2:
	exit('At least 2 room files are required.' + TRY_HELP_PARAM, 1)


#
# Main
#


allrooms = []
allroomnames = []

# Parsing rooms
for infile in args.filenames:
	parsedrooms = FoER.parse_rooms(infile)
	newrooms = []
	overwrrooms = []

	print(f'Parsed file {infile} with total of {len(parsedrooms)} rooms.', file=sys.stderr)

	for r in parsedrooms:
		rname = r.get('name')
		if not rname in allroomnames:
			if args.verbose: print(f' + New room "{rname}".', file=sys.stderr)
			newrooms.append(r)
		else:
			if args.verbose: print(f' ! Overwritng room "{rname}".', file=sys.stderr)
			overwrrooms.append(r)

	if args.safeconcat  and  len(overwrrooms) > 0:
		print(f'Cannot safe append. Intersection of the next rooms from file "{infile}":', *[x.get('name') for x in overwrrooms], sep='\n ! ')
		exit("Violation of the --append-only, abort.", 2)

	# Add spaces before 1st <room> tag
	if len(allrooms) > 0 and len(newrooms) > 0: allrooms[-1].tail = '\n  '

	for r in overwrrooms:
		allrooms[allroomnames.index(r.get('name'))] = r

	allrooms = allrooms + newrooms
	allroomnames = allroomnames + [ n.get('name') for n in newrooms ]


# Sorting
if args.sortmode > 0:
	editorLikeSort = True if args.sortmode == 1 else False

	if args.verbose:
		if editorLikeSort:
			print(f'Sort as in the default level editor...', file=sys.stderr)
		else:
			print(f'Sort in lexicographic order...', file=sys.stderr)

	FoER.sort_rooms(allrooms, editorLikeSort)


# Writing out
if args.verbose:
	print('United rooms:', *['"' + x.get('name') + '"' for x in allrooms], sep='\n * ', file=sys.stderr)

if args.outfile != FoER.STDOUT_OUT_FILE:
	print(f'Total {len(allrooms)} united rooms. Writing to "{args.outfile}"...', file=sys.stderr)
else:
	print(f'Total {len(allrooms)} united rooms. Piping to stdout...', file=sys.stderr)

FoER.write_rooms(allrooms, args.outfile)

