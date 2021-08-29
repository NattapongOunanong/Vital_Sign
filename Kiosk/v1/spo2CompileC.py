#!/usr/bin/env python
# coding: utf-8

from binascii import unhexlify,hexlify
from getmac import get_mac_address as gma
from datetime import datetime
from collections import deque
from statistics import mean, stdev
from ctypes import *

import time
import asyncio
import numpy as np

from comPort import selecComport
from calcSpo2 import calcSpo2

class spo2_1(selecComport,calcSpo2):
    def __init__(self, path_to_c_function):
        calcSpo2.__init__(self)
        self.spo2Function = CDLL(path_to_c_function)
            
    '''
    These method response to "cmd"
    ''' 
    def start(self):
        self.spo2Function.start()
                    
    def stop(self):
        self.spo2Function.stop()
            
    def reset(self):
        self.spo2Function.reset()
        
    def status(self):
        self.spo2Function.status()
        
class spo2_2(selecComport):
    def __init__(self, path_to_c_function):
        calcSpo2.__init__(self)
        self.spo2Function = CDLL(path_to_c_function)
            
    '''
    These method response to "cmd"
    ''' 
    def start(self):
        self.spo2Function.start()
                    
    def stop(self):
        self.spo2Function.stop()
            
    def reset(self):
        self.spo2Function.reset()
        
    def status(self):
        self.spo2Function.status()

        
if __name__=='__main__':
    from configparser import ConfigParser
    hardwareConfig = ConfigParser()
    hardwareConfig.read("config/banbangkhae.ini")
    spo2=device(hardwareConfig["spo2"])