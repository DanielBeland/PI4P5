# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 15:00:05 2018

@author: Olivier
"""
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
from collections import deque
# Create figure for plotting
i=1
nb=11
# Initialize communication with TMP102
val= np.random.randint(100,size=(1,nb), dtype=int)
# This function is called periodically from FuncAnimation
def setupP(n):
    fig = plt.figure()
    
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
    return [fig, ax, xs, ys,line,n]
def update_val():
    return np.random.randint(100,size=(1,nb), dtype=int)
def animate(i,val,ax,xs,ys,lines,n):

    # Read temperature (Celsius) from TMP102
    # Add x and y to lists
    val=update_val()
    

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
def main():
    ani = animation.FuncAnimation(a[0], animate,fargs=(val,a[1],a[2],a[3],a[4],a[5]), interval=1, blit=True)
    plt.show()
    return ani

if __name__ == "__main__":
    a=setupP(nb)
    print(a)
    b=main()
