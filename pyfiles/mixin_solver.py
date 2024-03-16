import numpy as np

from math import factorial, atan
import time

from calfem.core import beam3e
from calfem.core import bar3e
from calfem.core import bar3s
from calfem.core import assem
from calfem.core import coordxtr
from calfem.core import solveq
#from calfem.core import extractEldisp

class SolverMixin:

    def genBeams(self):
        # Elementdata, beam elements
        self.Coord1             = np.zeros((self.npiles_tot+1, 3))
        self.Dof1               = np.zeros((self.npiles_tot+1, 6))
        self.Edof1              = np.zeros((self.npiles_tot, 12))
    
        dpap                    = 0.000001
        self.Coord1[0, 2]       = dpap

        for i in range(self.npiles_tot):
            self.Coord1[i+1, 0] = self.x1vec[i]
            self.Coord1[i+1, 1] = self.y1vec[i]

        for i in range(self.npiles_tot+1):
            self.Dof1[i, :] = [6*i+1, 6*i+2, 6*i+3, 6*i+4, 6*i+5, 6*i+6]
        
        for i in range(self.npiles_tot):
            self.Edof1[i, :] = [1, 2, 3, 4, 5, 6, 6*i+7, 6*i+8, 6*i+9, 6*i+10, 6*i+11, 6*i+12]
        
        [self.Ex1, self.Ey1, self.Ez1] = coordxtr(self.Edof1, self.Coord1, self.Dof1, 2)

    def genPiles(self):
        # Elementdata, bar elements
        self.Coord2             = np.zeros((2*self.npiles_tot, 3))
        self.Dof2               = np.zeros((2*self.npiles_tot, 3))
        self.Edof2              = np.zeros((self.npiles_tot, 6))
        
        for i in range(self.npiles_tot):
            self.Coord2[i, 0] = self.x1vec[i]
            self.Coord2[i, 1] = self.y1vec[i]
        
            self.Coord2[i+self.npiles_tot, 0] = self.x2vec[i]
            self.Coord2[i+self.npiles_tot, 1] = self.y2vec[i]
            self.Coord2[i+self.npiles_tot, 2] = -self.plenvek[i]
        
        for i in range(2*self.npiles_tot):
            self.Dof2[i, :] = [6*i+7, 6*i+8, 6*i+9]
        
        for i in range(self.npiles_tot):
            self.Edof2[i, :] = [6*i+7, 6*i+8, 6*i+9, 6*i+(6*self.npiles_tot)+7, 6*i+(6*self.npiles_tot)+8, 6*i+(6*self.npiles_tot)+9]
        
        [self.Ex2, self.Ey2, self.Ez2] = coordxtr(self.Edof2, self.Coord2, self.Dof2, 2)

        self.nDofs = int(np.max(self.Edof2))
        

    def assembElem(self):    

        self.K          = np.zeros((self.nDofs, self.nDofs))
        self.Edof1      = self.Edof1.astype(int)
        self.Edof2      = self.Edof2.astype(int)
        
        for i in range(self.npiles_tot):
        
            p1 = np.array([0, 0, 0])
            p2 = np.array([self.Ex1[i, :][0], self.Ey1[i, :][0], self.Ez1[i, :][0]])
            p3 = np.array([self.Ex1[i, :][1], self.Ey1[i, :][1], self.Ez1[i, :][1]])

            v1 = np.subtract(p2, p1)
            v2 = np.subtract(p3, p1)
            eo = np.cross(v1, v2)
        
            Ke = beam3e(self.Ex1[i, :], self.Ey1[i, :], self.Ez1[i, :], eo, self.ep1)
            self.K = assem(self.Edof1[i, :], self.K, Ke)

            Ke = bar3e(self.Ex2[i, :], self.Ey2[i, :], self.Ez2[i, :], self.ep2)
            self.K = assem(self.Edof2[i, :], self.K, Ke)
    

        
    def generateLoads(self,nr):

        f = np.array(np.zeros((self.nDofs, 1)))

        f[0] = self.lc[nr,0]*1000
        f[1] = self.lc[nr,1]*1000
        f[2] = self.lc[nr,2]*1000
        f[3] = self.lc[nr,3]*1000
        f[4] = self.lc[nr,4]*1000
        f[5] = self.lc[nr,5]*1000

        return f


    def analyseResults(self,a):

        Nvek = np.zeros((self.npiles_tot))

        nElements = self.Edof2.shape[0]
        nDofs = self.Edof2.shape[1]
        Ed = np.zeros([nElements, nDofs])
        i = 0
        for row in self.Edof2:
            idx = row-1
            Ed[i, :] = a[np.ix_(idx)].T
            i += 1

        for i in range(self.npiles_tot):

            x1, x2  = self.Ex2[i,:]
            y1, y2  = self.Ey2[i,:]
            z1, z2  = self.Ez2[i,:]

            dx = x2-x1
            dy = y2-y1
            dz = z2-z1
            L = np.sqrt(dx*dx+dy*dy+dz*dz)

            E = self.ep2[0]
            A = self.ep2[1]

            eps = (dx*Ed[i][0]/L + dy*Ed[i][1]/L + dz*Ed[i][2]/L)/L

            Ntest = -eps*E*A

            Nvek[i] = Ntest

        return Nvek

    def pileExpand(self,nr):
        # Expanding pile data from a single quadrant

        a = [1, -1, -1, 1]
        b = [1, 1, -1, -1]
        c = [0, 90, 180, 270]

        # Kvadrantdata
        self.x2vec_q        = np.zeros((self.npiles))
        self.y2vec_q        = np.zeros((self.npiles))
        self.plenvek_q      = np.ones((self.npiles))*self.plen

        # Full data 
        self.bearing        = np.zeros((self.npiles_tot))
        self.x1vec          = np.zeros((self.npiles_tot))
        self.y1vec          = np.zeros((self.npiles_tot))
        self.z1vec          = np.zeros((self.npiles_tot))
        self.x2vec          = np.zeros((self.npiles_tot))
        self.y2vec          = np.zeros((self.npiles_tot))
        self.inclvek        = np.zeros((self.npiles_tot))
        self.plenvek        = np.zeros((self.npiles_tot))
        self.z1vec          = np.zeros((self.npiles_tot))


        # Set current pile config from arr-vec
        self.bearing_q      = self.bearing_arr[nr]
        self.x1vec_q        = self.xvec_arr[nr]
        self.y1vec_q        = self.yvec_arr[nr]
        self.inclvek_q         = self.incl_arr[nr]

        for i in range(self.npiles):
            if self.inclvek_q[i] == 0:
                self.x2vec_q[i] = self.x1vec_q[i]
                self.y2vec_q[i] = self.y1vec_q[i]
            else:
                self.x2vec_q[i] = self.x1vec_q[i] + np.cos(np.radians(self.bearing_q[i]))*self.plen/self.inclvek_q[i]
                self.y2vec_q[i] = self.y1vec_q[i] + np.sin(np.radians(self.bearing_q[i]))*self.plen/self.inclvek_q[i]

        iter = 0
        for i in range(4):
            for j in range(self.npiles):

                self.x1vec[iter]    = a[i]*self.x1vec_q[j]
                self.y1vec[iter]    = b[i]*self.y1vec_q[j]
                self.x2vec[iter]    = a[i]*self.x2vec_q[j]
                self.y2vec[iter]    = b[i]*self.y2vec_q[j]
                self.inclvek[iter]  = self.inclvek_q[j]
                self.plenvek[iter]  = self.plenvek_q[j]

                if i > 0:
                    if self.bearing[iter-self.npiles] == c[i]:
                        self.bearing[iter] = self.bearing[iter-self.npiles]
                    else:
                        self.bearing[iter] = self.bearing[iter-self.npiles] + 180
                else:
                    self.bearing[iter] = self.bearing_q[j]

                iter = iter + 1
    
    def pileInfluenceRun(self):

        print("- Running influence analysis...")

        self.read_loadcases()

        # Materialegenskaper
        E                       = 2.0e11
        A1                      = 1.2193e-2
        
        A                       = 1000.0
        G                       = 1000.0
        Iy                      = 1000.0
        Iz                      = 1000.0
        Kv                      = 1000.0
        
        self.ep1                = [E, G, A, Iy, Iz, Kv]
        self.ep2                = [E, A1]

        self.running                = True
        self.nSolvedCfg    = 0
        process_store               = 0

        self.nMaxPileConfig = np.zeros((self.nSavedCfg,self.npiles_tot))
        self.nMinPileConfig = np.zeros((self.nSavedCfg,self.npiles_tot))
        
        for config in range(self.nSavedCfg):
            self.currentConfig = config

            if self.running != True:
                return
            
            while self.pause == True:
                time.sleep(0.1)

            configprogress = int((100*config)/self.nSavedCfg)
            signals = configprogress - process_store
            for i in range(signals):
                self.signal.progress.emit()
            process_store = configprogress
            
            self.pileExpand(config)

            self.influence_solver() # Combined the influence solver to its own method

            Nvek = np.zeros((self.npiles_tot,self.nrVal))

            for i in range(self.nrVal):
                for j in range(self.npiles_tot):

                    Nvek[j,i] = self.Ninfl[j,:] @ self.lc[i,:]
        
            for i in range(self.npiles_tot):
                self.nMaxPileConfig[config,i] = np.max(Nvek[i])
                self.nMinPileConfig[config,i] = np.min(Nvek[i])
            
            self.signal.check.emit()
            self.nSolvedCfg = self.nSolvedCfg + 1

        if self.running == True:
            self.signal.completed.emit()


    def influence_solver(self):

        # Generates an influence matrix 

        self.Ninfl = np.zeros((self.npiles_tot,6))

        if self.method == 0: # FE Method 

            self.genBeams()
            self.genPiles()  
            
            self.f                  = np.zeros((self.nDofs, 1))
            self.bc                 = np.arange((6*self.npiles_tot)+7, self.nDofs+1)
            self.K                  = np.zeros((self.nDofs, self.nDofs))

            self.assembElem()

            for i in range(6):
                f = np.zeros((self.nDofs, 1))
                f[i] = 1
                [a, r] = solveq(self.K, f, self.bc)
                self.Ninfl[:,i] = self.analyseResults(a)

        if self.method == 1: # Simplified PKR54 method 
            
            unitloads = [1, -1, -1, 1, -1, -1]
            
            for m in range(6):
                fq          = np.zeros((6,1))
                fq[m]       = unitloads[m]

                k33       = self.ep2[0]*self.ep2[1]/self.plen

                Kq          = np.array([[0, 0, 0],
                                        [0, 0, 0],
                                        [0, 0, k33]])

                Sqprim      = np.zeros((6))
                Aq          = np.zeros((3,3))
                Dq          = np.zeros((6,3,self.npiles_tot))

                for i in range(self.npiles_tot):

                    z1 = self.x1vec[i]
                    z2 = self.y1vec[i]

                    alpha = np.radians(self.bearing[i])
                    
                    if self.inclvek[i] == 0:
                        beta = 0
                    else:
                        beta = atan(1/self.inclvek[i])

                    cq =        np.array([  [1, 0, 0],
                                            [0, 1, 0],
                                            [0, 0, 1],
                                            [0, 0, z2],
                                            [0, 0, -z1],
                                            [-z2, z1, 0]])
                    
                    Aq[0,0]         = np.cos(beta) * np.cos(alpha)
                    Aq[0,1]         = -np.sin(alpha)
                    Aq[0,2]         = np.sin(beta) * np.cos(alpha)
                    Aq[1,0]         = np.cos(beta) * np.sin(alpha)
                    Aq[1,1]         = np.cos(alpha)
                    Aq[1,2]         = np.sin(beta) * np.sin(alpha)
                    Aq[2,0]         = -np.sin(beta)
                    Aq[2,1]         = 0
                    Aq[2,2]         = np.cos(beta)

                    Dq[:,:,i]       = cq @ Aq
                    Sqprim          = np.add(Sqprim, Dq[:,:,i] @ Kq @ Dq[:,:,i].T)

                U           = np.linalg.inv(Sqprim) @ fq
                Fstore      = np.zeros((self.npiles_tot))

                for i in range(self.npiles_tot):

                    xq          = Dq[:,:,i].T @ U
                    Fq          = Kq @ xq

                    self.Ninfl[i,m] = -Fq[2][0]


    def checkCollision(self,bearing_try,incl_try,x1vec_q,y1vec_q):

        prec = 1
        for dir in self.colision:
            z = dir*self.p_spacing*self.incl*0.5
            xy2vec_q = set()

            for i in range(self.npiles):
                if incl_try[i] == 0:
                    x2vec_q = x1vec_q[i]
                    y2vec_q = y1vec_q[i]
                else:
                    x2vec_q = x1vec_q[i] + np.cos(np.radians(bearing_try[i]))*z/incl_try[i]
                    y2vec_q = y1vec_q[i] + np.sin(np.radians(bearing_try[i]))*z/incl_try[i]

                if x2vec_q <= 0 or y2vec_q <= 0:
                    return True
                
                xy2vec_q.add((round(x2vec_q, prec), round(y2vec_q, prec)))

                if len(xy2vec_q) != i+1:
                    return True
        return False
    
    def genPileConfigs(self):
        print("- Finding and filtering possible pile configurations...")

        self.running        = True
        self.pause          = False
        self.bearing_arr    = []
        self.incl_arr       = []
        self.xvec_arr       = []
        self.yvec_arr       = []
        self.set_arr        = []

        nInclPiles = self.npiles-self.nvert

        npos = len(self.xvec)

        # Pileset matrix
        setnr           = int(factorial(npos) / (factorial(npos-self.npiles)*factorial(self.npiles)))
        pilesetmat      = np.array(np.zeros((setnr,npos)))
        
        iter = 0
        for i in range(1 << npos):
            set_bin     = format(i, '0' + str(npos) + 'b')
            set_try     = [int(x) for x in [*set_bin]]
            if sum(set_try) == self.npiles:
                pilesetmat[iter,:] = set_try
                iter = iter + 1 

        # Pilexvec and Pileyvec
        pilexvec = []; pileyvec = []; setvec = []
        for i in range(setnr):
            pileset = pilesetmat[i]
            xvec = []; yvec = []
            for j in range(len(pileset)):
                if pileset[j] != 0:
                    xvec.append(self.xvec[j])
                    yvec.append(self.yvec[j])

            pilexvec.append(xvec)
            pileyvec.append(yvec)
            setvec.append(pileset)

        # Pileincl matrix
        pileinclmat = []
        for i in range(1 << self.npiles):
            incl_bin = format(i, '0' + str(self.npiles) + 'b')
            incl_form = [int(x) for x in [*incl_bin]]
            if sum(incl_form) == nInclPiles:
                incl_try = [x*self.incl for x in incl_form]
                pileinclmat.append(incl_try)

        # Piledir matrix
        piledirmat = []
        for i in range(1 << nInclPiles):
            bearing_bin = format(i, '0' + str(nInclPiles) + 'b')
            bearing_form = [int(x) for x in [*bearing_bin]]
            npilesDir = sum(bearing_form)
            if npilesDir >= self.singdir and npilesDir <= self.npiles-self.singdir:
                bearing_try_temp = [x*90 for x in bearing_form]
                piledirmat.append(bearing_try_temp)

        # Generating possible configurations
        n = 0
        self.nTotCfg = setnr*len(piledirmat)*len(pileinclmat)

        self.pos_per = setnr
        self.rot_per = len(piledirmat)
        self.inc_per = len(pileinclmat)

        signalstep = int(self.nTotCfg)/100
        ntemp = 0
        for i in range(setnr):

            if self.running != True:
                return
            
            while self.pause == True:
                time.sleep(0.1)

            x1vec_q = pilexvec[i]
            y1vec_q = pileyvec[i]
            set_try = setvec[i]
            
            for incl_try in pileinclmat:
                for bearing_try_temp in piledirmat:

                    bearing_try = np.zeros((self.npiles))
                    step = 0
                    n = n + 1

                    for j in range(self.npiles):
                        if incl_try[j] != 0:
                            bearing_try[j] = bearing_try_temp[step]
                            step = step + 1
                    ntemp = ntemp +1 
                    
                    if ntemp >= signalstep:
                        self.signal.progress.emit()
                        ntemp = 0

                    # Checking for collisions to filter out only suitable configurations
                    if self.checkCollision(bearing_try,incl_try,x1vec_q,y1vec_q) == False:
                        self.bearing_arr.append(bearing_try)
                        self.incl_arr.append(incl_try)
                        self.xvec_arr.append(x1vec_q)
                        self.yvec_arr.append(y1vec_q)
                        self.set_arr.append(set_try)

        self.nSavedCfg = len(self.bearing_arr)

        print("- Number of possible configurations: " + str(self.nSavedCfg) + " of " + str(self.nTotCfg))

#self = PileOptModel()