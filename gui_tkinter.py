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

import mainBT
import scanBT

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.platypus import *
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.charts.legends import LineLegend
import time
import datetime

starttime=time.time()
test=False

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
#   Défini le nombre de page ainsi que leur nom
        for F in (StartPage, RecordingPage):
        
            frame = F(container, self)
            
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="nsew")
            
        
        self.show_frame(StartPage)
        page_name = RecordingPage.__name__
        self.frames[page_name] = frame
#        Permet de naviguer entre les differentes pages
    def show_frame(self, cont):
            
        frame=self.frames[cont]
        frame.tkraise()
        frame.event()
#    Permet d'obtenir le nom de la page
    def get_page(self, page_name):
        return self.frames[page_name]
        
## Starting page, openend when app is launched################################
class StartPage(tk.Frame):
#    Initialise l'allure de la page
    def __init__(self,parent,controller):
        CreateSettingFile()
        
        tk.Frame.__init__(self,parent)
        self.parent=parent
        StartPage.configure(self,bg='gray')
        self.image = tk.PhotoImage(file='logo.png')
        self.image_disp=self.image.subsample(4,4)
        self.label = tk.Label(self, image=self.image_disp,borderwidth=2, relief="solid")
        self.label.pack()
        
        button_new=ttk.Button(self, text="Start new recording",
                          command=lambda: controller.show_frame(RecordingPage))
        
        button_new.pack()
        
        button_load=ttk.Button(self, text="Generate recording report",
                              command=lambda: Rapport())
        button_load.pack() 
        button_Setting=ttk.Button(self, text="Settings",
                              command=lambda: PopSettingPage(self))
        button_Setting.pack() 

#        Ce qui se passe quand on arrive sur la page
    def event(self):
        mainBT.stopThreads(mainBT.thread_list)
        pass
    
 
## Page for the live plot of sensor data#####################################
class RecordingPage(tk.Frame):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
#        
        self.image = tk.PhotoImage(file='bluetooth.png')
        self.image_disp=self.image.subsample(6,6)
        self.label = tk.Label(self, image=self.image_disp, bg='green',borderwidth=2, relief="solid")
        self.label.grid(rowspan=2,column=0,pady=10)
        if test:
            self.comlist=[1,2,3]
        else:
            self.comlist=scanBT.scanBT()
        
        self.v = tk.StringVar()
        self.v.set(self.comlist[0])
        self.BluetoothOption = ttk.OptionMenu(self, self.v, self.comlist[0], *self.comlist,command=self.setPort)
        mainBT.sPort=self.comlist[0]
        self.BluetoothOption.grid(row=0,column=1,pady=10)
        self.RefreshButton=ttk.Button(self,text='Refresh', command=lambda: RefreshBluetooth(self))
        self.RefreshButton.grid(row=1,column=1,pady=10)
        
        
        self.saveLocationPath=tk.StringVar()
        self.saveLocationPath.set('')
        self.saveLocationText=tk.StringVar()
        self.saveLocationText.set('')
        self.saveLocationLabel=ttk.Label(self,textvariable=self.saveLocationText)
        self.saveLocationLabel.grid(row=2,column=0,pady=10)
        
        self.editButton=ttk.Button(self,text='Edit',command=lambda: EditSaveLocation(self))
        self.editButton.grid(row=2,column=1,pady=10)
        
        self.startButton=ttk.Button(self,text='Start',command=lambda: StartRecording(self))
        self.startButton.grid(row=3,column=0,pady=10)
        self.stopButton=ttk.Button(self,text='Stop',command=lambda: StopRecording(self))
        self.stopButton.config(state="disabled")
        self.stopButton.grid(row=3,column=1,pady=10)
        
        self.homeButton=ttk.Button(self, text="Home",
                  command=lambda: controller.show_frame(StartPage))
        self.homeButton.grid(row=4,columnspan=2,pady=10)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    def setPort(self,value):
        mainBT.sPort=value[0:4]
    
    def event(self):
        state = str(self.startButton['state'])
        if state == 'normal':
            EditSaveLocation(self)
#Fonction pour le boutton refresh des ports bluetooth
def RefreshBluetooth(self):
    self.comlist=scanBT.scanBT() #Scan les ports
    menu = self.BluetoothOption["menu"]
    menu.delete(0, "end")
    for string in self.comlist:
        menu.add_command(label=string, 
                         command=lambda value=string: self.v.set(value))#Viens ajouter les ports a la liste
    self.v.set(self.comlist[0])

