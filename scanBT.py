import serial.tools.list_ports

bluetoothLibrary=True
try:
    from bluetooth import *
except ModuleNotFoundError:
    bluetoothLibrary=False

if bluetoothLibrary:
    def scanBT():
        comlist = serial.tools.list_ports.comports()
        nearby_devices = discover_devices(duration=3, lookup_names = True)
        
        comport_list=[]
        for i in range(len(comlist)):
            for j in range(len(nearby_devices)):
                if (nearby_devices[j][0].translate({ord(c): None for c in ':'})) in comlist[i].hwid:
                    comport_list.append("%(com)s : %(type)s" %{'com': comlist[i].description[-5:-1], 'type':nearby_devices[j][1]})
            if len(comport_list) < i+1:
                comport_list.append("%(com)s : %(type)s" %{'com': comlist[i].description[-5:-1], 'type':comlist[i].description[:-7]})
        if len(comport_list)==0:
            comport_list = "No device found"
        return comport_list
else:
    def scanBT():
        comlist = serial.tools.list_ports.comports()
        comport_list=[]
        for i in range(len(comlist)):
            comport_list.append("%(com)s : %(type)s" %{'com': comlist[i].description[-5:-1], 'type':comlist[i].description[:-7]})
        if len(comport_list)==0:
            comport_list = "No device found"
        return comport_list
            
        
if __name__ == '__main__':
    a=scanBT()
    #print("%(com)s : %(type)s" %{'com': a[0][-5:-1], 'type':a[0][:-7]})
    print(a)