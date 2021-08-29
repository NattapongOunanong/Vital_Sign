import serial
from datetime import datetime
import pandas
from binascii import unhexlify,hexlify
import xlsxwriter
arduino_port = "COM6"
baud=4800
samples=1e5

for k in range(5):
    file_Name="raw_{}.csv".format(datetime.now()).replace(":","_")
    workbook   = xlsxwriter.Workbook(file_Name)
    worksheet=workbook.add_worksheet()
    ser = serial.Serial(arduino_port, baud)
    # file=open(file_Name,'w')
    line=0
    data=[]
    while line <= samples:
        getData=str(ser.read())
        # getData=str(int(hexlify(ser.read()),16))
        data.append(getData)
        line+=1
    worksheet.write_column('A1', data)
    # file.writelines(data)
    # file.close()
    workbook.close()
    ser.close()