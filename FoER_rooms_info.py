import libfoerrooms as FoER
from libfoerrooms import msgexit as exit
import sys
import argparse
import re


argparser = argparse.ArgumentParser(
	usage='''
  %(prog)s file.xml [roomname ...] [-o [NAME ...]] [-b [NAME ...]]
  %(prog)s --help|--version''',
	description=f'FoER locations room statistic script v{FoER.SCRIPT_VERSION}. (c) Keirlex'
)

argparser.add_argument('filename', metavar='file.xml', help='File to read.')
argparser.add_argument('roomnames', metavar='[roomname ...]', nargs='*', help='Room names to analyze. Without them print info for all rooms.')
argparser.add_argument('-o', '--obj', '--objects', nargs='*', dest='objnames', help='Show objects stat (+filter names if passed).')
argparser.add_argument('-b', '--back', '--background', nargs='*', dest='backnames', help='Show background decorations stat (+filter names if passed).')
argparser.add_argument('-r', '--regex-stat', action='store_true', help='Use regex search for all stat names ([-o], [-b]).')
argparser.add_argument('-i', '--regex-stat-invert', action='store_true', help='Invert rules for the stat regex search.')
argparser.add_argument('-R', '--regex-rooms', action='store_true', help='Use regex search for the [roomname ...]')
argparser.add_argument('-I', '--regex-rooms-invert', action='store_true', help='Invert rules for the rooms regex search.')
argparser.add_argument('-s', '--sort-abc', action='store_true', help='Sort stat output by name instead of by number.')
argparser.add_argument('-e', '--reverse', action='store_true', help='Reverse the sorted output.')
argparser.add_argument('-t', '--total', action='store_true', help='Print total stats without room names.')
#argparser.add_argument('-c', '--csv', '--excel', action='store_true', help='Output to CSV format (Excel-importable).')
argparser.add_argument('-a', '--print-all-rooms', '--all-rooms', action='store_true', help='Print headers for empty rooms.')
argparser.add_argument('-v', '--verbose', action='store_true', help='Be verbose. Extra output prints to stderr.')
argparser.add_argument('-V', '--version', action='version', version=f'{FoER.SCRIPT_VERSION}', help='Print out version of the script and exit.')
TRY_HELP_PARAM=f'\nSee "{sys.argv[0]} --help" for usage.'


args = argparser.parse_args()
#print(args)

def safe_len(v) -> int:
	return 0 if v is None else len(v)

#
# Main
#

parseall = args.objnames is None and args.backnames is None
parseobj   = parseall or args.objnames is not None
parsedecor = parseall or args.backnames is not None
parseall = parseobj and parsedecor #Overwrite with new meaning

if args.verbose:
	if args.regex_stat:
		print('Statistic regex enabled', 'to DECLINE' if args.regex_stat_invert else 'to ALLOW', 'matching object and background names.', file=sys.stderr)

	if parseobj:
		nm= '"' + '", "'.join(args.objnames) + '"'
		print('Parsing objects', f'with name(s) {nm}' if safe_len(args.objnames) > 0 else 'without name filter', file=sys.stderr)
	else:
		print('Parsing of objects is disabled', file=sys.stderr)

	if parsedecor:
		nm= '"' + '", "'.join(args.backnames) + '"'
		print(f'Parsing background decorations', f'with name(s) {nm}' if safe_len(args.backnames) > 0 else 'without name filter', file=sys.stderr)
	else:
		print('Parsing of background decors is disabled', file=sys.stderr)

	if args.regex_rooms:
		print('Rooms regex enabled', 'to DECLINE' if args.regex_rooms_invert else 'to ALLOW', 'matching room names.', file=sys.stderr)

	print('Sort statistics by', 'NAME' if args.sort_abc else 'COUNT', 'and reverse the output.' if args.reverse else '', file=sys.stderr)


allrooms = []

allrooms = FoER.parse_rooms(args.filename)
#print(f'Parsed file {args.filename} with total of {len(allrooms)} rooms.', file=sys.stderr)

if len(allrooms) == 0:
	exit('No rooms.')


