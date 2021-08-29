#!/usr/bin/env python
# coding: utf-8

from binascii import unhexlify,hexlify
from getmac import get_mac_address as gma
from datetime import datetime
from collections import deque
from statistics import mean, stdev
import time
import asyncio
import numpy as np

from getComPort import selecComport
from calcSpo2 import calcSpo2

class device(selecComport,calcSpo2):
    def __init__(self, hardwareConfig):
        calcSpo2.__init__(self)
        self.device_name=hardwareConfig["name"]
        self.baudrate=hardwareConfig["baudrate"]
        self.comportName=hardwareConfig["comPort"]
        self.byteArray=[]
        self.blockSpo2=[]
        self.blockRaw=[]
        self.bufferRaw=[]
        # self.getSerial(self.comportName)
        
        '''
            spo2 Calculation parameters
        '''
        self.numItem=eval(hardwareConfig['numMean'])
        self.stdevTol=eval(hardwareConfig['stdevTol'])
        
        '''
            message handling variables
        '''
        self.isRunning = None
        self.msgReady=None
        self._msg={
            "name":self.device_name,
            "DID":gma(),
            "status":None,
            "spo2":{"value":None,"raw":None,"hr":None},
            "dt":-1
        }
        self.value=None
        self.raw=None
        self.hr=None
        self.logHeader="[spo2]: "
    
    def streamInit(self):
        if isinstance(self.ser,str):
            self.getSerial(self.comportName)
        if not self.ser.isOpen():
            self.ser.open()
            
    '''
    These method response to "cmd"
    ''' 
    def start(self):
        file=open("data.txt",'r')
        print("{}Start..............".format(self.logHeader))
#         self.streamInit()
        self.isRunning=True
        spo2Array=deque([],self.numItem)
        hrArray=deque([],self.numItem)
#         while self.ser.isOpen():
        while self.isRunning:
#             byte=int(hexlify(self.ser.read()),16)
            byte=int(file.readline())
            time.sleep(0.000001)
            self.verifyNumbyte(byte)
            if len(self.blockRaw)>=100:
                self.bufferRaw.append(list(self.blockRaw))
            if len(self.blockSpo2)>=100:
                spo2Array,hrArray,var=self.verifyResult(spo2Array,hrArray)
                self.msgReady=False
                if var is True:
                    file.close()
                    break
            if len(self.bufferRaw)>3:
                self.getStream()
        self.value=mean(spo2Array)
        self.hr=mean(hrArray)
        self.msg=1
        print("{}..............Finish".format(self.logHeader))
#         self.ser.close()
        file.close()
        self.isRunning=False
        self.msgReady=False
                    
    def stop(self):
        try:
            self.ser.close()
        except:
            pass
        self.isRunning=False
            
    def reset(self):
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
        time.sleep(0.1)

    '''
    These are utility functions
    '''
    def verifyNumbyte(self,byte):
        # if len(self.byteArray)>6:
        #     self.byteArray.clear()
        if byte == 0 and len(self.byteArray)>=7:
            if self.byteArray[0]==184:
                self.byteArray.clear()
                return
            elif self.byteArray[0]==0:
                self.byteArray.pop(0)
            self.byteArray.append(byte)
            self.blockSpo2.append(list(self.byteArray[2:4]))
            self.blockRaw.append([int(self.byteArray[1])])
            self.raw=[int(self.byteArray[1])]
            self.msg=0
            self.byteArray.clear()
        else:
            self.byteArray.append(byte)
            
    def verifyResult(self,spo2Array,hrArray):
        data=np.asarray(self.blockSpo2)
        hr,boolHr,value,boolValue=self.calc_hr_and_spo2(data[:,1], data[:,0])
        spo2Array.append(value) if boolValue is True else -1
        hrArray.append(hr) if boolHr is True else -1
        self.blockSpo2.clear()
        self.msg=1
        if len(spo2Array)==self.numItem:
            if stdev(spo2Array)<=self.stdevTol:
                return spo2Array,hrArray,True
            else:
                return spo2Array,hrArray,False
        else:
            return spo2Array,hrArray,False
        
    def getStream(self):
        rawDataBlock=list(self.bufferRaw.pop(0))
        
    @property
    def msg(self):
        return self._msg
    
    @msg.setter
    def msg(self, statMsg):
        
        if statMsg == 1:
            self._msg["status"]=True
            self._msg["spo2"]={"value":None,"hr":None}
            self._msg["spo2"]["value"]=self.value
            self._msg["spo2"]["hr"]=self.hr
        elif statMsg ==2:
            self._msg["status"]=True
        elif statMsg ==3:
            self._msg["status"]=False
        else:
            self._msg["status"]=True
            self._msg["spo2"]["raw"]=self.raw
        self._msg["dt"]=int(datetime.timestamp(datetime.now())*1000)
        self.msgReady=True
        
if __name__=='__main__':
    from configparser import ConfigParser
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config\banbangkhae.ini")
    spo2=device(hardwareConfig["spo2"])