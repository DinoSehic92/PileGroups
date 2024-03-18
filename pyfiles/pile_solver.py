import numpy as np

from math import atan

from calfem.core import beam3e
from calfem.core import bar3e
from calfem.core import assem
from calfem.core import coordxtr
from calfem.core import solveq

class pileGroupSolver:

    def __init__(self, x1vec, y1vec, x2vec, y2vec, bearing, inclvek, npiles_tot, plen, ep1, ep2, method, lc, nrVal):

        self.x1vec          = x1vec # Coordinate system rotated??
        self.y1vec          = y1vec
        self.x2vec          = x2vec
        self.y2vec          = y2vec
        self.bearing        = bearing
        self.inclvek        = inclvek
        self.npiles_tot     = npiles_tot
        self.plen           = plen
        self.ep1            = ep1
        self.ep2            = ep2
        self.method         = method
        self.lc             = lc
        self.nrVal          = nrVal

        self.Ninfl          = np.zeros((self.npiles_tot,6))
        self.Nvek           = np.zeros((self.npiles_tot,self.nrVal))

        if self.method == 0:
            self.fe_solver()
        if self.method == 1:
            self.pkr_solver()

        self.influence_solver()


    def influence_solver(self):

        for i in range(self.nrVal):
            for j in range(self.npiles_tot):
                self.Nvek[j,i] = self.Ninfl[j,:] @ self.lc[i,:]


    def fe_solver(self):

        self.generate_elements()

        self.bc                     = np.arange((6*self.npiles_tot)+7, self.nDofs+1)

        self.assemble_elements()

        for i in range(6):
            f                       = np.zeros((self.nDofs, 1))
            f[i]                    = 1
            [self.a, self.r]        = solveq(self.K, f, self.bc)
            self.Ninfl[:,i]         = self.analyseResults()


    def pkr_solver(self):
            
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

            U = np.linalg.inv(Sqprim) @ fq

            for i in range(self.npiles_tot):
                xq              = Dq[:,:,i].T @ U
                Fq              = Kq @ xq

                self.Ninfl[i,m] = -Fq[2][0]


    def generate_elements(self):
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

        # Elementdata, bar elements
        self.Coord2             = np.zeros((2*self.npiles_tot, 3))
        self.Dof2               = np.zeros((2*self.npiles_tot, 3))
        self.Edof2              = np.zeros((self.npiles_tot, 6))
        
        for i in range(self.npiles_tot):
            self.Coord2[i, 0] = self.x1vec[i]
            self.Coord2[i, 1] = self.y1vec[i]
        
            self.Coord2[i+self.npiles_tot, 0] = self.x2vec[i]
            self.Coord2[i+self.npiles_tot, 1] = self.y2vec[i]
            self.Coord2[i+self.npiles_tot, 2] = -self.plen
        
        for i in range(2*self.npiles_tot):
            self.Dof2[i, :] = [6*i+7, 6*i+8, 6*i+9]
        
        for i in range(self.npiles_tot):
            self.Edof2[i, :] = [6*i+7, 6*i+8, 6*i+9, 6*i+(6*self.npiles_tot)+7, 6*i+(6*self.npiles_tot)+8, 6*i+(6*self.npiles_tot)+9]
        
        [self.Ex2, self.Ey2, self.Ez2] = coordxtr(self.Edof2, self.Coord2, self.Dof2, 2)

        self.nDofs = int(np.max(self.Edof2))   
        

    def assemble_elements(self): 

        self.K           = np.zeros((self.nDofs, self.nDofs))
        self.Edof1       = self.Edof1.astype(int)
        self.Edof2       = self.Edof2.astype(int)
        
        for i in range(self.npiles_tot):
        
            p1          = np.array([0, 0, 0])
            p2          = np.array([self.Ex1[i, :][0], self.Ey1[i, :][0], self.Ez1[i, :][0]])
            p3          = np.array([self.Ex1[i, :][1], self.Ey1[i, :][1], self.Ez1[i, :][1]])
    
            v1          = np.subtract(p2, p1)
            v2          = np.subtract(p3, p1)
            eo          = np.cross(v1, v2)
        
            self.Ke     = beam3e(self.Ex1[i, :], self.Ey1[i, :], self.Ez1[i, :], eo, self.ep1)
            self.K      = assem(self.Edof1[i, :], self.K, self.Ke)
            self.Ke     = bar3e(self.Ex2[i, :], self.Ey2[i, :], self.Ez2[i, :], self.ep2)
            self.K      = assem(self.Edof2[i, :], self.K, self.Ke)

    
    def generateLoads(self, nr):

        f = np.array(np.zeros((self.nDofs, 1)))

        f[0] = self.lc[nr,0]*1000
        f[1] = self.lc[nr,1]*1000
        f[2] = self.lc[nr,2]*1000
        f[3] = self.lc[nr,3]*1000
        f[4] = self.lc[nr,4]*1000
        f[5] = self.lc[nr,5]*1000

        return f


    def analyseResults(self):

        Npile       = np.zeros((self.npiles_tot))

        nElements   = self.Edof2.shape[0]
        nDofs       = self.Edof2.shape[1]
        Ed          = np.zeros([nElements, nDofs])
        i = 0
        for row in self.Edof2:
            idx = row-1
            Ed[i, :] = self.a[np.ix_(idx)].T
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

            Npile[i] = -eps*E*A

        return Npile
