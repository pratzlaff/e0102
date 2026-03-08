import argparse
import astropy.io.fits
import glob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
from scipy import interpolate
import sys

srcdir=os.path.dirname(__file__)
datadir=os.popen(srcdir+'/datadir').read()
gainfits=f'{datadir}/fits/{os.environ["CONTAMID"]}/results/gainfits_{os.environ["DET"].lower()}.txt'
linefits=f'{datadir}/fits/{os.environ["CONTAMID"]}/results/linefits_{os.environ["DET"].lower()}.txt'
obsinfo=f'{datadir}/obs_info/{os.environ["DET"].lower()}.txt'

def get_mtl_file(obsid):
    obsid = f'{int(obsid):05d}'
    return glob.glob(f'{datadir}/{obsid}/repro/acisf{obsid}_*_mtl1.fits')[0]

def read_mtl_file(mtl):
    with astropy.io.fits.open(mtl) as hdulist:
        data = hdulist[1].data
        return data['time'], data['fp_temp']

def make_gain_correction_plot(obsid, en, gf, new, lo, hi, position):
    colors = { 'Low':'b',
               'Mid':'r',
               'High':'#39FF14'
              }
    fig, ax = plt.subplots()
    ax.plot(en, gf-en, 'bo', linestyle='dashed', label='Linear correction (gainfit)')
    ax.plot(en, new-en, 'ro-', label='Best-fit non-linear correction')
    ax.plot(en, lo-en, color='r', linestyle='dotted', label='1-σ uncertainty')
    ax.plot(en, hi-en, color='r', linestyle='dotted')
    ax.set_title(f'Cor. for obsid {obsid}, {os.environ["CONTAMID"]}')
    ax.set_xlabel('Energy (keV)')
    ax.set_ylabel('ΔE (Measured - Theoretical; keV)')
    ax.legend(frameon=False, loc='lower left')
    ax.set_xlim(0.5, 1.5)
    ax.set_ylim(-.04, .04)
    ax.text(0.05, 0.85, position+' ChipY', transform=plt.gca().transAxes, fontsize=18, color=colors[position])
    plt.tight_layout()
    return fig

def make_fp_temp_plot(obsid):
    mtl = get_mtl_file(obsid)
    time, fp_temp = read_mtl_file(mtl)
    fig, ax = plt.subplots()
    ax.scatter((time-time[0])/1e3, fp_temp-273.15, s=1)
    ax.set_title(f'ObsID: {int(obsid):05d}')
    ax.set_xlabel('Time since observation start [ks]')
    ax.set_ylabel('FP_TEMP [C]')
    plt.tight_layout()
    return fig

def make_spline_test_plot(obsid, spline_new, spline_en):
    x = np.arange(1250)+350
    x = np.arange(1500)
    if False:
        # B-spline
        shift = interpolate.make_splrep(spline_new, spline_en)(x)
    else:
        shift = interpolate.CubicSpline(spline_new, spline_en, bc_type='natural')(x)

    fig, ax = plt.subplots()
    ax.plot(x, shift, 'k-')
    ax.set_title(f'ObsID {obsid:05d}')
    plt.tight_layout()
    return fig
        
def get_positions():
    global obsinfo
    obsid, chipy = np.loadtxt(obsinfo, unpack=True, usecols=(0,3))
    obsid = obsid.astype(int).tolist()
    chipy = chipy.tolist()

    pos = { }
    for o, c in zip(obsid, chipy):
        if c < 1/3*1024:
            pos[o] = 'Low'
        elif c < 2/3*1024:
            pos[o] = 'Mid'
        else:
            pos[o] = 'High'
    return pos

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

def plot_various(args):
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

    if args.obsids is None:
        pdffile = f'{datadir}/fits/{os.environ["CONTAMID"]}/results/gain_corrections_{os.environ["DET"].lower()}.pdf'
        pdf_gc = PdfPages(pdffile)

        pdffile = f'{datadir}/fits/{os.environ["CONTAMID"]}/results/spline_test_{os.environ["DET"].lower()}.pdf'
        pdf_st = PdfPages(pdffile)

        pdffile = f'{datadir}/fits/{os.environ["CONTAMID"]}/results/fp_temp_{os.environ["DET"].lower()}.pdf'
        pdf_fptemp = PdfPages(pdffile)

    obsids = obsids1.astype(int)

    positions = get_positions()

    for i, obsid in enumerate(obsids):
        if args.obsids is not None and obsid not in args.obsids:
            continue
        new = np.array([ en_new[l][i] for l in lines ])
        lo_ = np.array([ lo[l][i] for l in lines ])
        hi_ = np.array([ hi[l][i] for l in lines ])
        gf = en * slope[i] + offset[i]

        fig = make_gain_correction_plot(obsid, en, gf, new, lo_, hi_, positions[obsid])
        pdffile=f'{datadir}/fits/{os.environ["CONTAMID"]}/{obsid:05d}/{obsid:05d}_gain_corrections.pdf'
        plt.savefig(pdffile)
        if args.obsids is None:
            pdf_gc.savefig(fig)
        plt.close()

        spline_new = np.array([0.001] + [ en_new[l][i] for l in lines ] + [1.6, 2.0])*1000
        ii, = np.where(np.isnan(spline_new))
        spline_new[ii] = gf[ii-1]*1e3

        fig = make_spline_test_plot(obsid, spline_new, spline_en)
        pdffile=f'{datadir}/fits/{os.environ["CONTAMID"]}/{obsid:05d}/{obsid:05d}_spline_test.pdf'
        plt.savefig(pdffile)
        if args.obsids is None:
            pdf_st.savefig(fig)
        plt.close()

        fig = make_fp_temp_plot(obsid)
        pdffile=f'{datadir}/fits/{os.environ["CONTAMID"]}/{obsid:05d}/{obsid:05d}_fp_temp.pdf'
        plt.savefig(pdffile)
        if args.obsids is None:
            pdf_fptemp.savefig(fig)
        plt.close()

    if args.obsids is None:
        pdf_gc.close()
        pdf_st.close()
        pdf_fptemp.close()

def main():
    parser = argparse.ArgumentParser(description='Plot gain corrections, splines, fp_temp.')
    parser.add_argument('--obsids', nargs='+', type=int)
    args = parser.parse_args()

    plot_various(args)

if __name__ == '__main__':
    main()
