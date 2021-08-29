#!/usr/bin/env python
# coding: utf-8

import time
import paho.mqtt.client as mqtt
import numpy as np
import asyncio
from binascii import unhexlify,hexlify
from json import dumps
from calc_spo2 import calc_SPO2
from statistics import mean, stdev
from getmac import get_mac_address as gma


from json import dumps, loads
from threading import Thread

from getComportclass import *
from serial_spo2 import *
from bloodPressure_rbd7k import *
from thermalGun import *

rbp7k=readRBD7k()
thermalgun=thermalgun()
spo2=readSPO2()

class mqttClient(mqtt.Client):
    def __init__(self):
        super().__init__()
        self.urlBroker='3.0.54.110'
        self.portBroker=8082
        self.usr="mqtt"
        self.password="12345"
        self.publisherTopic='vitalSign'
        self.subscribeTopic='remoteCommand'
        self.devices={
            "krKristaz":thermalgun.sendCommand,
            "raycomRPD7000": rbp7k.sendCommand,
            "spo2": spo2.sendCommand
                        }
        self.vitalSign={
             "patientId":"None",
             "DID":gma(),
             "name":"Device Brand",
             "spo2":{"value":None,"raw":[],"hr":None},
             "hr":None,
             "temp":None,
             "pressure":{"dia":None,"sys":None,"hr":None},
             "dt": None
            }
        self.client_id="pI"
        
    def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code {0}".format(str(rc)))
        client.subscribe(self.subscribeTopic)
        
    def on_disconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected Disconnection: mqttServer.py")
        client.reconnect()
        
    def on_message(self,client, userdata, msg):
        print("Message received-> " + msg.topic + "=> " + str(msg.payload))
        message = loads(msg.payload.decode('utf8').replace("'", '"'))
        asyncio.run(self.devices[message["name"]](message["cmd"]))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)
        
    def run(self):
        self.username_pw_set(username=self.usr, password=self.password)
        self.connect(self.urlBroker, self.portBroker, 60)
        
        rc = 0
        while rc == 0:
            rc = self.loop()
        if rc!=0:
            self.run()
        return rc



mqttc = mqttClient()
rc = mqttc.run()

print("rc: "+str(rc))