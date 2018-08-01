
# coding: utf-8

#
# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')
#
# get_ipython().run_line_magic('matplotlib', 'qt5')

import matplotlib
matplotlib.use('Agg') # off-screen rendering
from matplotlib.gridspec import GridSpec

# import sys
#sys.path.insert(0, '..')

from os import path
import numpy as np

from imp import reload
import lib.Ldata as dm
import lib.Ldraw as vis
from conf_mov import *

matplotlib.rcParams.update(style)



def make_movie(data,trange,movfn):
    frame1 = vis.LFrame(data, 
        figsize=(width_1col, width_1col*0.7), 
        dpi=160)
    gs = GridSpec(5,10)
    paneT = vis.PaneTime(frame1, gs[4,3:7])
    paneP3 = vis.PanePhase3DM(frame1, gs[0:4, 0:4])
    paneEig = vis.PaneEig2D(frame1, gs[0:4, 7:10])
    paneP3.ax.set(**p3attr)
    paneP3.ax.set_xticklabels(['-20', '', '0', '', '20'], va='bottom')
    paneP3.ax.set_yticklabels(['-20', '', '0', '', '20'], va='bottom')
    paneP3.ax.set_zticklabels(['-30', '-20', '-10', '0', '10'], va='top')
    paneP3.setBG(**bgprop)

    paneEig.ax.set(**pEigattr)
    paneEig.ax.set_xticklabels(['', '-20', '', '-10', '', '0', '', '10', ''])
    paneEig.ax.grid(True)

    nfold = len(data['xyz'])

    p3_prop = []
    for i in range(nfold):
        p3_prop.append(p3line_prop.copy())

    ref_prop = p3_prop[0]
    ref_prop['color'] = 'red'
    ref_prop['marker'] = 'o'

    paneP3.set_line_prop(p3_prop)
    paneEig.set_line_prop(eig2DLineProp)

    frame1.mkMov(movfn, trange)

for infn, outfn,trange in zip(['m_orbit.hdf5','lm_orbit.hdf5'],
                        ['lorenz01.mp4','lorenz02.mp4'],
                        [[0.0,4.0],[0.0,12.0]]
                    ):
    fn = path.join('data',infn)
    data = dm.loadData(fn)
    movfn = path.join('..','movie',outfn)
    make_movie(data,trange,movfn)
