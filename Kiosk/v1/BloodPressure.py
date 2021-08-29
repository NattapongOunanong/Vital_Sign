import device

class BloodPressure(device.device):
    def __init__(self,daviceType):
        device.device.__init__(self,daviceType)
        self.sys=None
        self.dia=None
        self.hr=None
        self.pressure={}
           
    @property
    def msgObj(self):
        return self._msgObj
    
    @msgObj.setter
    def msgObj(self, isVitalSign):
        self._msgObj.name=self.name
        self._msgObj.type=self.type
        self._msgObj.sys=self.sys
        self._msgObj.dia=self.dia
        self._msgObj.hr=self.hr
            
        self.dt=True
        self._msgObj.dt=self.dt
        self.msgQueue.put(dict(self._msgObj.__dict__))
        # Flush vital sign data: Blood Pressure
        self.sys=None
        self.dia=None
        self.hr=None
        
        
    
    # ************Not use***************
        
    def run(self):
        self.baudrate = 9600
        self.getSerial('COM7')
        
    # **********************************
        
# if __name__ == '__main__':
#     bp=BloodPressure()
#     bp.run()
#     bp.sys=1
#     print(bp.sys)