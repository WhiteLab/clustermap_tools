#!/usr/bin/env python
"""Filters table for minimum row instances.

Usage:
    min_sample_ct.py (-t TABLE) (-n VALUE) (-s SAMPLE)

Options:
    -h, --help
    -t TABLE         table name
    -n NUMBER        min value needed
    -s SAMPLE       min number samples needed
"""
from docopt import docopt

args = docopt(__doc__)
tbl = open(args['-t'], 'r')
min_samp = int(args['-s'])
min_val = int(args['-n'])

head = next(tbl)
head = head.rstrip('\n')
print head

for line in tbl:
    line = line.rstrip('\n')
    data = line.split('\t')
    ct = 0
    for i in xrange(1, len(data), 1):
        if float(data[i]) >= min_val:
            ct += 1
    if ct >= min_samp:
        print line
tbl.close()
