# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 14:42:00 2019

@author: Olivier
"""
import random
import time
import serial
import sys
import datetime as dt

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
from tkinter import filedialog
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Save_values import *
from real_time_plot import *
from threadStart import tStart

global load
global latest_data_point
global stopSignal

file_path=[]
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(5,5), dpi=100)
nbChannel=11
frameCounter = 1
timeToDisplay = 1000 
#val= np.random.randint(1000,size=(1,nbChannel), dtype=int)
load=False

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
    
def worker_acquisition(q_raw,nbChannel):
    t = current_thread()
    ser = serial.Serial()
    ser.baudrate = 9600
    ser.timeout = 2
#    while True:
#        port='COM11'
#        ser.port = port
#        ser.open()
#        break
#    data=np.zeros((nbChannel), dtype=int)
    while not t.shutdown_flag.is_set():
        # Acquire
        data=np.zeros((nbChannel), dtype=int)
#        data = np.random.randint(100,size=(11), dtype=int)
        # Delay to emulate the Bluetooth API call
#        dataRaw=ser.readline().split(b',')
#        data[0:len(dataRaw)-1] = list(map(np.int32, dataRaw[0:len(dataRaw)-1]))
        data = np.random.randint(1000,size=(11), dtype=int)
        print(data)
        time.sleep(0.01)
        # Enqueue
        q_raw.put(data)


def worker_integrity_check(q_raw, q_processed, lock, nbChannel):
    global latest_data_point
    t = current_thread()
    firstTime=True
    while not t.shutdown_flag.is_set():
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
    while not t.shutdown_flag.is_set(): 
        time.sleep(10)
        curr_size = q_processed.qsize() # doc says qsize is unreliable but no one else get's from this queue so it should not be that bad
#        print(curr_size)
        if curr_size > 1000:
            data=np.zeros((curr_size,nbChannel), dtype=int)
            for i in range(curr_size):
                data[i] = q_processed.get()
                q_processed.task_done()
            write(data,'data.csv')
    curr_size = q_processed.qsize()
    data=np.zeros((curr_size,nbChannel), dtype=int)
    for i in range(curr_size):
        data[i] = q_processed.get()
        q_processed.task_done()
    write(data,'data.csv')


def setupP(n,fig,ttd):
    global latest_data_point
    latest_data_point = np.zeros(n, dtype=int)
    xs = np.linspace(1,10,ttd)
    ax=[None]*n
    ys=[None]*n
    line=[None]*n
    for k in range(n):
        ax[k] = fig.add_subplot(n, 1, k+1)
        ax[k].set_ylim(0, 1023) #Changer pour chaque capteur
        ys[k] = deque([0]*ttd)
        
        linek, = ax[k].plot(xs, ys[k])
        line[k]=linek
    return [ax, xs, ys,line,n]

def animate(frameCounter,ax,xs,ys,lines,n):

    for l in range(n):
        
        ys[l].popleft()
        ys[l].append(latest_data_point[l])

        lines[l].set_xdata(xs)
        lines[l].set_ydata(ys[l])

    # Format plot
#    plt.xticks(rotation=45, ha='right')
#    plt.subplots_adjust(bottom=0.30)
    return lines
# Set up plot to call animate() function periodically
    
    
    
#    
#    pullData = open("sampleData.txt","r").read()
#    dataList=pullData.split('\n')
#    xList=val
#    yList=[]

def loadData(self):
    global load
    file_path=select_file()
    setup_data=setup_save_plot(file_path)
    spos=plot_save_data(setup_data[0],setup_data[1],setup_data[2])
    update_ax(spos,setup_data[0],setup_data[1],setup_data[2])
    load=True
    return setup_data[1]


class PolyleptiqueApp(tk.Tk):
    
    def __init__(self,*args,**kwargs):
        
        
        tk.Tk.__init__(self,*args,**kwargs)
        
#        tk.Tk.iconbitmap(self,default="logo.ico")
        tk.Tk.wm_title(self, "Polyleptique")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames= {}
        
        for F in (StartPage, PageOne, PageTwo):
        
            frame = F(container, self)
            
            self.frames[F] = frame
            
            frame.grid(row=0,column=0,sticky="nsew")
            
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        frame=self.frames[cont]
        frame.tkraise()
        frame.event()
        
#    def on_exit(self):
#        """When you click to exit, this function is called"""
#        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
#            self.destroy()
        
        

class StartPage(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Start Page",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button_new=ttk.Button(self, text="Start new recording",
                          command=lambda: controller.show_frame(PageOne))
        
        button_new.pack()
        
        button_load=ttk.Button(self, text="Load previous data",
                              command=lambda: controller.show_frame(PageTwo))
        button_load.pack() 
        
    def event(self):
        pass
        
class PageOne(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Page 1",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button1=ttk.Button(self, text="Back To home",
                          command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
    def event(self):
        pass
        
class PageTwo(tk.Frame):
    def __init__(self,parent,controller):

        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Page 2",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button1=ttk.Button(self, text="Back To home",
                          command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        
        
    def event(self):

            
        if load==True:
            MsgBox=tk.messagebox.askquestion("New Data","Do you want to load new data?")
            if MsgBox=='yes':
                self.canvas.get_tk_widget().destroy()
                setup_data=loadData(self)
                self.canvas_load = FigureCanvasTkAgg(setup_data, self)
                self.canvas_load.draw()
                self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
                self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
            else:
                pass
        else:
            setup_data=loadData(self)
            self.canvas_load = FigureCanvasTkAgg(setup_data, self)
            self.canvas_load.draw()
            toolbar = NavigationToolbar2Tk(self.canvas, self)
            toolbar.update()
            self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
            self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
#class PageThree(tk.Frame):
#    def __init__(self,parent,controller):
#        tk.Frame.__init__(self,parent)
#        label=ttk.Label(self,text="Graph Page",font=LARGE_FONT)
#        
#        label.pack(pady=10,padx=10)
#        
#        button1=ttk.Button(self, text="Back To home",
#                          command=lambda: controller.show_frame(StartPage))
#        
#        button1.pack()
#
#        canvas = FigureCanvasTkAgg(fig, self)
#        canvas.draw()
#        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
#        
#        toolbar = NavigationToolbar2Tk(canvas, self)
#        toolbar.update()
#        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
#        
#    def event(self):
#        pass
#def updateVal():
#    return np.random.randint(1000,size=(1,nbChannel), dtype=int)
def select_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    return file_path
def setup_save_plot(file_path):
    data = np.genfromtxt(file_path, delimiter=',')
    fig_load=Figure()
    ax=[None]*data.shape[1]
    for k in range(data.shape[1]):
        ax[k] = fig_load.add_subplot(data.shape[1], 1, k+1)
        plt.subplots_adjust(bottom=0.25)
        ax[k].axis([0, 10, 0, 1])
    return[data,fig_load,ax]

def plot_save_data(data,fig_load,ax):
    for k in range(data.shape[1]):
        ax[k].plot(np.arange(data.shape[0]-1),data[1:data.shape[0],k],'b')
        axpos = plt.axes([0.2, 0.1, 0.65, 0.03])
    spos = Slider(axpos, 'Pos', 0.1, data.shape[0]-12)
    return spos
def update_ax(spos,data,fig_load,ax):
    def update(val):
        pos=spos.val
        for k in range(data.shape[1]):
            ax[k].axis([pos,pos+10,-1,1])
            fig_load.canvas.draw_idle()

    spos.on_changed(update)

        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()   
             
# Initialize the Queue's
q_raw = Queue(10000)
q_processed = Queue(10000)
thread_list=[]
# Data acquisition worker
t_acq = StopableThread(target=worker_acquisition, args=(q_raw,nbChannel,), name="Acquisition")
t_acq.start()
thread_list.append(t_acq)
# Integrity check worker[s]
# If integrity check is long, add more workers
num_intergrity_workers = 3
threads_integrity = []
latest_data_point_lock = Lock()
for i in range(num_intergrity_workers):
    t_i = StopableThread(target=worker_integrity_check, args=(q_raw, q_processed, latest_data_point_lock,nbChannel,), name="Integrity-{}".format(i))
    threads_integrity.append(t_i)
    thread_list.append(t_i)
    t_i.start()

thread_list
t_save = StopableThread(target=worker_write_to_file, args=(q_processed,nbChannel,), name="Writer")
t_save.start()
thread_list.append(t_save)
#gui=Thread(target=gui_t, args=(root,), name="GUI")
#tStart(gui)

root=PolyleptiqueApp()
root.protocol("WM_DELETE_WINDOW", on_closing)

a=setupP(nbChannel,fig,timeToDisplay)              
ani=animation.FuncAnimation(fig, animate,fargs=(a[0],a[1],a[2],a[3],a[4]), interval=10, blit=True)

#gui = Thread(target=gui_t, args=(root,), name="GUI")
#tStart(gui)

root.mainloop()

for th in thread_list:
    th.shutdown_flag.set()
    th.join()
    
