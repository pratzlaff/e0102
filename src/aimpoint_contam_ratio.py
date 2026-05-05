import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from numpy.random import rand
import os
import re
import sys

srcdir=os.path.dirname(__file__)
datadir=os.popen(srcdir+'/datadir').read()
contamfits=f'{datadir}/fits/ciao4.18.0_caldb4.12.3_contamfit_all/results/contamfits_{os.environ["DET"].lower()}.txt'
obsinfo=f'{datadir}/obs_info/{os.environ["DET"].lower()}.txt'

def read_obsinfo(obsinfo):
    obsid, date, chy, node = np.loadtxt(obsinfo, unpack=True, usecols=(0,1,3,4))
    return obsid, date, chy, node

def read_contamfits(contamfits):
    obsid, \
    tauL, tauLlo, tauLhi, \
    OtoC, OtoClo, OtoChi, \
    FtoC, FtoClo, FtoChi, \
    redchi \
    = np.loadtxt(contamfits, unpack=True, usecols=[0,
                                                  1,3,4,
                                                  5,7,8,
                                                  9,11,12,
                                                  -2]
                 )
    data = {'tauL':{'val':tauL, 'lo':tauLlo, 'hi':tauLhi},
            'OtoC':{'val':OtoC, 'lo':OtoClo, 'hi':OtoChi},
            'FtoC':{'val':FtoC, 'lo':FtoClo, 'hi':FtoChi},
            'redchi':{'val':redchi, 'lo':redchi, 'hi':redchi},
            }
    return obsid, data

def best_fit_contam_ratio(args):
    global obsinfo
    obsid, date, chy, node = read_obsinfo(obsinfo)
    obsid2, data = read_contamfits(contamfits)

    date_dict = { d:o for d,o in zip(obsid, date) }

    # aimpoint CHIPY regions
    ylim = { 's3':[341,341+341],
             'i3':[342*2, 1024]
            }.get(os.environ["DET"].lower())

    keys = { 'O/C':'OtoC',
             'F/C':'FtoC',
            }
    ratio = data[keys[args.ratio]]['val']

    # special cases of simultaneous fits
    simul = { 89999. : 26987.,
              89998. : 26987.,
              99999. : 25617.,
              99998. : 25617.,
              99995. : 99997.,
              99996. : 99997.,
              99997. : 99997.,
             }
    if args.obsid in simul:
        ii, = np.where(obsid2==simul[args.obsid])
        print(ratio[ii[0]])
        sys.exit(0)

    # determine which ObsIDs were taken in the same year
    ii, = np.where(
        (date.astype(int) == int(date_dict[args.obsid])) &
        (chy>=ylim[0]) & (chy<=ylim[1])
    )
    if ii.size:
        sum = 0
        for o in obsid[ii]:
            jj, = np.where(obsid2 == o)
            sum += ratio[jj[0]]
        print(sum/ii.size)

def main():
    parser = argparse.ArgumentParser(
        description='Given an obsid, find the best fit O/C or F/C at the aimpoint for that round of E0102 observations.'
    )
    parser.add_argument('obsid', type=float)
    parser.add_argument('ratio', choices=('O/C','F/C'))
    args = parser.parse_args()

    best_fit_contam_ratio(args)

if __name__ == '__main__':
    main()
