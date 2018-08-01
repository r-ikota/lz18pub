# coding: utf-8

from os import path

import numpy as np
import lib.Ldata as dm
import lib.Lode as ode

fn = path.join('data','d0100.hdf5')
bdata =  dm.loadData(fn)
trange = np.linspace(.0, 4., 801)
ltrange = np.linspace(.0, 12., 2401) #long trange

data_sts = ode.evolvL(bdata, trange)
ode.appendEigVecs(data_sts)
outfn = path.join('data','s_orbit.hdf5')
dm.saveData(outfn, data_sts)

mdata = dm.triaxisPtbSSS(bdata)
data_mts = ode.evolvLM(mdata, trange)
ode.appendEigVecs(data_mts)
outfn = path.join('data','m_orbit.hdf5')
dm.saveData(outfn,data_mts)

lmdata = dm.triaxisPtbSSS(bdata,mag=5.0e-2)
ldata_mts = ode.evolvLM(lmdata, ltrange)
ode.appendEigVecs(ldata_mts)
outfn = path.join('data','lm_orbit.hdf5')
dm.saveData(outfn,ldata_mts)
