from queue import Queue
import genericFun
        
class device(genericFun.generalFun):
    def __init__(self):
        genericFun.generalFun.__init__(self)
        self.isRunning=None
        self.dt=None
        self.action=None
        
        self._msgObj=''
        self.msgQueue=Queue(maxsize=1e3)
        
    def get_status(self):
        self.status()
        
    def status(self):
        # When server asked for list of device
        self.dt=True
        self.msg={
            "name":self.name,
            "type":self.type,
            "dt":self.dt
        }
        self.msgQueue.put(dict(self.msg))
        self.action=(yield)
        
    def get_value(self):
        self.msgObj=True
        
    @property
    def msgObj(self):
        return self._msgDict
    
    @msgObj.setter
    def msgObj(self, isStream):
        self._msgDict={
            "name":self.name,
            "type":self.type
        }
        for vitalSign in self.vitalSign:
            self._msgDict[vitalSign]=eval("self."+"{}".format(vitalSign))
            # eval("self."+"{}=None".format(vitalSign))
            # eval("del "+"self."+"{}".format(vitalSign))
        if isStream:
                # for stream data
            self._msgDict['dt']=list(self.timestamp)
            self.timestamp.clear()
        else:
            # if only need to publish once
            self.dt=True
            self._msgDict['dt']=self.dt
            
        self.msgQueue.put(self._msgDict)
        # print(self._msgDict)
        
        
    @property
    def dt(self):
        return self._dt
    
    @dt.setter
    def dt(self, dummy):
        self._dt=self.getTimestamp()
        
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
                # if self.action != None:
                #     print(self.action, e,"\n")
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
    