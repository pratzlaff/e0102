import numpy as np
import os
from pprint import pprint
import re
import sys

srcdir=os.path.dirname(__file__)
datadir=os.popen(srcdir+'/datadir').read()

def read_simul(det):
    data = { }
    regex = re.compile(r'^(\d{5})=(.*)')
    for line in open(f'{srcdir}/../data/simul/{det}'):
        if match :=regex.search(line):
            g = match.groups()
            data[int(g[0])] = [ int(o) for o in g[1].split(',') ]
    return data

def shiftfits_file(det):
    return f'{datadir}/fits/{os.environ["CONTAMID"]}/results/shiftfits_{det}.txt'

def contamfits_file(det):
    return f'{datadir}/fits/{os.environ["CONTAMID"]}/results/contamfits_{det}.txt'

def obsinfo_file(det):
    return f'{datadir}/obs_info/{det}.txt'

def read_obsinfo(obsinfo):
    obsid, date, chy, node = np.loadtxt(obsinfo, unpack=True, usecols=(0,1,3,4))
    return obsid.astype(int), date, chy, node

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
    mg11, mg11lo, mg11hi, \
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
                                                  20,22,23,
                                                  -2]
                 )
    data = {'cons':{'val':cons, 'lo':conslo, 'hi':conshi},
            'O7':{'val':o7, 'lo':o7lo, 'hi':o7hi},
            'O8':{'val':o8, 'lo':o8lo, 'hi':o8hi},
            'Ne9':{'val':ne9, 'lo':ne9lo, 'hi':ne9hi},
            'Ne10':{'val':ne10, 'lo':ne10lo, 'hi':ne10hi},
            'Mg11':{'val':mg11, 'lo':mg11lo, 'hi':mg11hi},
            'redchi':{'val':redchi, 'lo':redchi, 'hi':redchi},
            }

    if not grep_header('Mg', shiftfits):
        del data['Mg']

    return obsid, data

def read_contamfits(contamfits):
    obsid, \
    tauL, tauLlo, tauLhi, \
    OtoC, OtoClo, OtoChi, \
    FtoC, FtoClo, FtoChi, \
    redchi \
    = np.loadtxt(contamfits, unpack=True, usecols=[0,
                                                  1,3,4,
                                                  5,7,8,
                                                  9,11,12,
                                                  -2]
                 )
    data = {'tauL':{'val':tauL, 'lo':tauLlo, 'hi':tauLhi},
            'OtoC':{'val':OtoC, 'lo':OtoClo, 'hi':OtoChi},
            'FtoC':{'val':FtoC, 'lo':FtoClo, 'hi':FtoChi},
            'redchi':{'val':redchi, 'lo':redchi, 'hi':redchi},
            }
    return obsid.astype(int), data

def detector(obsid):
    for det in 'i3', 's3':
        obsid_, _, _, _= read_obsinfo(obsinfo_file(det))
        if obsid in obsid_:
            return det
        simul = read_simul(det)
        if obsid in simul:
            return det
    raise ValueError(f'no detector found for {obsid=}')

def chipy_region(obsid):
    for det in 'i3', 's3':
        simul = read_simul(det)
        if obsid in simul:
            obsid = simul[obsid][0]
            continue
    for det in 'i3', 's3':
        obsid_, _, chy_, _= read_obsinfo(obsinfo_file(det))
        ii, = np.where(obsid == obsid_)
        if ii.size:
            chipy = chy_[ii[0]]
            region = 'High'
            if chipy < 682:
                region = 'Mid'
            if chipy < 341:
                region =  'Low'
            return region
    raise ValueError(f'no CHIPY found for {obsid=}')
