import serial.tools.list_ports
import serial

class selecComport:
    def __init__(self, baudrate, device_name):
        self.ser=''
        self.baudrate=baudrate
        self.device_name=device_name
        
    def getSerial(self, port):           
        self.ser = serial.Serial(
        port="{}".format(port),
        baudrate=self.baudrate,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1,
        write_timeout=5
     #   bytesize=serial.EIGHTBITS
    )

    def getlistPort(self):
        myPorts = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        print(myPorts)
        for num, port in enumerate(myPorts):
            if port[0] == '/dev/ttyAMA0':
                pass
            else:
                print("({0}) {1}".format(num+1,port[0]))
        return myPorts
    
    def enterPort(self,myPorts):
        select_Num = 'port'
        while not isinstance(select_Num,int):
            select_Num = input("Enter Port Number {}: ".format(self.device_name))
            try:
                select_Num=int(select_Num)
            except:
                raise "Invalid Input try again..."
        select_Ports=myPorts[select_Num-1][0]
        return self.getSerial(select_Ports)
    
    def getSerObj(self):
        myPorts=self.getlistPort()
        if len(myPorts)<1:
            return "No ComPort Available"
        if myPorts[0][0]=="ttyAMA0":
            return "No ComPort Available"
        if len(myPorts)==1:
            return self.getSerial(myPorts[0][0])        
        return self.enterPort(myPorts)