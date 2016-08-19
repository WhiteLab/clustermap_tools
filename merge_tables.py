#!/usr/bin/env python
"""Merges tables based on a single column, column denoted array-style. Designed for variant output - will merge gene,
position, and base change as name for row

Usage: ./merge_tables.py (<list> <col> <hflag> <tflag>) [options]

Arguments:
    <list>   list of tables
    <col>    index of column to merge, array style
    <hflag>  1 if tables have header, 0 if not
    <tflag>  1 if showing on-target only

Options:
    -h --help
    -s SUFFIX       if given, will omit from column name.  otherwise file name used as column header
    -a ACCEPT       if given, a list of acceptable effects - i.e. NON_SYNONYMOUS
    -r TN RATIO     if given, can specify min t/n ratio
    -f VAF          if given, can specify minimum variant allele freq
    -c COVERAGE     if given, require min coverage of position before accepting
    -m MIN          if given, min number of samples a variant must be in before accepting
    -t TUMOR        if given, special tumor sample designation to allow for different vaf acceptance criteria
    -v TVAF         used with -t to set separate vaf acceptance for tumor sample

"""
from docopt import docopt
import os
import sys
import pdb

args = docopt(__doc__)
tlist = open(args['<list>'])
col = int(args['<col>'])
hflag = int(args['<hflag>'])
tflag = int(args['<tflag>'])
# setting up possible parameters and column posotions for additional filtering when required
tn = 0.0
tn_col = 11
if '-r' in args and args['-r'] is not None:
    tn = float(args['-r'])
vaf = 0.0
vcol = 10
if '-f' in args and args['-f'] is not None:
    vaf = float(args['-f'])

cov = 0
ncol = 5
tcol = 8
if '-c' in args and args['-c'] is not None:
    cov = int(args['-c'])

sflag = 1
suffix = ''
if '-s' in args and args['-s'] is not None:
    suffix = args['-s']
else:
    sys.stderr.write('No suffix given.  Using file names as headers\n')
    sflag = 0
alist = {}
aflag = 0
if '-a' in args and args['-a'] is not None:
    aflag = 1
    list_h = open(args['-a'], 'r')
    for line in list_h:
        line = line.rstrip('\n')
        alist[line] = 1
# min sample occurance flag
mflag = 0
if '-m' in args and args['-m'] is not None:
    mflag = int(args['-m'])

new_tbl = {}
flist = []
# chr1	2488217	GTTxTGA	C	A	149	0	0.00%	99	5	4.81%	10000.00	NA	TNFRSF14	INTRON	CODING			283	KEEP	ON
temp = {}
vlist = []
# count number of times variant seen
vct = {}
for tbl in tlist:
    sys.stderr.write('Processing table ' + tbl)
    tbl = tbl.rstrip('\n')
    fh = open(tbl, 'r')
    tbl = os.path.basename(tbl)
    if sflag:
        tbl = tbl.replace(suffix, '')
    flist.append(tbl)
    if hflag:
        head = next(fh)
    new_tbl[tbl] = {}
    for line in fh:
        line = line.rstrip('\n')
        if len(line) < 1:
            continue
        data = line.split('\t')
        if tflag and data[-1] == 'OFF':
            continue
        if aflag and data[14] not in alist:
            continue
        if tn > 0 and data[tn_col] < tn:
            continue
        if vaf > 0:
            check = float(data[vcol].rstrip('%'))
            if '-t' in args and args['-t'] is not None and args['-t'] == tbl:
                if check < float(args['-v']):
                    continue
            else:
                if check < vaf:
                    continue
        if cov > 0:
            n_cov = int(data[ncol]) + int(data[(ncol+1)])
            t_cov = int(data[tcol]) + int(data[(tcol+1)])
            if n_cov < cov or t_cov < cov:
                continue
        # pdb.set_trace()
        var = data[3] + '-' + data[4]

        row = '_'.join([data[13], data[0], data[1], var])
        #pdb.set_trace()
        if mflag > 0:
            if row not in vct:
                vct[row] = 1
            else:
                vct[row] += 1
        if row not in temp:
            temp[row] = 1
            vlist.append(row)
        new_tbl[tbl][row] = data[col]
    fh.close()
tlist.close()
flist.sort()
vlist.sort()
sys.stdout.write('Sample/variant' + '\t' + '\t'.join(flist) + '\n')
for variant in vlist:
    if mflag > 0 and vct[variant] < mflag:
        continue
    sys.stdout.write(variant)
    for samp in flist:
        if variant in new_tbl[samp]:
            sys.stdout.write('\t' + new_tbl[samp][variant])
        else:
            sys.stdout.write('\t0')
    sys.stdout.write('\n')
