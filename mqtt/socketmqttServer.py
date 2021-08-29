from flask import Flask, request
from flask_restful import Resource, Api, reqparse, fields, marshal
from flask_swagger_ui import get_swaggerui_blueprint
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from sqlalchemy import create_engine
from json import dumps
import flask_compressor

import time
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = '127.0.0.1'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 5000   # default port for non-tls connection
app.config['MQTT_REFRESH_TIME'] = 1  # set the time interval for sending a ping to the broker to 5 seconds

socketio = SocketIO(app)
mqtt = Mqtt(app)

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish('home/mytopic', 'hello')


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe('home/mytopic2')


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected")
    mqtt.subscribe('home/mytopic')
    
@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print(message, 'hello')
    socketio.emit('mqtt_message', data='hello')

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)
    
if __name__ == '__main__':
    socketio.run(app,host='127.0.0.1', port=5000, debug=True)