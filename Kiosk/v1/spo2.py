import readStreamData

class spo2(readStreamData.readStream):
    def __init__(self, dataType, deviceObj):
        readStreamData.readStream.__init__(self, dataType, deviceObj)
        # self.name=None
        self.value=None
        self.raw=[]
        self.hr=None
        
    @property
    def msgObj(self):
        return self._msgObj
    
    @msgObj.setter
    def msgObj(self, isStream):
        self._msgObj.name=self.name
        self._msgObj.type=self.type
        self._msgObj.value=self.value
        self._msgObj.raw=self.raw
        self._msgObj.hr=self.hr
        
        if isStream:
            # for stream data
            self._msgObj.dt=self.timestamp
        else:
            # if only need to publish once
            self.dt=True
            self._msgObj.dt=self.dt
        
        self.msgQueue.put(dict(self._msgObj.__dict__))
        
        self.value=None
        self.raw=[]
        self.hr=None
        
if __name__ == '__main__':
    spo2=spo2(16)
    # spo2.run()
    spo2.value=True
    spo2._raw=1
    spo2.startStream()