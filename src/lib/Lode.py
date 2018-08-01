from __future__ import division
import numpy as np
import scipy as sp
from scipy.integrate import odeint
from scipy import linalg


_trr = 1.0e-8

def normalizeVec(v):
    '''
    Normalize a vector
    '''

    n = linalg.norm(v)
    if n > _trr: 
        v /= n
    return v

def F(xyz, t, sigma, r, b):
    '''
    The Lorenz Eq: 
        du/dt = F(u),
        u = (x,y,z)
    F =         
        [
            [-sigma * x + sigma * y],
            [-sigma * x - y - x * z],
            [-b * z + x * y - b * (r + sigma)]
        ]
    '''

    dxdt = np.array(
                [- sigma * xyz[0] + sigma * xyz[1],
                -sigma * xyz[0] - xyz[1] - xyz[0]*xyz[2],
                - b * xyz[2] + xyz[0] * xyz[1] -b*(r + sigma)]
            )
    return dxdt

def DF(xyz, t, sigma, r, b):
    '''
    The Jacobian DF of F.
    DF = 
        [
            [-sigma, sigma, 0],
            [-sigma - z, -1, -x],
            [y, x, -b]
        ]
    '''

    jcb = np.array(
        ((- sigma, sigma, 0.0),
            (-sigma - xyz[2], -1.0, - xyz[0]),
            (xyz[1], xyz[0], -b))
        )
    return jcb

def SDF(xyz, t, sigma, r, b):
    '''
    Symmetric Part of the Jacobian:
    SDF = (DF + DF^T)/2
    '''

    symj = np.array(
        ((-2.0*sigma, -xyz[2], xyz[1]),
         (-xyz[2], -2.0, 0.0),
         (xyz[1], 0.0, -2.0*b))
        )/2.
    return symj

def ADF(xyz, t, sigma, r, b):
    '''
    AntiSymmetric Part of the Jacobian:
    ADF = (DF - DF^T)/2
    '''

    asymj = np.array(
        ((0.0, 2.0*sigma + xyz[2],  - xyz[1]),
         (-2.0*sigma - xyz[2], 0.0, -2.0*xyz[0]),
         (xyz[1], 2.0*xyz[0], 0.0))
        )/2.
    return asymj    

def arrangeEigVecs(prevEV, currEV):
    '''    
    Rearrange eigenvalues and eigenvectors of the Jacobian DF so that they are continuous in time.
    The returned value is a tuple consisting of an array 
    of eigenvalues e and an array of eigenvectors v.

    input:
        prevEV: (pE, pV)
            pE[i]: the ith eigenvalue
            pV[i]: the ith eigenvector

    output:
        reordered_cE, reordered_cV
            reordered_cE[i]: the ith eigenvalue
            reordered_cV[i]: the ith eigenvector
    '''

    pE, pV = prevEV; cE, cV = currEV
    _cE = list(cE); _cV = list(cV)

    reordered_cE = []; reordered_cV = []
    for i,e in enumerate(pE):
        r = [e - ee for ee in _cE]
        imin = np.argmin(np.abs(r))
        reordered_cE.append(_cE.pop(imin))
        _V = normalizeVec(_cV.pop(imin))
        if linalg.norm(_V - pV[i]) > linalg.norm(_V + pV[i]):
            reordered_cV.append(-_V)
        else:
            reordered_cV.append(_V)
    return (np.array(reordered_cE), np.array(reordered_cV))



def getEigVecs(xyz, param):
    '''
    input::
        xyz: reference orbit
        param: parameters

    return::
        evA: (eigenvals, vecs) for DF
        evB: (eigenvals, vecs) for (DF + DF^T)/2
            evA: (eA, vA)
                eA: [ [e1(t0), e2(t0),...], [e1(t1), e2(t1),...], ... ]
                vA: [ [v1(t0), v2(t0),...], [v1(t1), v2(t1),...], ... ]
            evB: (eB, vB)
    '''

    sigma, r, b = param
    p = xyz[0]
    JA = DF(p, 0.0, sigma, r, b); JB = SDF(p, 0.0, sigma, r, b)
    ea, va = linalg.eig(JA); eb, vb = linalg.eigh(JB)
    vaT = []; vbT = []
    for vT, vTm in zip((vaT, vbT), (va.T, vb.T)):
        for v in vTm:
            vT.append(normalizeVec(v)) 

    #arrange eigenvalues in the desceindig order and arrange eigenvectors accordingly
    sidx_a = sp.argsort(sp.real(-ea)) #sorted index for ea
    sidx_b = sp.argsort(sp.real(-eb)) 
    ea = ea[sidx_a]
    eb = eb[sidx_b]
    vaT = np.array(vaT)[sidx_a]
    vbT = np.array(vbT)[sidx_b]

    # make sure that vb is a right-handed system
    if linalg.det(vbT) < 0.0:
        vbT[2] = -vbT[2]


    eA = [ea]
    eB = [eb]
    vA = [vaT]
    vB = [vbT]

    for p in xyz[1:]:
        JA = DF(p, 0.0, sigma, r, b); JB = SDF(p, 0.0, sigma, r, b)

        for J, E, V in zip((JA, JB), (eA, eB), (vA, vB)):
            e, v = linalg.eig(J)
            pe = E[-1]; pvT = V[-1]  # previous e, vT
            e,v = arrangeEigVecs((pe, pvT), (e, v.T))
            E.append(e); V.append(v)
    eA, vA, eB, vB = map(np.array, (eA, vA, eB, vB))
    return ( (eA, vA), (eB, vB) )


def evolvL(data, tarray):
    xyz = data['xyz']
    param = data['param']
    sigma, r, b = param

    xyzsol = odeint(F, xyz, tarray, args=(sigma, r, b), Dfun=DF)

    tsdata = dict( 
                    DataType = 'sts',
                    xyz = xyzsol, 
                    param = param.copy(),
                    tarray = tarray.copy()
                )

    return tsdata


def evolvLM(mdata, tarray):
    mxyz = mdata['xyz']
    param = mdata['param']
    sigma, r, b = param

    mxyzsol = []
    for xyz in mxyz:
        xyzsol = odeint(F, xyz, tarray, args=(sigma, r, b), Dfun=DF)
        mxyzsol.append(xyzsol)

    tsdata = dict(                    
                    DataType = 'mts',
                    xyz=mxyzsol,
                    param=param.copy(), 
                    tarray=tarray.copy()
                )

    return tsdata

def appendEigVecs(data):
    # if 'evA' in data:
    #     print('The data alsready has evA and evB.')
    #     return False
    
    if data['DataType'] == 'sts':
        xyz = data['xyz']
    elif data['DataType'] == 'mts':
        xyz = data['xyz'][0]
        
    evA, evB = getEigVecs(xyz, data['param'])

    data['eigValDF'] = evA[0]
    data['eigVecDF'] = evA[1]
    data['eigValSymDF'] = evB[0]
    data['eigVecSymDF'] = evB[1]


