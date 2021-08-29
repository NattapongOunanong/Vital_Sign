#!/usr/bin/env python
# coding: utf-8
from json import dumps, loads
from threading import Thread

import time
import paho.mqtt.client as mqtt
import asyncio

class commProtocol(mqtt.Client):
    def __init__(self, mqttParam, hardware, hardwareConfig):
        super().__init__()
        self.urlBroker=mqttParam['url']
        self.portBroker=int(mqttParam['port'])
        self.usr=mqttParam['username']
        self.password=mqttParam['password']
        self.mqttTopic=eval(mqttParam['topic'])
        self.publisherTopic=self.mqttTopic['publisher']
        self.subscribeTopic=self.mqttTopic['subscriber']
        self.listeningMsgKey=["name","cmd"]
        self.isPublish=None
        self.hardware=hardware
        self.hardwareConfig=hardwareConfig
        
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code {0}\n".format(str(rc)))
        for subtopic in self.subscribeTopic:
            client.subscribe(subtopic)
        
    def on_disconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnection")
        client.reconnect()
        
    def on_message(self,client, userdata, msg):
        print("Message received-> " + msg.topic + ": " + str(msg.payload)+"\n")
        message = eval(msg.payload.decode('utf8'))
        if message["cmd"]=="status" and not message.get("name"):
            self.notifyDevName(client)
            return
        for msg in self.listeningMsgKey:
            try:
                message[msg]
            except:
                print("Invalid Message")
                return
        actionThread=Thread(target=self.publisher,args=[message,client])
        actionThread.start()

    def on_subscribe(self, client, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos)+"\n")
        
    def on_log(self, mqttc, obj, level, string):
        print(string+"\n")
        
    def publisher(self, msg, client):
        if self.hardware[msg["name"]].isRunning==True and msg["cmd"]=="start":
            print("[{}]: is Running".format(self.hardware[msg["name"]].device_name))
            return
        testThread=Thread(target=getattr(self.hardware[msg["name"]],msg["cmd"]))
        testThread.start()
        if self.hardware[msg["name"]].msgReady == True:
            client.publish(self.publisherTopic[0], dumps([self.hardware[msg["name"]].msg]))
            self.hardware[msg["name"]].msgReady = False
        time.sleep(0.5)
        dt=0
        while self.hardware[msg["name"]].isRunning:
            if dt<self.hardware[msg["name"]].msg['dt']:
                if self.hardware[msg["name"]].msgReady == True:
                    client.publish(self.publisherTopic[0], dumps([self.hardware[msg["name"]].msg]))
                    dt=self.hardware[msg["name"]].msg['dt']
                    
    def notifyDevName(self, client):
        dictHardware=[]
        for name in self.hardware:
            for typeHardware in eval(self.hardwareConfig[name]['type']):
                dictHardware.append({"name": name, "type": typeHardware})
        client.publish(self.publisherTopic[1], dumps(dictHardware))
                
    def run(self):
        self.username_pw_set(username=self.usr, password=self.password)
        self.connect(self.urlBroker, self.portBroker, 60)
        
        rc = 0
        while rc == 0:
            rc = self.loop()
        if rc!=0:
            self.run()
        return rc

if __name__=='__main__':
    from configparser import ConfigParser
    '''
        get MQTTS config
    '''
    protocolParam = ConfigParser()
    protocolParam.read('config/emetWorksCommProtocol.ini')
    
    '''
        get hardware config
    '''
    hardwareConfig = ConfigParser()
    hardwareConfig.read('config/banbangkhae.ini')
    '''
        get associated class objectS
    '''
    import importlib
    hardwareObj={}
    for config in hardwareConfig.sections():
        hardwareObj[config]=getattr(importlib.import_module(config),"device")(hardwareConfig[config])
    
    '''
        create MQTT class and run it
    '''
    
    mqttc = commProtocol(mqttParam=protocolParam['mqtt'], hardware=hardwareObj, hardwareConfig=hardwareConfig)
    
    rc = mqttc.run()

    print("rc: "+str(rc))