# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 13:49:52 2019

@author: danie
"""
import random
import time
import serial
import sys
import datetime as dt
import inspect
import os

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



fileNameOk=False
while not fileNameOk :   
    fileSaveName=filedialog.asksaveasfilename(defaultextension=".csv", initialdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) ,title = "Enter new file name or select existing file to overwrite",filetypes = (("csv file","*.csv"),("all files","*.*")))
    if fileSaveName and fileSaveName[-3:]=="csv" :
        fileNameOk=True
    else:
        if not messagebox.askokcancel("Invalid file format", "Please enter a valid file name."):
            break