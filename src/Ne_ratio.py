import argparse
import numpy as np
import os

def get_datadir():
    srcdir=os.path.dirname(__file__)
    return os.popen(srcdir+'/datadir').read()

def read_obsinfo():
    obsid, date = np.loadtxt(get_datadir() + '/obs_info/all.txt', unpack=True, usecols=(0,1))
    return obsid, date

def read_shiftfits(shiftfits):
    obsid, ne10, ne10lo, ne10hi, ne9, ne9lo, ne9hi = np.loadtxt(shiftfits, unpack=True, usecols=(0,8,10,11,12,14,15))
    return obsid, ne9, ne10

def Ne_ratio(args):

    obsid1, ne9, ne10 = read_shiftfits(args.shiftfits)
    obsid2, date = read_obsinfo()
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
