import numpy as np
import csv


def writeF(val,filename):
    with open(filename, mode='ab') as file:
        binary_format = bytearray(val)
        file.write(binary_format)
    
#def setup(filename):    
#    with open(filename, mode='w',newline='') as data:
#        data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    
#        data_writer.writerow(['1','2','3','4','5','6','7','8','9','10','11'])
#valz=np.random.randint(0,100,size=(20,1000*60*60*24))
#print(valz)
#write(valz,'ex.bin')
#f=open('ex.bin',mode='wb')
#valz=np.random.randint(0,100,size=(10,1))
#print(valz)
#writeF(valz,f)
#f.close()