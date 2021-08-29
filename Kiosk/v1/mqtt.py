#!/usr/bin/env python
# coding: utf-8
from json import dumps, loads

import time
import paho.mqtt.client as mqtt

from queue import Queue 

message=1

class mqtt(mqtt.Client):
    def __init__(self, mqttParam):
        super().__init__()
        # config for mqtt server
        self.message=Queue(maxsize=10)
        self.urlBroker=mqttParam['url']
        self.portBroker=int(mqttParam['port'])
        self.usr=mqttParam['username']
        self.password=mqttParam['password']
        self.mqttTopic=eval(mqttParam['topic'])
        self.publisherTopic=self.mqttTopic['publisher']
        self.subscribeTopic=self.mqttTopic['subscriber']
        self.listeningMsgKey=["name","cmd"]
        self.isPublish=None
        
    '''
        Callback Functions
    '''
    def on_connect(self, client, userdata, flags, rc):
        # When connected to broker
        print("Connected with result code {0}\n".format(str(rc)))
        for subtopic in self.subscribeTopic:
            client.subscribe(subtopic)
        
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnection")
        client.reconnect()
        
    def on_message(self,client, userdata, msg):
        # Do the following when message is published to subscribed topic
        try:
            self.message.put(msg)
        except Exception as e:
            print(e)
        print("Message received-> " + msg.topic + ": " + str(msg.payload)+"\n")

    def on_subscribe(self, client, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos)+"\n")
        
    def on_log(self, mqttc, obj, level, string):
        # show log on the terminal
        print(string+"\n")
                
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
    message=None
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
    # import importlib
    # hardwareObj={}
    # for config in hardwareConfig.sections():
    #     hardwareObj[config]=getattr(importlib.import_module(config),config)(hardwareConfig[config])
    
    '''
        create MQTT class and run it
    '''
    
    mqttc = commProtocol(mqttParam=protocolParam['mqtt'])
    
    rc = mqttc.run()

    print("rc: "+str(rc))