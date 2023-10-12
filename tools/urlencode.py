#!/usr/bin/python3
import sys
try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus
data = sys.stdin.readlines()
dat = ""
for line in data:
    dat += line
print (quote_plus(str(dat)))
