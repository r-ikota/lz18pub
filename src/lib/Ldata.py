'''
Data management module.
datatypes are:
    sss: single snap shot
    mss: multiple snap shot
    sts: single time series
    mts: multiple time series
'''

import numpy as np
import os, time
import h5py

def mkDateStr():

    now = time.time()
    ts = time.localtime(now)
    dformat = "{0:04d}-{1:02d}{2:02d}-{3:02d}{4:02d}-{5:02d}"
    d = dformat.format(ts.tm_year, ts.tm_mon, ts.tm_mday,
                    ts.tm_hour, ts.tm_min, ts.tm_sec)
    return d


def mkSSSData(
        xyz=np.array(( -5.66424041,  -5.87909411,  23.30838448)), 
        param = np.array((10.0, 28.0, 2.666666))
        ):
    '''
    makeData(xyz, sigma, r, b)
    xyz: a list or numpy array of size three
    param: (sigma, r, b)
        sigma: default value 10.0
        r: default value 28.0
        b: default value 2.666666
    
    data: return value, a dictionary {'xyz': xyz, 'param': param}
    '''
    
    xyz = np.array(xyz)

    data = dict(DataType='sss', xyz=np.asarray(xyz), param=np.asarray(param))
    return data

def saveData(fpath, data, overwrite=False):
    
    if os.path.exists(fpath) and (not overwrite):
        print(fpath + ' already exists!'); return None
    DataType = data.pop('DataType')
    with h5py.File(fpath, 'w') as fh:
        for k,v in data.items():
            fh[k] = v
        dset_xyz = fh['xyz']
        dset_xyz.attrs['DataType'] = DataType
    data['DataType'] = DataType
    
def loadData(fpath):

    if not os.path.exists(fpath): 
        print(fpath + ' does NOT exist!')
        return None

    with h5py.File(fpath, 'r') as fh:
        dset_xyz = fh['xyz']
        DataType = dset_xyz.attrs['DataType']
        data = dict(DataType=DataType)        
        for k in fh:
            data[k] = fh[k][()]

    return data


def pickSSS(tsdata, t):
    eps = 1.0e-8
    tarray = tsdata['tarray']
    if t < tarray[1]:
        tind = 0
    else:
        tind = np.argmax(tarray[tarray < t + eps])
    t = tarray[tind]

    if tsdata['DataType'] == 'sts':
        xyz = tsdata['xyz'][tind] 
    elif tsdata['DataType'] == 'mts':
        xyz = tsdata['xyz'][0][tind]

    data = dict(
                DataType = 'sss', 
                param = tsdata['param'].copy(), 
                xyz = xyz.copy()
                ) 

    return data


def sliceSTS(stsdata, slicearray):
    pass

def sliceMTS(stsdata, slicearray):
    pass


def _mkMSS(sssdata, nfold, ptbd):
    if sssdata['DataType'] != 'sss':
        print('data type is not sss.')
        return False
    xyz = sssdata['xyz'].copy()
    mxyz = np.vstack((xyz, ptbd))
    mssdata = dict(
                    DataType='mss', 
                    nfold=nfold, 
                    param=sssdata['param'].copy(), 
                    xyz=mxyz
                )
    return mssdata

def cubePtbSSS(sssdata, mag=5.0e-1):
    pn = (1,-1)
    nfold = 8
    xyz = sssdata['xyz']
    ptbd = [xyz + mag*np.array((i, j, k)) 
            for i in pn for j in pn for k in pn]
    return _mkMSS(sssdata, nfold, ptbd)

def triaxisPtbSSS(sssdata, mag=5.0e-1):
    nfold = 6
    xyz = sssdata['xyz']
    A = np.eye(3)
    ptbd = xyz + mag*np.vstack((A, -A))

    return _mkMSS(sssdata, nfold, ptbd)


def randPtbSSS(sssdata, nfold=4, eps=5.0e-2):
    ptbd = sssdata['xyz'] + np.random.random((nfold,3)) - .5
    return _mkMSS(sssdata, nfold, ptbd)

