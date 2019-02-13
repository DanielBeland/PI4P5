from collections import deque
import statistics
import numpy as np

minECG = 0
maxECG = 200
minEMG = -250
maxEMG = 250
minACC = 0
maxACC = 1000
minR = 0
maxR = 100
minEDA = 0
maxEDA = 1023

yaxis=[(minECG,maxECG),(minEMG,maxEMG),(minEMG,maxEMG),(minEMG,maxEMG),(minEMG,maxEMG),(minACC,maxACC),(minACC,maxACC),(minACC,maxACC),(minACC,maxACC),(minR,maxR),(minEDA,maxEDA)]

def defineY(axs):
    for i in range(len(axs)):
        axs[i].set_ylim(yaxis[i])
    return axs

#preinitiate ecgData and ecgFreq as [0]*n
def prepECG(ecgData, ecgFreq, previousVal,previousTime, newData, newTime):
#    FIFO and median to remove spikes
    ecgData.popleft()
    ecgData.append(newData)
    newVal=statistics.median(ecgData)
#    Rising edge detection
    if newVal > previousVal:
        period=newTime-previousTime #à convertir en secondes
        ecgFreq.popleft()
        ecgFreq.append(1/period)
    return [ecgData,ecgFreq,newVal,newTime,statistics.mean(ecgFreq)]

#preinitite emgData as [250]*n
def prepEMG(emgData,newData):
    emgData.popleft()
    emgData.append(newData)
    return [emgData,newData-statistics.mean(emgData)]
    
#preinitiate accData as [[300,300]]*n or [[300,300,300]]*n
def prepACC(accData,newData):
    accData.popleft()
    accData.append()
    for i in len(newData):
        Data[i]=newData[i]-statistics.mean(accData[:][i])
    return Data


def prepR(previousVal,previousTime, rCounter, newData, newTime):
#    FIFO and median to remove spikes
    rData.popleft()
    rData.append(newData)
    newVal=statistics.median(rData)
#    Rising edge detection
    if newVal > previousVal:
        rCounter=rCounter+1
    else:
        a
    if rCounter==3:
        rCounter=0
        period=newTime-previousTime #à convertir en secondes
        rFreq.popleft()
        rFreq.append(1/period)
    return [newVal,newTime,statistics.mean(rFreq)]
    
    