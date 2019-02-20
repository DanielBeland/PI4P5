from collections import deque
import numpy as np

minECG = 0
maxECG = 2
minEMG = -500
maxEMG = 500
minACC = 0
maxACC = 1000
minR = 0
maxR = 100
minEDA = 0
maxEDA = 1023

yaxis=[(minECG,maxECG),(minEMG,maxEMG),(minEMG,maxEMG),(minEMG,maxEMG),(minEMG,maxEMG),(minACC,maxACC),(minACC,maxACC),(minACC,maxACC),(minACC,maxACC),(minR,maxR),(minEDA,maxEDA)]

title=["ECG","EMG","EMG","EMG","EMG","ACC","ACC","ACC","ACC","RES","EDA"]

def defineY(axs):
    for i in range(len(axs)):
        axs[i].set_ylim(yaxis[i])
    return axs

#preinitiate ecgData and ecgFreq as [0]*n, n must be an odd number
def prepECG(ecgData, ecgFreq, previousVal,previousTime, newData, newTime):
#    FIFO and median to remove spikes
    ecgData.popleft()
    ecgData.append(newData)
    newVal=np.median(ecgData)
#    Rising edge detection
    if newVal > previousVal:
        period=newTime-previousTime #à convertir en secondes
        ecgFreq.popleft()
        ecgFreq.append(1/(period+1))
    return [ecgData,ecgFreq,newVal,newTime,np.mean(ecgFreq)]

#preinitite emgData as [250]*n
def prepEMG(emgData,newData):
    emgData.popleft()
    emgData.append(newData)
#    print(newData)
#    print(emgData)
#    print(np.mean(emgData))
    return [emgData,newData-np.mean(emgData)]
    
#preinitiate accData as [[300,300]]*n or [[300,300,300]]*n
def prepACC(accData,newData):
    accData.popleft()
    accData.append(newData)
    Data=np.zeros((len(newData)), dtype=int)
    for i in range(len(newData)):
        Data[i]=newData[i]-np.mean([k[i] for k in accData])
    return [accData,np.linalg.norm(Data)]

#preinitiate rData as [0]*1000
def prepR(rData, newData):
#    FIFO and median to remove spikes
    rData.popleft()
    rData.append(newData)
    data=abs((np.fft.fft(rData)).imag)
    freq = np.fft.fftfreq((np.arange(1000)).shape[-1])
    return [rData, abs(freq[np.argmax(data)])*100] #replace 10 with conversion factor for Hz
    
    
def defineTitle(axs):
    
    for i in range(len(axs)):
        axs[i].set_ylabel(title[i], rotation=0, fontsize=15, labelpad=20)
    return axs

if __name__ == '__main__':
    processedData=[]
    emgData1=deque([250]*1000)
    data=[400]*1500
    for i in range(1100):
        [emgData1,processedData]=prepEMG(emgData1,data[i])
#        print(emgData1)
        print(processedData)