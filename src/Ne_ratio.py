import argparse
import numpy as np
import os

from E0102 import obsinfo_file, read_obsinfo
from E0102 import read_shiftfits

def Ne_ratio(args):
    obsid1, data = read_shiftfits(args.shiftfits)
    ne9 = data['Ne9']['val']
    ne10 = data['Ne10']['val']
    obsid2, date, _, _ = read_obsinfo(obsinfo_file('all'))
    dates = { obsid2[i]:date[i] for i in range(len(date)) }
    ii = np.array([i for i in range(len(obsid1)) if dates.get(obsid1[i], 3000) < 2011])

    ne9 = ne9[ii]
    ne10 = ne10[ii]
    if args.sum:
        print(ne9.sum()/ne10.sum())
    else:
        print((ne9/ne10).mean())
    return 

def main():
    parser = argparse.ArgumentParser(
        description='Calculate ratio of Ne IX and X normalizations.'
    )
    parser.add_argument('-s', '--sum', action='store_true', help='Sum normalizations before taking ratio.')
    parser.add_argument('shiftfits', help='Energy shift fit results file.')
    args = parser.parse_args()

    Ne_ratio(args)

if __name__ == '__main__':
    main()
