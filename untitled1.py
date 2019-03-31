from scanBT import *
import serial
import numpy as np
import time
from threading import Thread, Lock, current_thread
import threading
from queue import Queue, Empty, Full
nbChannel = 18
wrongCounter=0
disC=0
t = current_thread()
ser = serial.Serial()
ser.baudrate = 9600
ser.timeout = 2
port='COM3' #str(connected[1][-5:-1])
ser.port = port
ser.open()
while True:

    data=np.zeros((nbChannel+2), dtype=int)
    dataRaw=ser.read_until().split(b',')
    
    data[0:len(dataRaw)-1] = list(map(np.int32, dataRaw[0:len(dataRaw)-1]))
    print(data)
#            print(data
