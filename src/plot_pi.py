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
    fig, ax = plt.subplots()
    for pifile in args.pifiles:
        pi, rate, exposure = read_pi(pifile)
        rate_err=np.sqrt(rate/exposure)
        plt.errorbar(pi, rate, yerr=rate_err, fmt='.', label=pifile)
    plt.legend()
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
    parser.add_argument('pifiles', nargs='+')
    args = parser.parse_args()

    plot_pi(args)

if __name__ == '__main__':
    main()
