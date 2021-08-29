import serial

ser = serial.Serial('COM3', 4800, 
                    parity=serial.PARITY_ODD,
                    bytesize=serial.EIGHTBITS, 
                    stopbits=serial.STOPBITS_ONE,
                    timeout=1,
                    write_timeout=5
                )
while True:
    print(int.from_bytes(ser.read(),"big"))