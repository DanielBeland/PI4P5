import random
import time
import serial
import sys
import datetime as dt
import inspect
import os

import matplotlib
#matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import matplotlib.pyplot as plt

from queue import Queue, Empty, Full
from threading import Thread, Lock, current_thread

from collections import deque
from tkinter import filedialog, Scale
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Save_values import *
from real_time_plot import *
from graph import *

latest_data_point = []
thread_list = []

class StopableThread(threading.Thread):
 
    def __init__(self, level=None, *args, **kwargs):
        super(StopableThread, self).__init__(*args, **kwargs)
 
        # The shutdown_flag is a threading.Event object that
        # indicates whether the thread should be terminated.
        self.shutdown_flag = threading.Event()
 
        # ... Other thread setup code here ...
 
    def run(self):
        print('Thread #%s started' % self.ident)
 
        self._target(*self._args, **self._kwargs)
 
        # ... Clean shutdown code here ...
        print('Thread #%s stopped' % self.ident)
    
def worker_acquisition(q_raw,nbChannel,select_file_lock):
    t = current_thread()
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.timeout = 2
    while True:
        port='COM8'
        ser.port = port
        ser.open()
        break
#    data=np.zeros((nbChannel), dtype=int)
    if select_file_lock.acquire():
        i=0
        while not t.shutdown_flag.is_set():
            # Acquire
#            print(q_raw.qsize())
            data=np.zeros((nbChannel+7), dtype=int)
    #        data = np.random.randint(100,size=(11), dtype=int)
            # Delay to emulate the Bluetooth API call
            dataRaw=ser.readline().split(b',')
            data[0:len(dataRaw)-1] = list(map(np.int32, dataRaw[0:len(dataRaw)-1]))
    
#            data=np.zeros((nbChannel+7), dtype=int)
            i=i+1
#           Formated Data
#            
#            data[0] = np.random.randint(2, dtype=int)
#            data[1:5] = np.random.randint(500, size=4,dtype=int)
#            data[5:15] = np.random.randint(0,1000, size=10,dtype=int)
#            data[15]= np.random.randint(50,100,dtype=int)
#            data[16]= np.random.randint(0,1023,dtype=int)
            data[17] = i
            
#            print(data)
#            time.sleep(0.001)
            # Enqueue
            q_raw.put(data)


def worker_integrity_check(q_raw, q_processed, lock, nbChannel):
    global latest_data_point
    t = current_thread()
    firstTime=True
    ecgData=deque([0]*3)
    ecgFreq=deque([0]*3)
    previousVal=0
    previousTime=0
    emgData1=deque([250]*1000)
    emgData2=deque([250]*1000)
    emgData3=deque([250]*1000)
    emgData4=deque([250]*1000)
    accData1=deque([[300,300,300]]*1000)
    accData2=deque([[300,300,300]]*1000)
    accData3=deque([[300,300]]*1000)
    accData4=deque([[300,300]]*1000)
    rData=deque([0]*1000)
    freqX=np.fft.fftfreq((np.arange(1000)).shape[-1])
    while not t.shutdown_flag.is_set():
        try:
            # Dequeue raw
            data = q_raw.get(block=False)
#            print(data)
            q_raw.task_done() #necessary for multithreaded operations on Queue
        except Empty:
            if firstTime:
                latest_data_point = np.zeros((nbChannel), dtype=int)
                firstTime=False
            # Reenter the loop if raw queue is empty, maybe sleep to let it some time to fill
            # time.sleep(0.1)
            continue
        
        # Integrity check and correction
#        if  not data.shape[0]==nbChannel:
#            data = np.zeros(nbChannel, dtype=int)
#        else:
#            for x in range(data.shape[0]):
#                if (data[x] < 0 or not isinstance(data[x], np.int32)):
#                    data[x] = 0
        processedData=np.zeros((nbChannel), dtype=int)
        [ecgData,ecgFreq,previousVal,previousTime,processedData[0]]=prepECG(ecgData, ecgFreq, previousVal,previousTime, data[0], data[17])
        [emgData1,processedData[1]]=prepEMG(emgData1,data[1])
        [emgData2,processedData[2]]=prepEMG(emgData2,data[2])
        [emgData3,processedData[3]]=prepEMG(emgData3,data[3])
        [emgData4,processedData[4]]=prepEMG(emgData4,data[4])
        [accData1, processedData[5]]=prepACC(accData1,data[5:8])
        [accData2, processedData[6]]=prepACC(accData2,data[8:11])
        [accData3, processedData[7]]=prepACC(accData3,data[11:13])
        [accData4, processedData[8]]=prepACC(accData4,data[13:15])
        [rData, processedData[9]]=prepR(rData, data[15])
        processedData[10] = data[16]
        if lock.acquire(blocking=False): # If lock is taken don't block just pass
            latest_data_point = processedData
#            print(latest_data_point)
            lock.release()
        # Enqueue processed

        q_processed.put(processedData)
    if lock.acquire(blocking=False): # If lock is taken don't block just pass
        latest_data_point = np.zeros((nbChannel), dtype=int)
#            print(latest_data_point)
        lock.release()


def worker_write_to_file(q_processed,nbChannel,select_file_lock,saveSize,fileSaveName):
    setup(fileSaveName)
    t = current_thread()
    select_file_lock.release()
    while not t.shutdown_flag.is_set(): 
        time.sleep(1)
        curr_size = q_processed.qsize() # doc says qsize is unreliable but no one else get's from this queue so it should not be that bad
#        print(curr_size)
        if curr_size > saveSize:
            data=np.zeros((curr_size,nbChannel), dtype=int)
            for i in range(curr_size):
                data[i] = q_processed.get()
                q_processed.task_done()
            write(data,fileSaveName)
    curr_size = q_processed.qsize()
    data=np.zeros((curr_size,nbChannel), dtype=int)
    for i in range(curr_size):
        data[i] = q_processed.get()
        q_processed.task_done()
    write(data,fileSaveName)
    
def initializeThreads(fileSaveName, nbChannel, nbIntegrityWorkers, qSize, saveSize):
    # Initialize the Queue's
    q_raw = Queue(qSize)
    q_processed = Queue(qSize)
    thread_list=[]
    select_file_lock=Lock()
    select_file_lock.acquire(blocking=True)
    # Data acquisition worker
    t_acq = StopableThread(target=worker_acquisition, args=(q_raw,nbChannel,select_file_lock,), name="Acquisition")
    t_acq.start()
    thread_list.append(t_acq)
    # Integrity check worker[s]
    # If integrity check is long, add more workers
    num_intergrity_workers = nbIntegrityWorkers
    threads_integrity = []
    latest_data_point_lock = Lock()
    for i in range(num_intergrity_workers):
        t_i = StopableThread(target=worker_integrity_check, args=(q_raw, q_processed, latest_data_point_lock,nbChannel,), name="Integrity-{}".format(i))
        threads_integrity.append(t_i)
        thread_list.append(t_i)
        t_i.start()
    
    t_save = StopableThread(target=worker_write_to_file, args=(q_processed,nbChannel,select_file_lock,saveSize,fileSaveName,), name="Writer")
    t_save.start()
    thread_list.append(t_save)
    return thread_list

def stopThreads(threads):
    for th in threads:
        th.shutdown_flag.set()
        th.join()
    threads=[]