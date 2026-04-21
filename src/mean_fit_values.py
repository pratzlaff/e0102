import argparse
import numpy as np
import os
import re

def get_datadir():
    srcdir=os.path.dirname(__file__)
    return os.popen(srcdir+'/datadir').read()

def read_obsinfo():
    obsid, date = np.loadtxt(get_datadir() + '/obs_info/all.txt', unpack=True, usecols=(0,1))
    return obsid, date

def read_shiftfits(shiftfits):
    col_names = (
        'obsid',
        'cons', 'conslo', 'conshi',
        'Mg11', 'Mg11lo', 'Mg11hi',
        'Ne10', 'Ne10lo', 'Ne10hi',
        'Ne9', 'Ne9lo', 'Ne9hi',
        'O8', 'O8lo', 'O8hi',
        'O7', 'O7lo', 'O7hi',
    )
    col_ind = (0,1,2,3,4,6,7,8,10,11,12,14,15,16,18,19,20,22,23)
    data = np.loadtxt(shiftfits, unpack=True, usecols=col_ind)
    data = { n:d for n, d in zip(col_names, data) }
    for k in 'O7', 'O7lo', 'O7hi':
        data[k] /= 2.09009
    return data

def mean_fit_values(args):
    data = read_shiftfits(args.shiftfits)
    obsid, date = read_obsinfo()
    dates = { o:d for o,d in zip(obsid, date) }
    ii = []
    for i, o in enumerate(data['obsid']):
        d = dates.get(o, 3000)
        if d>=args.ymin and d<=args.ymax:
            ii.append(i)
    means = []
    output = ('cons', 'conslo', 'conshi',
              'O7', 'O7lo', 'O7hi',
              'O8', 'O8lo', 'O8hi',
              'Ne9', 'Ne9lo', 'Ne9hi',
              'Ne10', 'Ne10lo', 'Ne10hi',
              'Mg11', 'Mg11lo', 'Mg11hi',
              )
    for key in output:
        means.append(data[key][ii].mean())
        if not re.match('^cons', key):
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
