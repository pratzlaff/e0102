import argparse
import astropy.io.fits
import matplotlib.pyplot as plt
import os
import numpy as np
import sys

def get_evtfile(args):
    obsid = f'{args.obsid:05d}'
    return get_datadir() + f'/{obsid}/repro/acisf{obsid}_repro_evt2.fits'

def get_evtfile_shifted(args):
    obsid = f'{args.obsid:05d}'
    return get_datadir() + f'/fits/{os.environ["CONTAMID"]}/{obsid}/{obsid}_evt2_energy_shift.fits'

def gainfit_energies(args):
    obsid, slope, offset = read_gainfits()
    i = np.where(obsid == args.obsid)[0][0]
    energies = np.array((1.3522, 1.0217, 0.9221, 0.6536, 0.5739))
    return energies * slope[i] + offset[i]

def energy_shifts(args):
    gf_energies = gainfit_energies(args)
    energies = np.array((1.3522, 1.0217, 0.9221, 0.6536, 0.5739))
    print(gf_energies)
    lf = read_linefits()
    obsid = lf[0]
    i = np.where(obsid == args.obsid)[0][0]
    if (len(lf) == 31):
        es_x = np.array((lf[16][i], lf[19][i], lf[22][i], lf[25][i], lf[28][i]))
        es_x = energies
        es_y = np.array((
            1.3522-lf[16][i],
            1.02170-lf[19][i],
            0.9221-lf[22][i],
            0.6536-lf[25][i],
            0.5739-lf[28][i]
        ))
    else:
        gf_energies = gf_energies[1:]
        energies = energies[1:]
        es_x = np.array((lf[14][i], lf[17][i], lf[20][i], lf[23][i]))
        es_x = energies
        es_y = np.array((
            1.02170-lf[14][i],
            0.9221-lf[17][i],
            0.6536-lf[20][i],
            0.5739-lf[23][i]
        ))
    
    mask = np.isnan(es_y)
    es_y[mask] = energies[mask] - gf_energies[mask]
    return es_x*1000, es_y*1000, mask
    
def read_gainfits():
    obsid, slope, offset = np.loadtxt(get_gainfits(), unpack=True, usecols=(0, -4, -2))
    return obsid, slope, offset

def read_linefits():
    return np.loadtxt(get_linefits(), unpack=True)

def get_datadir():
    srcdir=os.path.dirname(__file__)
    return os.popen(srcdir+'/datadir').read()

def get_gainfits():
    return get_datadir() + f'/fits/{os.environ["CONTAMID"]}/results/gainfits_{os.environ["DET"].lower()}.txt'

def get_linefits():
    return get_datadir() + f'/fits/{os.environ["CONTAMID"]}/results/linefits_{os.environ["DET"].lower()}.txt'

def read_energy(evtfile):
    with astropy.io.fits.open(evtfile) as hdulist:
        hdu = hdulist['events']
        obsid = hdu.header['obs_id']
        energy = hdu.data['energy']
        
        return obsid, energy

def plot_energy_shift(args):
    
    evt = get_evtfile(args)
    evt_shifted = get_evtfile_shifted(args)

    es_x, es_y, gain_mask = energy_shifts(args)

    obsid, energy = read_energy(evt)
    obsid, energy_shifted = read_energy(evt_shifted)

    ii = (energy_shifted>args.emin) & (energy_shifted<args.emax)
    energy = energy[ii]
    energy_shifted = energy_shifted[ii]

    x = energy_shifted
    y = energy_shifted-energy
    plt.scatter(x, y, s=0.1, linewidths=0)
    plt.plot(es_x, es_y, 'ok', label='Line fits')
    if np.sum(gain_mask):
        plt.plot(es_x[gain_mask], es_y[gain_mask], 'or', label='Gain fits')
    title = args.title
    if not title:
        contamid = os.environ.get('CONTAMID', None)
        title = f'ObsID {int(obsid):05d}'
        if contamid is not None:
            title += f': {contamid}'
    plt.title(title)
    plt.xlabel('Energy (eV)')
    plt.ylabel('Energy Shift (eV)')
    plt.legend(frameon=False)
    plt.tight_layout()
    if args.outfile:
        plt.savefig(args.outfile)
    else:
        plt.show()
        
def main():
    parser = argparse.ArgumentParser(
        description='Plot energy shift.'
    )
    parser.add_argument('-o', '--outfile', help='Output file.')
    parser.add_argument('--emin', default=350.)
    parser.add_argument('--emax', default=1600.)
    parser.add_argument('--title', help='Plot title')
    parser.add_argument('obsid', type=int)
    args = parser.parse_args()

    plot_energy_shift(args)

if __name__ == '__main__':
    main()
