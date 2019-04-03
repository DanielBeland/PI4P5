from scanBT import *
from datetime import datetime
from collections import deque
from struct import *
import serial
import numpy as np
import time
from threading import Thread, Lock, current_thread
import threading
from queue import Queue, Empty, Full
from stateCheck import check
#connected=scanBT()
#print(connected)
sPort=[]
c_state=[0,0,0]
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
             
def stopThreads(threads):
    for th in reversed(threads):
        th.shutdown_flag.set()
        th.join()
    threads=[]
    
def writeF(val,filename,ext):
    if 'bin' in ext:
        with open(filename, mode='ab') as file:
            binary_format = bytearray(val)
            file.write(binary_format)
    elif 'csv' in ext:
        with open(filename, mode='a',newline='') as data:
            data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for i in range(val.shape[0]):
                data_writer.writerow(val[i,:])
        
def setupF(filename,nbChannel,ext):
    if 'bin' in ext:
        with open(filename, mode='wb') as file:
            binary_format = bytearray(np.arange(nbChannel)+1) #+1 to shift from 0 to 1
            file.write(binary_format)
    elif 'csv' in ext:
        with open(filename, mode='w',newline='') as data:
            data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow(np.arange(nbChannel)+1)
    
def worker_acquisition(q_save,q_check,nbChannel,select_file_lock,connection_lock,test):
    wrongCounter=0
    disC=0
    time1=0
    time2=0
    t = current_thread()
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.timeout = 0.02
    if test:
        port='COM3'
    else :
        port=sPort[0:4] #str(connected[1][-5:-1])
    ser.port = port
    if select_file_lock.acquire():
        select_file_lock.release()
        while not t.shutdown_flag.is_set():
            if test:
                connection_lock.release()
                while not t.shutdown_flag.is_set():
                    data=np.append(np.random.randint(1,1000,size=36), [np.random.randint(0,2,size=2)])
                    q_save.put(data)
                    q_check.put(data)
                    time.sleep(0.005)
            else :
                while not t.shutdown_flag.is_set():
                    try:
            #TODO : enregistrer le temps de connexion
                        ser.open()
                        print('Connected')
                        connection_lock.acquire(blocking=False)
                        connection_lock.release()
                        break
                    except Exception as e:
                        print(e)
                        time.sleep(1)
                while not t.shutdown_flag.is_set() :
                    data=np.zeros((nbChannel+2), dtype=int)
                    dataRaw=np.zeros((nbChannel+1), dtype=int)
                    dataR=ser.read_until()
                    try:
#                        dataRead=ser.read_until()
                        dataRaw=unpack('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',dataR)
                    except Exception as e:
#                        print(e)
                        data[-2]=1
#                        time.sleep(10)
                        if len(dataR)==0:
#                            print('Problem')
                            pass
                            time1=int(round(datetime.now().timestamp() * 1000))
                            if (time1-time2)>3000:
                                disC=1
                                time2=time1
                            else:
                                disC+=1
#                                disC+=1
#                                time2=time1
                                if disC > 15:
                                    disC=0
                                    print('Disconnected')
                                    ser.close()
                                    connection_lock.acquire()
                                    print('Trying to reconnect')
                                    break
#                            else :
#                                disC=1
                        else:
                            pass
                            
#                            wrongCounter+=1
#                            print("WRONG COUNTERRRRRRRRRRR")
        #                    print(wrongCounter)
#                            dataRaw=np.zeros((nbChannel+1), dtype=int)
#                            data[-2]=1
                    
                    
                    
                    data[0:-2]=dataRaw[0:-1]
        #            print(data)
                    q_save.put(data)
                    q_check.put(data)
        print("ACQUISITION TERMINATED")
        
        try:
            ser.close()
        except NameError as e:
            print(e)
    
def worker_write_to_file(q_save,nbChannel,saveSize,fileSaveName,select_file_lock,ext):
    t = current_thread()
    setupF(fileSaveName,nbChannel+2,ext)
    data=[]
    select_file_lock.release()
    timeStart=int(time.time())
    while not t.shutdown_flag.is_set():
        time.sleep(1)
        curr_size = q_save.qsize() # doc says qsize is unreliable but no one else get's from this queue so it should not be that bad
#        print(curr_size)
        if curr_size > saveSize:
            data=np.zeros((curr_size,nbChannel+2), dtype=int)
            for i in range(curr_size):
                data[i] = q_save.get()
                q_save.task_done()
            writeF(data,fileSaveName,ext)
    curr_size = q_save.qsize()
    data=np.zeros((curr_size,nbChannel+2), dtype=int)
    for i in range(curr_size):
        data[i] = q_save.get()
        q_save.task_done()
    writeF(data,fileSaveName,ext)
    writeF(np.asarray([timeStart,int(time.time())]),fileSaveName,ext)
    print('WRITER TERMINATED')

    
def worker_check(q_check,q_save,nbChannel,select_file_lock,connection_lock):
    global c_state
    t = current_thread()
    state1 = deque()
    state2=deque()
    state3=deque()
    while not t.shutdown_flag.is_set():
        if select_file_lock.acquire():
            select_file_lock.release()
            if connection_lock.acquire():
                connection_lock.release()
                print('CHECK STARTED')
                while not t.shutdown_flag.is_set():
                    if connection_lock.acquire(blocking=False):
                        connection_lock.release()
                        try:
                            new=q_check.get(block=True, timeout=0.0105)
                            q_check.task_done()
                            c_state=check(new,state1,state2,state3)
                        except Empty:
    #                        print("EMPTY")
                            pass
                    else:
#                        print('dc')
                        try:
                            new=q_check.get(block=True, timeout=0.01)
                            q_check.task_done()
                        except Empty:
    #                        print("EMPTY")
                            new=np.zeros((nbChannel+2), dtype=int)
                            new[-1]=1
                            q_save.put(new)
                        c_state=check(new,state1,state2,state3)
                        
                    
                    
    c_state=[0,0,0]
    print('CHECKER TERMINATED')

def initializeThreads(fileSaveName,nbChannel,qSize,saveSize,test):
    
    select_file_lock=Lock()
    select_file_lock.acquire(blocking=True)
    
    connection_lock=Lock()
    connection_lock.acquire(blocking=True)
    
    q_save = Queue(qSize)
    q_check = Queue(qSize)
    
    thread_list=[]
    
    t_acq = StopableThread(target=worker_acquisition, args=(q_save,q_check,nbChannel,select_file_lock,connection_lock,test,), name="Acquisition")
    t_acq.start()
    thread_list.append(t_acq)
    
    t_check = StopableThread(target=worker_check, args=(q_check,q_save,nbChannel,select_file_lock,connection_lock,), name="State-Checker")
    t_check.start()
    thread_list.append(t_check)
    
    t_save = StopableThread(target=worker_write_to_file, args=(q_save,nbChannel,saveSize,fileSaveName,select_file_lock,fileSaveName[-4:],), name="Writer")
    t_save.start()
    thread_list.append(t_save)
    
    return thread_list

#if __name__ == '__main__':
#    nbChannel = 18
#    #input = 18 variables, 2 sont ajoutés, 19 : bool si l'entrée est pas du bon format, 20 : bool si le BT est déconecté
#    initializeThreads('ex1.bin',nbChannel,300000,1000,False)
