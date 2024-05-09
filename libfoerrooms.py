import sys
import xml.etree.ElementTree as XMLTree
import contextlib

SCRIPT_VERSION = "0.6"
STDOUT_OUT_FILE = "-"


"""
	Parse rooms from filename to list.
	Returns list(XMLTree.ElementTree)
"""
def parse_rooms(filename: str) -> list:
	try:
		xmltree = XMLTree.parse(filename)
	except Exception as e:
		#print(f'Cannot open file "{filename}" for reading.', repr(e), sep='\n')
		raise OSError(f'Cannot open file "{filename}" for reading.') from e

	xmlroot = xmltree.getroot()
	rooms = list()

	for i, item in enumerate(xmlroot):
		if item.tag != 'room':
			#print(f'Tag "{item.tag}" is not a room!', file=sys.stderr)
			raise XMLTree.ParseError(f'Tag "{item.tag}" is not a room! Error in opening tag {i+1}.')
			return None

		#print(f'{item}. "{item.text}", "{item.tail}"')
		rooms.append(item)

	return rooms


"""
	Well, it's almost editor-like sort: order by minimal level, but all back layers slides to the end of the list.
	Auxiliary internal func
"""
def sort_rooms_editormode(elemroom):
	name = elemroom.get('name', '')
	optionstag = elemroom.find('options')

	# Back layer sort
	backattrib = 'b' if 'back' == optionstag.get('tip', '-') else 'a'

	# Level sort
	minlevelattrib = optionstag.get('level')
	if not minlevelattrib:
		minlevelattrib = '0'

	# Gen
	prename = backattrib + minlevelattrib + '_'

	return prename + name

"""
	Sort rooms by their names / almost like in the original level editor
	In place func
"""
def sort_rooms(roomslist: list, editorlikesort=True):
	if editorlikesort:
		keyfunc = sort_rooms_editormode
	else:
		keyfunc = lambda x: x.get('name')

	roomslist.sort(key=keyfunc)



"""
	Write list(rooms) XML to the 'filename' or to stdout
"""
@contextlib.contextmanager
def write_rooms(rooms: list, filename: str = "out_rooms.xml"):
	xmltree = XMLTree.ElementTree(XMLTree.Element("all"))
	xmlroot = xmltree.getroot()
	xmlroot.text = '\n  '
	xmlroot.tail = '\n'

	rooms2 = rooms.copy()

	if len(rooms2) > 0:
		# Right ends
		for r in rooms2[:-2 ] :
			r.tail = '\n  '

		rooms2[-1].tail = '\n'

		# Save all
		xmlroot.extend(rooms2)

	writefd = sys.stdout if filename == STDOUT_OUT_FILE else filename

	try:
		xmltree.write(writefd, encoding="unicode", xml_declaration=False)
	except BrokenPipeError:
		print('Exception: Broken pipe', file=sys.stderr)
		pass



"""
	A wrapper around the exit()
	Auxiliary wrapper func
"""
def msgexit(msg='', code=0):
	if msg:
		print(msg, file=sys.stderr)

	sys.exit(code)

