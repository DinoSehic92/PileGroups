import numpy as np
import time
from math import factorial

class pileConfigGenerator:

    def __init__(self, xvec, yvec, nvert, incl, singdir, npiles, colision, p_spacing, signal):

        self.xvec = xvec
        self.yvec = yvec
        self.nvert = nvert
        self.incl = incl
        self.singdir = singdir
        self.npiles = npiles
        self.colision = colision
        self.p_spacing = p_spacing
        self.signal = signal

        print(colision)

        self.generate_all_cfg()
        self.filter_cfg()

    def generate_all_cfg(self):

        nInclPiles          = self.npiles-self.nvert
        npos                = len(self.xvec)

        # Pileset matrix
        self.setnr       = int(factorial(npos) / (factorial(npos-self.npiles)*factorial(self.npiles)))
        pilesetmat      = np.array(np.zeros((self.setnr,npos)))
        
        iter = 0
        for i in range(1 << npos):
            set_bin     = format(i, '0' + str(npos) + 'b')
            set_try     = [int(x) for x in [*set_bin]]
            if sum(set_try) == self.npiles:
                pilesetmat[iter,:] = set_try
                iter = iter + 1 

        # Pilexvec and Pileyvec
        self.pilexvec = []; self.pileyvec = []; self.setvec = []
        for i in range(self.setnr):
            pileset = pilesetmat[i]
            xvecset = []; yvecset = []
            for j in range(len(pileset)):
                if pileset[j] != 0:
                    xvecset.append(self.xvec[j])
                    yvecset.append(self.yvec[j])

            self.pilexvec.append(yvecset)
            self.pileyvec.append(xvecset)
            self.setvec.append(pileset)

        # Pileincl matrix
        self.pileinclmat = []
        for i in range(1 << self.npiles):
            incl_bin = format(i, '0' + str(self.npiles) + 'b')
            incl_form = [int(x) for x in [*incl_bin]]
            if sum(incl_form) == nInclPiles:
                incl_try = [x*self.incl for x in incl_form]
                self.pileinclmat.append(incl_try)

        # Piledir matrix
        self.piledirmat = []
        for i in range(1 << nInclPiles):
            bearing_bin = format(i, '0' + str(nInclPiles) + 'b')
            bearing_form = [int(x) for x in [*bearing_bin]]
            npilesDir = sum(bearing_form)
            if npilesDir >= self.singdir and npilesDir <= self.npiles-self.singdir:
                bearing_try_temp = [x*90 for x in bearing_form]
                self.piledirmat.append(bearing_try_temp)


    def filter_cfg(self):
        iter                = 0
        self.nTotCfg        = self.setnr*len(self.piledirmat)*len(self.pileinclmat)
        self.pos_per        = self.setnr
        self.rot_per        = len(self.piledirmat)
        self.inc_per        = len(self.pileinclmat)

        self.bearing_arr    = []
        self.incl_arr       = []
        self.x1vec_arr      = []
        self.y1vec_arr      = []
        self.set_arr        = []

        for i in range(self.setnr):

            if self.signal.running == False:
                return
            while self.signal.paused == True:
                time.sleep(0.1)

            x1vec_try   = self.pilexvec[i]
            y1vec_try   = self.pileyvec[i]
            set_try     = self.setvec[i]
            
            for incl_try in self.pileinclmat:
                for bearing_try_temp in self.piledirmat:

                    bearing_try = np.zeros((self.npiles))
                    step = 0

                    for j in range(self.npiles):
                        if incl_try[j] != 0:
                            bearing_try[j] = bearing_try_temp[step]
                            step = step + 1
                    iter = iter + 1 

                    if iter % int(self.nTotCfg/100) == 0 :
                        self.signal.progress.emit()

                    # Checking for collisions to filter out only suitable configurations
                    if self.check_for_colision(self.colision, self.p_spacing, self.npiles, self.incl, x1vec_try, y1vec_try, bearing_try, incl_try) == False:
                        self.bearing_arr.append(bearing_try)
                        self.incl_arr.append(incl_try)
                        self.x1vec_arr.append(x1vec_try)
                        self.y1vec_arr.append(y1vec_try)
                        self.set_arr.append(set_try)

        self.nSavedCfg = len(self.bearing_arr)

        self.signal.completed.emit()


    def check_for_colision(self, colision, p_spacing, npiles, incl, x1vec_try, y1vec_try, bearing_try, incl_try):

        prec = 1

        for level in colision:
            z = level*p_spacing*incl*0.5
            xy2vec_q = set()

            for i in range(npiles):
                if incl_try[i] == 0:
                    x2vec_q = x1vec_try[i]
                    y2vec_q = y1vec_try[i]
                else:
                    x2vec_q = x1vec_try[i] + np.cos(np.radians(bearing_try[i]))*z/incl_try[i]
                    y2vec_q = y1vec_try[i] + np.sin(np.radians(bearing_try[i]))*z/incl_try[i]

                if x2vec_q <= 0 or y2vec_q <= 0:
                    return True
                
                xy2vec_q.add((round(x2vec_q, prec), round(y2vec_q, prec)))

                if len(xy2vec_q) != i+1:
                    return True
        return False