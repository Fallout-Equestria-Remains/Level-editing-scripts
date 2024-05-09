import libfoerrooms as FoER
from libfoerrooms import msgexit as exit
import sys
import argparse
import re


DEFAULT_OUT_FILE="outrooms_cutted.xml"

argparser = argparse.ArgumentParser(
	usage='''
  %(prog)s file.xml roomname [roomname ...] [-o OUTFILE] [-c] [-abdrv]
  %(prog)s file.xml roomname [roomname ...] -x [-abdrv]
  %(prog)s --help|--version''',
	description=f'FoER locations room cutter v{FoER.SCRIPT_VERSION}. (c) Keirlex'
)

argparser.add_argument('infile', metavar='file.xml', help='Input file to cut from. Without the "-c" arg file will be changed.')
argparser.add_argument('cutnames', metavar='roomname [...]', nargs='*', help='These rooms will be cutted from the input file.')
argparser.add_argument('-o', '--output', dest='outfile', default=DEFAULT_OUT_FILE, help=f'Output file to write. If name set to "-", output to stdout. If whole "-o" is omitted, will be used name "{DEFAULT_OUT_FILE}". Note that output file will be overwritten!')
argparser.add_argument('-c', '--copy', '--no-change', '--no-cut', action='store_true', help='Do not change the input file. Copy rooms to output instead of cut.')
argparser.add_argument('-r', '--regex', action='store_true', help='Use regex search for the room names.')
argparser.add_argument('-x', '--delete', '--remove', '--purge', action='store_true', help='Just remove rooms from input file, do not write them anywhere')
#argparser.add_argument('-a', '--absence-abort', action='store_true', dest='absenceabort', help='Terminate program without changing anything if some room cannot be found (also for regex).')
argparser.add_argument('-d', '--dry-run', action='store_true', dest='dryrun', help='Do not change anything and stop right before writing.')
argparser.add_argument('-b', '--back-layers', action='store_true', dest='removebacklayers', help='Also cut back layer rooms for deleted rooms.')
argparser.add_argument('-v', '--verbose', action='store_true', help='Be verbose and print more info (including processed room names).')
argparser.add_argument('-V', '--version', action='version', version=f'{FoER.SCRIPT_VERSION}', help='Print out version of the script and exit.')
TRY_HELP_PARAM=f'\nSee "{sys.argv[0]} --help" for usage.'


args = argparser.parse_args()

if len(args.cutnames) < 1:
	exit('At least 1 room name is required.' + TRY_HELP_PARAM, 1)

if args.copy and args.delete:
	exit('Both --no-change and --delete args provided, nothing to be changed :/' + TRY_HELP_PARAM, 3)


#
# Main
#

cutrooms, leftrooms = [], []

parsedrooms = FoER.parse_rooms(args.infile)
print(f'Parsed file {args.infile} with total of {len(parsedrooms)} rooms.', file=sys.stderr)


def check_roomname_for_cut(rname: str) -> bool:
	global args

	if args.regex:
		return any([re.search(pattern, rname) is not None for pattern in args.cutnames])
	else:
		return rname in args.cutnames

cutbackroomnames = []


# Process all rooms:
for r in parsedrooms:
	rname = r.get('name')

	if args.verbose: print(f' + Parsed room "{rname}".', file=sys.stderr)

	if check_roomname_for_cut(rname):
		if args.verbose: print(f' - Room for cut "{rname}".', file=sys.stderr)
		cutrooms.append(r)

		# Prepare to cut back layers
		if args.removebacklayers:
			optionstag = r.find('options')
			if optionstag is not None:
				backname = optionstag.get('back', None)

				if args.verbose: print(f' - Added a back layer room "{backname}".', file=sys.stderr)

				if backname:
					cutbackroomnames.append(backname)

	#elif args.absenceabort:
	#	exit(f'Violation of the --abcense-abort, room "{rname}" is missing.', 2)
	else:
		leftrooms.append(r)

# Process back layers
if args.removebacklayers and len(cutbackroomnames) > 0:
	if args.verbose: print('Searching again for back layer rooms', file=sys.stderr)

	for r in leftrooms:
		rname = r.get('name')

		if rname in cutbackroomnames:
			if args.verbose: print(f' - Back layer room for cut "{rname}".', file=sys.stderr)

			cutrooms.append(r)
			leftrooms.remove(r)


# Output
if args.dryrun:
	print('--dry-run, stop before writing.', file=sys.stderr)
	print(f'Left {len(leftrooms)} rooms:', *['"' + x.get('name') + '"' for x in leftrooms], sep='\n * ', file=sys.stderr)
	print(f'Should be cutted {len(cutrooms)} rooms:', *['"' + x.get('name') + '"' for x in cutrooms], sep='\n * ', file=sys.stderr)
else:
	if not args.delete:
		if len(cutrooms) == 0:
			print('No rooms cut, so no output', file=sys.stderr)
		else:
			if args.outfile != FoER.STDOUT_OUT_FILE:
				print(f'Cut {len(cutrooms)} rooms. Writing to "{args.outfile}"...', file=sys.stderr)
			else:
				print(f'Cut {len(cutrooms)} rooms. Piping to stdout...', file=sys.stderr)

			FoER.write_rooms(cutrooms, args.outfile)

	if not args.copy:
		if len(leftrooms) == 0:
			print('No rooms left, so no writing back', file=sys.stderr)
		else:
			print(f'Left {len(leftrooms)} rooms. Writing back to "{args.infile}"...', file=sys.stderr)
			FoER.write_rooms(leftrooms, args.infile)

