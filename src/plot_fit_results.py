# adapted from /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/plot_fit_results.pro

import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
import sys

def read_obsinfo(obsinfo):
    obsid, date, chy, node = np.loadtxt(obsinfo, unpack=True, usecols=(0,1,3,4))
    return obsid, date, chy, node

def read_shiftfits(shiftfits):
    obsid, \
    cons, conslo, conshi, \
    ne10, ne10lo, ne10hi, \
    ne9, ne9lo, ne9hi, \
    o8, o8lo, o8hi, \
    o7, o7lo, o7hi, \
    redchi \
    = np.loadtxt(shiftfits, unpack=True, usecols=[0,
                                                  1,2,3,
                                                  4,6,7,
                                                  8,10,11,
                                                  12,14,15,
                                                  16,18,19,
                                                  22]
                 )
    return obsid, {'cons':{'val':cons, 'lo':conslo, 'hi':conshi},
                   'O7':{'val':o7, 'lo':o7lo, 'hi':o7hi},
                   'O8':{'val':o8, 'lo':o8lo, 'hi':o8hi},
                   'Ne9':{'val':ne9, 'lo':ne9lo, 'hi':ne9hi},
                   'Ne10':{'val':ne10, 'lo':ne10lo, 'hi':ne10hi},
                   }, redchi

def make_plot(x, y, ylo, yhi, chy, node, title, ylabel, factor):

    colors = [ 'b', 'r', '#39FF14' ]
    symbols = [ 'D', '^', 's', 'x' ]
    labels = ['Low ChipY', 'Mid ChipY', 'High ChipY']

    if factor is None:
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

    ax.set_xlim(ax.get_xlim())
    ax.set_ylim(ax.get_ylim())

    # from https://jakevdp.github.io/PythonDataScienceHandbook/04.06-customizing-legends.html
    lines=[]
    for i in range(3):
        lines += ax.plot(0, 0, color=colors[i], label=labels[i])
    for i in has_nodes:
        lines += ax.plot(0, 0, symbols[i], color='k', label=f'Node {i}')
    ax.legend(lines[:3], labels, loc='upper right', frameon=False)

    from matplotlib.legend import Legend

    leg = Legend(ax, lines[3:], [f'Node {i}' for i in has_nodes], loc='upper left', frameon=False)
    ax.add_artist(leg)
    ax.set_xlabel('Date')
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    plt.tight_layout()

    return fig

def plot_fit_results(args):
    obsid, date, chy, node = read_obsinfo(args.obsinfo)
    obsid2, data, redchi = read_shiftfits(args.shiftfits)
    if np.sum(obsid!=obsid2):
        raise RuntimeError(f"obsids don't match in '{args.obsinfo}' and '{args.shiftfits}'")

    title = f'{os.environ["DET"].upper()} subarray {os.environ["CONTAMID"]}: '
    titles = { }
    for key in data:
        titles[key] = title + f'{key} normalization'
    titles['cons'] = title + 'overall normalization'
    titles['redchi'] = title + 'goodness of fit'

    ylabels = { }
    for key in titles:
        ylabels[key] = 'Best-fit normalization'
    ylabels['redchi'] = 'reduced Q-stat'

    if args.pdf:
        pdf = PdfPages(args.pdf)

    fig = make_plot(date,
              data['cons']['val'], data['cons']['lo'], data['cons']['hi'],
              chy,
              node,
              titles['cons'],
              ylabels['cons'],
              None
              )
    if args.pdf:
        pdf.savefig(fig)
    else:
        plt.show()

    for line in 'O7', 'O8', 'Ne9', 'Ne10':
        fig = make_plot(date,
                  data[line]['val'], data[line]['lo'], data[line]['hi'],
                  chy,
                  node,
                  titles[line],
                  ylabels[line],
                  data['cons']['val']
                  )
        if args.pdf:
            pdf.savefig(fig)
        else:
            plt.show()

    fig = make_plot(date,
              redchi, redchi, redchi,
              chy,
              node,
              titles['redchi'],
              ylabels['redchi'],
              None
              )
    if args.pdf:
        pdf.savefig(fig)
        pdf.close()
    else:
        plt.show()


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