def CheckState():
#Fonction qui vient faire varier l'interface en fonction des soucis qui pourrait arriver
    crise=mainBT.c_state[0]
    connexion1=mainBT.c_state[1]
    connexion2=mainBT.c_state[2]
    
    if connexion1: #Montre des troubles de connexion
        root.get_page("RecordingPage").label.config(bg='orange')
    elif connexion2: #Montre une perte de connexion
        root.get_page("RecordingPage").label.config(bg='red')
    else: 
        root.get_page("RecordingPage").label.config(bg='green')
    if crise==1:
       root.get_page("RecordingPage").configure(bg='red')
       root.get_page("RecordingPage").saveLocationLabel.configure(background='red')
    else:
        root.get_page("RecordingPage").configure(bg='gray')
        root.get_page("RecordingPage").saveLocationLabel.configure(background='gray')
    root.after(500,CheckState) #Vient verifier toutes les 500 millisecondes
def StartRecording(self):
    if len(self.saveLocationPath.get())>4:#Verifie s'il y a un nom de fichier
        fileSaveName=self.saveLocationPath.get()
        #Commence l'enregistrement
        mainBT.thread_list = mainBT.initializeThreads(fileSaveName, nbChannel, qSize,saveFrequency*samplingRate,test)
        #Desactive tous les autres boutons
        self.startButton.config(state='disabled')
        self.stopButton.config(state='enabled')
        self.BluetoothOption.config(state='disabled')
        self.editButton.config(state='disabled')
        self.homeButton.config(state='disabled')
        self.RefreshButton.config(state='disabled')
    else:#S'il n'y a pas de nom de fichier
        messagebox.showwarning("No file name", "Please enter a save file")
def StopRecording(self):
    if messagebox.askokcancel("Stop", "Do you want to stop recording?"):
        mainBT.stopThreads(mainBT.thread_list)#Arrete l'enregistrement
        #Reactivation de tous les boutons
        self.startButton.config(state='enabled')
        self.stopButton.config(state='disabled')
        self.BluetoothOption.config(state='enabled')
        self.editButton.config(state='enabled')
        self.homeButton.config(state='enabled')
        self.RefreshButton.config(state='enabled')
    
    ########### CREATE SUMMARY#################
    
