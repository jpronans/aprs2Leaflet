#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
import time
import aprslib
import logging
import os
#import utf8

parser = SafeConfigParser()
parser.read('config.ini')
if parser.get('logging', 'level') == "debug":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def callback(packet):
    ignorePacket = 1

    # Station needs to be moving and not an APRS Droid App. RF Stations only
    if 'latitude' in packet and 'longitude' in packet and 'speed' in packet and packet['to'] != 'APDR13':
        # Packet has the speed attribute, but is it greater than 0?
        if float(packet['speed']) > 0.0:
            ignorePacket = 0; 
            logging.debug("Speed is > 0, record packet") 
            f = open("/var/www/ireland.aprs2.net/aprstations.js","a+")
            #Move the pointer (similar to a cursor in a text editor) to the end of the file. 
            f.seek(0, os.SEEK_END)

            #This code means the following code skips the very last character in the file - 
            #i.e. in the case the last line is null we delete the last line 
            #and the penultimate one
            pos = f.tell() - 1

	    #Read each character in the file one at a time from the penultimate 
	    #character going backwards, searching for a newline character
	    #If we find a new line, exit the search
	    while pos > 0 and f.read(1) != "\n":
		pos -= 1
		f.seek(pos, os.SEEK_SET)

	    #So long as we're not at the start of the file, delete all the characters ahead of this position
	    if pos > 0:
		f.seek(pos, os.SEEK_SET)
		f.truncate()
	        try:
	            outStr = "\n["+str(packet['latitude'])+", "+str(packet['longitude'])+", 1], <!-- "+str(packet['raw'])+" -->\n"
		    f.write(outStr)

	        except:
	            outStr = "Exception in string output, probably UTF8"
	            logging.debug(outStr)
                f.write("];\n")
	        f.close()
	        
                logging.info(outStr)
	        f = open("aprslogged.txt", "a")
	        try:
	            f.write(packet['raw']+"\n")
	        except:
	            logging.debug("Exception in string output, probably UTF8")
	        f.close()

    if (ignorePacket == 1):
        f = open("aprsignored.txt", "a")
	outStr = packet['raw']+"\n"
	try:
	    f.write(outStr)
	except:
	    logging.debug("Exception in string output, probably UTF8")
        f.close()
	#logging.debug(outStr)

# Prepare the APRS connection
aprs = aprslib.IS(parser.get('aprs', 'callsign'),
                  parser.get('aprs', 'password'),
                  parser.get('aprs', 'host'),
                  parser.get('aprs', 'port'))

# Listen for specific packet
aprs.set_filter(parser.get('aprs', 'filter'))

while True:
    # Open the APRS connection to the server
    aprs.connect()

    # Set a callback for when a packet is received
    try:
        aprs.consumer(callback)
    except:
        logging.info("Exception in aprs.consumer, restarting connection to APRS server")


