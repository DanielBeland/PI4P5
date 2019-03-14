# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 14:42:00 2019

@author: Olivier
"""
import random
import serial
import sys
import os
import inspect

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import numpy as np

from queue import Queue, Empty, Full
from threading import Thread, Lock, current_thread

from collections import deque
from tkinter import filedialog, Scale, Entry
from matplotlib.widgets import Slider

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Save_values import *
from real_time_plot import *
import AcqVerSav_threads
import graph

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch


from PIL import ImageTk, Image
import time
starttime=time.time()


class PolyleptiqueApp(tk.Tk):
    
    def __init__(self,*args,**kwargs):
        
        
        tk.Tk.__init__(self,*args,**kwargs)
        tk.Tk.wm_iconbitmap(self,default="logo.ico")
        tk.Tk.wm_title(self, "Polyleptique")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames= {}
        
        for F in (StartPage, RecordingPage):
        
            frame = F(container, self)
            
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="nsew")
            
        
        self.show_frame(StartPage)
        page_name = RecordingPage.__name__
        self.frames[page_name] = frame
        
    def show_frame(self, cont):
            
        frame=self.frames[cont]
        frame.tkraise()
        frame.event()
    
    def get_page(self, page_name):
        return self.frames[page_name]
        
## Starting page, openend when app is launched################################3
class StartPage(tk.Frame):
    
    def __init__(self,parent,controller):
        CreateSettingFile()
        
        tk.Frame.__init__(self,parent)
        self.parent=parent
        StartPage.configure(self,bg='gray')
        label=tk.Label(self,text="Start Page",font=LARGE_FONT)
        
        label.pack(pady=10,padx=10)
        
        button_new=ttk.Button(self, text="Start new recording",
                          command=lambda: controller.show_frame(RecordingPage))
        
        button_new.pack()
        
        button_load=ttk.Button(self, text="Create Summary",
                              command=lambda: Rapport())
        button_load.pack() 
        button_Setting=ttk.Button(self, text="Settings",
                              command=lambda: PopSettingPage(self))
        button_Setting.pack() 

    
        
    def event(self):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        pass
    

    
## Page for the live plot of sensor data#####################################
class RecordingPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
#        label=ttk.Label(self,text="Page 1",font=LARGE_FONT)
#        
#        label.pack(pady=10,padx=10)
#        
#        button1=ttk.Button(self, text="Back To home",
#                          command=lambda: controller.show_frame(StartPage))
#        
#        button1.pack()
#        
#        button2=ttk.Button(self, text="Create/Select save file",
#                          command=lambda: controller.show_frame(LivePlotPage))
#        
#        button2.pack()
#        
        self.image = tk.PhotoImage(file='bluetooth.png')
        self.image_disp=self.image.subsample(6,6)
        self.label = tk.Label(self, image=self.image_disp, bg='green',borderwidth=2, relief="solid")
        self.label.grid(row=0,column=0,pady=10)
        self.comlist=['com1','com2','com3']
        
        self.v = tk.StringVar()
        self.v.set(self.comlist[0])
        self.BluetoothOption = ttk.OptionMenu(self, self.v, self.comlist[0], *self.comlist)
        self.BluetoothOption.grid(row=0,column=1,pady=10)
        self.saveLocationText=tk.StringVar()
        self.saveLocationText.set('File Save Name: ')
        self.saveLocationLabel=ttk.Label(self,textvariable=self.saveLocationText)
        self.saveLocationLabel.grid(row=1,column=0,pady=10)
        
        self.editButton=ttk.Button(self,text='Edit',command=lambda: EditSaveLocation(self))
        self.editButton.grid(row=1,column=1,pady=10)
        
        self.startButton=ttk.Button(self,text='Start',command=lambda: StartRecording(self))
        self.startButton.grid(row=2,column=0,pady=10)
        self.stopButton=ttk.Button(self,text='Stop',command=lambda: StopRecording(self))
        self.stopButton.config(state="disabled")
        self.stopButton.grid(row=2,column=1,pady=10)
        
        self.homeButton=ttk.Button(self, text="Home",
                  command=lambda: controller.show_frame(StartPage))
        self.homeButton.grid(row=3,columnspan=2,pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    
    def event(self):
        state = str(self.startButton['state'])
        if state == 'normal':
            EditSaveLocation(self)
def CheckState():
    state=[np.random.randint(0,2),np.random.randint(0,2)]
    crise=state[0]
    connexion=state[1]
    if crise==1:
        root.get_page("RecordingPage").label.config(bg='red')
    else:
        root.get_page("RecordingPage").label.config(bg='green')
    if connexion==1:
       root.get_page("RecordingPage").configure(bg='red')
    else:
        root.get_page("RecordingPage").configure(bg='gray')
    root.after(1000,CheckState)
def StartRecording(self):
    if len(self.saveLocationText.get())>16:
        fileSaveName=self.saveLocationText.get()[16:]
        AcqVerSav_threads.thread_list = AcqVerSav_threads.initializeThreads(fileSaveName, nbChannel, nbIntegrityWorkers, qSize,saveFrequency*samplingRate)
        self.startButton.config(state='disabled')
        self.stopButton.config(state='enabled')
        self.BluetoothOption.config(state='disabled')
        self.editButton.config(state='disabled')
    else:
        messagebox.showwarning("No file name", "Please enter a save file")
def StopRecording(self):
    if messagebox.askokcancel("Stop", "Do you want to stop recording?"):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        self.startButton.config(state='enabled')
        self.stopButton.config(state='disabled')
        self.BluetoothOption.config(state='enabled')
        self.editButton.config(state='enabled')
    
    ########### CREATE SUMMARY#################
    
def Rapport():
    PAGE_HEIGHT=defaultPageSize[1]
    styles=getSampleStyleSheet()
    Title="Rapport de la session d'enregistrement"
    Elements=[]
    HeaderStyle=styles["Heading1"]
    CapteurStyle=styles["Heading2"]
    ParaStyle=styles["Normal"]
    PreStyle=styles["Code"]
    capteur=["ECG","EMG bras droite","EMG bras gauche","EMG jambe droite","EMG jambe gauche","Accéléromètre bras droite","Accéléromètre bras gauche","Accéléromètre jambe droite","Accéléromètre jambe gauche","Respiration","EDA"]
    def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.3):
        s=Spacer(0.2*inch, sep*inch)
        para=klass(txt,style)
        sect=[s,para]
        result=KeepTogether(sect)
        return result
    def graphout(data):
        drawing = Drawing(400, 200)
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.height = 125
        lp.width = 300
        lp.data = data
        lp.joinedLines = 1
        lp.lines[0].symbol = makeMarker('FilledCircle')
    #    lp.lines[1].symbol = makeMarker('Circle')
        lp.lineLabelFormat = '%2.0f'
        #lp.strokeColor = colors.black
    #    lp.xValueAxis.valueMin = 0
    #    lp.xValueAxis.valueMax = 300
    #    lp.xValueAxis.valueSteps = [1, 2, 2.5, 3, 4, 5]
        lp.xValueAxis.labelTextFormat = '%2.1f'
    #    lp.yValueAxis.valueMin = 0
    #    lp.yValueAxis.valueMax = 1
    #    lp.yValueAxis.valueSteps = [1, 2, 3, 5, 6]
        drawing.add(lp)
        return drawing
    def select_file():
        root = tk.Tk()
        root.withdraw()
    
        file_path = filedialog.askopenfilename()
        data = np.genfromtxt(file_path, delimiter=',')
        return [data, file_path]
    
    def go(file_path):
        GenName='Rapport'
        PatientName=os.path.basename(file_path)[:-4]
        SummaryName=GenName+'_'+PatientName+'.pdf'
        doc=SimpleDocTemplate(SummaryName)
        doc.build(Elements)
        
    myTitle=header(Title)
    info=[myTitle]
    Elements.extend(info)
    [data,file_path]=select_file()
    for i in range(11):
        Capteur=header(capteur[i], sep=0.1, style=CapteurStyle)
        meanData=header('Mean='+str(np.mean(data[1:data.shape[0],i])), sep=0.1, style=ParaStyle)
        stdData=header('Standard Deviation='+str(np.std(data[1:data.shape[0],i])), sep=0.1, style=ParaStyle)
        minData=header('Minimum='+str(np.min(data[1:data.shape[0],i])), sep=0.1, style=ParaStyle)
        maxData=header('Maximum='+str(np.max(data[1:data.shape[0],i])), sep=0.1, style=ParaStyle)
        ydata=[]
        xdata=[]
        data_graph=[]
    
            
        xdata=np.arange(data.shape[0]-1)
        ydata=data[1:data.shape[0],i]
        data_graph = [tuple(zip(xdata,ydata))]
        graph = graphout(data_graph)
        info_capteur=[Capteur, meanData,stdData,maxData,minData,graph]
        Elements.extend(info_capteur)
    
    go(file_path)
    
            
## Page for the settings#####################################
class SettingPage(tk.Frame):
    def __init__(self,parent):
        tk.Frame.__init__(self,parent)
        self.parent=parent
        top=self.top=tk.Toplevel(parent)
        top.title("Settings")
        
        buttonPath=ttk.Button(top, text="Define Default Path",
                          command=lambda: DefinePath(self))
        
        buttonPath.grid(row=2,columnspan=2, pady=10)
        
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
        self.LabelText=tk.StringVar()
        self.LabelText.set('Path: '+ SettingData[0])
        self.labelPathName=ttk.Label(top,textvariable=self.LabelText)
        self.labelPathName.grid(row=3,columnspan=2,pady=10)
        
        
        self.ExtensionText=ttk.Label(top,text='Default save extension')
        self.ExtensionText.grid(row=4,column=0,pady=10)
        
        d = "."
        optionListTemp =  [d+e for e in SettingData[2].split(d)]
        optionListTemp[len(optionListTemp)-1]=optionListTemp[len(optionListTemp)-1][:-1]
        self.optionList=optionListTemp[1:len(optionListTemp)]
                
        
        self.v = tk.StringVar()
        self.v.set(self.optionList[0])
        self.ExtensionOptions = ttk.OptionMenu(top, self.v, SettingData[1][:-1], *self.optionList,command=self.DefineExtension)
        self.ExtensionOptions.grid(row=4,column=1,pady=10)
        
        
        self.addExtensionButton=ttk.Button(top,text="Add extension", command = self.AddExtension)
        self.addExtensionButton.grid(row=5,column=0,pady=10)
        
        self.RemoveExtensionButton=ttk.Button(top,text="Remove extension", command=self.RemoveExtension)
        self.RemoveExtensionButton.grid(row=5,column=1,pady=10)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.okButton=ttk.Button(top,text="Ok", command=self.ExitSetting)
        self.okButton.grid(columnspan=2, pady=10)
        
        
    def event(self):
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    DefaultPath=SettingFile.readline()
        self.LabelText.set('Path: '+DefaultPath)
        self.labelPathName=ttk.Label(self,textvariable=self.LabelText)
    def DefineExtension(self,value):
        newLine="\n"
        SettingData=[""]
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
                    SettingData[1]=value+newLine
                    with open("SettingsFile.txt","w") as SettingFile:
                        SettingFile.writelines(SettingData)
                
    def AddExtension(self):
        self.w=AddExtensionWindow(self.parent) 
        self.master.wait_window(self.w.top)
        self.top.destroy()
        PopSettingPage(self)
    def RemoveExtension(self):
        self.w=RemoveExtensionWindow(self.parent) 
        self.master.wait_window(self.w.top)
        self.DefineExtension
        self.top.destroy()
        PopSettingPage(self)
    def ExitSetting(self):
        self.top.destroy()
                    
        
#### Setup Load data plot ################
        
def PopSettingPage(self):
    self.w=SettingPage(self.master)
    self.master.wait_window(self.w.top)
    
    
    
class AddExtensionWindow(object):
    def __init__(self, parent):
        top=self.top=tk.Toplevel(parent)
        self.l=ttk.Label(top,text="Add extension of form: .aaa")
        self.l.pack()
        self.e=tk.Entry(top)
        self.e.pack()
        self.b=ttk.Button(top,text='Ok',command=self.cleanup)
        self.b.pack()
    def cleanup(self):
        newLine="\n"
        self.value=self.e.get()
        if self.value[0]!=".":
            tk.messagebox.showwarning("Extension Error","Invalide Extension, add ""."" in front of extension name")
        else:
            SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
            for root, dirs, files in os.walk(SettingsDirectory):
                if 'SettingsFile.txt' in files:
                    with open("SettingsFile.txt","r") as SettingFile:
                        SettingData=SettingFile.readlines()
            SettingData[2]=SettingData[2][:-1]+self.value+newLine
            with open("SettingsFile.txt","w") as SettingFile:
                SettingFile.writelines(SettingData)
        self.top.destroy()
class RemoveExtensionWindow(object):
    def __init__(self, parent):
        top=self.top=tk.Toplevel(parent)
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
        
        d = "."
        optionListTemp =  [d+e for e in SettingData[2].split(d)]
        optionListTemp[len(optionListTemp)-1]=optionListTemp[len(optionListTemp)-1][:-1]
        self.optionList=optionListTemp[1:len(optionListTemp)]


        self.l=[None]*len(self.optionList)
        self.b=[]
        for k in range(len(self.optionList)):
            self.b.append(ttk.Button(top,text='Delete extension '+self.optionList[k],command=lambda k=k: self.DeleteExten(k)))
            self.b[k].grid()
    def DeleteExten(self,k):
        newLine="\n"

        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
        
        for x in range(len(self.optionList)):
            if self.optionList[x]==self.optionList[k]:
                self.optionList[x]=""
        SettingData[2]=''
        for i in range(len(self.optionList)):
            SettingData[2]=SettingData[2]+self.optionList[i]
        SettingData[2]=SettingData[2]+newLine
        with open("SettingsFile.txt","w") as SettingFile:
            SettingFile.writelines(SettingData)
        self.top.destroy()

def CreateSettingFile():
    SettingData=[""]
    newLine="\n"
    SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
            if not SettingData[0]:
                optionList = ['.dat', '.csv', '.mat', '.xls']
                with open("SettingsFile.txt","w+") as SettingFile:
                    SettingData=[SettingData[0]+newLine,".dat\n",optionList[0]+optionList[1]+optionList[2]+newLine]
                    SettingFile.writelines(SettingData)
        
def DefinePath(self):
    self.savePath=filedialog.askdirectory()
    newLine="\n"
    if not self.savePath:
        pass
    else:    
        pathStr='Path: '
        self.LabelText.set(pathStr+self.savePath)
        SettingData=[""]
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
        with open("SettingsFile.txt","w+") as SettingsFile:
            SettingData[0]=self.savePath+newLine
            SettingsFile.writelines(SettingData)
    self.top.destroy()
    PopSettingPage(self)

def EditSaveLocation(self):
    newLine="\n"
    fileNameOk=False
    while not fileNameOk :   
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
                    Extensions=SettingData[2][:-1]
                    if SettingData[0]=="\n":
                        fileSaveName=filedialog.asksaveasfilename(defaultextension=SettingData[1][:-1], initialdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) ,title = "Select file")
                        if not fileSaveName:
                            pass
                        else:
                            with open("SettingsFile.txt","w+") as SettingFile:
                                SettingData[0]=os.path.dirname(fileSaveName)+newLine
                                SettingFile.writelines(SettingData)
                    else:
                        fileSaveName=filedialog.asksaveasfilename(defaultextension=SettingData[1][:-1], initialdir = SettingData[0] ,title = "Select file2")
                        if not fileSaveName:
                            break
        if not fileSaveName:
            break
        if fileSaveName and fileSaveName[-4:] in Extensions :
            fileNameOk=True
            self.saveLocationText.set('File Save Name: '+fileSaveName)
        else:
            messagebox.showerror("Invalid file format", "Please check the extension or add it in the settings page.")
            break
    
    
    
    
    
    
def loadDataSetup(self):
    global load
    Filename=loadFile()
    setup_data=LoadData(Filename)
    load=True
    return setup_data

def loadFile():
    file_path = filedialog.askopenfilename()
    return file_path

def LoadData(Filename):
    file_path=Filename
    data = np.genfromtxt(file_path, delimiter=',')
    fig_load=Figure(figsize=(10,7))
    ax = fig_load.add_subplot(data.shape[1], 1, 1)
    ax.axis([0, 1000, 0, 1])
    ax.plot(np.arange(data.shape[0]-1),data[1:data.shape[0],0],'b')
    ax.get_xaxis().set_visible(False)
    fig_load.subplots_adjust(hspace = .3)
    return[data,fig_load,ax]
    
    #ax=[None]*11
#    for k in range(data.shape[1]):
#        ax[k] = fig_load.add_subplot(data.shape[1], 1, k+1)
#        ax[k].axis([0, 1000, 0, 1])
#        ax[k].plot(np.arange(data.shape[0]-1),data[1:data.shape[0],k],'b')
#        ax[k].get_xaxis().set_visible(False)
#        if k==data.shape[1]-1:
#            ax[k].get_xaxis().set_visible(True)
#    fig_load.subplots_adjust(hspace = .3)
#    graph.defineY(ax)
#    graph.defineTitle(ax)
#    return[data,fig_load,ax]
    
def PlotStartPage():
    fig_StartPage=Figure(figsize=(10,7))

    ax=[None]*11
    for k in range(11):
        ax[k] = fig_StartPage.add_subplot(11, 1, k+1)
        ax[k].get_xaxis().set_visible(False)
    graph.defineTitle(ax)
    graph.defineY(ax)
    fig_StartPage.subplots_adjust(hspace=0.3)
    return[fig_StartPage,ax]
    
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
        ax[k].get_xaxis().set_visible(False)
        
        linek, = ax[k].plot(xs, ys[k])
        line[k]=linek
    graph.defineY(ax)
    graph.defineTitle(ax)
    fig.subplots_adjust(hspace=0.3)
    
    
    
    
    return [ax, xs, ys,line,n]

######## Save on closing window################3

    
    
        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        AcqVerSav_threads.stopThreads(AcqVerSav_threads.thread_list)
        root.destroy()   


global load
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(10,7), dpi=100)

load=False
root=PolyleptiqueApp()
root.protocol("WM_DELETE_WINDOW", on_closing)



nbChannel=11
frameCounter = 1
samplingRate = 1000 #in Hz
timeToDisplay = 1 #in s
saveFrequency = 10 #in seconds
nbIntegrityWorkers=1
qSize = 100000

a=setupP(nbChannel,fig,timeToDisplay*samplingRate)
#ani=animation.FuncAnimation(fig, animate, frames=frameCounter, fargs=(a[0],a[1],a[2],a[3],a[4]), interval=1000/samplingRate, blit=True)

#gui = Thread(target=gui_t, args=(root,), name="GUI")
#tStart(gui)
CheckState()
root.mainloop()


#    AcqVerSav_threads.state [0 0 ]