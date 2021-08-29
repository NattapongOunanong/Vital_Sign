#!/usr/bin/env python
# coding: utf-8
import device
import comport
import tkinter as tk
class bloodPressure(device.device,comport.comport):
    def __init__(self, hardwareConfig):
        comport.comport.__init__(self)
        device.device.__init__(self)
        
        # device configuration: name, baudrate, device type, port address, command list, and measurement timeout
        self.name=hardwareConfig["name"]
        self.type=hardwareConfig["type"]
        self.baudrate=hardwareConfig["baudrate"]
        self.addr=hardwareConfig["comport"]
        self.commandList=eval(hardwareConfig["command"].replace("\'", "\""))
        self.timeout=eval(hardwareConfig["timeout"])
        self.deviceResponse=None
        
        # pressure data in byte array
        self.sysByte=14
        self.diaByte=16
        self.hrByte=18
        
        self.numAttempt=0
        self.setMsgHeader(self.name)
        self.resultNumByte=18
        self.maxAttempt=3
        self.data=None
        
        self.sys=None
        self.dia=None
        self.hr=None
        self.vitalSign=["sys", "dia", "hr"]
        
        '''
            Flag variables
        '''
        self.isReadSuccess=None #see if device return correct data
        self.isSendSuccess=None
    
    
    '''
        Action Function for device
    '''        
    def start(self):
        self.isReadSuccess=False
        
        if not self.shouldSendStart():
            return
        
        self.printWithHeader("Begin Blood Pressure Measurement")
        startByteCommand = self.hexStringtoByteArray(self.commandList["start"])
        self.send(startByteCommand) #send commmand to raycome
        
        getData=self.getData()
        while True:
            next(getData)
            yield
        self.isRunning=False
        '''
            Uncomment if not connect to the device
        '''
        # self.sys=1
        # self.dia=2
        # self.hr=3
        # self.msgObj=True
        self.action = (yield)
        #***********************************************************
        
    def stop(self):
        # Stop The Device
        self.printWithHeader("Stop Blood Pressure Measurement")
        stopByteCommand=self.hexStringtoByteArray(self.commandList["stop"])
        self.send(stopByteCommand)
        self.isRunning=False
        self.action=(yield)
            
    
            
            
            
            
    '''
        Function below is not meant to be called from outside of the class
    '''
    def shouldSendStart(self):
        #*********Return if the device is measuring blood pressure***************
        if self.isRunning:
            self.printWithHeader("Already Running...")
            return False
        #************************************************************************
        
        # see if number of attempts exceed threshold value **********************
        self.numAttempt+=1
        if self.numAttempt>self.maxAttempt:
            self.printWithHeader("Number of measurements exceeded {} attempts, please check your setup".format(self.maxAttempt))
            self.numAttempt=0
            self.action=None
            self.isRunning=False
            return False
        
        return True
        #*************************************************************************
        
    def getData(self):
        self.getDeviceResponse()
        # if device acknowledge command and return the corrected number of bytes,
        # wait until measurement is completed
        self.checkSendSuccess()
        if self.isSendSuccess:
            waitIter=self.wait4Data()
            self.isReadSuccess=False
            self.action=None
            while not self.isReadSuccess and self.isRunning:
                # print("hello")
                isDone = next(waitIter)
                if isDone == True:
                    break
                yield self.isReadSuccess
                
        if self.isReadSuccess:
            
            self.getPressure()
            yield self.isReadSuccess
        else:
            self.printWithHeader("Recieve Wrong Data Format ... Will Try Again")
            self.isRunning=False
            next(self.reset())
            self.retryMeasurement()
            yield self.isReadSuccess
            return
        
        self.numAttempt=0
        
        # Retrieve Data from Hex String, and convert it to vital sign
        self.sys=self.hexStr2Int(hexstr=self.data[self.sysByte])
        self.dia=self.hexStr2Int(hexstr=self.data[self.diaByte])
        self.hr=self.hexStr2Int(hexstr=self.data[self.hrByte])
        self.printWithHeader("Completed Measurement")
        self.msgObj=False
        self.action=None
        self.isRunning=False
        
    def getDeviceResponse(self):
        # Read out acknowledgement of the command from the raycome-RPD7000 device
        serialResponse = self.read(8)
        self.deviceResponse = self.hexifyByteArray(serialResponse)
    
    def getPressure(self):
        hexstr=[]
        for data in range(self.getNumDataInBuffer()):
            hexstr.append(self.read())
        self.data=hexstr

    def wait4Data(self):
        # 
        elaspedTime=0
        startTime=self.getTimestamp()
        self.timeUp=False
        while self.getNumDataInBuffer()<=self.resultNumByte:
            yield self.isReadSuccess
            elaspedTime=self.timer(duration=self.timeout, elaspedTime=elaspedTime, startTime=startTime)
            if self.timeUp:
                self.printWithHeader("Reading Timeout...try again")
                self.retryMeasurement()
                return
        self.isReadSuccess=True
        yield self.isReadSuccess
        
    def checkSendSuccess(self):
        # Validate response from device
        if len(self.deviceResponse)== 16:
            self.isSendSuccess = True
            self.isRunning=True
            self.printWithHeader("Corrected Device's Response")
        else:
            self.isSendSuccess = False
            self.printWithHeader("Recieved Unexpected Device's Response")
            self.retryMeasurement()
            self.wait(5)
    
    def retryMeasurement(self):
        next(self.stop())
        self.wait(5) #Wait until device is completely retract (approximately 5 seconds)
        self.isReadSuccess=False
        self.timeUp=False
        self.start()
        

            
# Code below if for testing send/read "raycome" only
if __name__=='__main__':
    from configparser import ConfigParser
    import comport, time
    window = tk.Tk()
    protocolConfig = ConfigParser()
    protocolConfig.read("config/banbangkhae.ini")
    raycomRPD7000=raycomRPD7000(protocolConfig["raycomRPD7000"])
    raycomRPD7000.main()