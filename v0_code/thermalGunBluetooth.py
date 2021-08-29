# import pexpect
import requests
import json

# DEVICE = "18:7a:94:73:01:a3" #Thermal Gun Address - 'Complete Local Name' = 'btutu-01A3'

# child = pexpect.spawn("gatttool -I")
# child.sendline("connect {0}".format(DEVICE))
# child.expect("Connection successful", timeout=20)

# URL = "http://127.0.0.1:5000/vitalSign"

class thermalgun:
    def __init__(self):
        self.url = "http://127.0.0.1:5000/vitalSign/"
        self.bAddress = "18:7a:94:73:01:a3"
        self.child = pexpect.spawn("gatttool -I")
        
    def connect(self):
        self.child.sendline("connect {0}".format(DEVICE))
        self.child.expect("Connection successful", timeout=20)
                
    def post(self):
        
        
while 1:
	# child.expect("Notification handle =",timeout=None)
	# measuredTemp={"Temperature":int(child.buffer.decode("unicode-escape")[18:23].replace(" ",""),16)/10}
	measuredTemp={"patient_id":1,"temperature":36.6, "done":False}
	response = requests.put(url=URL, data=json.dumps(measuredTemp))
	print(requests.get(url=URL, params = {"status":True, "tool":"ThermalGun"}).content)
	print(requests.get(url=URL).content)
	print(response.content)
