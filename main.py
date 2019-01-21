import random
import time
import serial
import sys

import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from queue import Queue, Empty, Full
from threading import Thread, Lock, current_thread

from Save_values import *
from real_time_plot import *
from threadStart import tStart
from collections import deque

frameCounter = 1
nbChannel = 4
timeToDisplay = 1000
global latest_data_point
global stopSignal

def worker_acquisition(q_raw,nbChannel):
    t = current_thread()
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.timeout = 2
    while True:
        port='COM11'
        ser.port = port
        ser.open()
        break
#    data=np.zeros((nbChannel), dtype=int)
    while getattr(t, "do_run", True):
        # Acquire
        data=np.zeros((nbChannel), dtype=int)
#        data = np.random.randint(100,size=(11), dtype=int)
        # Delay to emulate the Bluetooth API call
        dataRaw=ser.readline().split(b',')
        data[0:len(dataRaw)-1] = list(map(np.int32, dataRaw[0:len(dataRaw)-1]))
#        data[len(dataRaw):11] = np.random.randint(100,size=(11-len(dataRaw)), dtype=int)

        # Enqueue
        q_raw.put(data)


def worker_integrity_check(q_raw, q_processed, lock, nbChannel):
    global latest_data_point
    t = current_thread()
    firstTime=True
    while getattr(t, "do_run", True):
        try:
            # Dequeue raw
            data = q_raw.get(block=False)
            q_raw.task_done() #necessary for multithreaded operations on Queue
        except Empty:
            if firstTime:
                latest_data_point = np.zeros((nbChannel), dtype=int)
                firstTime=False
            # Reenter the loop if raw queue is empty, maybe sleep to let it some time to fill
            # time.sleep(0.1)
            continue
        # Integrity check and correction
        if  not data.shape[0]==nbChannel:
            data = np.zeros(nbChannel, dtype=int)
        else:
            for x in range(data.shape[0]):
                if (data[x] < 0 or not isinstance(data[x], np.int32)):
                    data[x] = 0
        if lock.acquire(blocking=False): # If lock is taken don't block just pass
            latest_data_point = data
#            print(latest_data_point)
            lock.release()
        # Enqueue processed

        q_processed.put(data)
    
def worker_write_to_file(q_processed,nbChannel):
    setup('data.csv')
    t = current_thread()
    while getattr(t, "do_run", True): 
        time.sleep(1)
        curr_size = q_processed.qsize() # doc says qsize is unreliable but no one else get's from this queue so it should not be that bad
#        print(curr_size)
        if curr_size > 150:
            data=np.zeros((curr_size,nbChannel), dtype=int)
            for i in range(curr_size):
                data[i] = q_processed.get()
                q_processed.task_done()
            write(data,'data.csv')
            

def setupP(n,ttd):
    fig = plt.figure()
    
    xs = np.linspace(1,10,ttd)
    ax=[None]*n
    ys=[None]*n
    line=[None]*n
    for k in range(n):
        ax[k] = fig.add_subplot(n, 1, k+1)
        ax[k].set_ylim(0, 1000)
        ys[k] = deque([0]*ttd)
        
        linek, = ax[k].plot(xs, ys[k])
        line[k]=linek
    return [fig, ax, xs, ys,line,n]

def animate(frameCounter,ax,xs,ys,lines,n):

    for l in range(n):
        
        ys[l].popleft()
        ys[l].append(latest_data_point[l])

        lines[l].set_xdata(xs)
        lines[l].set_ydata(ys[l])

    return lines
    
def plot():
    ani = animation.FuncAnimation(animantionSettings[0], animate,fargs=(animantionSettings[1],animantionSettings[2],animantionSettings[3],animantionSettings[4],animantionSettings[5]), interval=1, blit=True)
    plt.show()
    return ani
            
def main():

    # Initialize the Queue's
    q_raw = Queue(10000)
    q_processed = Queue(10000)

    # Data acquisition worker
    t_acq = Thread(target=worker_acquisition, args=(q_raw,nbChannel,), name="Acquisition")
    tStart(t_acq)

    # Integrity check worker[s]
    # If integrity check is long, add more workers
    num_intergrity_workers = 3
    threads_integrity = []
    latest_data_point_lock = Lock()
    for i in range(num_intergrity_workers):
        t_i = Thread(target=worker_integrity_check, args=(q_raw, q_processed, latest_data_point_lock,nbChannel,), name="Integrity-{}".format(i))
        threads_integrity.append(t_i)
        tStart(t_i)
    
    t_save = Thread(target=worker_write_to_file, args=(q_processed,nbChannel,), name="Writer")
    tStart(t_save)
    # Dans un monde idéal et en supposant que ton programme va grossir, 
    # toutes ces fonctions worker_ devraient en fait être des classes qui héritent de Thread et dont tu redéfinis la fonction run
    # Ça dépend de la complexité voulue, mais tu pourras avoir des attributs pour chaque thread comme ça, au lieu de des variables locales
    return plot()
if __name__ == "__main__":
    try:
        animantionSettings=setupP(nbChannel,timeToDisplay)
        plotData=main()
    except KeyboardInterrupt:
        #Code to close serial connection if KeyboardInterrupt is raised
        raise