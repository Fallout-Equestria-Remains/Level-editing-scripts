import libfoerrooms as FoER
from libfoerrooms import msgexit as exit
import sys
import argparse


argparser = argparse.ArgumentParser(
	usage='%(prog)s file.xml -r|-s|-S [-v] [--help|--version]',
	description=f'FoER locations room sorter v{FoER.SCRIPT_VERSION}. (c) Keirlex'
)

argparser.add_argument('filename', metavar='file.xml', help='File to sort (in place).')
argparser.add_argument('-s', '--sort', action='store_const', default=0, const=1, dest='sortmode', help='Sort output by room names like in the default level editor.')
argparser.add_argument('-S', '--sort-abc', action='store_const', default=0, const=2, dest='sortmode', help='Sort output by room names in lexicographic order.')
argparser.add_argument('-t', '--remove-test', action='store_true', dest='testoptionremove', help='Remove test tags from options.')
argparser.add_argument('-r', '--reverse', action='store_true', help='Reverse output.')
argparser.add_argument('-v', '--verbose', action='store_true', help='Be verbose and print more info (including processed room names).')
argparser.add_argument('-V', '--version', action='version', version=f'{FoER.SCRIPT_VERSION}', help='Print out version of the script and exit.')
TRY_HELP_PARAM=f'\nSee "{sys.argv[0]} --help" for usage.'


args = argparser.parse_args()
nowriteback=False

if args.sortmode == 0 and not args.reverse and not args.testoptionremove:
	print('Note: no operation to do, --sort nor --sort-abc nor --reverse nor --remove-test not passed' + TRY_HELP_PARAM + '\n', file=sys.stderr)
	nowriteback=True


#
# Main
#


allrooms = []

allrooms = FoER.parse_rooms(args.filename)
print(f'Parsed file {args.filename} with total of {len(allrooms)} rooms.', file=sys.stderr)

if len(allrooms) == 0:
	exit('No rooms.')


if args.verbose:
	print('Orig rooms:', *['"' + x.get('name') + '"' for x in allrooms], sep='\n * ', file=sys.stderr)



# Process rooms
if args.sortmode == 1:
	print('Sort as in the default level editor...', file=sys.stderr)
	FoER.sort_rooms(allrooms, True)
elif args.sortmode == 2:
	print('Sort in lexicographic order...', file=sys.stderr)
	FoER.sort_rooms(allrooms, False)

if args.reverse:
	print('Reverse...', file=sys.stderr)
	allrooms.reverse()

if args.testoptionremove:
	print('Remove test attribute from options tag...', file=sys.stderr)
	cnt = 0

	for r in allrooms:
		optionstag = r.find('options')
		try:
			del optionstag.attrib['test']
			cnt += 1
			if args.verbose: print(f' - Removed test="1" in room "{r.get("name")}"', file=sys.stderr)
		except KeyError: #Skip empty
			pass

	print(f'Removed {cnt} "tests".', file=sys.stderr)



# Writing out
if args.verbose and not nowriteback:
	print('Processed rooms:', *['"' + x.get('name') + '"' for x in allrooms], sep='\n * ', file=sys.stderr)

if nowriteback:
	print(f'No operation, nothing interesting to write back to file "{args.filename}"', file=sys.stderr)
else:
	print(f'Writing back {len(allrooms)} rooms to "{args.filename}"...', file=sys.stderr)
	FoER.write_rooms(allrooms, args.filename)