def Rapport():
    #Mise en place des parametre par defaut et des informations de base
    PAGE_HEIGHT=defaultPageSize[1]
    styles=getSampleStyleSheet()
    Title="<para alignment='center'>Rapport de la session d'enregistrement</para>"
    logo = "logo.png"
    formatted_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    Elements=[]
    HeaderStyle=styles["Heading1"]
    CapteurStyle=styles["Heading2"]
    ParaStyle=styles["Normal"]
    capteur=["EMG bras droite","EMG bras gauche","EMG jambe droite","EMG jambe gauche","Accéléromètre bras droite x","Accéléromètre bras droite y","Accéléromètre bras droite z","Accéléromètre bras gauche x","Accéléromètre bras gauche y","Accéléromètre bras gauche z","Accéléromètre jambe droite x","Accéléromètre jambe droite y","Accéléromètre jambe gauche x","Accéléromètre jambe gauche y","Rythme respiratoir","EDA","Rythme cardiaque","Stabilité de la connexion","Déconnexion"]

    def header(txt, style=HeaderStyle, klass=Paragraph, sep=0.3):
        s=Spacer(0.2*inch, sep*inch)
        para=klass(txt,style)
        sect=[s,para]
        result=KeepTogether(sect)
        return result
    def graphout(data):
        drawing = Drawing(400, 210)
        lp = LinePlot()
        lp.x = 50
        lp.y = 50
        lp.height = 150
        lp.width = 400
        lp.data = data
        lp.joinedLines = 1
        lp.lineLabelFormat = None
        lp.lines[1].strokeColor=colors.black
        lp.lines[2].strokeColor=colors.black
        lp.lines[1].strokeWidth=0.5
        lp.lines[2].strokeWidth=0.5
        lp.xValueAxis.labelTextFormat = '%2.1f'
        drawing.add(lp)
        return drawing
    def select_file():
        root = tk.Tk()
        root.withdraw()
    
        file_path = filedialog.askopenfilename()
        if not file_path:
            return [0,0]
        else:
            if file_path[-3:]=='bin':
                with open(file_path, mode='rb') as file:
                    fileContent = file.read()
                    matrice=np.asarray([], dtype=np.int8)
                    for numbers in range(int(len(fileContent)/4)):
                        c=int.from_bytes(fileContent[numbers*4:(numbers+1)*4],byteorder='little')
                        matrice=np.append([matrice],c)
                    data=matrice[:-2].reshape(int(len(matrice)/(nbChannel+2)),nbChannel+2)
                    LenDataEmg=len(data)-1
                    #Separation des donnees EMG et des autres
                    data_emg1=np.reshape(data[1:,list(range(0, 21,4))],(6*LenDataEmg,1))
                    data_emg2=np.reshape(data[1:,list(range(1, 22,4))],(6*LenDataEmg,1))
                    data_emg3=np.reshape(data[1:,list(range(2, 23,4))],(6*LenDataEmg,1))
                    data_emg4=np.reshape(data[1:,list(range(3, 24,4))],(6*LenDataEmg,1))
                    #Reste des donnees
                    data=data[1:,list(range(24, nbChannel+2))]
                    #Heure de l'enregistrement
                    RecTime=matrice[-2:]
                    
                return [data_emg1,data_emg2,data_emg3,data_emg4,data,file_path,RecTime]
                                    
            else:
                messagebox.showerror("Invalid file format", "Please select a valide file with extension .bin")
    
    def go(file_path):
        #Nom du rapport de la forme Rapport_NomDuPatient_DateEnregistrement.pdf
        GenName='Rapport'
        PatientName=os.path.basename(file_path)[:-4]
        Scan_date=datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime).strftime('%Y_%m_%d')
        SummaryName=GenName+'_'+PatientName+'_'+Scan_date+'.pdf'
        directory = os.path.split(file_path)[0]
        doc=SimpleDocTemplate(directory+'/'+SummaryName)
        doc.build(Elements)
    [data_emg1,data_emg2,data_emg3,data_emg4,data,file_path,RecTime]=select_file()
    if file_path==0:
        pass
    else:
        #Creation de la page titre
        im = Image(logo, 2*inch, 2*inch)
        Elements.append(im)
        Elements.append(Spacer(2*inch, 2*inch))
        
        Elements.append(Paragraph(Title, styles["Heading1"]))
        Elements.append(Spacer(2*inch, 2*inch))
        
        GenName='Patient'
        PatientName=os.path.basename(file_path)[:-4]
        Patient_Name='<para alignment="center">{0}</para>'.format(GenName+' '+PatientName)
        Elements.append(Paragraph(Patient_Name, styles["Normal"]))
        
        Scan_date=datetime.datetime.fromtimestamp(os.stat(file_path).st_mtime).strftime('%Y-%m-%d')
        Recording_datetime_text="L'enregistrement se terminant le "+Scan_date
        Recording_datetime = '<para alignment="center">{0}</para>'.format(Recording_datetime_text)
        Elements.append(Paragraph(Recording_datetime, styles["Normal"]))
        Elements.append(Spacer(2*inch, 2*inch))
        ptext = '<para alignment="center">{0}</para>'.format(formatted_time)
        Elements.append(Paragraph(ptext, styles["Normal"]))
        
        
        Elements.append(PageBreak())

     ## -18 car +2 pour les channels booleen, mais -20 pour les colonnes de trop de l'emg
        for i in range(nbChannel-18):

            Capteur=header(capteur[i], sep=0.1, style=CapteurStyle)
            ydata=[]
            xdata=[]
            data_graph=[]
            #Definition des valeurs en y
            if i==0:
                ydata=data_emg1[0:data_emg1.shape[0],0]
            elif i==1:
                ydata=data_emg2[0:data_emg2.shape[0],0]
            elif i==2:
                ydata=data_emg3[0:data_emg3.shape[0],0]
            elif i==3:
                ydata=data_emg4[0:data_emg4.shape[0],0]
            else:
                ydata=data[0:data.shape[0],i-4]
            #Nombre d'intervalle défini par le facteur de division
            N=int(np.floor(len(ydata)//100))
            #Booleen pour la stabilité de la connexion
            if i==nbChannel-19:
                xdata=np.arange(RecTime[0], RecTime[1],(RecTime[1]-RecTime[0])/len(ydata))
                PourcentConn=header('Pourcentage de connection='+str(round((len(ydata)-sum(ydata))/len(ydata),3)), sep=0.1, style=ParaStyle)
                data_graph = [tuple(zip(xdata,ydata))]
                N=int(len(ydata))

                graph = graphout(data_graph)
                info_capteur=[Capteur, PourcentConn,graph]
            #Booleen pour la deconnexion
            elif i==nbChannel-20:
                xdata=np.arange(RecTime[0], RecTime[1],(RecTime[1]-RecTime[0])/len(ydata))
                PourcentConn=header('Pourcentage de connection='+str(round((len(ydata)-sum(ydata))/len(ydata),3)), sep=0.1, style=ParaStyle)
                
                ydata_moyen=1-(np.nanmean(ydata[:(len(ydata)//N)*N].reshape(-1,N), axis=1))
                data_graph = [tuple(zip(xdata,ydata_moyen))]
                graph = graphout(data_graph)
                info_capteur=[Capteur, PourcentConn,graph]
                
            #Les autres donnees
            else:
                indexes=np.where(np.array(data[0:data.shape[0],13]) == 1)[0]
                replacements=float('nan')
                ydata=list(ydata)
                #On remplace les 0 qui ont été ajouté par l'instabilité de la connexion par des NaN
                for index in indexes:
                    ydata[index] = replacements
                ydata=np.array(ydata)
                #Calcul des valeurs statistiques en excluant les NaN
                meanData=header('Mean='+str(round(np.nanmean(ydata),3)), sep=0.1, style=ParaStyle)
                stdData=header('Standard Deviation='+str(round(np.nanstd(ydata),3)), sep=0.1, style=ParaStyle)
                minData=header('Minimum='+str(round(np.nanmin(ydata),3)), sep=0.1, style=ParaStyle)
                maxData=header('Maximum='+str(round(np.nanmax(ydata),3)), sep=0.1, style=ParaStyle)
            
            
            
                #Separation de nos valeurs en differents intervale defini plus haut. La moyenne est prise a chaque fois
                #Si un interval est composer uniquement de NaN, la valeur 0 est attribuee
                ydata_moyen=np.nan_to_num(np.nanmean(ydata[:(len(ydata)//N)*N].reshape(-1,N), axis=1))
                #Definition de l'axe x en fonction du temps de debut et de fin de l'enregistrement
                xdata=np.arange(RecTime[0], RecTime[1],(RecTime[1]-RecTime[0])/len(ydata_moyen))
                #Courbe statistique de +/- un ecart type
                ydata_plus=[x+y for x,y in zip(ydata_moyen,np.nan_to_num(np.nanstd(ydata[:(len(ydata)//N)*N].reshape(-1,N), axis=1)))]
                ydata_moins=[x-y for x,y in zip(ydata_moyen,np.nan_to_num(np.nanstd(ydata[:(len(ydata)//N)*N].reshape(-1,N), axis=1)))]
                #Combinaison de toutes les courbes pour les envoyer a la fonction graphique
                data_graph = [tuple(zip(xdata,ydata_moyen)),tuple(zip(xdata,ydata_plus)),tuple(zip(xdata,ydata_moins))]
                
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
#        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.okButton=ttk.Button(top,text="OK", command=self.ExitSetting)
        self.okButton.grid(columnspan=2, pady=10)
        
        
    def event(self):
        SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
        for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    DefaultPath=SettingFile.readline()
        self.LabelText.set('Path: '+DefaultPath)
        self.labelPathName=ttk.Label(self,textvariable=self.LabelText)
    #Defini l'extension par defaut et l'ecrit dans le fichier SettingsFile
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
    def ExitSetting(self):
        self.top.destroy()
                    
        
def PopSettingPage(self):
    self.w=SettingPage(self.master)
    self.master.wait_window(self.w.top)
    

def CreateSettingFile():
    SettingData=[""]
    newLine="\n"
    SettingsDirectory=os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(SettingsDirectory):
            if 'SettingsFile.txt' in files:
                with open("SettingsFile.txt","r") as SettingFile:
                    SettingData=SettingFile.readlines()
            if not SettingData[0]:
                #Deux extensions defini par defaut
                optionList = ['.bin']
                with open("SettingsFile.txt","w+") as SettingFile:
                    SettingData=[SettingData[0]+newLine,".bin\n",optionList[0]+newLine]
                    SettingFile.writelines(SettingData)
#Defini le path de sauvegarde par defaut et l'ecrit dans le fichier SettingsFile 
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
#Defini le fichier de sauvegarde dans le fenetre d'enregistrement
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
                        fileSaveName=filedialog.asksaveasfilename(defaultextension=SettingData[1][:-1], initialdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
                        if not fileSaveName:
                            pass
                        else:
                            #L'ecrit dans le fichier SettingFile pour que ca devienne le nouveau dossier par defaut
                            with open("SettingsFile.txt","w+") as SettingFile:
                                SettingData[0]=os.path.dirname(fileSaveName)+newLine
                                SettingFile.writelines(SettingData)
                    else:
                        fileSaveName=filedialog.asksaveasfilename(defaultextension=SettingData[1][:-1], initialdir = SettingData[0])
                        if not fileSaveName:
                            break
        if not fileSaveName:
            break
        #verifie que l'extension est autorisée
        if fileSaveName and fileSaveName[-4:] in Extensions :
            fileNameOk=True
            self.saveLocationText.set(os.path.basename(fileSaveName)[:-4])
            self.saveLocationPath.set(fileSaveName)
            
        else:
            messagebox.showerror("Invalid file format", "Please check the extension")
            break
    
        
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        mainBT.stopThreads(mainBT.thread_list)
        root.destroy()   


global load
LARGE_FONT=("Verdana",12)
style.use("ggplot")
fig = Figure(figsize=(10,7), dpi=100)

load=False
root=PolyleptiqueApp()
root.protocol("WM_DELETE_WINDOW", on_closing)



nbChannel=37
frameCounter = 1
samplingRate = 100 #in Hz
saveFrequency = 300 #in seconds
qSize = samplingRate*saveFrequency*100

CheckState()
root.mainloop()