def sort_counts(counts: dict) -> list:
	global args

	if args.sort_abc:
	#Sort by name
		reversesort = args.reverse
		keysort = lambda x: x[0]
	else:
	#Sort by number
		reversesort = not args.reverse
		keysort = lambda x: int(x[1])

	#if args.sort_number:
	#	return sorted(counts.items(), key=lambda x: int(x[1]))

	return sorted(counts.items(), key=keysort, reverse=reversesort)

def check_name_in(cname: str, lst: list, regexed: bool, regexinverted: bool) -> bool:
	if regexed:
		return regexinverted ^ any([re.search(pattern, cname) is not None for pattern in lst])
	else:
		return cname in lst

def check_roomname(rname: str) -> bool:
	global args
	return check_name_in(rname, args.roomnames, args.regex_rooms, args.regex_rooms_invert)

def check_ingame_obj_name(oname: str, lst: list, tag: str) -> bool:
	global args, parseobj, parsedecor
	return check_name_in(oname, lst, args.regex_stat, args.regex_stat_invert)


def parse_ingame_obj_tags(tag: str, cmplist: list, force=True) -> dict:
	if cmplist == None:
		if force: cmplist = []
		else: return {}

	counts = dict()

	for d in r.findall(tag):
		objname = d.get('id')

		if len(cmplist) == 0  or  check_ingame_obj_name(objname, cmplist, tag):
			if not counts.get(objname): counts[objname] = 0
			counts[objname] += 1

	#sortedcounts = sort_counts(counts)

	return counts

def print_list_stat(title, items, allowingflag=True, printtitle=True):
	if not allowingflag:
		return

	items = sort_counts(items)
	if len(items)>0:
		if printtitle: print(f'==== {title}')

		for (k, v) in items:
			print(f'{v} {k}')



sumobjects = dict()
sumdecors = dict()

def sum_dicts(ddest, dsrc):
	for k in dsrc.keys():
		if ddest.get(k):
			ddest[k] += dsrc[k]
		else:
			ddest[k] = dsrc[k]



if args.verbose: print(f'  Initialized!\n', file=sys.stderr)

# Parse rooms
for r in allrooms:
	rname = r.get('name')

	if len(args.roomnames) > 0  and  not check_roomname(rname):
		if args.verbose: print(f'Skip room "{rname}" because it does not meet the name regex', file=sys.stderr)
		continue

	if args.verbose: print(f'Reading room "{rname}"...', file=sys.stderr)

	#Parse objects and decors
	objects, decors=None, None

	if parseobj:
		objects=parse_ingame_obj_tags('obj', args.objnames)
	if parsedecor:
		decors=parse_ingame_obj_tags('back', args.backnames)

	#Sum to total stats
	if objects is not None:
		sum_dicts(sumobjects, objects)
	if decors is not None:
		sum_dicts(sumdecors, decors)

	#print(f'== objects {sumobjects}\n== decors {sumdecors}\n')

	if not args.total:
		if safe_len(objects) == 0 and safe_len(decors) == 0:
			if args.print_all_rooms: print(f'========== Room "{rname}" (empty)')
			continue

		print(f'========== Room "{rname}"')
		print_list_stat('Objects', objects, parseobj, parseall)
		print_list_stat('Background', decors, parsedecor, parseall)

	# Map (not implemented yet)
#	if args.levelmap:
#		data = r.findall('a')


if args.total:
	print(f'========== Total statistics')
	print_list_stat('Objects', sumobjects, parseobj, parseall)
	print_list_stat('Background', sumdecors, parsedecor, parseall)

if len(sumdecors) == 0 and len(sumobjects) == 0:
	print('Nothing found...\n\nCurrent name filters (use the "--verbose" flag for more info):')

	if parseobj:
		nm= '"' + '", "'.join(args.objnames) + '"'
		print('Parsing objects', f'with name(s) {nm}' if safe_len(args.objnames) > 0 else 'without name filter')
	else:
		print('Parsing of objects is disabled')

	if parsedecor:
		nm= '"' + '", "'.join(args.backnames) + '"'
		print(f'Parsing background decorations', f'with name(s) {nm}' if safe_len(args.backnames) > 0 else 'without name filter')
	else:
		print('Parsing of background decors is disabled')
