import time, pexpect
import paho.mqtt.client as mqtt
from serial_spo2 import *
from bloodPressure_rbd7k import *
# from thermalgun import *
from json import dumps, loads

# rbp7k=readRBD7k()
# rbp7k.getSerObj()
# thermalgun=thermalgun()
spo2=readSPO2()
spo2.Command