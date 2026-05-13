import argparse
import numpy as np
import re
import sys

from E0102 import chipy_region

def read_fits(fitsfile):
    for line in open(fitsfile):
        if m := re.match(r'^#(ObsID.*)$', line):
            cols = m.groups()[0].split('\t')[:-4]
            continue
    d = np.loadtxt(fitsfile, usecols=list(range(len(cols))), unpack=True)
    return cols, d


def chipy_region_filter(args):
    cols, d = read_fits(args.fitsfile)
    print('#'+'\t'.join(cols))
    for i in range(d[0].size):
        if chipy_region(int(d[0,i])) == args.region:
            line = f'{int(d[0,i]):05d}'
            for j in range(int((len(d)-1)/4)):
                line += f'\t{d[j*4+1,i]:8.3e}\t{d[j*4+2,i]:6.1e}\t{d[j*4+3,i]:8.3e}\t{d[j*4+4,i]:8.3e}'
            print(line)
def main():
    parser = argparse.ArgumentParser(
        description='Filter fit results on CHIPY region.'
    )
    parser.add_argument('fitsfile')
    parser.add_argument('region', choices=('Low','Mid','High'))
    args = parser.parse_args()

    chipy_region_filter(args)

if __name__ == '__main__':
    main()
