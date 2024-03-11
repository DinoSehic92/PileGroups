import pyfiles
import numpy as np 
import time

from PySide6.QtCore import Signal, QObject

#from multiprocessing import Process, Queue
import threading

pg_data = pyfiles.PileOptModel()

class MainTestClass:


            #print(str(round(np.max(nMaxPileConfig[i]))) + " | " + str(round(np.min(nMinPileConfig[i]))))

    def worker_boss_easy(self):


        w1 = threading.Thread(target=self.worker1, args=(0, 100)) 
        #w2 = threading.Thread(target=self.worker2, args=(100, 100)) 
        #w3 = threading.Thread(target=self.worker3, args=(200, 100)) 
        #w4 = threading.Thread(target=self.worker3, args=(300, 100)) 

        w1.start()
        #w2.start()
        #w3.start()
        #w4.start()

        w1.join()
        #w2.join()
        #w3.join()
       # w4.join()

        



    
    def worker1(self, startConfig, chunk):
        nMax, nMin = pyfiles.pileInfluenceRun(self.setupdata, startConfig, chunk)
        #q1.put([nMax,nMin])


    def worker2(self, startConfig, chunk):
        nMax, nMin = pyfiles.pileInfluenceRun(self.setupdata, startConfig, chunk)
        #q2.put([nMax,nMin])
        
    def worker3(self, startConfig, chunk):
        nMax, nMin = pyfiles.pileInfluenceRun(self.setupdata, startConfig, chunk)
        #q2.put([nMax,nMin])

    def generate_configs(self):

        self.signal = 0
        self.prio = 1

        pyfiles.PileOptModel.genPileConfigs(pg_data,self.colision,self.signal,self.prio)
        self.setupdata = pg_data.bearing_arr, pg_data.incl_arr, pg_data.xvec_arr, pg_data.yvec_arr, pg_data.npiles_q, pg_data.pLen, pg_data.ep1, pg_data.ep2, pg_data.nrVal, pg_data.lc

        
    def read_input(self):
        npiles          = 6
        nvert           = 0
        singdir         = 2
        plen            = 7
        incl            = 4
        path            = "C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases4.xlsx"
        
        self.NmaxLim = 200
        self.NminLim = -3000

        self.pile_d          = 0.8
        
        self.colision        = [-2, -1, 0, 1, 2]

        self.xvec            = [1.6, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8, 0.8, 0.8, 0.8]
        self.yvec            = [4.6, 3.8, 3.0, 2.2, 1.4, 4.6, 3.8, 3.0, 2.2, 1.4]


        pyfiles.PileOptModel.defineSettings(pg_data,self.xvec,self.yvec,npiles,nvert,singdir,plen,incl,path,self.NmaxLim,self.NminLim,self.pile_d)

self = MainTestClass()


if __name__ == "__main__": 
    print("Test")

    self.read_input()
    self.generate_configs()
    

    t0=time.time()
    self.worker_boss_easy()
    #nMax, nMin = pyfiles.pileInfluenceRun(self.setupdata, 200, 10)
#
    #for i in range(len(nMax)):
    #    print(str(round(np.max(nMax[i]))) + " | " + str(round(np.min(nMin[i]))))

    #self.worker_boss_easy()

    ela = time.time()-t0

    print(ela)
