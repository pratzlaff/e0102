import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
from scipy import interpolate

srcdir=os.path.dirname(__file__)
datadir=os.popen(srcdir+'/datadir').read()
gainfits=f'{datadir}/fits/{os.environ["CONTAMID"]}/results/gainfits_{os.environ["DET"].lower()}.txt'
linefits=f'{datadir}/fits/{os.environ["CONTAMID"]}/results/linefits_{os.environ["DET"].lower()}.txt'

def read_linefits():
    global linefits
    obsids, mg11, mg11lo, mg11hi, ne10, ne10lo, ne10hi, ne9, ne9lo, ne9hi, o8, o8lo, o8hi, o7, o7lo, o7hi = np.loadtxt(linefits, usecols=[0,]+list(range(16,16+15)), unpack=True)
    en = { 'O7':o7, 'O8':o8, 'Ne9':ne9, 'Ne10':ne10, 'Mg11':mg11 }
    lo = { 'O7':o7lo, 'O8':o8lo, 'Ne9':ne9lo, 'Ne10':ne10lo, 'Mg11':mg11lo }
    hi = { 'O7':o7hi, 'O8':o8hi, 'Ne9':ne9hi, 'Ne10':ne10hi, 'Mg11':mg11hi }
    return obsids, en, lo, hi

def read_gainfits():
    global gainfits
    obsids, slope, offset = np.loadtxt(gainfits, usecols=(0,-4,-2), unpack=True)
    return obsids, slope, offset

def plot_gain_corrections(args):
    global gainfits, linefits
    en = { 'O7':0.573900,
           'O8':0.653600,
           'Ne9':0.922100,
           'Ne10':1.02170,
           'Mg11':1.3522
          }
    obsids1, en_new, lo, hi = read_linefits()
    obsids2, slope, offset = read_gainfits()
    if (np.sum(obsids1 != obsids2)):
        raise RuntimeError(f"obsids don't match in '{linefits}' and '{gainfits}'")

    lines = [ 'O7', 'O8', 'Ne9', 'Ne10', 'Mg11' ]
    spline_en = np.array([0.001] + [ en[l] for l in lines ] + [1.6, 2.0])*1000
    en = np.array([ en[l] for l in lines ])

    pdffile = f'{datadir}/fits/{os.environ["CONTAMID"]}/results/gain_corrections_{os.environ["DET"].lower()}.pdf'
    pdf_gc = PdfPages(pdffile)

    pdffile = f'{datadir}/fits/{os.environ["CONTAMID"]}/results/spline_test_{os.environ["DET"].lower()}.pdf'
    pdf_st = PdfPages(pdffile)

    obsids = obsids1.astype(int)

    for i, obsid in enumerate(obsids):
        new = np.array([ en_new[l][i] for l in lines ])
        lo_ = np.array([ lo[l][i] for l in lines ])
        hi_ = np.array([ hi[l][i] for l in lines ])
        gf = en * slope[i] + offset[i]

        fig, ax = plt.subplots()

        ax.plot(en, gf-en, 'bo', linestyle='dashed', label='Linear correction (gainfit)')
        ax.plot(en, new-en, 'ro-', label='Best-fit non-linear correction')
        ax.plot(en, lo_-en, color='r', linestyle='dotted', label='1-σ uncertainty')
        ax.plot(en, hi_-en, color='r', linestyle='dotted')
        ax.set_title(f'Cor. for obsid {obsid}, {os.environ["CONTAMID"]}')
        ax.set_xlabel('Energy (keV)')
        ax.set_ylabel('ΔE (Measured - Theoretical; keV)')
        ax.legend(frameon=False, loc='lower left')
        ax.set_xlim(0.5, 1.5)
        ax.set_ylim(-.04, .04)
        plt.tight_layout()

        pdffile=f'{datadir}/fits/{os.environ["CONTAMID"]}/{obsid:05d}/{obsid:05d}_gain_corrections.pdf'
        plt.savefig(pdffile)

        pdf_gc.savefig(fig)

        plt.close()

        spline_new = np.array([0.001] + [ en_new[l][i] for l in lines ] + [1.1, 1.5])*1000
        x = np.arange(1500.)
        tck = interpolate.splrep(spline_new, spline_en)
        shift = interpolate.splev(x, tck)

        fig, ax = plt.subplots()
        ax.plot(x, shift, 'k-')
        ax.set_title(f'ObsID {obsid:05d}')
        plt.tight_layout()
        
        pdffile=f'{datadir}/fits/{os.environ["CONTAMID"]}/{obsid:05d}/{obsid:05d}_spline_test.pdf'
        plt.savefig(pdffile)

        pdf_st.savefig(fig)

        plt.close()

    pdf_gc.close()
    pdf_st.close()

def main():
    parser = argparse.ArgumentParser(
        description='Plot gain fit corrections.'
    )
    args = parser.parse_args()

    plot_gain_corrections(args)

if __name__ == '__main__':
    main()
