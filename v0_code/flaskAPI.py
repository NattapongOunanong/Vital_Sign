from flask import Flask, request
from flask_restful import Resource, Api, reqparse, marshal
from flask_apispec import marshal_with, use_kwargs, FlaskApiSpec, MethodResource, doc
from flask_expects_json import expects_json
from webargs import fields
from json import dumps
import time

from bloodPressure_rbd7k import *
from serial_spo2 import *
from thermalgun import *

from schemas import *

app = Flask(__name__)
docs = FlaskApiSpec(app)
api = Api(app)

# rbp7k=readRBD7k()
# rbp7k.getSerObj()
# thermalgun=thermalgun()
spo2=mqttSPO2()
spo2.connect()

# name_space=api.namespace('main', description='Main APIs')

@doc(description='Temperature Data is Called from Device', tags=['Thermal Gun'])
@marshal_with(thermalGunSchema, code=200)
@marshal_with(ErrorhandlingSchema, code=400)
class thermalGun(MethodResource):
    def get(self):
        print(use_kwargs,request.args)
        if not request.args:
            return {"status":False}
        if request.args['status']=='True':
            # print(thermalGunSchema().dumps({"status":True, "temperature":38,"timestamp":5}))
            return {"status":True}
        return {"status":True, "temperature":38,"timestamp":5}
    
    # @use_kwargs(thermalGunSchema2)
    # @expects_json(thermalGunSchema)
    # @use_kwargs(thermalGunSchema)
    def post(self, **kwargs):
        data = request.get_json(force=True)
        print(data.get('status'))
        time.sleep(1)
        return {"status":True, "temperature":38,"timestamp":5}
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        # pass through HTTP errors
        if isinstance(e, HTTPException):
            return e
        return render_template("500_generic.html", e=e), 500

@doc(description='Blood Pressure - Request command', tags=['Blood Pressure'])
@marshal_with(bloodPressSchema, code=200)
@marshal_with(respbpSchema, code=201)
@marshal_with(ErrorhandlingSchema, code=400)
class rpb7k(MethodResource):
    def get(self):
        if not request.args:
            return "No parameter given"
        if request.args['status']==True:
            return dumps(Devices['bloodpressure']['status'])
        return dumps(Devices['bloodpressure'])
    
    def post(self):
        # print(request.args['command'])
        rbp7k.sendCommand(request.form['command'])
        response=dumps({"response":rbp7k.mResponse()})
        
        return "Success", 200

@doc(description='Stream Data (Activate/Deavtivate MQTT)', tags=['SPO2'])
@marshal_with(spo2webSchema)
class spo2(MethodResource):
    def get(self):
        if not request.args:
            return "No parameter given"
        if request.args['status']==True:
            return Devices["spo2"]['status']
        return "success", 200
    
    # @expects_json(thermalGunSchema)
    def post(self):
        try:
            spo2.ser.close()
        except:
            if request.form['mqtt']==True:
                spo2.getSerObj()
                spo2.start()
            else:
                spo2.stop()
        Devices['bloodpressure']['mqtt']=request.form['mqtt']
        return "", 200
        
api.add_resource(thermalGun, '/thermalGun') # Route_1 Thermal Gun
api.add_resource(rpb7k, '/bloodPressure') # Route_2 Blood Pressure
api.add_resource(spo2,'/spo2')

app.add_url_rule('/thermalGun', view_func=thermalGun.as_view('gun'))
app.add_url_rule('/bloodPressure', view_func=rpb7k.as_view('bp'))
app.add_url_rule('/spo2', view_func=spo2.as_view('spo2_swagger'))

docs.register(thermalGun)
docs.register(rpb7k)
docs.register(spo2)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    

# Note:
# Kiosk Command 'Acknowledgement code: AA instead of CC'
# baud rate 9600
# temp, spo2,
# pressure- sys, dia, hr