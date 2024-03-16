import numpy as np

from calfem.core import beam3e
from calfem.core import bar3e
from calfem.core import bar3s
from calfem.core import assem
from calfem.core import coordxtr
from calfem.core import solveq


def pileExpand(bearing_arr, incl_arr, xvec_arr, yvec_arr, npiles_q, pLen, case):
    # Expanding pile data from a single quadrant

    a = [1, -1, -1, 1]
    b = [1, 1, -1, -1]
    c = [0, 90, 180, 270]

    # Kvadrantdata
    x2vec_q        = np.zeros((npiles_q))
    y2vec_q        = np.zeros((npiles_q))
    lvec_q         = np.ones((npiles_q))*pLen

    # Full data 
    bearing        = np.zeros((npiles_q*4))
    x1vec          = np.zeros((npiles_q*4))
    y1vec          = np.zeros((npiles_q*4))
    z1vec          = np.zeros((npiles_q*4))
    x2vec          = np.zeros((npiles_q*4))
    y2vec          = np.zeros((npiles_q*4))
    incl           = np.zeros((npiles_q*4))
    lvec           = np.zeros((npiles_q*4))
    z1vec          = np.zeros((npiles_q*4))


    # Set current pile config from arr-vec
    bearing_q      = bearing_arr[case]
    x1vec_q        = xvec_arr[case]
    y1vec_q        = yvec_arr[case]
    incl_q         = incl_arr[case]

    for i in range(npiles_q):
        if incl_q[i] == 0:
            x2vec_q[i] = x1vec_q[i]
            y2vec_q[i] = y1vec_q[i]
        else:
            x2vec_q[i] = x1vec_q[i] + np.cos(np.radians(bearing_q[i]))*pLen/incl_q[i]
            y2vec_q[i] = y1vec_q[i] + np.sin(np.radians(bearing_q[i]))*pLen/incl_q[i]

    iter = 0
    for i in range(4):
        for j in range(npiles_q):

            x1vec[iter]    = a[i]*x1vec_q[j]
            y1vec[iter]    = b[i]*y1vec_q[j]
            x2vec[iter]    = a[i]*x2vec_q[j]
            y2vec[iter]    = b[i]*y2vec_q[j]
            incl[iter]     = incl_q[j]
            lvec[iter]     = lvec_q[j]

            if i > 0:
                if bearing[iter-npiles_q] == c[i]:
                    bearing[iter] = bearing[iter-npiles_q]
                else:
                    bearing[iter] = bearing[iter-npiles_q] + 180
            else:
                bearing[iter] = bearing_q[j]

            iter = iter + 1

    return x1vec, y1vec, x2vec, y2vec, incl, lvec, bearing

def GenerateElements(x1vec, y1vec, x2vec, y2vec, lvec, npiles):
    # Elementdata, beam elements
    Coord1             = np.zeros((npiles+1, 3))
    Dof1               = np.zeros((npiles+1, 6))
    Edof1              = np.zeros((npiles, 12))

    dpap               = 0.000001
    Coord1[0, 2]       = dpap

    for i in range(npiles):
        Coord1[i+1, 0] = x1vec[i]
        Coord1[i+1, 1] = y1vec[i]

    for i in range(npiles+1):
        Dof1[i, :] = [6*i+1, 6*i+2, 6*i+3, 6*i+4, 6*i+5, 6*i+6]
    
    for i in range(npiles):
        Edof1[i, :] = [1, 2, 3, 4, 5, 6, 6*i+7, 6*i+8, 6*i+9, 6*i+10, 6*i+11, 6*i+12]
    
    [Ex1, Ey1, Ez1] = coordxtr(Edof1, Coord1, Dof1, 2)

    # Elementdata, bar elements
    Coord2             = np.zeros((2*npiles, 3))
    Dof2               = np.zeros((2*npiles, 3))
    Edof2              = np.zeros((npiles, 6))
    
    for i in range(npiles):
        Coord2[i, 0] = x1vec[i]
        Coord2[i, 1] = y1vec[i]
    
        Coord2[i+npiles, 0] = x2vec[i]
        Coord2[i+npiles, 1] = y2vec[i]
        Coord2[i+npiles, 2] = -lvec[i]
    
    for i in range(2*npiles):
        Dof2[i, :] = [6*i+7, 6*i+8, 6*i+9]
    
    for i in range(npiles):
        Edof2[i, :] = [6*i+7, 6*i+8, 6*i+9, 6*i+(6*npiles)+7, 6*i+(6*npiles)+8, 6*i+(6*npiles)+9]
    
    [Ex2, Ey2, Ez2] = coordxtr(Edof2, Coord2, Dof2, 2)

    nDofs = int(np.max(Edof2))

    Edof1      = Edof1.astype(int)
    Edof2      = Edof2.astype(int)

    return Edof1, Edof2, nDofs, Ex1, Ey1, Ez1, Ex2, Ey2, Ez2

