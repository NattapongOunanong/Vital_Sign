from binascii import unhexlify,hexlify
from threading import Thread, activeCount
from getComportClass import *
from json import dumps
from getmac import get_mac_address as gma
from datetime import datetime
import paho.mqtt.client as mqtt
import asyncio
import time

import warnings
warnings.filterwarnings(action="ignore")
                        
class readRBD7k(selecComport):
    def __init__(self):
        super().__init__(baudrate = 9600,device_name="raycomRPD7000")
        self.commandList={
            "status":"CC 80 03 03 01 01 00 00",
            "start" : "CC 80 03 03 01 02 00 03",
            "stop" : "CC 80 03 03 01 03 00 02",
            "lockscreen" : "CC 80 03 03 01 08 00 02",
            "unlockscreen" : "CC 80 03 03 01 08 00 02",
            "read" : None,
            "calibrate" : None,
            "reset": None
        }
        self.acknowledgeList={
            "status":self.acknowledgeStatus,
            "start" : self.acknowledgeStart,
            "stop":self.acknowledgeStop,
            "lockscreen":None,
            "unlockscreen":None,
            "read" : None,
            "calibrate" : None,
            "reset": self.acknowledgeReset
        }
        self.client = mqtt.Client()
        self.client.username_pw_set(username="mqtt", password="12345")
        self.client.on_disconnect = self.onDisconnect
        self.client.on_connect = self.onConnect
        self.client.connect('3.0.54.110', 8082, 60)
        self.startFlag=False
        self.getSerial('/dev/ttyUSB0')
    
    async def sendCommand(self,command):
        try: 
            self.ser.write(self.HexStringtoByteArray(self.commandList[command]))
            self.machineRes()
        except:
            pass
        actionThread=Thread(target=self.acknowledgeList[command])
        actionThread.start()
    
    def machineRes(self):
        response = hexlify(self.ser.read(8)).decode('unicode-escape').upper()
        return response
    
    def readMeasurement(self):
        self.startFlag=True
        hexstr=[]
        startTime=time.perf_counter()
        timeout=120
        while self.ser.in_waiting != 20:
            finishTime=time.perf_counter()
            diff=finishTime-startTime
            if diff>=timeout:
                return
        for data in range(self.ser.in_waiting):
            hexstr.append(self.ser.read())
        self.getsysdiahr(hexstr)
    
    def getsysdiahr(self,hexstr):
        sys = int.from_bytes(hexstr[14],"big")
        dia = int.from_bytes(hexstr[16],"big")
        hr = int.from_bytes(hexstr[18],"big")
        message=self.getMsg(self.device_name,sys,dia,hr)
        self.client.publish("vitalSign",dumps(message))
        self.startFlag=False
    
    @staticmethod 
    def getMsg(device_name,sys,dia,hr):
        message=[{
            "DID":gma(),
            "name":device_name,
            "pressure":{
                "sys":sys,
                "dia":dia,
                "hr":hr},
            "dt": datetime.timestamp(datetime.now())*1000
        }]
        return message
    
    @staticmethod
    def HexStringtoByteArray(command):
        command=command.replace(" ","")
        command=unhexlify(command)
        return command
    
    def comportConnect(self):
        if isinstance(self.ser, str):
            self.getSerObj()
        print("Connection Established")
            
    def acknowledgeStatus(self):
        message={
            "DID":gma(),
            "name":self.device_name,
            "status": None,
            "dt": datetime.timestamp(datetime.now())*1000
        }
        try: 
            portOpen=self.ser.isOpen()
            if portOpen:
                message["status"]=True
            else:
                message["status"]=False
        except:
            return
        self.client.publish("vitalSign",dumps([message]))
    
    def acknowledgeStart(self):
        if self.startFlag == True:
            print("Machine is Running")
            return
        self.readMeasurement()
        self.startFlag=False
        
    def acknowledgeStop(self):
        self.ser.close()
        self.startFlag=False
        time.sleep(1)
        self.ser.open()
        
    def acknowledgeReset(self):
        self.ser = ""
        self.getSerial('/dev/ttyUSB0')
        self.startFlag=False
        
    def onDisconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnection From Broker Server: Raycome-RPD7000")
        self.client.reconnect()
        
    def onConnect(self,client, userdata, flages, rc):
        print("Raycome-RPD7000",rc,userdata,flages)