import device
class readStream(device.device):
    def __init__(self):
        device.device.__init__(self)
        self.dataArray=[]
        self.blockArray=[]
        self.bufferArray=[]
        self.timestamp=[]
        
        self.numByte=7
        self.numBlock=100
        self.startByte=0
        
        self.isStartByte=None
        self.isEnoughData=None
        self.isBeginString=None
        
        self.data=None
        self.streamData=None
        
        # self.ser=self.connect()
        # self.file=open("spo2_data.txt",'r')
        
    def startStream(self,ser):
        while True:
            '''
                For reading data from file (Currently, don't have the hardware)
            '''
            # yield
            # self.data = int(self.file.readline())
            try:
                self.data = int.from_bytes(self.read(),"big")
            except Exception as e:
                print(e)
            if not isinstance(self.data,int):
                print("Found Blank Space")
                self.close()
                break
            # self.dataArray.append(self.data)
            
            self.checkStartByte()
            
            if self.isStartByte:
                self.isBeginString=True
                # self.dataArray.append(self.data)
                self.isStartByte=False #Reset variable back to False
                
            if self.isBeginString:
                self.dataArray.append(self.data)
                self.dt=True
                self.timestamp.append(int(self.dt))
                self.checkNumByte()
                
            self.checkEnoughData()
            if self.isEnoughData:
                # return self.streamData
                return
        self.file.close()
        return self.streamData

            
    def checkStartByte(self):
        if self.data == self.startByte:
            self.isStartByte = True
        else:
            self.isStartByte = False
        # self.dataArray.clear()
            
    def checkNumByte(self):
        if len(self.dataArray)>=self.numByte:
            self.blockArray.append(list(self.dataArray))
            self.isBeginString=False
            self.dataArray.clear()
            
    def checkEnoughData(self):
        if len(self.blockArray)>=self.numBlock:
            self.streamData=list(self.blockArray)
            self.blockArray.clear()
            self.isEnoughData=True
            # return self.raw
        else:
            self.isEnoughData=False
        
    def raw2Integer(self):
        return int(self.data,self.dataType)
                    
    
        
if __name__ == '__main__':
    rStream=readStream()
    rStream.startStream()