#!/usr/bin/env python
# coding: utf-8

from getmac import get_mac_address as gma
from datetime import datetime

import pexpect
import asyncio

class device:
    def __init__(self, hardwareConfig):
        self.device_name=hardwareConfig["name"]
        self.child = pexpect.spawn("gatttool -I")
        self.deviceAddr="18:7a:94:73:01:a3"
        self.deviceAddr=hardwareConfig["blueAddr"]
        self.temp=None
        self.msgReady=None
        self.isRunning=None
        self._msg={
            "name":self.device_name,
            "DID":gma(),
            "temp":None,
            "dt":-1
        }
        self.logHeader="[krKristaz]: "
        
    '''
        *****These Functions are used by commProtocol*****
    '''            
    def start(self):
        index=None
        if self.isRunning==True:
            print("{}Already Listening ...".format(self.logHeader))
            return
        self.isRunning=True
        while index != 0:
            self.child.sendline("connect {0}".format(self.deviceAddr))
            index = self.child.expect(["Connection successful",pexpect.EOF, pexpect.TIMEOUT])
            if self.isRunning==False or index==1:
                print("{} Aborted Connection Attempt".format(self.logHeader))
                return
        print("{} Begin Listening ...".format(self.logHeader))
        while self.isRunning==True:
            ind = self.child.expect(["Notification handle =",pexpect.EOF, pexpect.TIMEOUT], timeout=1)
            if ind == 1:
                break
            elif ind==2:
                self.msgReady=False
            else:
                self.temp=int(self.child.buffer.decode("unicode-escape")[18:23].replace(" ",""),16)/10
                self.msg=1
            self.child.sendline("connect {0}".format(self.deviceAddr))
        self.isRunning=False
        self.msgReady=False
    
    def stop(self):
        self.child.sendline("disconnect {0}".format(self.deviceAddr))
        self.isRunning=False
        self.msgReady=False
        print("{} Stop Listenning".format(self.logHeader))
        
    
    def reset(self):
        self.child.sendline("disconnect {0}".format(self.deviceAddr))
        self.child.close()
        self.child = pexpect.spawn("gatttool -I")
        self.isRunning=False
        self.msgReady=False
        
#     def run(self):
#         print(self.msg)


    '''
        Function below is not meant to be called from outside of the class
    '''
    @property
    def msg(self):
        return self._msg
    
    @msg.setter
    def msg(self, statMsg):
        
        if statMsg == 1:            
            self._msg["temp"]=self.temp
        else:
            self._msg["temp"]=None
        self._msg["dt"]=int(datetime.timestamp(datetime.now())*1000)
        self.msgReady=True
        
if __name__=='__main__':
    from configparser import ConfigParser
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config\banbangkhae.ini")
    krKristaz=device(hardwareConfig["krKristaz"])