import serial.tools.list_ports

class showComport:    
    def getlistPort(self):
        '''
            Call this function to print out all available Serial Port
        '''
        myPorts = [tuple(p) for p in list(serial.tools.list_ports.comports())]
        # print(myPorts)
        for num, port in enumerate(myPorts):
            if port[0] == '/dev/ttyAMA0':
                pass
            else:
                print("({0}) {1}".format(num+1,port[0]))
        return myPorts
    
    def enterPort(self,myPorts):
        select_Num = 'port'
        while not isinstance(select_Num,int):
            select_Num = input("Enter Port Number {}: ".format(self.deviceName))
            try:
                select_Num=int(select_Num)
            except:
                raise "Invalid Input try again..."
        select_Ports=myPorts[select_Num-1][0]
        return self.getSerial(select_Ports)
    
    def getSerObj(self):
        '''
            Call this function if need manually select Serial Port
        '''
        myPorts=self.getlistPort()
        if len(myPorts)<1:
            return "No ComPort Available"
        if myPorts[0][0]=="ttyAMA0":
            return "No ComPort Available"
        if len(myPorts)==1:
            return self.getSerial(myPorts[0][0])        
        return self.enterPort(myPorts)
    
if __name__=="__main__":
    comport=showComport()
    comport.getSerObj()