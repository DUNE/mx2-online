from ECLAPI import ECLConnection
import getopt, sys, os
from datetime import datetime

Usage = """
python ecl_list.py [<options>]
Options are:
    -c <category>
    -t <tag>
    -f <form>
    -a "yyyy-mm-dd hh:mm:ss"
    -a <n>days
    -a <n>hours
    -a <n>minutes
    -l <limit>
    -U <url>
"""

if not sys.argv[1:]:
    print(Usage)
    sys.exit(1)

URL = "http://dbweb4.fnal.gov:8080/ECL/demo"
user = "xml"
password = "password"

cat = None
form = None
limit = None
tag = None
after = None

opts, args = getopt.getopt(sys.argv[1:], 'c:f:l:t:a:U:')
for opt, val in opts:
    if opt == '-c': cat = val
    if opt == '-f': form = val
    if opt == '-l': limit = int(val)
    if opt == '-t': tag = val
    if opt == '-a': after = val
    if opt == '-U': URL = val
    
conn = ECLConnection(URL, user, password)
lst = conn.list(category = cat, form=form, limit=limit, tag=tag, after=after)
for i in lst:
    print(i)
