import device

class temp_krKristaz(device.device):
    def __init__(self,communicationProtocol):
        device.device.__init__(self,communicationProtocol)
        self.name = 'krKristaz'
        self.type = 'Temp'
        
        self.communication = communicationProtocol()
        self.value=0
        
        
    @property
    def msgObj(self):
        return self._msgObj
    
    @msgObj.setter
    def msgObj(self, isVitalSign):
        self._msgObj.name=self.name
        self._msgObj.type=self.type
        self._msgObj.temp=self.temp
        self.dt=True
        self._msgObj.dt=self.dt
        self.msgQueue.put(dict(self._msgObj.__dict__))
        self._msgObj.temp=None
        
if __name__ == '__main__':
    tmp = temp()
    
    
    
        def __init__(self, deviceObject):
            genericFun.generalFun.__init__(self)
        self.device = deviceObject()
        self.name=None
        self.type=None
        # self.DID=gma()
        self.isRunning=None
        self.dt=None
        self.action=None
        self.value=0
        
        # class msgObj(object):
        #     pass
        self._msgObj=''
        self.msgQueue=Queue(maxsize=1e3)