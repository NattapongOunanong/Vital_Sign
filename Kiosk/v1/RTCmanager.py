
from configparser import ConfigParser

import comport, gattPi
import raycomRPD7000
import spo2BlackBox
import threading
import krKristaz
# import krKristaz as something

class RTCmanager(object):
    def __init__(self):
        configDevice=ConfigParser()
        configDevice.read("config/banbangkhae.ini")
        
        self.payload=None #message Object
        self.deviceDict={}
        
        # #reate 
        self.raycomRPD7000=raycomRPD7000.raycomRPD7000(configDevice["raycomRPD7000"], comport.comport)
        self.spo2=spo2BlackBox.spo2BlackBox(configDevice['spo2'], 10, comport.comport)
        self.krKristaz=krKristaz.krKristaz(configDevice["krKristaz"], gattPi.gattTool)
        self.deviceDict["raycomRPD7000"]=self.raycomRPD7000
        self.deviceDict["spo2"]=self.spo2
        self.deviceDict["krKristaz"]=self.krKristaz
        
        # Create a list of queue to accommodate iteration
        self.msgQueue=[self.spo2.msgQueue, self.raycomRPD7000.msgQueue, self.krKristaz.msgQueue]
        self.numDevice=len(self.deviceDict)
        
        # Create thread for each device
        for deviceName in self.deviceDict:
            target = eval("self."+str(deviceName)+".main") # eg. self.spo2.main, self.raycomRPD7000.main
            thread = threading.Thread(target=target, name=deviceName)
            thread.daemon=True
            thread.start()
        
    def analyze(self,command):
        # Convert message object into to dictionary
        self.payload=eval(command.payload)
        self.send()
        
    def send(self):
        # Send "cmd" to the thread with the same "name"
        if 'name' not in self.payload:
            # if "name" is not provided, send "cmd" to all devices
            for deviceName in self.deviceDict:
                self.deviceDict[deviceName].action=self.payload['cmd']
            return
        else:
            self.deviceDict[self.payload['name']].action=self.payload['cmd']
        

        