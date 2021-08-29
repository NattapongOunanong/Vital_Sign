from marshmallow import Schema,fields

class respbpSchema(Schema):
    sys=fields.Integer(require=True)
    dia=fields.Integer(require=True)
    hr=fields.Integer(require=True)
    
class thermalGunSchema(Schema):
    status=fields.Boolean()
    temperature=fields.Float()
    timestamp=fields.Integer()
    
class bloodPressSchema(Schema):
    status=fields.Boolean()
    command=fields.String(require=True)
    data=fields.Nested(respbpSchema)
    
class spo2webSchema(Schema):
    status=fields.Boolean()
    mqttStat=fields.Boolean()
    timestamp=fields.Integer()

class DevicesSchema(Schema):
    thermalGun=fields.Nested(thermalGunSchema)
    bloodPressure=fields.Nested(bloodPressSchema)
    spo2=fields.Nested(spo2webSchema)
    
class ErrorhandlingSchema(Schema):
    message=fields.String()