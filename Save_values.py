import numpy as np
import csv


def write(val,filename):
    with open(filename, mode='a',newline='') as data:
        data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(val.shape[0]):
            data_writer.writerow(val[i,:])
def setup(filename):    
    with open(filename, mode='w',newline='') as data:
        data_writer = csv.writer(data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
        data_writer.writerow(['1','2','3','4','5','6','7','8','9','10','11'])
