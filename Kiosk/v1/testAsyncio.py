#!/usr/bin/env python
# coding: utf-8

import BloodPressure
import asyncio
import functools
                        
class raycomRPD7000(BloodPressure.BloodPressure):
    def __init__(self, hardwareConfig,device):
        BloodPressure.BloodPressure.__init__(self, device)
        
        # device configuration: name, baudrate, device type, port address, command list, and measurement timeout
        self.device.name=hardwareConfig["name"]
        self.device.type="pressure"
        self.device.baudrate=hardwareConfig["baudrate"]
        self.device.addr=hardwareConfig["comPort"]
        self.commandList=eval(hardwareConfig["command"].replace("\'", "\""))
        self.timeout=eval(hardwareConfig["timeout"])
        self.deviceResponse=None
        
        # pressure data in byte array
        self.sysByte=14
        self.diaByte=16
        self.hrByte=18
        
        self.numAttempt=0
        self.setMsgHeader(self.device.name)
        self.resultNumByte=18
        self.maxAttempt=3
        self.data=None
        
        self.action=None
        self.onAction=None
        
        '''
            Flag variables
        '''
        self.isReadSuccess=None #see if device return correct data
        self.isSendSuccess=None
        self.isDone=None
    
    def connect(self):
        try:
            self.device.connect()
            self.printWithHeader("Connected")
        except Exception as e:
            pass
        self.isDone=True
        yield self.isDone
        
    def start(self):
        self.isReadSuccess=False
        if self.isRunning:
            return
        
        self.printWithHeader("Begin Blood Pressure Measurement")
        startByteCommand = self.hexStringtoByteArray(self.commandList["start"])
        self.send(startByteCommand)
        self.getDeviceResponse()
        
        # self.printWithHeader(str(len(self.deviceResponse))+self.deviceResponse)
        
        self.numAttempt+=1
        if self.numAttempt>self.maxAttempt:
            self.printWithHeader("Number of measurements exceeded {} attempts, please check your setup".format(self.maxAttempt))
            self.numAttempt=0
            self.isRunning=False
            return False
        
        self.checkSendSuccess()
        # if device acknowledge command and return 
        if self.isSendSuccess:
            waitIter=self.wait4Data()
            self.isReadSuccess=False
            while not self.isReadSuccess:
                yield next(waitIter)
            self.data=self.getPressure()
        
        if self.isReadSuccess:
            pass
        else:
            self.printWithHeader("Fail to get correct data format...")
            self.reset()
            self.start()
            return
        
        self.numAttempt=0
        
        # self.printWithHeader("Number of Byte Output "+str(len(self.data)))
        
        self.sys=self.hexStr2Int(hexstr=self.data[self.sysByte])
        self.dia=self.hexStr2Int(hexstr=self.data[self.diaByte])
        self.hr=self.hexStr2Int(hexstr=self.data[self.hrByte])
        self.pressure=True
        print(self.pressure)
        return self.pressure
        
    def stop(self):
        self.printWithHeader("Stop Blood Pressure Measurement")
        stopByteCommand=self.hexStringtoByteArray(self.commandList["stop"])
        self.send(stopByteCommand)
        self.reset()
            
    def send(self, command):
        self.device.ser.write(command)
            
    '''
        Function below is not meant to be called from outside of the class
    '''
    def getDeviceResponse(self):
        # Read out acknowledgement of the command from the raycome-RPD7000 device
        serialResponse = self.readMeasurement(8)
        self.deviceResponse = self.hexifyByteArray(serialResponse)
    
    def getPressure(self):
        print("in getPressure")
        hexstr=[]
        if not self.isReadSuccess:
            return False
        for data in range(self.device.getNumDataInBuffer()):
            hexstr.append(self.readMeasurement())
        return hexstr 

    def wait4Data(self):
        print("in wait4Data")
        elaspedTime=0
        startTime=self.getTimestamp()
        self.timeUp=False
        while self.device.getNumDataInBuffer()<=self.resultNumByte:
            yield self.isReadSuccess
            elaspedTime=self.timer(duration=self.timeout, elaspedTime=elaspedTime, startTime=startTime)
            if self.timeUp:
                self.printWithHeader("Reading Timeout...try again")
                self.stop()
                self.wait(5)
                self.isReadSuccess=False
                return
        self.isReadSuccess=True
        
    def checkSendSuccess(self):
        if len(self.deviceResponse)== 16:
            self.isSendSuccess = True
            self.printWithHeader("Corrected Device's Response")
        else:
            self.isSendSuccess = False
            self.printWithHeader("Recieved Unexpected Device's Response")
            self.stop()
            # self.printWithHeader("sleep 4 second")
            # time.sleep(1)
            
    def main(self):
        while True:
            if self.action != None:
                try: 
                    if self.onAction==self.action:
                        next(actionFun)
                except Exception as e:
                    pass
                else:
                    actionFun = eval("self.{}()".format(self.action))
                    self.onAction=self.action
                
            
# Code below if for testing send/read "raycome" only
if __name__=='__main__':
    from configparser import ConfigParser
    import comport, time
    protocolConfig = ConfigParser()
    protocolConfig.read("config/banbangkhae.ini")
    raycomRPD7000=raycomRPD7000(protocolConfig["raycomRPD7000"], comport.comport)
    raycomRPD7000.main()
    
    # raycomRPD7000.connect()
    # raycomRPD7000.
    # raycomRPD7000.start()
    # # time.sleep(3)
    # raycomRPD7000.stop()