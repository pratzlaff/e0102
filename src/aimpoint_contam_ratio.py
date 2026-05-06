import argparse
import numpy as np
import os
import sys

from E0102 import obsinfo_file, read_obsinfo
from E0102 import contamfits_file, read_contamfits
from E0102 import chipy_region, detector

def best_fit_contam_ratio(args):

    det = detector(args.obsid)

    aimreg = { 'i3':'High',
               's3':'Mid',
              }
    if (chipy_region(args.obsid) == aimreg[det]):
        sys.exit(0)

    obsid, date, chy, node = read_obsinfo(obsinfo_file(det))

    old = None
    try:
        old = os.environ['CONTAMID']
    except:
        pass
    os.environ['CONTAMID'] = 'ciao4.18.0_caldb4.12.3_contamfit_all'
    obsid2, data = read_contamfits(contamfits_file(det))
    if old is not None:
        os.environ['CONTAMID'] = old

    date_dict = { d:o for d,o in zip(obsid, date) }

    # aimpoint CHIPY regions
    ylim = { 's3':[341,341+341],
             'i3':[342*2, 1024]
            }.get(det)

    keys = { 'O/C':'OtoC',
             'F/C':'FtoC',
            }
    ratio = data[keys[args.ratio]]['val']

    # special cases of simultaneous fits
    simul = {
              # 2022 split observations, S3
              26988 : 26987,
              27760 : 26987,
              89999 : 26987,

              26989 : 26987,
              27761 : 26987,
              89998 : 26987,


              # 2022 split observations, I3
              25622 : 25617,
              26359 : 25617,
              99999 : 25617,

              25621 : 25617,
              26358 : 25617,
              99998 : 25617,

              # 2023 split observations, I3
              26986 : 99997,
              27745 : 99997,
              99997 : 99997,

              26990 : 99997,
              27762 : 99997,
              99996 : 99997,

              26991 : 99997,
              27773 : 99997,
              99995 : 99997,
             }
    if args.obsid in simul:
        ii, = np.where(obsid2==simul[args.obsid])
        sys.stderr.write(f'{args.obsid} (simul): using {obsid2[ii[0]]} value\n')
        print(ratio[ii[0]])
        sys.exit(0)

    # determine which ObsIDs were taken in the same year
    ii, = np.where(
        (date.astype(int) == int(date_dict[args.obsid])) &
        (chy>=ylim[0]) & (chy<=ylim[1])
    )
    sys.stderr.write(f'{args.obsid}: found {ii.size} match\n')
    if ii.size:
        sum = 0
        for o in obsid[ii]:
            jj, = np.where(obsid2 == o)
            assert(jj.size==1)
            sum += ratio[jj[0]]
        print(sum/ii.size)
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description='Given an obsid, find the best fit O/C or F/C at the aimpoint for that round of E0102 observations.'
    )
    parser.add_argument('obsid', type=int)
    parser.add_argument('ratio', choices=('O/C','F/C'))
    args = parser.parse_args()

    best_fit_contam_ratio(args)

if __name__ == '__main__':
    main()
