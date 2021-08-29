#!/usr/bin/env python
# coding: utf-8
# import Temp
import gattPi
import device

class temp(gattPi.gattTool, device.device):
    def __init__(self, hardwareConfig):
        gattPi.gattTool.__init__(self)
        device.device.__init__(self)
        # device configuration: name, device type, bluetooth address
        self.name=hardwareConfig["name"]
        self.type=hardwareConfig["type"]
        self.addr=hardwareConfig["blueAddr"]
        self.headerMsg="[krKristaz]:"
        self.vitalSign=["temp"]
        
        self.ismsgReady=None
        self.isRunning=None
        
    def start(self):
        index=None
        while index != 0:
            # print(index)
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
            ind = self.read()
            if ind==1:
                break
            elif ind==2:
                continue
            else:
                self.read()
                self.decodeTemp()
            self.connect()
            self.printWithHeader("Temperature: "+str(self.temp) +" dt: "+str(self.dt))
            if self.action != "start":
                break
            yield
        self.reset()
    
    def stop(self):
        self.disconnect()
        # self.close()
        self.printWithHeader("Stop Listenning")
        self.action=(yield)
        
    def decodeTemp(self):
        a=self.child.buffer.decode("unicode-escape")[18:23].replace(" ","")
        self.temp = int(a,16)/10
        # self.printWithHeader("decode", self.temp)
        self.msgObj=False
        
        
if __name__=='__main__':
    from configparser import ConfigParser
    import gattPi
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config/banbangkhae_Pi.ini")
    krKristaz=krKristaz(hardwareConfig["krKristaz"])
    krKristaz.start()