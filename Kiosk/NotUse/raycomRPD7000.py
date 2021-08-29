#!/usr/bin/env python
# coding: utf-8

from binascii import unhexlify,hexlify
from getmac import get_mac_address as gma
from datetime import datetime
import time
import asyncio

import comPort
                        
class raycomRPD7000(comPort.selecComport):
    def __init__(self, hardwareConfig):
        # super().__init__()
        self.device_name=hardwareConfig["name"]
        self.baudrate=hardwareConfig["baudrate"]
        self.comportName=hardwareConfig["comPort"]
        self.commandList=eval(hardwareConfig["command"].replace("\'", "\""))
        
        self.numAttempt=0
        self.isRunning = None
        self.msgReady=None
        self.timeout=eval(hardwareConfig["timeout"])
        
        self.sys=None
        self.dia=None
        self.hr=None
        self._msg={
            "name":self.device_name,
            "DID":gma(),
            "status":None,
            "pressure":{"sys":None,"dia":None,"hr":None},
            "dt":-1
        }
        # self.getSerial(self.comportName)
        self.logHeader="[raycomeRPD7000]: "



    '''
        *****These Functions are used by commProtocol*****
    '''                
    def start(self):
        self.numAttempt+=1
        if self.numAttempt>3:
            print("{}Number of measurements exceeded 3 attempts, please check your setup".format(self.logHeader))
            return
        print("{}Begin Measuring Blood Pressure".format(self.logHeader))
        self.readMeasurement()
        self.numAttempt=0
        self.isRunning=False
        time.sleep(0.5)
        self.msgReady=False
        
    def stop(self):
        print("{}Stop the Process".format(self.logHeader))
        self.ser.write(self.HexStringtoByteArray(self.commandList["stop"]))
        self.ser.close()
        time.sleep(5)
        self.ser.open()
        self.isRunning=False
        
    def reset(self):
        print("{}Reset Serial Port".format(self.logHeader))
        self.ser = ""
        self.getSerial(self.comportName)
        self.isRunning=False
        
    def status(self):
        try:
            if self.ser.isOpen():
                self.msg=2
        except:
            self.msg=3
        self.msg["dt"]=int(datetime.timestamp(datetime.now())*1000)
        self.msgReady=True
        print("{0}status {1}".format(self.logHeader, self._msg['status']))
        time.sleep(0.1)
        
    def run(self):
        while True:
            a=1
            
            
            
    '''
        Function below is not meant to be called from outside of the class
    '''
    
    def machineRes(self):
        response = hexlify(self.ser.read(8)).decode('unicode-escape').upper()
        return response
    
    def readMeasurement(self):
        self.isRunning=True
        self.ser.write(self.HexStringtoByteArray(self.commandList["start"]))
        self.machineRes()
        hexstr=[]
        startTime=time.perf_counter()
        
        while self.ser.in_waiting <=18:
            finishTime=time.perf_counter()
            diff=finishTime-startTime
            if diff>=self.timeout:
                self.isRunning=False
                print("{}Reading Timeout...try again".format(self.logHeader))
                self.msg=0
                self.stop()
                self.msgReady=False
                self.start()
                return
        for data in range(self.ser.in_waiting):
            hexstr.append(self.ser.read())
        self.getsysdiahr(hexstr)
    
    def getsysdiahr(self,hexstr):
        self.sys = int.from_bytes(hexstr[14],"big")
        self.dia = int.from_bytes(hexstr[16],"big")
        self.hr = int.from_bytes(hexstr[18],"big")
        self.msg=1
        self.isRunning=False
        
    @property
    def msg(self):
        return self._msg
    
    @msg.setter
    def msg(self, statMsg):
        self._msg["pressure"]={"sys":None,"dia":None,"hr":None}
        if statMsg == 1:
            self._msg["status"]=True       
            self._msg["pressure"]["sys"]=self.sys
            self._msg["pressure"]["dia"]=self.dia
            self._msg["pressure"]["hr"]=self.hr
        elif statMsg ==2:
            self._msg["status"]=True
            del self._msg["pressure"]
        elif statMsg ==3:
            self._msg["status"]=False
            del self._msg["pressure"]
        else:
            self._msg["pressure"]["sys"]=-1
            self._msg["pressure"]["dia"]=-1
            self._msg["pressure"]["hr"]=-1
        self._msg["dt"]=int(datetime.timestamp(datetime.now())*1000)
        self.msgReady=True
        
    @staticmethod
    def HexStringtoByteArray(command):
        command=command.replace(" ","")
        command=unhexlify(command)
        return command
    
if __name__=='__main__':
    from configparser import ConfigParser
    protocolConfig = ConfigParser()
    protocolConfig.read("config/banbangkhae.ini")
    raycomRPD7000=device(protocolConfig["raycomRPD7000"])