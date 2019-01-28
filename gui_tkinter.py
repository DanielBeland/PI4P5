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
from tkinter import filedialog, Scale
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Save_values import *
from real_time_plot import *
import AcqVerSav_threads

global load

file_path=[]
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(5,5), dpi=100)
nbChannel=11
frameCounter = 1
timeToDisplay = 1000 
#val= np.random.randint(1000,size=(1,nbChannel), dtype=int)
load=False



def setupP(n,fig,ttd):
    AcqVerSav_threads.latest_data_point
    AcqVerSav_threads.latest_data_point = np.zeros(n, dtype=int)
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
        ys[l].append(AcqVerSav_threads.latest_data_point[l])

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
    plot_save_data(setup_data[0],setup_data[1],setup_data[2])
    load=True
    return setup_data


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
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
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
        AcqVerSav_threads.thread_list = AcqVerSav_threads.initializeThreads(nbChannel, 3, 10000)
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
                self.canvas_load.get_tk_widget().destroy()
                setup_data=loadData(self)
                self.canvas_load = FigureCanvasTkAgg(setup_data[1], self)
                self.canvas_load.draw()
                self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
                self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
                self.slider = Scale(self, from_=0, to=setup_data[0].shape[0]-12, orient=tk.HORIZONTAL, command=lambda x: self.update_ax(setup_data[0],setup_data[1],setup_data[2]))
                self.slider.pack()
            else:
                pass
        else:
            setup_data=loadData(self)
            self.canvas_load = FigureCanvasTkAgg(setup_data[1], self)
            self.canvas_load.draw()
            toolbar = NavigationToolbar2Tk(self.canvas_load, self)
            toolbar.update()
            self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
            self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
            self.slider = Scale(self, from_=0, to=setup_data[0].shape[0]-12, orient=tk.HORIZONTAL,length=600, command=lambda x: self.update_ax(setup_data[0],setup_data[1],setup_data[2]))
            self.slider.pack() 
    def update_ax(self,data,fig_load,ax):
        pos=self.slider.get()
        for k in range(data.shape[1]):
            ax[k].axis([pos,pos+10,-1,1])
            fig_load.canvas.draw_idle()
def select_file():
    root = tk.Tk()
    root.withdraw()
    root.update()
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
        plt.axes([0.2, 0.1, 0.65, 0.03])

        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        root.destroy()   



root=PolyleptiqueApp()
root.protocol("WM_DELETE_WINDOW", on_closing)

a=setupP(nbChannel,fig,timeToDisplay)              
ani=animation.FuncAnimation(fig, animate,fargs=(a[0],a[1],a[2],a[3],a[4]), interval=10, blit=True)

#gui = Thread(target=gui_t, args=(root,), name="GUI")
#tStart(gui)

root.mainloop()


