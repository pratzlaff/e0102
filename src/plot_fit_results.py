# adapted from /data/paul11/plucinsk/chandra/data/e0102/I3/scripts/plot_fit_results.pro

import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from numpy.random import rand
import os
import re
import sys

from E0102 import shiftfits_file, read_shiftfits
from E0102 import contamfits_file, read_contamfits
from E0102 import obsinfo_file, read_obsinfo
from E0102 import read_simul

read_func=None
read_file=None

iachec = {
    'cons':{'val':1, 'lo':0.9, 'hi':1.1},
    'O7':{'val':0.002745},
    'O8':{'val':0.004393},
    'Ne9':{'val':0.001381},
    'Ne10':{'val':0.001378},
    'Mg11':{'val':0.000108671},
}
for key in iachec:
    for limit in 'lo', 'hi':
        iachec[key][limit] = iachec[key]['val'] * iachec['cons'][limit]
cons_iachec_2016 = 1.072

def make_plots(args, date, data, chy, node):

    title = f'{args.detector.upper()} subarray {os.environ["CONTAMID"]}: '
    titles = { }

    if args.type == 'norm':
        for key in data:
            titles[key] = title + f'{key} normalization'
            titles['cons'] = title + 'overall normalization'
    elif args.type == 'contam':
        for k in data:
            titles[k] = title + k
    titles['redchi'] = title + 'goodness of fit'

    ylabels = { }
    if args.type == 'norm':
        for key in titles:
            ylabels[key] = 'Best-fit normalization'
    elif args.type == 'contam':
        ylabels = { k:'' for k in data }
    ylabels['redchi'] = 'Reduced Q-stat'
    ylabels['tauL'] = 'τ';
    ylabels['OtoC'] = 'O/C';
    ylabels['FtoC'] = 'F/C';

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

        factor = np.ones(x.shape)
        if args.type == 'norm':
            factor = data['cons']['val']
            if key == 'redchi' or key == 'cons':
                factor = np.ones(x.shape)
            # for the case where parameter 1 is frozen
            factor[np.isnan(factor)] = 1

        ii = x<2037
        x = x[ii]
        y = y[ii]*factor[ii]
        ylo = ylo[ii]*factor[ii]
        yhi = yhi[ii]*factor[ii]
        chy = chy[ii]
        node = node[ii]

        if not (~np.isnan(y)).sum():
            continue

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
                x_ = x_ + 0.3*(rand(x_.size)-0.5)
                y_ = y[ii][jj]
                ylo_ = ylo[ii][jj]
                yhi_ = yhi[ii][jj]
                if key != 'redchi':
                    kk = ((y_-ylo_)>0) & ((yhi_-y_)>0)
                    x_ = x_[kk]
                    y_ = y_[kk]
                    ylo_ = ylo_[kk]
                    yhi_ = yhi_[kk]
                ax.errorbar(x_, y_, (y_-ylo_, yhi_-y_), fmt=symbols[i], color=colors[j])

        xlim = ax.get_xlim()
 
        if args.type == 'norm':
            if key in iachec:
                ax.plot(xlim, [iachec[key]['val']]*2, 'k-')
                ax.plot(xlim, [iachec[key]['lo']]*2, 'k:')
                ax.plot(xlim, [iachec[key]['hi']]*2, 'k:')

            if key == 'cons':
                ax.plot(xlim, [cons_iachec_2016]*2, 'r-')

        ylim = ax.get_ylim()
        ax.set_ylim(ax.get_ylim())
        ax.set_xlim(xlim)
        if key == 'redchi' and args.detector == 's3' and args.type == 'norm':
            ax.set_ylim(1, 3)

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

        if args.type == 'norm':
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

    if args.pdf:
        pdf.close()

def no_simul(args):
    global read_func, read_file

    obsinfo = obsinfo_file(args.detector)
    obsid, date, chy, node = read_obsinfo(obsinfo)
    obsid2, data = read_func(read_file)
    ii = obsid2<80000
    if np.sum(obsid!=obsid2[ii]):
        raise RuntimeError(f"obsids don't match in '{obsinfo} and '{read_file}'")

    to_delete = []
    for i, o in enumerate(obsid2):
        if o >= 80000:
            to_delete.append(i)
    to_delete.reverse()

    for i in to_delete:
        for key1 in data:
            for key2 in data[key1]:
                data[key1][key2] = np.delete(data[key1][key2], i)
    return date, chy, node, data

def simul(args):
    global read_func, read_file

    obsinfo = obsinfo_file(args.detector)
    obsid, date, chy, node = read_obsinfo(obsinfo)
    obsid2, data = read_func(read_file)
    ii = obsid2<80000
    if np.sum(obsid!=obsid2[ii]):
        raise RuntimeError(f"obsids don't match in '{obsinfo}' and '{read_file}'")

    obsid = [f'{int(o):05d}' for o in obsid]
    obsid2 = [f'{int(o):05d}' for o in obsid2]

    s = read_simul(args.detector)
    s = { f'{o:05d}' : [f'{o:05d}' for o in s[o] ] for o in s }
    for simuled in s:
        to_simul = s[simuled]
        for o in to_simul[:-1]:
            index = obsid.index(o)
            obsid.pop(index)
            date = np.delete(date, index)
            chy = np.delete(chy, index)
            node = np.delete(node, index)
        obsid[obsid.index(to_simul[-1])] = simuled

        # then shiftfits
        for o in to_simul:
            index = obsid2.index(o)
            obsid2.pop(index)
            for key1 in data:
                for key2 in data[key1]:
                    data[key1][key2] = np.delete(data[key1][key2], index)

    return date, chy, node, data

def plot_fit_results(args):
    date, chy, node, data = simul(args) if args.simul else no_simul(args)
    make_plots(args, date, data, chy, node)
    if args.pdf is None:
        plt.show()

def main():
    parser = argparse.ArgumentParser(
        description='Plot fit results'
    )
    parser.add_argument('-p', '--pdf', help='Output PDF file.')
    parser.add_argument('--simul', default=True, action=argparse.BooleanOptionalAction, help='Plot simul fit results, rather than for individual ObsIDs.')
    parser.add_argument('type', choices=('norm','contam'))
    parser.add_argument('detector', choices=('i3','s3'))
    args = parser.parse_args()

    global read_func, read_file
    read_func = { 'norm':read_shiftfits, 'contam':read_contamfits }[args.type]
    read_file = { 'norm':shiftfits_file(args.detector), 'contam':contamfits_file(args.detector) }[args.type]

    plot_fit_results(args)

if __name__ == '__main__':
    main()
