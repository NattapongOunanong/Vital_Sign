#!/usr/bin/env python
import time
import serial

ser = serial.Serial(
        port='COM3', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 9600,
        timeout=1,
	rtscts =True,
	#dsrdtr =True,
	write_timeout=10.0
)

#ser.close()
#ser.open()
while 1:
	# print(ser.readline())
	#ser.writelines(bytes("Hi", 'utf-8'))
	returnVal=ser.writelines(str.encode("CC 80 03 03 01 08 01 02"))
	print(returnVal)
	returnVal=ser.write(bytes("CC 80 03 03 01 03 00 02", 'utf-8'))
	print(returnVal)
