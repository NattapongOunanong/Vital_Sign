import serial

class comport:
    def __init__(self):
        self.ser=None
        self.baudrate=None
        self.addr=None
        
    def connect(self):
        # Create pyserial Object to communicate with serial port
        '''
            Call this function to get Serial Port Object
        '''
        self.ser = serial.Serial(
            port="{}".format(self.addr),
            baudrate=self.baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            write_timeout=5
        )
        
    def reconnect(self):
        try:
            # Re-open serial port
            self.ser.close()
            self.ser.open()
        except:
            # reset serial port if error occur
            self.reset()
        
    def disconnect(self):
        try: 
            self.ser.close()
        except:
            pass
           
    def read(self, *numByte):
        # read out data from serial port
        if not numByte:
            return self.ser.read()
        return self.ser.read(numByte[0])
    
    def getStatus(self):
        if self.ser is None:
            return False
        else:
            return self.ser.isOpen()
        
    def reset(self):
        self.ser=None
        self.connect()
        self.action=(yield)
    
    def getNumDataInBuffer(self):
        # get a number of byte available in input buffer
        # return 19
        return self.ser.in_waiting
    
    def send(self, cmd):
        return self.ser.write(cmd)
    
        
