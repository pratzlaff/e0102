import argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import sys

def read_obsinfo(obsinfo):
    obsid, year, chipy = np.loadtxt(obsinfo, unpack=True, usecols=(0,1,3))
    obsid = obsid.astype(int).tolist()
    chipy = chipy.tolist()
    year = year.tolist()
    year = { obsid[i]:year[i] for i in range(len(obsid)) }
    year[99999] = year[27760]
    year[99998] = year[27761]

    hi, mid, lo = [], [], []
    for o, c in zip( obsid, chipy):
        if c < 1/3*1024:
            lo.append(o)
        elif c < 2/3*1024:
            mid.append(o)
        else:
            hi.append(o)
    lo.append(99999)
    hi.append(99998)

    return year, lo, mid, hi

def read_shiftfits(shiftfits,*,is_old):
    usecols = list(range(4))
    if is_old:
        usecols += list(range(4,4+16))
    else:
        usecols += list(range(8,8+16))
    obsid,c,clo,chi,ne10,ne10err,ne10lo,ne10hi,ne9,ne9err,ne9lo,ne9hi,o8,o8err,o8lo,o8hi,o7,o7err,o7lo,o7hi = np.loadtxt(shiftfits, unpack=True, usecols=usecols)
    data = { 'obsid':obsid.astype(int),
             'cons':c,
             'conserr':0.5*(chi-clo),
             'O7':o7,
             'O7err':0.5*(o7hi-o7lo),
             'O8':o8,
             'O8err':0.5*(o8hi-o8lo),
             'Ne9':ne9,
             'Ne9err':0.5*(ne9hi-ne9lo),
             'Ne10':ne10,
             'Ne10err':0.5*(ne10hi-ne10lo),
            }
    for k in 'O7', 'O8', 'Ne9', 'Ne10':
        data[k+'err'] = np.abs(data['cons']*data[k])*np.sqrt(((data['conserr']/data['cons'])**2+(data[k+'err']/data[k])**2))
        data[k] *= data['cons']
    return data

def cmp_old_new(args):
    old = read_shiftfits(args.old_shiftfits, is_old=True)
    new = read_shiftfits(args.new_shiftfits, is_old=False)

    year, lo, mid, hi = read_obsinfo(args.obsinfo)

    # the order of these will be same as in the "old" shiftfits
    years = [year[o] for o in old['obsid']]
    ratios = {
        'O7':[],
        'O8':[],
        'Ne9':[],
        'Ne10':[],
    }
    ratio_errs = { k:[] for k in ratios }

    for i, o in enumerate(old['obsid']):
        if o < 80000:
            j = np.where(new['obsid'] == o)[0][0]
        else:
            j = np.where(new['obsid'] == o-10000)[0][0]
        for e in ratios:
            a = float(new[e][j]-old[e][i])
            aerr = float(np.sqrt(new[e+'err'][j]**2 + old[e+'err'][i]**2))

            b = float(new[e][j])
            berr = float(new[e+'err'][j])

            ratio = float(a/b)

            ratio_err = float(np.abs(ratio)*np.sqrt(((aerr/a)**2+(berr/b)**2)))
                
            #sys.stderr.write(f'{int(o)=}, old={float(old[e][i]):3g}, new={float(new[e][j]):3g}, {a=:3g}, {aerr=:3g}, {b=:3g}, {berr=:3g} , {ratio=:3g}, {ratio_err=:3g}\n')
            ratios[e].append(ratio)
            ratio_errs[e].append(ratio_err)

    if args.pdf:
        pdf = PdfPages(args.pdf)

    regstr = ['Low ChipY', 'Mid ChipY', 'High ChipY']
    colors = [ 'b', 'r', '#39FF14' ]
    for j, reg in enumerate([lo, mid, hi]):
        fig, axes = plt.subplots(2, 2, sharex=True, figsize=(11,8.5))
        fig.suptitle('E0102 S3 Best-Fit Normalizations: ', fontsize=16, x=0.1, ha='left')
        fig.text(x=0.55, y=0.96, s=regstr[j], color=colors[j], transform=fig.transFigure, horizontalalignment='center', fontsize=16)
        for k, line in enumerate(ratios):

            row = int(k / 2)
            col = k % 2
            ax = axes[row, col]

            x, y, yerr, obsids = [], [], [], []
            for o in reg:
                try:
                    i = np.where(old['obsid']==o)[0][0]
                except:
                    sys.stderr.write(f'skipping {o}, {line}, {regstr[j]}\n')
                    continue
                obsids.append(o)
                x.append(years[i])
                y.append(float(ratios[line][i]))
                yerr.append(float(ratio_errs[line][i]))
            if False:
                np.savetxt(sys.stderrnp.column_stack((obsids,x,y,yerr)),fmt='%3g')
            if args.err:
                ax.errorbar(x, y, yerr, color=colors[j], fmt='o')
            else:
                ax.plot(x, y, 'o', color=colors[j])
            ax.set_title(f'{line}')
            if row==1:
                ax.set_xlabel('Date')
            if col==0:
               ax.set_ylabel(r'$\frac{\text{new}-\text{old}}{\text{new}}$')

        plt.tight_layout()
        if args.pdf:
            pdf.savefig(fig)
        else:
            plt.show()

    if args.pdf:
        pdf.close()

def main():
    parser = argparse.ArgumentParser(
        description='Compare old vs new shiftfits.'
    )
    parser.add_argument('-p', '--pdf', help='Output plot file.')
    parser.add_argument('-e', '--err', action='store_true', help='Include error bars.')
    parser.add_argument('--obsinfo', default='/data/legs/rpete/data/e0102/obs_info/s3.txt')
    parser.add_argument('old_shiftfits')
    parser.add_argument('new_shiftfits')
    args = parser.parse_args()
    args.err = True

    cmp_old_new(args)

if __name__ == '__main__':
    main()
