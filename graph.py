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

#preinitiate ecgData and ecgFreq as [0]*n, n must be an odd number
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
    accData.append(newData)
    Data=np.zeros((len(newData)), dtype=int)
    for i in range(len(newData)):
        Data[i]=newData[i]-statistics.mean([k[i] for k in accData])
    return [accData,np.linalg.norm(Data)]

#preinitiate rData as [0]*1000
def prepR(rData, newData):
#    FIFO and median to remove spikes
    rData.popleft()
    rData.append(newData)
    data=abs((np.fft.fft(rData)).imag)
    freq = np.fft.fftfreq((np.arange(1000)).shape[-1])
    return [rData, abs(freq[np.argmax(data)])*100] #replace 10 with conversion factor for Hz
    
    