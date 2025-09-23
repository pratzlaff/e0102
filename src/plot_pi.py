import argparse
import astropy.io.fits
import matplotlib.pyplot as plt

def read_pi(pifile):
    with astropy.io.fits.open(pifile) as hdulist:
        data = hdulist['spectrum'].data
        return data['pi'], data['count_rate']

def plot_pi(args):
    fig, ax = plt.subplots()
    for pifile in args.pifiles:
        pi, rate = read_pi(pifile)
        plt.plot(pi, rate, label=pifile)
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
