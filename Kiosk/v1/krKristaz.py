#!/usr/bin/env python
# coding: utf-8
import Temp

class krKristaz(Temp.temp):
    def __init__(self, hardwareConfig, device):
        Temp.temp.__init__(self, device)
        # device configuration: name, device type, bluetooth address
        self.name=hardwareConfig["name"]
        self.type=hardwareConfig["type"]
        self.device.addr=hardwareConfig["blueAddr"]
        self.headerMsg="[krKristaz]:"
        
        self.ismsgReady=None
        self.isRunning=None
        
    def start(self):
        index=None
        while index != 0:
            index=self.connect()
            if index==1:
                self.printWithHeader("Connection Aborted")
                return
            # return to main()
            yield
            
        self.printWithHeader("Connection Successful...")
        self.printWithHeader("Begin Listening...")
        self.isRunning=True
        while self.isRunning==True:
            ind = self.readMeasurement()
            if ind==1:
                break
            elif ind==2:
                continue
            else:
                self.readMeasurement()
                self.decodeTemp()
            self.connect()
            self.printWithHeader("Temperature: "+str(self.temp) +" dt: "+str(self.dt))
            if self.action != "start":
                break
            yield
        self.reset()
    
    def stop(self):
        # self.action=(yield)
        self.disconnect()
        # self.close()
        self.printWithHeader("Stop Listenning")
        self.action=(yield)
        
    def decodeTemp(self):
        a=self.device.child.buffer.decode("unicode-escape")[18:23].replace(" ","")
        self.temp = int(a,16)/10
        # self.printWithHeader("decode", self.temp)
        self.msgObj=True
        
        
if __name__=='__main__':
    from configparser import ConfigParser
    import gattPi
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config/banbangkhae_Pi.ini")
    krKristaz=krKristaz(hardwareConfig["krKristaz"], gattPi.gattTool)
    krKristaz.start()