import pexpect
import paho.mqtt.client as mqtt
import asyncio
import time
from datetime import datetime
from threading import Thread
from json import dumps
from getmac import get_mac_address as gma

class thermalgun:
    def __init__(self):
        self.child = pexpect.spawn("gatttool -I")
        self.device="18:7a:94:73:01:a3"
        self.command={
            "start":self.connect,
            "stop":self.disconnect,
            "reset":self.reset
        }
        self.client = mqtt.Client()
        self.client.on_disconnect = self.onDisconnect
        self.client.username_pw_set(username="mqtt", password="12345")
        self.client.connect('3.0.54.110', 8082)
        self.statusFlag=False
        
    def connect(self):
        index=None
        if self.statusFlag==True:
            print("Already Listening ...")
            return
        self.statusFlag=True
        while index != 0:
            self.child.sendline("connect {0}".format(self.device))
            index = self.child.expect(["Connection successful",pexpect.EOF, pexpect.TIMEOUT])
            if self.statusFlag==False or index==1:
                print("Abort Connection Attempt")
                return
        print("Connection Successful")
        while self.statusFlag==True:
            ind = self.child.expect(["Notification handle =",pexpect.EOF, pexpect.TIMEOUT], timeout=1)
            if ind == 1:
                break
            elif ind==2:
                self.client.reconnect()
                continue
            msg=self.getMsg()
            self.child.sendline("connect {0}".format(self.device))
            self.client.publish("vitalSign",dumps(msg))
            self.client.disconnect()
        self.statusFlag=False
    
    def disconnect(self):
        self.child.sendline("disconnect {0}".format(self.device))
        self.statusFlag=False
        print("Stop Listenning to Thermal Gun \n")
        
    def getMsg(self):
        msg=[{
            "DID":gma(),
            "patientId":None,
            "name":"krKristaz",
            "temp":int(self.child.buffer.decode("unicode-escape")[18:23].replace(" ",""),16)/10,
            "dt":datetime.timestamp(datetime.now())*1000
        }]
        return msg
    
    def reset(self):
        self.child.sendline("disconnect {0}".format(self.device))
        self.child.close()
        self.child = pexpect.spawn("gatttool -I")
        
    async def sendCommand(self,command):
        listeningThread=Thread(target=self.command[command])
        listeningThread.start()
    
    def onDisconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection KRkristaz")
        self.client.reconnect()