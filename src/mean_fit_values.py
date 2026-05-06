import argparse
import numpy as np
import os
import re

from E0102 import obsinfo_file, read_obsinfo
from E0102 import shiftfits_file, read_shiftfits

def get_datadir():
    srcdir=os.path.dirname(__file__)
    return os.popen(srcdir+'/datadir').read()

def mean_fit_values(args):

    obsid, data = read_shiftfits(args.shiftfits)
    for k in 'val', 'lo', 'hi':
        data['O7'][k] /= 2.09009

    obsid2, date, _, _ = read_obsinfo(obsinfo_file('all'))
    dates = { o:d for o,d in zip(obsid2, date) }
    ii = []
    for i, o in enumerate(obsid):
        d = dates.get(o, 3000) # excludes simul results
        if d>=args.ymin and d<=args.ymax:
            ii.append(i)
    means = []
    for k1 in 'cons', 'O7', 'O8', 'Ne9', 'Ne10', 'Mg11':
        for k2 in 'val', 'lo', 'hi':
            means.append(data[k1][k2][ii].mean())
            if not re.match('^cons', k1):
                means[-1] *= 1e3
    means = [ f'{mean:.3f}' for mean in means]
    print('\t'.join(means))

def main():
    parser = argparse.ArgumentParser(
        description='Calculate means of fitted values in a given time period.',
    )
    parser.add_argument('shiftfits', help='Energy shift fit results file.')
    parser.add_argument('ymin', type=float, help='Minimum year.')
    parser.add_argument('ymax', type=float, help='Maximum year.')
    args = parser.parse_args()

    mean_fit_values(args)

if __name__ == '__main__':
    main()
