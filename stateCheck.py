from collections import deque
import numpy as np

def check(data,dq1,dq2,dq3):
    
    dq1.append(data[0:-2])
    dq2.append(data[-2])
    dq3.append(data[-1])
    
    if len(dq1)>200:
        dq1.popleft()
    if len(dq2)>200:
        dq2.popleft()
    if len(dq3)>200:
        dq3.popleft()
    s1=0
    s2=np.mean(dq2)>0.2
#    print(s2)
    s3=max(dq3)
#    print(s3)
    return [s1,s2,s3]