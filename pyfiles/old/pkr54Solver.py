import numpy as np
import math
import time

def pkr_full():
    # Full implementation of PÅLKOMMISSIONENS RAPPORT 54


    xvec        = [1.6, 1.6, 1.6, 1.6, 0.8, 0.8, -1.6, -1.6, -1.6, -1.6, -0.8, -0.8, -1.6, -1.6, -1.6, -1.6, -0.8, -0.8, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8]
    yvec        = [4.6, 3.8, 3.0, 2.2, 4.6, 2.2, 4.6, 3.8, 3.0, 2.2, 4.6, 2.2, -4.6, -3.8, -3.0, -2.2, -4.6, -2.2, -4.6, -3.8, -3.0, -2.2, -4.6, -2.2]

    bearing     = [0, 0, 90, 90, 0, 90, 180, 180, 90, 90, 180, 90, 180, 180, 270, 270, 180, 270, 360, 360, 270, 270, 360, 270]
    incl        = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    lenvec      = [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]


    fq          = np.zeros((6,1))
    fq[4]       = 200



    E           = 210e9
    A           = 0.0012
    L           = 10
    m           = 0

    k11 = k22 = 0
    k15 = k51 = 0
    k24 = k42 = 0
    k33       = A*E/L
    k44 = k55 = 0
    k66       = 0


    Kq          = np.array([[k11, 0, 0, 0, k15, 0],
                            [0, k22, 0, k24, 0, 0],
                            [0, 0, k33, 0, 0, 0],
                            [0, k42, 0, k44, 0, 0],
                            [k51, 0, 0, 0, k55, 0],
                            [0, 0, 0, 0, 0, k66]])

    npiles      = len(xvec)
    Sqprim      = np.zeros((6))

    cqstore     = []
    Aqstore     = []

    cq = np.zeros((6,6,npiles))
    Aq = np.zeros((6,6,npiles))

    for i in range(npiles):

        z1 = xvec[i]
        z2 = yvec[i]
        z3 = 0

        alpha = np.radians(bearing[i])
        beta = math.atan(1/incl[i])

        cq[:,:,i] = np.array([  [1, 0, 0, 0, 0, 0],
                                [0, 1, 0, 0, 0, 0],
                                [0, 0, 1, 0, 0, 0],
                                [0, -z3, z2, m, 0, 0],
                                [z3, 0, -z1, 0, m, 0],
                                [-z2, z1, 0, 0, 0, m]])
        

        
        Aq[0,0,i] = Aq[3,3,i] = np.cos(beta) * np.cos(alpha)
        Aq[0,1,i] = Aq[3,4,i] = -np.sin(alpha)
        Aq[0,2,i] = Aq[3,5,i] = np.sin(beta) * np.cos(alpha)
        Aq[1,0,i] = Aq[4,3,i] = np.cos(beta) * np.sin(alpha)
        Aq[1,1,i] = Aq[4,4,i] = np.cos(alpha)
        Aq[1,2,i] = Aq[4,5,i] = np.sin(beta) * np.sin(alpha)
        Aq[2,0,i] = Aq[5,3,i] = -np.sin(beta)
        Aq[2,1,i] = Aq[5,4,i] = 0
        Aq[2,2,i] = Aq[5,5,i] = np.cos(beta)




        Dq = cq[:,:,i] @ Aq[:,:,i]

        Sqprim = np.add(Sqprim, Dq @ Kq @ Dq.T)


    U = np.linalg.inv(Sqprim) @ fq

    Fstore = np.zeros((npiles))

    for i in range(npiles):
        
        Dq = cq[:,:,i] @ Aq[:,:,i]

        xq = Dq.T @ U

        Fq = Kq @ xq

        Fstore[i] = round(Fq[2][0])

    print(Fstore)


def pkr_reduced():
    # Testing out if approach could be reduced/simplified for current situation


    xvec        = [1.6, 1.6, 1.6, 1.6, 0.8, 0.8, -1.6, -1.6, -1.6, -1.6, -0.8, -0.8, -1.6, -1.6, -1.6, -1.6, -0.8, -0.8, 1.6, 1.6, 1.6, 1.6, 0.8, 0.8]
    yvec        = [4.6, 3.8, 3.0, 2.2, 4.6, 2.2, 4.6, 3.8, 3.0, 2.2, 4.6, 2.2, -4.6, -3.8, -3.0, -2.2, -4.6, -2.2, -4.6, -3.8, -3.0, -2.2, -4.6, -2.2]

    bearing     = [0, 0, 90, 90, 0, 90, 180, 180, 90, 90, 180, 90, 180, 180, 270, 270, 180, 270, 360, 360, 270, 270, 360, 270]
    incl        = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
    lenvec      = [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]


    fq          = np.zeros((6,1))
    fq[4]       = 200



    E           = 210e9
    A           = 0.0012
    L           = 10
    m           = 0

    k11 = k22 = 0
    k15 = k51 = 0
    k24 = k42 = 0
    k33       = A*E/L
    k44 = k55 = 0
    k66       = 0


    Kq          = np.array([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, k33]])

    npiles      = len(xvec)
    Sqprim      = np.zeros((6))


    Aq = np.zeros((3,3))
    Dq = np.zeros((6,3,npiles))

    for i in range(npiles):

        z1 = xvec[i]
        z2 = yvec[i]
        z3 = 0

        alpha = np.radians(bearing[i])
        beta = math.atan(1/incl[i])

        cq =        np.array([  [1, 0, 0],
                                [0, 1, 0],
                                [0, 0, 1],
                                [0, -z3, z2],
                                [z3, 0, -z1],
                                [-z2, z1, 0]])
        

        
        Aq[0,0] = np.cos(beta) * np.cos(alpha)
        Aq[0,1] = -np.sin(alpha)
        Aq[0,2] = np.sin(beta) * np.cos(alpha)
        Aq[1,0] = np.cos(beta) * np.sin(alpha)
        Aq[1,1] = np.cos(alpha)
        Aq[1,2] = np.sin(beta) * np.sin(alpha)
        Aq[2,0] = -np.sin(beta)
        Aq[2,1] = 0
        Aq[2,2] = np.cos(beta)




        Dq[:,:,i] = cq @ Aq

        Sqprim = np.add(Sqprim, Dq[:,:,i] @ Kq @ Dq[:,:,i].T)


    U = np.linalg.inv(Sqprim) @ fq

    Fstore = np.zeros((npiles))

    for i in range(npiles):

        xq = Dq[:,:,i].T @ U
        Fq = Kq @ xq
        Fstore[i] = round(Fq[2][0])

    print(Fstore)
    


t0 = time.time()
for i in range(1):
    pkr_full()
    pkr_reduced()
elapsed = time.time() - t0

print(elapsed)
