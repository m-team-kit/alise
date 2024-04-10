#!/usr/bin/python3
import sys

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus

if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        print(quote_plus(arg))
else:
    data = sys.stdin.readlines()
    dat = ""
    for line in data:
        dat += line
    print(quote_plus(str(dat)))
