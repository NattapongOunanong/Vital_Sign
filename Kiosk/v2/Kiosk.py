from configparser import ConfigParser
import threading

import mqtt
import jsonSerializer
import RTCmanager

import logging

import krKristaz as temp
import raycomRPD7000 as bloodPressure
import spo2BlackBox as spo2

class Kiosk():
    def __init__(self, config):
        self.mqtt = mqtt.mqtt(config["mqtt"])
        self.RTCmanager=RTCmanager.RTCmanager()
        self.jsonSerializer=jsonSerializer.jsonGen()
        self.tmpMsg=None
        
        self.pressure=bloodPressure.bloodPressure(configDevice["raycomRPD7000"])
        self.spo2=spo2.spo2(configDevice['spo2'])
        self.temp=temp.temp(configDevice["krKristaz"])
        
        self.deviceDict={}
        self.deviceDict["temp"]=self.temp
        self.deviceDict["pressure"]=self.pressure
        self.deviceDict["spo2"]=self.spo2
        # print(self.deviceDict)
        
        # Create a list of queue to accommodate iteration
        self.msgQueue=[self.spo2.msgQueue, self.pressure.msgQueue,self.temp.msgQueue ]
        self.numDevice=len(self.deviceDict)
        
    def run(self):
        threadList=[]
        # Create Thead for mqtt Protocol
        thread = threading.Thread(target=self.mqtt.run)
        thread.daemon=True
        thread.start()
        
        # Create thread for each device
        for deviceName in self.deviceDict:
            target = eval("self."+str(deviceName)+".main") # eg. self.spo2.main, self.raycomRPD7000.main
            thread = threading.Thread(target=target, name=deviceName)
            thread.daemon=True
            thread.start()
            threadList.append(thread)
        
        # Run forever
        while True:
                        
            for deviceObj in self.deviceDict.values():
                try:
                    message = deviceObj.msgQueue.get_nowait()
                    self.jsonSerializer.jsonManager(message)
                except Exception as e:
                    pass
                
            # if mqtt queue (on_message) is not empty
            if not self.mqtt.message.empty():
                self.tmpMsg = self.mqtt.message.get_nowait()
                cmd_do = self.RTCmanager.analyze(self.tmpMsg,self.deviceDict.keys())
                # **************For "cmd"=="Status"*****************
                if eval(self.tmpMsg.payload)['cmd'] == "status":
                    for nameDevice in cmd_do:
                        self.deviceDict[nameDevice].action = "status"
                        message = self.deviceDict[nameDevice].msgQueue.get(block=True)
                        self.jsonSerializer.jsonManager(message)
                    self.jsonSerializer.jsonSendStatus()
                # *************************************************

                else:
                    self.deviceDict[cmd_do['type']].action = cmd_do['cmd']
            else:
                self.publish2Web()
                
    def publish2Web(self):
        # Publish mqtt Message to the Web
        while not self.jsonSerializer.msgQueue.empty():
            jsonMsg=self.jsonSerializer.msgQueue.get()
            if eval(self.tmpMsg.payload)['cmd'] == "status":
                self.mqtt.publish("remoteCtrlReply",jsonMsg)
            else:
                try:
                    self.mqtt.publish("vitalSign",jsonMsg)
                except Exception as e:
                    print(e)


if __name__ == '__main__':
    configFile={"hardware":"config/banbangkhae_Pi.ini",
                "commProtocol":"config/emetWorksCommProtocol.ini"
            }
    config=ConfigParser()
    config.read(configFile["commProtocol"])
    configDevice= ConfigParser()
    configDevice.read(configFile["hardware"])


    kiosk=Kiosk(config)

    kiosk.run()