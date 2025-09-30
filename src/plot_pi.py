import argparse
import astropy.io.fits
import matplotlib.pyplot as plt
import numpy as np

def read_pi(pifile):
    with astropy.io.fits.open(pifile) as hdulist:
        data = hdulist['spectrum'].data
        hdr = hdulist['spectrum'].header
        return data['pi'], data['count_rate'], hdr['exposure']

def plot_pi(args):
    fig, ax = plt.subplots(figsize=(11, 8.5))
    for pifile in args.pifiles:
        pi, rate, exposure = read_pi(pifile)
        rate_err=np.sqrt(rate/exposure)
        if args.xleft:
            ii = pi >= args.xleft
            pi = pi[ii]
            rate = rate[ii]
            rate_err = rate_err[ii]
        if args.xright:
            ii = pi <= args.xright
            pi = pi[ii]
            rate = rate[ii]
            rate_err = rate_err[ii]
        fmt = '.-'
        plt.errorbar(pi, rate, yerr=rate_err, fmt=fmt, label=pifile)
    plt.xlabel('PI')
    plt.ylabel('Rate')
    plt.legend(loc='lower left')
    plt.tight_layout()

    if args.outfile:
        plt.savefig(args.outfile)
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Plot PI files.'
    )
    parser.add_argument('-o', '--outfile', help='Output graphics file.')
    parser.add_argument('--xleft', type=float, help='Left X limit')
    parser.add_argument('--xright', type=float, help='Right X limit')
    parser.add_argument('pifiles', nargs='+')
    args = parser.parse_args()

    plot_pi(args)

if __name__ == '__main__':
    main()
