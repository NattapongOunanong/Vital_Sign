
from configparser import ConfigParser

import threading

class RTCmanager(object):
    def __init__(self):
        self.payload=None #message Object
        
    def analyze(self,command,*deviceList):
        # Convert message object into to dictionary
        self.payload=eval(command.payload)
        if 'type' not in self.payload:
            return self.sendStatus(deviceList[0])
        if self.payload['type'] == 'hr':
            self.payload['type'] = 'pressure' # for now, cuz blood pressure can do heartrate
        return self.send()
        
    def send(self):
        # Send "cmd" to the thread with the same "name"
        return self.payload

    def sendStatus(self, deviceList):
        list_payload=[]
        for deviceName in deviceList:
            list_payload.append(deviceName)
        return list_payload