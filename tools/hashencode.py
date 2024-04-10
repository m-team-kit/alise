#!/usr/bin/python3
import sys
import hashlib

hash_method="sha1"
hash_function = getattr(hashlib, hash_method)()


if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        hash_function.update(arg.encode())
        hash = hash_function.hexdigest()
        print(hash)
else:
    data = sys.stdin.readlines()
    dat = ""
    for line in data:
        dat += line
    hash_function.update(str(dat).encode())
    hash = hash_function.hexdigest()
    print(hash)
