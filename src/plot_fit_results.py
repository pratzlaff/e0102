# adapted from /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/plot_fit_results.pro

import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
import re
import sys

srcdir=os.path.dirname(__file__)

iachec = {
    'cons':{'val':1, 'lo':0.9, 'hi':1.1},
    'O7':{'val':0.002745},
    'O8':{'val':0.004393},
    'Ne9':{'val':0.001381},
    'Ne10':{'val':0.001378},
    'Mg':{'val':0.000108671},
}
for key in iachec:
    for limit in 'lo', 'hi':
        iachec[key][limit] = iachec[key]['val'] * iachec['cons'][limit]
cons_iachec_2016 = 1.072

def read_obsinfo(obsinfo):
    obsid, date, chy, node = np.loadtxt(obsinfo, unpack=True, usecols=(0,1,3,4))
    return obsid, date, chy, node

def grep_header(expr, shiftfits):
    with open(shiftfits, 'r') as fh:
        for line in fh:
            if not re.match('^#', line):
                return False
            if re.search(expr, line):
                return True

def read_shiftfits(shiftfits):
    obsid, \
    cons, conslo, conshi, \
    ne10, ne10lo, ne10hi, \
    ne9, ne9lo, ne9hi, \
    o8, o8lo, o8hi, \
    o7, o7lo, o7hi, \
    mg, mglo, mghi, \
    redchi \
    = np.loadtxt(shiftfits, unpack=True, usecols=[0,
                                                  1,2,3,
                                                  4,6,7,
                                                  8,10,11,
                                                  12,14,15,
                                                  16,18,19,
                                                  20,22,23,
                                                  -2]
                 )
    data = {'cons':{'val':cons, 'lo':conslo, 'hi':conshi},
            'O7':{'val':o7, 'lo':o7lo, 'hi':o7hi},
            'O8':{'val':o8, 'lo':o8lo, 'hi':o8hi},
            'Ne9':{'val':ne9, 'lo':ne9lo, 'hi':ne9hi},
            'Ne10':{'val':ne10, 'lo':ne10lo, 'hi':ne10hi},
            'Mg':{'val':mg, 'lo':mglo, 'hi':mghi},
            'redchi':{'val':redchi, 'lo':redchi, 'hi':redchi},
            }

    if not grep_header('Mg', shiftfits):
        del data['Mg']

    return obsid, data

