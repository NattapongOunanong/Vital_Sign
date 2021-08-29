from binascii import unhexlify,hexlify
from datetime import datetime
import time

# Utility Function for all devices
class generalFun:
    def __init__(self):
        self.timeUp=None
        self.headerMsg=None
        
    '''
        Data Conversion
    '''
    @staticmethod
    def hexStr2Int(hexstr):
        return int.from_bytes(hexstr,"big")
        
    @staticmethod
    def hexStringtoByteArray(hexString):
        hexString=hexString.replace(" ","")
        byteArray=unhexlify(hexString)
        return byteArray
    
    @staticmethod
    def hexifyByteArray(hexString):
        return hexlify(hexString).decode('unicode-escape').upper()
        
    '''
        Time-related
    '''
    @staticmethod    
    def getTimestamp():
        # timestamp in milliseconds
        return int(datetime.timestamp(datetime.now())*1000)
    
    @staticmethod
    def wait(second):
        time.sleep(second)
    
    def timer(self, duration, elaspedTime, startTime):
        duration*=1000 #timeout
        self.timeUp=False
        elaspedTime=self.getTimestamp()-startTime
        if elaspedTime>=duration:
            self.timeUp=True
            return
        return elaspedTime
        # while timediff<=countDown:
        #     timediff=self.getTimestamp()-startTime
        # self.timeUp=True
            
    '''
        Print-related Functions
    '''
    def printWithHeader(self, msg2print):
        # log in this format- [device name]: something...
        # Useful when having multiple devices
        msg2print=str(msg2print)
        print(self.headerMsg+" "+msg2print+"\n")
        
    def setMsgHeader(self,name):
        self.headerMsg="["+str(name)+"]:"