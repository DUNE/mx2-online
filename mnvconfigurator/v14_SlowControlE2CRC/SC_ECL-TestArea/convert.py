import codecs
import sys
import os
import binascii
import base64

filepath = "/work/conditions/next_run_subrun.db"
database = open(filepath, "r")

contentfile = database.read()

database.close()

#content=codecs.decode(contentfile, "ascii")

#print content
converttry = binascii.b2a_base64(contentfile)
translate = base64.b64decode(converttry)
#ascii_string = str(base64.b64decode(converttry))
#print ascii_string

#unicodelet = codecs.decode(converttry, "utf-8")
#contentconvert = bytearray.fromhex(unicodelet.decode())
print translate
#databasetemp = open("temptext", "w")

#translate = codecs.decode(contentconvert, "ascii")

#content = codecs.decode(translate, "hex")
#print contentconvert

#databasetemp.write(contentconvert)
#print translate
#databasetemp.close()
