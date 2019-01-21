# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 14:42:00 2019

@author: Olivier
"""
import matplotlib
#matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import matplotlib.pyplot as plt
import threading
from collections import deque
from tkinter import filedialog
from matplotlib.widgets import Slider


import tkinter as tk
from tkinter import ttk
global load
file_path=[]
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(5,5), dpi=100)
nb=11
val= np.random.randint(100,size=(1,nb), dtype=int)
load=False
    
    
def setupP(n,fig):

    
    xs = np.linspace(1,10,10)
    ax=[None]*n
    ys=[None]*n
    line=[None]*n
    for k in range(n):
        ax[k] = fig.add_subplot(n, 1, k+1)
        ax[k].set_ylim(0, 100)
        ys[k] = deque([0]*10)
        
        linek, = ax[k].plot(xs, ys[k])
        line[k]=linek
    return [ax, xs, ys,line,n]

def animate(i,val,ax,xs,ys,lines,n):
    val=updateVal()

    # Limit x and y lists to 20 items
    for l in range(n):
        
        ys[l].popleft()
        ys[l].append(val[0][l])
        
    
        # Draw x and y lists
#        ax[l].clear()
#        ax[l].plot(xs, ys[l])
        lines[l].set_xdata(xs)
        lines[l].set_ydata(ys[l])

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
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
        
        tk.Tk.iconbitmap(self,default="logo.ico")
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
def updateVal():
    return np.random.randint(100,size=(1,nb), dtype=int)
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
        
    
    
    
a=setupP(nb,fig)      
app=PolyleptiqueApp()
ani=animation.FuncAnimation(fig, animate,fargs=(val,a[0],a[1],a[2],a[3],a[4]), interval=1000, blit=True)
app.mainloop()