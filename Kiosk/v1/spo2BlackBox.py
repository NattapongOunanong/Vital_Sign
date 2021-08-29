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


import spo2
import calcSpo2

class spo2BlackBox(spo2.spo2,calcSpo2.calcSpo2):
    def __init__(self, hardwareConfig, dataType, deviceObj):
        calcSpo2.calcSpo2.__init__(self)
        spo2.spo2.__init__(self, dataType, deviceObj)
        
        # self.name=hardwareConfig["name"]
        self.name="spo2"
        self.type=hardwareConfig["type"]
        
        self.device.baudrate=hardwareConfig["baudrate"]
        self.device.addr=hardwareConfig["comport"]
        self.setMsgHeader(self.name)
        
        '''
            spo2 Calculation parameters (From config file)
        '''
        self.numItem=eval(hardwareConfig['numMean'])
        self.stdevTol=eval(hardwareConfig['stdevTol'])
        
        self.hrTmp=None
        self.boolHr=None
        self.valueTmp=None
        self.boolValue=None
        
        self.spo2Stdev=None
        self.numMean=3
        self.stdevTol=0.5
        self.isStable=None
        
        self.hrArray=deque([],maxlen=self.numMean)
        self.spo2Array=deque([],maxlen=self.numMean)
        
        '''
            message handling variables 
        '''
        self.isRunning = None
        self.isSpo2Valid=None
        self.logHeader="[spo2]: "
        self.noFingerVal=184
            
    '''
         method response to "cmd"
    ''' 
    
    def start(self):
        self.printWithHeader("Start Stream")
        self.isSpo2Ready=False
        self.isSpo2Valid=False
        if self.isRunning:
            self.printWithHeader("Already Running...")
            self.action=(yield)
            return
        self.isRunning=True
        while True:
            
            self.startStream()
            self.raw=list(np.asarray(list(self.streamData))[:,2])
            self.msgObj=True
            self.timestamp=[]
            yield
            self.delNoFingerData()
            
            try:
                self.calculateSpo2()
                self.checkSpo2Valid()
                if self.isSpo2Valid:
                    # print(self.isSpo2Valid)
                    self.hrArray.append(self.hrTmp)
                    self.spo2Array.append(self.valueTmp)
                self.checkNumCalculatedSpo2()
                if self.isStable:
                    break
                    yield
            except Exception as e:
                continue
        self.isRunning=False
        
        # get mean for stable spo2 value and hr
        self.value=round(mean(self.spo2Array),2)
        self.hr=round(mean(self.hrArray),2)
        print(self.value,self.hr)
        self.msgObj=False
        self.printWithHeader("Complete")
        self.action = (yield)
                    
    def stop(self):
        self.printWithHeader("Stop")
        self.disconnect()
        self.reset()
        # self.msgQueue.queue.clear()
        self.action = (yield)
        
    

    '''
        These are utility functions
    '''
    def delNoFingerData(self):
        # Delete dtream data when no finger is detected
        for firstByte in range(len(self.streamData)-1,-1,-1):
            if self.streamData[firstByte][1]==self.noFingerVal:
                self.streamData.pop(firstByte)
                pass
        self.streamData=np.array(self.streamData)
    
    def calculateSpo2(self):
        self.hrTmp=None
        self.boolHr=None
        self.valueTmp=None
        self.boolValue=None
        self.hrTmp,self.boolHr,self.valueTmp,self.boolValue=self.calc_hr_and_spo2(self.streamData[:,3], self.streamData[:,2])
        
    def checkSpo2Valid(self):
        # see if "self.calc_hr_and_spo2" return True
        if self.boolValue:
            self.isSpo2Valid=True
        else:
            self.isSpo2Valid=False
            
    def checkNumCalculatedSpo2(self):
        # see if number of "spo2 value" is sufficient
        if len(self.spo2Array)==self.numMean:
            self.spo2Stdev=stdev(self.spo2Array)
            self.checkStdevTol()
            
    def checkStdevTol(self):
        # see if Stdev is lower than threshold value
        if self.spo2Stdev<=self.stdevTol:
            self.isStable = True
                
        
if __name__=='__main__':
    from configparser import ConfigParser
    import comport
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config/banbangkhae.ini")
    spo2Obj=spo2BlackBox(hardwareConfig['spo2'], 10, comport.comport)
    spo2Obj.action="start"