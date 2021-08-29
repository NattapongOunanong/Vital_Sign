import os
from flask import Flask, render_template, redirect, flash, request, url_for
from datetime import timedelta, datetime
from time import time
from flask_mqtt import Mqtt 

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = "localhost"
app.config['MQTT_BROKER_PORT'] = 1883

mqtt = Mqtt()
mqtt.init_app(app)
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('on_connect client : {} userdata :{} flags :{} rc:{}'.format(client, userdata, flags, rc))
    mqtt.subscribe("TEST")
    mqtt.subscribe("death")

@mqtt.on_subscribe()
def handle_subscribe(client, userdata, mid, granted_qos):
    print('on_subscribe client : {} userdata :{} mid :{} granted_qos:{}'.format(client, userdata, mid, granted_qos))

@mqtt.on_message()
def handle_message(client, userdata, message):
    print('on_message client : {} userdata :{} message.topic :{} message.payload :{}'.format(
    	client, userdata, message.topic, message.payload.decode()))

@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    print('on_disconnect client : {} userdata :{} rc :{}'.format(client, userdata, rc))
    
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

app.run(port=1883)