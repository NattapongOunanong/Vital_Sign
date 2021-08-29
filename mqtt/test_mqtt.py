import paho.mqtt.client as mqtt
import os,paho

# Define event callbacks
def on_connect(client, userdata, flags, rc):
    print("rc: " + str(rc), flags, userdata)

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(client, obj, level, string):
    print(string)

mqttc = mqtt.Client()
# Assign event callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

# Uncomment to enable debug messages
mqttc.on_log = on_log

# Connect
# mqttc.username_pw_set(url.username, url.password)
mqttc.connect('127.0.0.1', 1883)

# Start subscribe, with QoS level 0
# mqttc.subscribe('death')

# Publish a message
# mqttc.publish("TEST", "my message")

# Continue the network loop, exit when an error occurs
rc = 0
# while rc == 0:
#     rc = mqttc.loop_forever()
mqttc.loop_forever()
# print("rc: " + str(rc))
