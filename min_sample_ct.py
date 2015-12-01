#!/usr/bin/env python
"""Filters table for minimum row instances.

Usage:
    min_sample_ct.py (-t TABLE) (-n NUMBER)

Options:
    -h, --help
    -t TABLE         table name
    -o NUMBER        min number samples needed
"""
from docopt import docopt

args = docopt(__doc__)
tbl = open(args['-t'], 'r')
min_ct = int(args['-n'])

head = next(tbl)
print head

for line in tbl:
    line = line.rstrip('\n')
    data = line.split('\t')
    ct = 0
    for i in xrange(1, len(data), 1):
        if float(data[i]) > 0:
            ct += 1
    if ct >= min_ct:
        print line
tbl.close()
