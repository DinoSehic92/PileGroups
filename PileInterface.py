#from pyfiles import PileGroupOpt as pgo

import pyfiles

pgo = pyfiles.PileOptModel()



path        = "C:\\Utvecklingsprojekt\\PileGroups\\Underlag\Loadcases.xlsx"
nrVal       = 136  # 60,136, 640

xvec        = [0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5]
yvec        = [2, 3, 4, 2, 3, 4, 2, 3, 4]

npiles      = 8
incl        = 4
nvert       = 0
singdir     = 3
plen        = 9

Nmax        = 0
Nmin        = -2300



pyfiles.PileOptModel.defineSettings(pgo,xvec,yvec,npiles,nvert,singdir,plen,incl,path,nrVal,Nmax,Nmin)
pyfiles.PileOptModel.genPileConfigs(pgo)
pyfiles.PileOptModel.readLoadCases(pgo)
pyfiles.PileOptModel.pileInfluenceRun(pgo)
