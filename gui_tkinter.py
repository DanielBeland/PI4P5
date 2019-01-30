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
import os
import inspect
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








class PolyleptiqueApp(tk.Tk):
    
    def __init__(self,*args,**kwargs):
        
        
        tk.Tk.__init__(self,*args,**kwargs)
#        tk.Tk.wm_iconbitmap(self,default="logo.ico")
        tk.Tk.wm_title(self, "Polyleptique")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames= {}
        
        for F in (StartPage, LivePlotPage, LoadPlotPage, SettingPage):
        
            frame = F(container, self)
            
            self.frames[F] = frame
            
            frame.grid(row=0,column=0,sticky="nsew")
            
        
        self.show_frame(StartPage)
        
    def show_frame(self, cont):
        frame=self.frames[cont]
        frame.tkraise()
        frame.event()
    
        
        
## Starting page, openend when app is launched################################3
class StartPage(tk.Frame):
    
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=tk.Label(self,text="Start Page",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button_new=ttk.Button(self, text="Start new recording",
                          command=lambda: controller.show_frame(LivePlotPage))
        
        button_new.pack()
        
        button_load=ttk.Button(self, text="Load previous data",
                              command=lambda: controller.show_frame(LoadPlotPage))
        button_load.pack() 
        button_Setting=ttk.Button(self, text="Settings",
                              command=lambda: controller.show_frame(SettingPage))
        button_Setting.pack() 
        
    def event(self):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        pass
    
    
    
## Page for the live plot of sensor data#####################################
class LivePlotPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Page 1",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button1=ttk.Button(self, text="Back To home",
                          command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        
        button2=ttk.Button(self, text="Create/Select save file",
                          command=lambda: controller.show_frame(PageOne))
        
        button2.pack()
        
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
    def event(self):
        fileNameOk=False
        while not fileNameOk :   
            DefaultPath=""
            SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
            for root, dirs, files in os.walk(SettingsDirectory):
                if 'SettingsFile.txt' in files:
                    SettingFile=open("SettingsFile.txt","r")
                    DefaultPath=SettingFile.readline()
                    fileSaveName=filedialog.asksaveasfilename(defaultextension=".csv", initialdir = DefaultPath ,title = "Select file",filetypes = (("csv file","*.csv"),("all files","*.*")))   
            if DefaultPath=="":
                fileSaveName=filedialog.asksaveasfilename(defaultextension=".csv", initialdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) ,title = "Select file",filetypes = (("csv file","*.csv"),("all files","*.*")))
                SettingsFile=open("SettingsFile.txt","w+")
                SettingsFile.write(os.path.dirname(fileSaveName))
            if fileSaveName and fileSaveName[-3:]=="csv" :
                    fileNameOk=True
            else:
    #                if not messagebox.askokcancel("Invalid file format", "Please enter a valid file name."):
                break
        if fileNameOk:
            AcqVerSav_threads.thread_list = AcqVerSav_threads.initializeThreads(fileSaveName, nbChannel, nbIntegrityWorkers, qSize,saveFrequency*samplingRate)
        pass
    
## Page for the loaded data plot #########################
        
class LoadPlotPage(tk.Frame):
    def __init__(self,parent,controller):

        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Page 2",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
#        label.grid(row=1,column=0)
        
        button1=ttk.Button(self, text="Back To home",
                          command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
#        button1.grid(row=2,column=0)
        
        
    def event(self):

            
        if load==True:
            MsgBox=tk.messagebox.askquestion("New Data","Do you want to load new data?")
            if MsgBox=='yes':
                self.canvas_load.get_tk_widget().destroy()
                self.slider.destroy()
                setup_data=loadDataSetup(self)
                toolbar = NavigationToolbar2Tk(self.canvas_load, self)
                toolbar.update()    
                self.canvas_load = FigureCanvasTkAgg(setup_data[1], self)
                self.canvas_load.draw()
                self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
                self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
                self.slider = Scale(self, from_=0, to=setup_data[0].shape[0]-12, orient=tk.HORIZONTAL,length=600, command=lambda x: self.update_ax(setup_data[0],setup_data[1],setup_data[2]))
                self.slider.pack()
            else:
                pass
        else:
            setup_data=loadDataSetup(self)
            self.canvas_load = FigureCanvasTkAgg(setup_data[1], self)
            self.canvas_load.draw()
            toolbar = NavigationToolbar2Tk(self.canvas_load, self)
            toolbar.update()
            self.canvas_load.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand = True)
            self.canvas_load._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
#            self.canvas_load.get_tk_widget().grid(row=3,column=0)
            
            self.slider = Scale(self, from_=0, to=setup_data[0].shape[0]-12, orient=tk.HORIZONTAL, length=600, command=lambda x: self.update_ax(setup_data[0],setup_data[1],setup_data[2]))
            self.slider.pack() 
