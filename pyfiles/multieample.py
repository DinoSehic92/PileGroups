  
# importing the multiprocessing module 
from multiprocessing import Process, Queue
import time
  
def worker1(num, q): 
    
    for i in range(num*10):
        for j in range(num*10):
            for k in range(num*10):
                for m in range(num*10):
                    a = 1
    aa = 1
    q.put(aa)
    print("Finished A")

def worker2(num, q): 
    
    for i in range(num*10):
        for j in range(num*10):
            for k in range(num*10):
                for m in range(num*10):
                    b = 1
    bb = 2
    q.put(bb)
    print("Finished B")
  
def worker3(num, q): 
    
    for i in range(num*10):
        for j in range(num*10):
            for k in range(num*10):
                for m in range(num*10):
                    c = 1
    cc = 3
    q.put(cc)
    print("Finished C")

def worker4(num, q): 
    
    for i in range(num*10):
        for j in range(num*10):
            for k in range(num*10):
                for m in range(num*10):
                    d = 1
    dd = 4
    q.put(dd)
    print("Finished D")


if __name__ == "__main__": 
    # creating processes 
    t0 = time.time()

    store = [0,0,0,0,0,0,0,0]
    for i in range(1):
        s1 = Queue()
        s2 = Queue()
        s3 = Queue()
        s4 = Queue()

        s5 = Queue()
        s6 = Queue()
        s7 = Queue()
        s8 = Queue()

        w1 = Process(target=worker1, args=(10, s1)) 
        w2 = Process(target=worker2, args=(10, s2)) 
        w3 = Process(target=worker3, args=(10, s3)) 
        w4 = Process(target=worker4, args=(10, s4)) 

        w5 = Process(target=worker1, args=(10, s5)) 
        w6 = Process(target=worker2, args=(10, s6)) 
        w7 = Process(target=worker3, args=(10, s7)) 
        w8 = Process(target=worker4, args=(10, s8)) 




        w1.start()
        w2.start()
        w3.start()
        w4.start()

        w5.start()
        w6.start()
        w7.start()
        w8.start()

        w1.join()
        w2.join()
        w3.join()
        w4.join()

        w5.join()
        w6.join()
        w7.join()
        w8.join()

        store[0] = s1.get()
        store[1] = s2.get()
        store[2] = s3.get()
        store[3] = s4.get()
        store[4] = s5.get()
        store[5] = s6.get()
        store[6] = s7.get()
        store[7] = s8.get()

    print(store)


    elapsed = time.time() - t0

    # both processes finished 
    print("MP Done!") 
    print("Elapsed time: " + str(elapsed))



