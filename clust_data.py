#!/usr/bin/env python
"""Clustermap generator.

Usage: 
    clust_data.py (-t TABLE) (-o OUTPUT) [-l LOGNORM] [-z ZERO] [-c CMAP] [-d DESCRIPTIVE]

Options:
    -h, --help
    -t TABLE         table name
    -o OUTPUT        output file name
    -l LOGNORM       set id data is to be log transformed
    -z ZERO          zero value to use when log transforming
    -c CMAP          hex colormap to import, otherwise default used
    -d DESCRIPTIVE   add second table with descriptive data to create
                     separate heatmaps clustered based on data. Ids should be in rows,
                     with header for each row in first column
"""
import math
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from docopt import docopt
from matplotlib.colors import LinearSegmentedColormap
from pandas import DataFrame
import pdb

args = docopt(__doc__)
tbl = open(args['-t'], 'r')
out = args['-o']
center = 'weighted'
cluster = 'euclidean'


(norm, zero) = (None, None)
if '-l' in args:
    norm, zero = (args['-l'], args['-z'])
minval = 0.00001


def transform(mat, norm, zero):
    norm = float(norm)
    zero = float(zero)
    for i in xrange(0, len(mat), 1):
        for j in xrange(0, len(mat[i]), 1):
            if mat[i][j] < minval:
                mat[i][j] = zero
            else:
                mat[i][j] = math.log(mat[i][j], norm)
    mval = np.amin(mat)
    sys.stderr.write('Min value was ' + str(mval) + '\n')
    return mat


def isint(x):
    try:
        a = float(x)
        int(a)
    except ValueError:
        return False
    else:
        return True


def annotate(ann, ccols, ocols, clust, c):
    to_add = open(ann, 'r')
    head = next(to_add)
    head = head.rstrip('\n')
    bids = head.split('\t')
    # SHOULD HAVE ROW HEADERS
    Cols = bids[1:]
    maps = ('Reds', 'Reds', 'Greys', 'Greens')
    k = 0
    annot = []
    for line in to_add:
        line = line.rstrip('\n')
        data = line.split('\t')
        to_map = data[1:]
        rmap = []
        newCols = []
        # reorg data to match cluster

        for i in ccols:
            rmap.append(to_map[Cols.index(ocols[i])])
            newCols.append(ocols[i])
        rmap = np.asarray(rmap)
        Rows = []
        Rows.append(data[0])
        # flag if qualitative
        q = 0
        if isint(rmap[0]):
            rmap = rmap.astype(np.float)
        else:
            q = 1
            qdict = {}
            j = 0
            for i in xrange(0, len(rmap), 1):
                if rmap[i] not in qdict:
                    qdict[rmap[i]] = j
                    sys.stderr.write(str(j) + ' ' + rmap[i] + '\n')
                    j += 1
                rmap[i] = qdict[rmap[i]]
            rmap = rmap.astype(np.float)
        df = DataFrame(rmap, index=ocols, columns=Rows)

        df = df.transpose()
        new, cur = plt.subplots()
        cur = sns.heatmap(df, cmap=maps[k], rasterized=True)

        new.set_figheight(2)
        new.set_figwidth(c)
        new.set_dpi(600)
        cur.set_xticklabels(newCols, rotation=90)
        new.savefig('test' + str(k) + '.pdf')
        annot.append(new)
        k += 1
    return annot

head = next(tbl)
head = head.rstrip('\n')
bids = head.split('\t')
Cols = bids[1:]
Rows = []
init = next(tbl)
init = init.rstrip('\n')
ini = init.split('\t')
# populate numpy array with data
data = np.array(ini[1:])
Rows.append(ini[0])
sys.stderr.write('Initializing values\n')
k = 1
for line in tbl:
    line = line.rstrip('\n')
    datum = line.split('\t')
    Rows.append(datum[0])
    try:
        data = np.vstack([data, datum[1:]])
    except:
        sys.stderr.write('Failed at line ' + str(k) + '\n' + line + '\n')
        exit(1)
    k += 1
data = data.astype(np.float)
# check if optional log transform value set.  must give min to replace 0
# , will output lowest value in case supplied min is too small
try:
    if norm != None:
        sys.stderr.write('Log transforming values\n')
        data = transform(data, norm, zero)
except NameError:
    sys.stderr.write('No log transform requested, moving along\n')
# create pandas dataframe for clustering
df = DataFrame(data, index=Rows, columns=Cols)
#mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['font.size'] = '8'
sys.stderr.write('Clustering and drawing figures\n')
# set shape so that text labels are readable
(r, c) = data.shape
if r > 36:
    r = math.ceil(r / 6)
if r > 1000:
    r = math.ceil(r / 10)
#if c > 6:
#    c = math.ceil(c / 6)

sys.stderr.write('Dimensions set as width ' + str(c) + ' height ' + str(r) + '\n')
# if custom colormap supplied, use it
if args['-c'] != None:
    ccmap = []
    cval = open(args['-c'], 'r')

    for val in cval:
        val = val.rstrip('\n')
        cols = val.split('\t')
        cols = map(float, cols)
        ccmap.append(cols)

    usermap = mpl.colors.ListedColormap(ccmap)
    res = sns.clustermap(df, method=center, cmap=usermap, metric=cluster, figsize=(c, r), rasterized=True)
else:
    res = sns.clustermap(df, method=center, cmap='Purples', metric=cluster, figsize=(c, r), rasterized=True)
ax = res.ax_heatmap
xaxis = []
for ind in res.dendrogram_col.reordered_ind:
    xaxis.append(Cols[ind])
ax.set_xticklabels(xaxis, rotation=90)
yaxis = []
for ind in res.dendrogram_row.reordered_ind:
    yaxis.append(Rows[ind])
yaxis.reverse()
ax.set_yticklabels(yaxis, rotation=0)

# plt.show(res)
# create second table for annotation - for now will be drawn as a second table to concatenate in post
if args['-d'] != None:
    sys.stderr.write('Annotation table given, creating descriptive heatmaps based on clustering\n')
    an_maps = annotate(args['-d'], res.dendrogram_col.reordered_ind, df.columns, res, c)
res.savefig(out)

sys.stderr.write('Fin\n')
