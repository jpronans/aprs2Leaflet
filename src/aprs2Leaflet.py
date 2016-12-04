#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
#import time
import aprslib
import logging
import os
#import locale

parser = SafeConfigParser()
parser.read('config.ini')
if parser.get('logging', 'level') == "debug":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


# I don't care about aprsdroid or anything that doesn't have a 'speed' field.
def callback(packet):
    if ('latitude' in packet and
        'longitude' in packet and
        'speed' in packet and
        packet['to'] != 'APDR13'):
        f = open("aprstations.js", "a+")

        # Code taken from:
        # http://stackoverflow.com/questions/1877999/delete-final-line-in-file-via-python
        # Move the pointer (similar to a cursor in a text editor) to the end of the file.
        f.seek(0, os.SEEK_END)

        # This code means the following code skips the very last character in the file -
        # i.e. in the case the last line is null we delete the last line
        # and the penultimate one
        pos = f.tell() - 1

        # Read each character in the file one at a time from the penultimate 
        # character going backwards, searching for a newline character
        # If we find a new line, exit the search
        while pos > 0 and f.read(1) != "\n":
                pos -= 1
                f.seek(pos, os.SEEK_SET)

        # So long as we're not at the start of the file,
        # delete all the characters ahead of this position
        if pos > 0:
            f.seek(pos, os.SEEK_SET)
            f.truncate()

        # Generate the required format
        outStr = "\n[%.5f, %.5f, 1]    <!-- %s -->\n]];\n" % (float(packet['latitude']), float(packet['longitude']), repr(packet['raw']))

        # Write it
        try:
            f.write(outStr)

        except:
            outStr = "Could not write log file, check it.\n"
            logging.debug(outStr)

        # Close it
        f.close()

        logging.debug(outStr)
    else:
        # Record what we ignored
        f = open("aprsignored.txt", "a")
        outStr = "Ignoring: "+repr(packet['raw'])+"\n"
        try:
            f.write(outStr)
        except:
            logging.debug("Could not write 'ignored' file, check it.\n")

        f.close()

# Prepare the APRS connection
aprs = aprslib.IS(parser.get('aprs', 'callsign'),
                  parser.get('aprs', 'password'),
                  parser.get('aprs', 'host'),
                  parser.get('aprs', 'port'))

# Listen for specific packet
aprs.set_filter(parser.get('aprs', 'filter'))

# Open the APRS connection to the server
aprs.connect()

# Set a callback for when a packet is received
aprs.consumer(callback)
