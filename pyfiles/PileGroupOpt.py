import numpy as np
import win32api, win32con, win32process

import pylightxl as xl

from math import factorial, atan
import time

from calfem.core import beam3e
from calfem.core import bar3e
from calfem.core import bar3s
from calfem.core import assem
from calfem.core import coordxtr
from calfem.core import solveq
#from calfem.core import extractEldisp

class PileOptModel:

    def defineSettings(self,xvec,yvec,npiles,nvert,singdir,plen,incl,path,Nmax,Nmin,pile_dist):

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

        # Lastindata
        self.path               = path

        # Indata en kvadrant
        self.x1vec_q_s          = xvec
        self.y1vec_q_s          = yvec

        self.npiles_q           = npiles
        self.npiles             = npiles*4

        self.incl               = incl
        self.nVertPiles         = nvert
        self.nrSingDirPiles     = singdir
        self.pLen               = plen

        self.Nmaxval            = Nmax
        self.Nminval            = Nmin

        self.pile_dist          = pile_dist

        self.running            = False
        self.pause              = False

        self.readLoadCases()

    def genBeams(self):
        # Elementdata, beam elements
        self.Coord1             = np.zeros((self.npiles+1, 3))
        self.Dof1               = np.zeros((self.npiles+1, 6))
        self.Edof1              = np.zeros((self.npiles, 12))
    
        dpap                    = 0.000001
        self.Coord1[0, 2]       = dpap

        for i in range(self.npiles):
            self.Coord1[i+1, 0] = self.x1vec[i]
            self.Coord1[i+1, 1] = self.y1vec[i]

        for i in range(self.npiles+1):
            self.Dof1[i, :] = [6*i+1, 6*i+2, 6*i+3, 6*i+4, 6*i+5, 6*i+6]
        
        for i in range(self.npiles):
            self.Edof1[i, :] = [1, 2, 3, 4, 5, 6, 6*i+7, 6*i+8, 6*i+9, 6*i+10, 6*i+11, 6*i+12]
        
        [self.Ex1, self.Ey1, self.Ez1] = coordxtr(self.Edof1, self.Coord1, self.Dof1, 2)

    def genPiles(self):
        # Elementdata, bar elements
        self.Coord2             = np.zeros((2*self.npiles, 3))
        self.Dof2               = np.zeros((2*self.npiles, 3))
        self.Edof2              = np.zeros((self.npiles, 6))
        
        for i in range(self.npiles):
            self.Coord2[i, 0] = self.x1vec[i]
            self.Coord2[i, 1] = self.y1vec[i]
        
            self.Coord2[i+self.npiles, 0] = self.x2vec[i]
            self.Coord2[i+self.npiles, 1] = self.y2vec[i]
            self.Coord2[i+self.npiles, 2] = -self.lvec[i]
        
        for i in range(2*self.npiles):
            self.Dof2[i, :] = [6*i+7, 6*i+8, 6*i+9]
        
        for i in range(self.npiles):
            self.Edof2[i, :] = [6*i+7, 6*i+8, 6*i+9, 6*i+(6*self.npiles)+7, 6*i+(6*self.npiles)+8, 6*i+(6*self.npiles)+9]
        
        [self.Ex2, self.Ey2, self.Ez2] = coordxtr(self.Edof2, self.Coord2, self.Dof2, 2)

        self.nDofs = int(np.max(self.Edof2))
        

    def assembElem(self):    

        self.K          = np.zeros((self.nDofs, self.nDofs))
        self.Edof1      = self.Edof1.astype(int)
        self.Edof2      = self.Edof2.astype(int)
        
        for i in range(self.npiles):
        
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
    

    def readLoadCases(self):
        print("- Reading loadcases...")
        # Läser av excelark och genererar matris med samtliga lastfall
        wb = xl.readxl(self.path)
        sheet = wb.ws(ws='Sheet1')

        self.lc_temp =[] # Temporary list for storage before knowing number of loadcases

        for i in range(999):
            FX = sheet.index(row=4+i, col=3)
            FY = sheet.index(row=4+i, col=4)
            FZ = sheet.index(row=4+i, col=5)
            MX = sheet.index(row=4+i, col=6)
            MY = sheet.index(row=4+i, col=7)
            MZ = sheet.index(row=4+i, col=8)

            if FX != '':
                self.lc_temp.append([FX, FY, FZ, MX, MY, MZ])
            else:
                break

        self.nrVal = i

        # Consolidating list into a set size array
        self.lc = np.zeros((self.nrVal,6))
        for i in range(self.nrVal): 
            self.lc[i,:] = self.lc_temp[i]

        
    def generateLoads(self,nr):

        f = np.array(np.zeros((self.nDofs, 1)))

        f[0] = self.lc[nr,0]*1000
        f[1] = self.lc[nr,1]*1000
        f[2] = self.lc[nr,2]*1000
        f[3] = self.lc[nr,3]*1000
        f[4] = self.lc[nr,4]*1000
        f[5] = self.lc[nr,5]*1000

        return f


    def analyseLoadcases(self,f):
        [a, r] = solveq(self.K, f, self.bc)

        return a, r


    def analyseResults(self,a):

        Nvek = np.zeros((self.npiles))

        nElements = self.Edof2.shape[0]
        nDofs = self.Edof2.shape[1]
        Ed = np.zeros([nElements, nDofs])
        i = 0
        for row in self.Edof2:
            idx = row-1
            Ed[i, :] = a[np.ix_(idx)].T
            i += 1

        for i in range(self.npiles):
            #Ed = extractEldisp(self.Edof2[i, :], a)
            #N  = bar3s(self.Ex2[i, :], self.Ey2[i, :], self.Ez2[i, :], self.ep2, Ed)
            
            # previous approach relied on bar3s and extraxtEldisp from CALFEM to solve for Normal force from
            # global displacement vec a. Performed more efficiently without CALFEM, but kept for reference and comparison

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

            #Nold = round(N[0][0],5)
            #Nprint = round(Ntest,5)

            #if Nprint != Nold: 
                #print("ERROR")


            Nvek[i] = Ntest

        return Nvek

    
    def returnPileGroup(self):
        print(self.bearing_q)
        print(self.x1vec_q)
        print(self.y1vec_q)

    def pileExpand(self,nr):
        # Expanding pile data from a single quadrant

        a = [1, -1, -1, 1]
        b = [1, 1, -1, -1]
        c = [0, 90, 180, 270]

        # Kvadrantdata
        self.x2vec_q        = np.zeros((self.npiles_q))
        self.y2vec_q        = np.zeros((self.npiles_q))
        self.lvec_q         = np.ones((self.npiles_q))*self.pLen

        # Full data 
        self.bearing        = np.zeros((self.npiles_q*4))
        self.x1vec          = np.zeros((self.npiles_q*4))
        self.y1vec          = np.zeros((self.npiles_q*4))
        self.z1vec          = np.zeros((self.npiles_q*4))
        self.x2vec          = np.zeros((self.npiles_q*4))
        self.y2vec          = np.zeros((self.npiles_q*4))
        self.incl           = np.zeros((self.npiles_q*4))
        self.lvec           = np.zeros((self.npiles_q*4))
        self.z1vec          = np.zeros((self.npiles_q*4))


        # Set current pile config from arr-vec
        self.bearing_q      = self.bearing_arr[nr]
        self.x1vec_q        = self.xvec_arr[nr]
        self.y1vec_q        = self.yvec_arr[nr]
        self.incl_q         = self.incl_arr[nr]

        for i in range(self.npiles_q):
            if self.incl_q[i] == 0:
                self.x2vec_q[i] = self.x1vec_q[i]
                self.y2vec_q[i] = self.y1vec_q[i]
            else:
                self.x2vec_q[i] = self.x1vec_q[i] + np.cos(np.radians(self.bearing_q[i]))*self.pLen/self.incl_q[i]
                self.y2vec_q[i] = self.y1vec_q[i] + np.sin(np.radians(self.bearing_q[i]))*self.pLen/self.incl_q[i]

        iter = 0
        for i in range(4):
            for j in range(self.npiles_q):

                self.x1vec[iter]    = a[i]*self.x1vec_q[j]
                self.y1vec[iter]    = b[i]*self.y1vec_q[j]
                self.x2vec[iter]    = a[i]*self.x2vec_q[j]
                self.y2vec[iter]    = b[i]*self.y2vec_q[j]
                self.incl[iter]     = self.incl_q[j]
                self.lvec[iter]     = self.lvec_q[j]

                if i > 0:
                    if self.bearing[iter-self.npiles_q] == c[i]:
                        self.bearing[iter] = self.bearing[iter-self.npiles_q]
                    else:
                        self.bearing[iter] = self.bearing[iter-self.npiles_q] + 180
                else:
                    self.bearing[iter] = self.bearing_q[j]

                iter = iter + 1
    
    def pileInfluenceRun(self,signal_get,prio,method):

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        if prio == 3:
            print("Prio 3"); win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
        if prio == 2:
            print("Prio 2"); win32process.SetPriorityClass(handle, win32process.NORMAL_PRIORITY_CLASS)
        if prio == 1:
            print("Prio 1"); win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
        if prio == 0:
            print("Prio 0"); win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)
        
        print("- Running influence analysis...")
        self.running                = True
        self.signal                 = signal_get
        self.numberSolvedConfigs    = 0
        process_store               = 0

        self.nMaxPileConfig = np.zeros((self.nrConfigs,self.npiles))
        self.nMinPileConfig = np.zeros((self.nrConfigs,self.npiles))
        
        for config in range(self.nrConfigs):
            self.currentConfig = config

            if self.running != True:
                return
            
            while self.pause == True:
                time.sleep(0.1)

            configprogress = int((100*config)/self.nrConfigs)
            signals = configprogress - process_store
            for i in range(signals):
                self.signal.progress.emit()
            process_store = configprogress
            
            self.pileExpand(config)

            self.influence_solver(method) # Combined the influence solver to its own method

            Nvek = np.zeros((self.npiles,self.nrVal))

            for i in range(self.nrVal):
                for j in range(self.npiles):

                    Nvek[j,i] = self.Ninfl[j,:] @ self.lc[i,:]
        
            for i in range(self.npiles):
                self.nMaxPileConfig[config,i] = np.max(Nvek[i])
                self.nMinPileConfig[config,i] = np.min(Nvek[i])
            
            self.signal.check.emit()
            self.numberSolvedConfigs = self.numberSolvedConfigs + 1

        if self.running == True:
            self.signal.completed.emit()


    def influence_solver(self,method):

        # Generates an influence matrix 

        self.Ninfl = np.zeros((self.npiles,6))

        if method == 0: # FE Method 

            self.genBeams()
            self.genPiles()  
            
            self.f                  = np.zeros((self.nDofs, 1))
            self.bc                 = np.arange((6*self.npiles)+7, self.nDofs+1)
            self.K                  = np.zeros((self.nDofs, self.nDofs))

            self.assembElem()

            for i in range(6):
                f = np.zeros((self.nDofs, 1))
                f[i] = 1
                a, r = self.analyseLoadcases(f)
                self.Ninfl[:,i] = self.analyseResults(a)

        if method == 1: # Simplified PKR54 method 
            
            unitloads = [1, -1, -1, 1, -1, -1]
            
            for m in range(6):
                fq          = np.zeros((6,1))
                fq[m]       = unitloads[m]

                k33       = self.ep2[0]*self.ep2[1]/self.pLen

                Kq          = np.array([[0, 0, 0],
                                        [0, 0, 0],
                                        [0, 0, k33]])

                Sqprim      = np.zeros((6))
                Aq          = np.zeros((3,3))
                Dq          = np.zeros((6,3,self.npiles))

                for i in range(self.npiles):

                    z1 = self.x1vec[i]
                    z2 = self.y1vec[i]

                    alpha = np.radians(self.bearing[i])
                    
                    if self.incl[i] == 0:
                        beta = 0
                    else:
                        beta = atan(1/self.incl[i])

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
                Fstore      = np.zeros((self.npiles))

                for i in range(self.npiles):

                    xq          = Dq[:,:,i].T @ U
                    Fq          = Kq @ xq

                    self.Ninfl[i,m] = -Fq[2][0]


    def SingleRun(self,selectedConfig):

        print("- Running single config analysis...")

        self.pileExpand(selectedConfig)
        self.genBeams()
        self.genPiles()

        self.f                  = np.zeros((self.nDofs, 1))
        self.bc                 = np.arange((6*self.npiles)+7, self.nDofs+1)
        self.K                  = np.zeros((self.nDofs, self.nDofs))

        self.assembElem()

        Nmat = np.zeros((self.npiles,self.nrVal))

        for i in range(self.nrVal):
            f = self.generateLoads(i)
            a, r = self.analyseLoadcases(f)
            Nmat[:,i] = self.analyseResults(a)

        self.nmax_single = round(0.001*np.max(Nmat))
        self.nmin_single = round(0.001*np.min(Nmat))

        self.nmax_single_pile = np.zeros((self.npiles))
        self.nmin_single_pile = np.zeros((self.npiles))

        for i in range(self.npiles):
            self.nmax_single_pile[i] = round(0.001*np.max(Nmat[i,:]))
            self.nmin_single_pile[i] = round(0.001*np.min(Nmat[i,:]))

        print("Konfiguration " + str(selectedConfig) + ": " + str(self.nmax_single) + ", " + str(self.nmin_single))


    def checkCollision(self,bearing_try,incl_try,x1vec_q,y1vec_q,dirvec):

        prec = 1

        for dir in dirvec:
            #if dir == 0:
            #    return False

            z = dir*self.pile_dist*self.incl*0.5

            xy2vec_q = set()

            for i in range(self.npiles_q):
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
    
    def genPileConfigs(self,colision,signal_get,prio):
        print("- Finding and filtering possible pile configurations...")

        pid = win32api.GetCurrentProcessId()
        handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
        if prio == 3:
            print("Prio 3"); win32process.SetPriorityClass(handle, win32process.BELOW_NORMAL_PRIORITY_CLASS)
        if prio == 2:
            print("Prio 2"); win32process.SetPriorityClass(handle, win32process.NORMAL_PRIORITY_CLASS)
        if prio == 1:
            print("Prio 1"); win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)
        if prio == 0:
            print("Prio 0"); win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)


        self.running        = True

        self.signal = signal_get

        self.bearing_arr    = []
        self.incl_arr       = []
        self.xvec_arr       = []
        self.yvec_arr       = []
        self.set_arr        = []

        nInclPiles = self.npiles_q-self.nVertPiles

        npos = len(self.x1vec_q_s)

        # Pileset matrix
        setnr = int(factorial(npos) / (factorial(npos-self.npiles_q)*factorial(self.npiles_q)))
        pilesetmat = np.array(np.zeros((setnr,npos)))
        
        iter = 0
        for i in range(1 << npos):
            set_bin = format(i, '0' + str(npos) + 'b')
            set_try = [int(x) for x in [*set_bin]]
            if sum(set_try) == self.npiles_q:
                pilesetmat[iter,:] = set_try
                iter = iter + 1 

        # Pilexvec and Pileyvec
        pilexvec = []; pileyvec = []; setvec = []
        for i in range(setnr):
            pileset = pilesetmat[i]
            xvec = []; yvec = []
            for j in range(len(pileset)):
                if pileset[j] != 0:
                    xvec.append(self.x1vec_q_s[j])
                    yvec.append(self.y1vec_q_s[j])

            pilexvec.append(xvec)
            pileyvec.append(yvec)
            setvec.append(pileset)


        # Pileincl matrix
        pileinclmat = []
        for i in range(1 << self.npiles_q):
            incl_bin = format(i, '0' + str(self.npiles_q) + 'b')
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
            if npilesDir >= self.nrSingDirPiles and npilesDir <= self.npiles_q-self.nrSingDirPiles:
                bearing_try_temp = [x*90 for x in bearing_form]
                piledirmat.append(bearing_try_temp)

        # Generating possible configurations
        n = 0
        self.totConfigs = setnr*len(piledirmat)*len(pileinclmat)

        self.pos_per = setnr
        self.rot_per = len(piledirmat)
        self.inc_per = len(pileinclmat)

        signalstep = int(self.totConfigs)/100
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

                    bearing_try = np.zeros((self.npiles_q))
                    step = 0
                    n = n + 1
                    for j in range(self.npiles_q):
                        if incl_try[j] != 0:
                            bearing_try[j] = bearing_try_temp[step]
                            step = step + 1
                    ntemp = ntemp +1 
                    if ntemp >= signalstep:
                        self.signal.progress.emit()
                        ntemp = 0
                    
                    # Checking for collisions to filter out only suitable configurations
                    if self.checkCollision(bearing_try,incl_try,x1vec_q,y1vec_q,colision) == False:
                        self.bearing_arr.append(bearing_try)
                        self.incl_arr.append(incl_try)
                        self.xvec_arr.append(x1vec_q)
                        self.yvec_arr.append(y1vec_q)
                        self.set_arr.append(set_try)

        self.nrConfigs = len(self.bearing_arr)

        print("- Number of possible configurations: " + str(self.nrConfigs) + " of " + str(self.totConfigs))

#self = PileOptModel()