#            self.slider.grid(column=0,row=4) 
    def update_ax(self,data,fig_load,ax):
        pos=self.slider.get()
        for k in range(data.shape[1]):
            ax[k].set_xlim(pos,pos+10)
            fig_load.canvas.draw_idle()
            
            
            
            
## Page for the live plot of sensor data#####################################
class SettingPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label=ttk.Label(self,text="Page 1",font=LARGE_FONT)
        
        label.pack()
        
        button1=ttk.Button(self, text="Back To home",
                          command=lambda: controller.show_frame(StartPage))
        
        button1.pack()
        buttonPath=ttk.Button(self, text="default Path",
                          command=lambda: DefinePath(self))
        
        buttonPath.pack()
        DefaultPath=""
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                SettingFile=open("SettingsFile.txt","r")
                DefaultPath=SettingFile.readline()
        self.LabelText=tk.StringVar()
        self.LabelText.set('Path: '+DefaultPath)
        self.labelPathName=ttk.Label(self,textvariable=self.LabelText)
        self.labelPathName.pack()
    def event(self):
        pass
#### Setup Load data plot ################
        
def DefinePath(self):
    self.savePath=filedialog.askdirectory()
    pathStr='Path: '
    self.LabelText.set(pathStr+self.savePath)
    SettingsFile=open("SettingsFile.txt","w+")
    SettingsFile.write(self.savePath)
def loadDataSetup(self):
    global load
    setup_data=LoadData()
    load=True
    return setup_data
            
def LoadData():
    file_path = filedialog.askopenfilename()
    data = np.genfromtxt(file_path, delimiter=',')
    fig_load=Figure()
    ax=[None]*data.shape[1]
    for k in range(data.shape[1]):
        ax[k] = fig_load.add_subplot(data.shape[1], 1, k+1)
        ax[k].axis([0, 10, 0, 1])
        ax[k].plot(np.arange(data.shape[0]-1),data[1:data.shape[0],k],'b')
    ax[0].set_ylim(0, 1023) #Changer pour chaque capteur
    ax[1].set_ylim(0, 1023)
    ax[2].set_ylim(0, 1023)
    ax[3].set_ylim(0, 1023)
    ax[4].set_ylim(0, 1023)
    ax[5].set_ylim(0, 1023)
    ax[6].set_ylim(0, 1023)
    ax[7].set_ylim(0, 1023)
    ax[8].set_ylim(0, 1023)
    ax[9].set_ylim(0, 1023)
    ax[10].set_ylim(0, 1023)
    return[data,fig_load,ax]
    
    
####Setup Live Plot data and update##############
def setupP(n,fig,ttd):
    AcqVerSav_threads.latest_data_point
    AcqVerSav_threads.latest_data_point = np.zeros(n, dtype=int)
    xs = np.linspace(1,1000,ttd)
    ax=[None]*n
    ys=[None]*n
    line=[None]*n
    for k in range(n):
        ax[k] = fig.add_subplot(n, 1, k+1)
        ys[k] = deque([0]*ttd)
        
        linek, = ax[k].plot(xs, ys[k])
        line[k]=linek
        
    ax[0].set_ylim(0, 1023) #Changer pour chaque capteur
    ax[1].set_ylim(0, 1023)
    ax[2].set_ylim(0, 1023)
    ax[3].set_ylim(0, 1023)
    ax[4].set_ylim(0, 1023)
    ax[5].set_ylim(0, 1023)
    ax[6].set_ylim(0, 1023)
    ax[7].set_ylim(0, 1023)
    ax[8].set_ylim(0, 1023)
    ax[9].set_ylim(0, 1023)
    ax[10].set_ylim(0, 1023)
    
    
    
    
    return [ax, xs, ys,line,n]

def animate(frameCounter,ax,xs,ys,lines,n):

    for l in range(n):
        
        ys[l].popleft()
        ys[l].append(AcqVerSav_threads.latest_data_point[l])

        lines[l].set_xdata(xs)
        lines[l].set_ydata(ys[l])
    return lines
######## Save on closing window################3

        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        root.destroy()   


global load
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(5,5), dpi=100)

load=False

root=PolyleptiqueApp()
root.protocol("WM_DELETE_WINDOW", on_closing)



nbChannel=11
frameCounter = 1
samplingRate = 1000 #in Hz
timeToDisplay = 1 #in s
saveFrequency = 10 #in seconds
nbIntegrityWorkers=2
qSize = 100000

a=setupP(nbChannel,fig,timeToDisplay*samplingRate)
ani=animation.FuncAnimation(fig, animate, frames=frameCounter, fargs=(a[0],a[1],a[2],a[3],a[4]), interval=1000/samplingRate, blit=True)

#gui = Thread(target=gui_t, args=(root,), name="GUI")
#tStart(gui)

root.mainloop()


