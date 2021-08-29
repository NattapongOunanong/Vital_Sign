# from getmac import get_mac_address as gma
from queue import Queue
import genericFun
class msgObj(object):
            pass
        
class device(genericFun.generalFun):
    def __init__(self, deviceObject):
        genericFun.generalFun.__init__(self)
        self.device = deviceObject()
        self.name=None
        self.type=None
        # self.DID=gma()
        self.isRunning=None
        self.dt=None
        self.action=None
        
        # class msgObj(object):
        #     pass
        self._msgObj=''
        self.msgQueue=Queue(maxsize=1e3)
    
    def readStatus(self):
        # Return device name and type
        stat=(self.device.name,self.device.type)
        return stat
    
    def connect(self):
        return self.device.connect()
    
    def disconnect(self):
        self.isRunning=False
        self.device.disconnect()
        
    def readMeasurement(self, *numByte):
        self.isRunning=True
        return self.device.read(numByte)
    
    def checkStatus(self):
        return self.device.getStatus()
    
    def reset(self):
        self.isRunning=False
        self.printWithHeader("Reset Connection")
        try:
            self.device.reset()
        except:
            pass
        self.action=(yield)
        
    def reconnect(self):
        self.device.reconnect()
        
    def close(self):
        self.isRunning=False
        self.device.close()
        
    @property
    def dt(self):
        return self._dt
    
    @dt.setter
    def dt(self, dummy):
        self._dt=self.getTimestamp()
        
    # Publish to "remoteCtrlReply" topic to activate start button on the Web
    def status(self):
        self.action=(yield)
        self.msgObj=False
        self.isRunning=False
        
    # Run Coroutine for particular device
    def main(self):
        try:
            actionFun=self.connect()
        except Exception as e:
            print(e)
        actionFun=None
        while True:
            try:
                # next(actionFun)
                actionFun.send(None)
            except Exception as e:
                # print(self.action, e,"\n")
                if self.action == None:
                    actionFun=None
                else:
                    actionFun=eval("self.{}()".format(self.action))
            
        
if __name__=='__main__':
    import comport
    deviceObj = device(comport.comport)
    deviceObj.device.baudrate=9600
    deviceObj.device.addr='COM7'
    deviceObj.connect()
    print(deviceObj.checkStatus())
    