def make_plots(args, date, data, chy, node):

    title = f'{os.environ["DET"].upper()} subarray {os.environ["CONTAMID"]}: '
    titles = { }
    for key in data:
        titles[key] = title + f'{key} normalization'
    titles['cons'] = title + 'overall normalization'
    titles['redchi'] = title + 'goodness of fit'

    ylabels = { }
    for key in titles:
        ylabels[key] = 'Best-fit normalization'
    ylabels['redchi'] = 'Reduced Q-stat'

    if args.pdf:
        pdf = PdfPages(args.pdf)

    colors = [ 'b', 'r', '#39FF14' ]
    symbols = [ 'D', '^', 's', 'x' ]
    labels = ['Low ChipY', 'Mid ChipY', 'High ChipY']


    for key in data:
        x = date
        y = data[key]['val']
        ylo = data[key]['lo']
        yhi = data[key]['hi']

        factor = data['cons']['val']
        if key == 'redchi' or key == 'cons':
            factor = np.ones(x.shape)

        ii = x<2037
        x = x[ii]
        y = y[ii]*factor[ii]
        ylo = ylo[ii]*factor[ii]
        yhi = yhi[ii]*factor[ii]
        chy = chy[ii]
        node = node[ii]

        fig, ax = plt.subplots()

        has_nodes = []
        for i in range(4):
            ii = node==i
            if np.sum(ii):
                has_nodes.append(i)
            else:
                continue

            for j in range(3):
                jj = (chy[ii]>=341*j+1) & (chy[ii]<341*(j+1)+1)
                x_ = x[ii][jj]
                y_ = y[ii][jj]
                ylo_ = ylo[ii][jj]
                yhi_ = yhi[ii][jj]
                ax.errorbar(x_, y_, (y_-ylo_, yhi_-y_), fmt=symbols[i], color=colors[j])

        xlim = ax.get_xlim()
 
        if key in iachec:
            ax.plot(xlim, [iachec[key]['val']]*2, 'k-')
            ax.plot(xlim, [iachec[key]['lo']]*2, 'k:')
            ax.plot(xlim, [iachec[key]['hi']]*2, 'k:')

        if key == 'cons':
            ax.plot(xlim, [cons_iachec_2016]*2, 'r-')

        ylim = ax.get_ylim()
        ax.set_ylim(ax.get_ylim())
        ax.set_xlim(xlim)

       # from https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
        lines=[]
        for i in range(3):
            lines += ax.plot(0, 0, color=colors[i])
        for i in has_nodes:
            lines += ax.plot(0, 0, symbols[i], color='k')
        ax.legend(lines[:3], labels, loc='upper right', frameon=False)

        from matplotlib.legend import Legend

        leg = Legend(ax, lines[3:], [f'Node {i}' for i in has_nodes], loc='upper left', frameon=False)
        ax.add_artist(leg)

        if key in iachec:
            line = ax.plot(0, 0, '-', color='k')
            label = 'IACHEC value'
            leg = Legend(ax, line, [label], loc='lower left', frameon=False)
            ax.add_artist(leg)

        if key == 'cons':
            line = ax.plot(0, 0, '-', color='r')
            label = '2003-06 value'
            leg = Legend(ax, line, [label], loc='lower right', frameon=False)
            ax.add_artist(leg)

        ax.set_xlabel('Date')
        ax.set_ylabel(ylabels[key])
        ax.set_title(titles[key])

        plt.tight_layout()

        if args.pdf:
            pdf.savefig(fig)
        else:
            plt.show()

    if args.pdf:
        pdf.close()

def combine(args):
    global srcdir

    obsid, date, chy, node = read_obsinfo(args.obsinfo)
    obsid2, data = read_shiftfits(args.shiftfits)
    ii = obsid2<80000
    if np.sum(obsid!=obsid2[ii]):
        raise RuntimeError(f"obsids don't match in '{args.obsinfo}' and '{args.shiftfits}'")

    obsid = [f'{int(o):05d}' for o in obsid]
    obsid2 = [f'{int(o):05d}' for o in obsid2]

    combinedf=f'{srcdir}/../data/combine/{os.environ["DET"]}'
    with open(combinedf) as cfile:
        for line in cfile:

            # first deal with obs_info data
            match = re.search(r'^(\d{5})=(.*)$', line)
            combined = match.group(1)
            to_combine = match.group(2).split(',')
            for o in to_combine[:-1]:
                index = obsid.index(o)
                obsid.pop(index)
                date = np.delete(date, index)
                chy = np.delete(chy, index)
                node = np.delete(node, index)
            obsid[obsid.index(to_combine[-1])] = combined

            # then shiftfits
            for o in to_combine:
                index = obsid2.index(o)
                obsid2.pop(index)
                for key1 in data:
                    for key2 in data[key1]:
                        data[key1][key2] = np.delete(data[key1][key2], index)

    return date, chy, node, data

def plot_fit_results(args):
    date, chy, node, data = combine(args)
    make_plots(args, date, data, chy, node)

def main():
    parser = argparse.ArgumentParser(
        description='Plot fit results'
    )
    parser.add_argument('-p', '--pdf', help='Output PDF file.')
    parser.add_argument('obsinfo', help='Tabulated observation info file.')
    parser.add_argument('shiftfits', help='Tabulated fit results file.')
    args = parser.parse_args()

    plot_fit_results(args)

if __name__ == '__main__':
    main()