def assembElem(nDofs, Edof1, Edof2, Ex1, Ey1, Ez1, Ex2, Ey2, Ez2, npiles, ep1, ep2):    

    K          = np.zeros((nDofs, nDofs))
    
    for i in range(npiles):
    
        p1 = np.array([0, 0, 0])
        p2 = np.array([Ex1[i, :][0], Ey1[i, :][0], Ez1[i, :][0]])
        p3 = np.array([Ex1[i, :][1], Ey1[i, :][1], Ez1[i, :][1]])

        v1 = np.subtract(p2, p1)
        v2 = np.subtract(p3, p1)
        eo = np.cross(v1, v2)
    
        Ke = beam3e(Ex1[i, :], Ey1[i, :], Ez1[i, :], eo, ep1)
        K = assem(Edof1[i, :], K, Ke)

        Ke = bar3e(Ex2[i, :], Ey2[i, :], Ez2[i, :], ep2)
        K = assem(Edof2[i, :], K, Ke)

    return K

def analyseResults(Edof2, Ex2, Ey2, Ez2, ep2, npiles, a):

    Nvek = np.zeros((npiles))

    nElements = Edof2.shape[0]
    nDofs = Edof2.shape[1]
    Ed = np.zeros([nElements, nDofs])
    i = 0
    for row in Edof2:
        idx = row-1
        Ed[i, :] = a[np.ix_(idx)].T
        i += 1

    for i in range(npiles):

        x1, x2  = Ex2[i,:]
        y1, y2  = Ey2[i,:]
        z1, z2  = Ez2[i,:]

        dx = x2-x1
        dy = y2-y1
        dz = z2-z1
        L = np.sqrt(dx*dx+dy*dy+dz*dz)

        E = ep2[0]
        A = ep2[1]

        eps = (dx*Ed[i][0]/L + dy*Ed[i][1]/L + dz*Ed[i][2]/L)/L

        Ntest = -eps*E*A

        Nvek[i] = Ntest


    return Nvek

def pileInfluenceRun(setupdata, startConfig, chunk):

    bearing_arr = setupdata[0]
    incl_arr    = setupdata[1]
    xvec_arr    = setupdata[2]
    yvec_arr    = setupdata[3]
    npiles_q    = setupdata[4]
    pLen        = setupdata[5]
    ep1         = setupdata[6]
    ep2         = setupdata[7]
    nrVal       = setupdata[8]
    lc          = setupdata[9]


    npiles = 4*npiles_q

    nMaxPileConfig = np.zeros((chunk,npiles))
    nMinPileConfig = np.zeros((chunk,npiles))
    
    for step in range(chunk):
        config = startConfig + step

        x1vec, y1vec, x2vec, y2vec, incl, lvec, bearing = pileExpand(bearing_arr, incl_arr, xvec_arr, yvec_arr, npiles_q, pLen, config)
        Edof1, Edof2, nDofs, Ex1, Ey1, Ez1, Ex2, Ey2, Ez2 = GenerateElements(x1vec, y1vec, x2vec, y2vec, lvec, npiles)

        K = assembElem(nDofs, Edof1, Edof2, Ex1, Ey1, Ez1, Ex2, Ey2, Ez2, npiles, ep1, ep2) 

        Ninfl = np.zeros((npiles,6))

        bc = np.arange((6*npiles)+7, nDofs+1)

        for i in range(6):
            f = np.zeros((nDofs, 1))
            f[i] = 1
            [a, r] = solveq(K, f, bc)
            Ninfl[:,i] = analyseResults(Edof2, Ex2, Ey2, Ez2, ep2, npiles, a)

        Nvek = np.zeros((npiles,nrVal))

        for i in range(nrVal):
            for j in range(npiles):

                Nvek[j,i] = Ninfl[j,:] @ lc[i,:]
    
        for i in range(npiles):
            nMaxPileConfig[step,i] = np.max(Nvek[i])
            nMinPileConfig[step,i] = np.min(Nvek[i])
        

    return nMaxPileConfig, nMinPileConfig
