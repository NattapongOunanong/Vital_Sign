#!/usr/bin/python

import pexpect
# Use This Class to Communicate with Bluetooth Device via Raspberry Pi
class gattTool:
    def __init__(self):
        self.child = None
        self.addr = None
        
    def connect(self):
        if self.child==None:
            # Initialize Gatt Protocol in Raspberry Pi
            self.child = pexpect.spawn("gatttool -I")
        if self.addr is None:
            print("No Bluetooth Address Provided")
            return
        # Tell GATT to connect to device
        self.child.sendline("connect {0}".format(self.addr))
        # wait until Raspberry Pi Confirm Connection
        return self.child.expect(["Connection successful",pexpect.EOF, pexpect.TIMEOUT], timeout=0.5)
        
    def reconnect(self):
        # Reconnect to Bluetooth Device
        if self.addr is None:
            print("No Bluetooth Address Provided")
            return
        self.child.sendline("connect {0}".format(self.addr))
            
    def disconnect(self):
        # Disconnect from device
        self.child.sendline("disconnect {0}".format(self.addr))
        
    def read(self, *args):
        # Read Data from Notification, Argument is not Needed
        return self.child.expect(["Notification handle =",pexpect.EOF, pexpect.TIMEOUT], timeout=1)
    
    def close(self):
        self.child.close()
        self.child = None
        
    def reset(self):
        self.close()
        self.__init__()
        
if __name__=='__main__':
    gattToolTmp=gattTool()
    print(gattToolTmp.__dict__)