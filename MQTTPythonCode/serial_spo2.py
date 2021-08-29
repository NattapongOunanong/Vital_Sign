import time
import matplotlib.pyplot as plt
import numpy as np
import paho.mqtt.client as mqtt
import asyncio
from threading import Thread, currentThread
from collections import deque
from datetime import datetime
from binascii import unhexlify,hexlify
from statistics import mean, stdev
from getmac import get_mac_address as gma
from json import dumps
from calc_spo2 import *
from getComportClass import *

class readSPO2(selecComport,calc_SPO2):
    def __init__(self):
        super().__init__(baudrate=4800,device_name="spo2")
        self.getSerial('/dev/ttyUSB1')
        self.block=[]
        self.byteArray=[]
        self.client = mqtt.Client()
        self.client.username_pw_set(username="mqtt", password="12345")
        self.Command={
            "start": self.streamStart,
            "stop": self.streamStop,
            "status": self.streamStatus,
            "read":None,
            "calibrate":None,
            "reset":self.streamReset,
            "stream":None
        }
        self.SAMPLE_FREQ = 25
        self.MA_SIZE = 4
        self.BUFFER_SIZE = 100
        self.client.on_disconnect = self.onDisconnect
        self.client.on_connect = self.onConnect
        
    async def sendCommand(self,command):
        streamThread=Thread(name="readingSpo2",target=self.Command[command])
        streamThread.start()
    
    def streamInit(self):
        if isinstance(self.ser,str):
            try: 
                self.getSerObj()
            except:
                self.client.publish("vitalSign",dumps([{"name":self.device_name,"status":"Not Connected"}]))
        
        if not self.ser.isOpen():
            self.ser.open()
        self.client.connect('3.0.54.110', 8082, 60)
        
    def streamStart(self):
        self.streamInit()
        message={
            "name":self.device_name,
            "DID":gma(),
            "spo2":{"value":None,"raw":[],"hr":None}
        }
        spo2Array=deque([],3)
        hrArray=deque([],3)
        while self.ser.isOpen():
            byte=int(hexlify(self.ser.read()),16)
            message=self.verifyNumbyte(message,byte) 
            if len(self.block)>=100:
                spo2Array,hrArray,var=self.verifyResult(message,spo2Array,hrArray)
                if var is True:
                    del message["spo2"]["raw"]
                    break
                # message["spo2"]["raw"].clear()
        message["spo2"]['value']=spo2Array[-1]
        message["spo2"]['hr']=hrArray[-1]
        message["dt"]=datetime.timestamp(datetime.now())*1000
        self.client.publish("vitalSign",dumps([message]))
        print("Finish")
        self.ser.close()
        
    def verifyNumbyte(self,message,byte):
        if len(self.byteArray)>6:
            self.byteArray.clear()
        if byte == 0 and len(self.byteArray)>=5:
            self.block.append(list(self.byteArray[2:4]))
            # message["spo2"]["raw"].append(int(self.byteArray[1]))
            message["spo2"]["raw"]=[int(self.byteArray[1])]
            message["dt"]=datetime.timestamp(datetime.now())*1000
            self.client.publish("vitalSign",dumps([message]))
            self.byteArray.clear()
        else:
            self.byteArray.append(byte)
        return message
            
    def verifyResult(self,message,spo2Array,hrArray):
        print("Reading Stream Data...")
        data=np.asarray(self.block)
        hr,boolHr,value,boolValue=self.calc_hr_and_spo2(data[:,1], data[:,0])
        spo2Array.append(value) if boolValue is True else -1
        hrArray.append(hr) if boolHr is True else -1
        self.block.clear()
        message["dt"]=datetime.timestamp(datetime.now())*1000
        message['spo2'].pop('value', None);message['spo2'].pop('hr', None);
        # self.client.publish("vitalSign",dumps([message]))
        if len(spo2Array)==3:
            if stdev(spo2Array)<=3:
                return spo2Array,hrArray,True
            else:
                return spo2Array,hrArray,False
        else:
            return spo2Array,hrArray,False
                    
    def streamStop(self):
        try:
            self.ser.close()
        except:
            pass
        
    def streamStatus(self):
        message={
            "name":self.device_name,
            "DID":gma(),
            "status":None,
            "dt":datetime.timestamp(datetime.now())*1000
        }
        if self.isOpen():
            message["status"]=True
        else:
             message["status"]=False
        self.client.publish("vitalSign",dumps([message]))
            
    def streamReset(self):
        self.ser = ""
        self.getSerial('/dev/ttyUSB1')
        
    def onDisconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnection From Broker Server: SPO2")
        self.client.reconnect()
        
    def onConnect(self,client, userdata, flages, rc):
        print("SPO2",rc,userdata,flages)