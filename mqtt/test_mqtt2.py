import paho.mqtt.publish as publish
import time

if __name__ == '__main__': 
    while(True):
        msg = input("enter msg:").strip()
        result = publish.single("death", msg, hostname="127.0.0.1", port=1883) 