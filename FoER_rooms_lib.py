import sys
import xml.dom.minidom as xmldom
import contextlib

SCRIPT_VERSION='0.2'


STDOUT_OUT_FILE='\\/'

@contextlib.contextmanager
def write_file_or_stdout(filename = None):
    if filename and filename != STDOUT_OUT_FILE:
        fh = open(filename, 'w')
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


# Wrapper
def exit(exitmsg=''):
	if exitmsg:
		print( exitmsg )

	sys.exit()


def print_usage_args(rightparams, leftparams):

	righthelp, lefthelp = rightparams, leftparams

	rightwidth = max( [ len( i ) for i in righthelp ] )

	for i in range(len(lefthelp)):
		curleft = lefthelp[i].split('\n')
		curright = [righthelp[i]] + [''] * len(curleft)

		for i in range(len(curleft)):
			print( curright[i].ljust(rightwidth), curleft[i] )
		#print()


def get_xml_elem(xmltext, tag, attr):
	xml = xmldom.parseString(xmltext)
	return xml.getElementsByTagName(tag)[0].getAttribute(attr)


