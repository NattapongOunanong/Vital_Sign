from configparser import ConfigParser
import importlib
import threading

import mqtt
import jsonSerializer
import RTCmanager

import logging

# logging.basicConfig(level=logging.DEBUG,
#                       format='[%(levelname)s] (%(threadName)-9s) %(message)s',)

class Kiosk():
    def __init__(self, config):
        self.mqtt = mqtt.mqtt(config["mqtt"])
        self.RTCmanager=RTCmanager.RTCmanager()
        self.jsonSerializer=jsonSerializer.jsonGen()
        self.tmpMsg=None
        
    def run(self):
        # Create Thead for mqtt Protocol
        thread = threading.Thread(target=self.mqtt.run)
        thread.daemon=True
        thread.start()
        
        # Run forever
        while True:
            # logging.debug("test")
            
            # print(threading.enumerate())
            for deviceObj in self.RTCmanager.deviceDict.values():
                try:
                    message = deviceObj.msgQueue.get_nowait()
                    self.jsonSerializer.jsonManager(message)
                except Exception as e:
                    pass
                
            # if mqtt queue (on_message) is not empty
            if not self.mqtt.message.empty():
                self.tmpMsg = self.mqtt.message.get_nowait()
                self.RTCmanager.analyze(self.tmpMsg)
                
                # **************For "cmd"=="Status"*****************
                if eval(self.tmpMsg.payload)['cmd'] == "status":
                    for msg in self.RTCmanager.msgQueue:
                        message = msg.get(block=True)
                        self.jsonSerializer.jsonManager(message)
                    self.jsonSerializer.jsonSendStatus()
                # *************************************************

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
    configFile={"hardware":"config/banbangkhae.ini",
                "commProtocol":"config/emetWorksCommProtocol.ini"
            }
    config=ConfigParser()
    config.read(configFile["commProtocol"])
    configDevice= ConfigParser()
    configDevice.read(configFile["hardware"])


    kiosk=Kiosk(config)

    kiosk.run()