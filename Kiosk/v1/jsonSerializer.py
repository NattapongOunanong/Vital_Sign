import json
from queue import Queue
from getmac import get_mac_address as gma

class jsonGen(object):
    def __init__(self):
        self.msgQueue=Queue(maxsize=1e5)
        self.jsonArray=[]
        self.msg=None
        self.DID=gma()
        self.dataType={
            "spo2":self.jsonSpo2,
            "temp":self.jsonTemp,
            "pressure":self.jsonBloodPressure,
            "hr":self.jsonHR
        }
        
    def jsonManager(self, msg):
        # remove key with null data
        self.msg=self.deleteNull(msg)
        listType = eval(self.msg['type'])
        for numType in listType:
            if len(self.msg)==3: #request for status only have 3 elements
                self.msg['type']=numType
                self.jsonStatus(self.msg)
            else:
                # Convert to Json by calling Dictionary "self.dataType"
                try:
                    eval(self.dataType[numType](self.msg))
                except Exception as e:
                    print(e,self.dataType[numType](self.msg))
                
        if len(self.msg)==3:
            return
        else:
            self.convert2JSON()
            
    def convert2JSON(self):
        # Convert message into json then put into queue
        jsonMsg=json.dumps(list(self.jsonArray))
        self.msgQueue.put(jsonMsg)
        self.jsonArray.clear()
        
    def jsonSpo2(self, spo2):
        # put one stream data into queue one at a time
        if 'raw' in spo2: #one at a time, convert stream data
            for ind, raw in enumerate(spo2['raw']):
                spo2Msg={
                    "name":spo2['name'],
                    "DID":self.DID,
                    "type":spo2['type'][0],
                    "spo2":{"raw":[int(raw)]},
                    "dt":int(spo2['dt'][ind])
                }
                self.mergeJSON(spo2Msg)
                self.convert2JSON()
        else:
            # if no stream data, put hr and sp2 into queue
            spo2Msg={
                "name":spo2['name'],
                "DID":self.DID,
                "type":spo2['type'],
                "spo2":{"value":spo2['value'],"hr":spo2['hr']},
                "dt":spo2['dt']
            }
            self.mergeJSON(spo2Msg)
            self.convert2JSON()
            
        
    def jsonBloodPressure(self, pressure):
        # Blood pressure message format
        bloodpressureMsg={
            "name":pressure['name'],
            "DID":self.DID,
            "type":pressure['type'],
            "pressure":{"sys":pressure['sys'],"dia":pressure['dia'], "hr":pressure['hr']},
            "dt":pressure['dt']
        }
        self.mergeJSON(bloodpressureMsg)
        
    def jsonHR(self, msg):
        # Heartrate message format
        hrMsg={
            "name":msg['name'],
            "DID":self.DID,
            "type":msg['type'],
            "pressure":{"hr":msg['hr']},
            "dt":msg['dt']
        }
        self.mergeJSON(hrMsg)
        
    def jsonTemp(self,temp):
        # Temperature Message Format
        tempMsg={
            "name":temp['name'],
            "DID":self.DID,
            "type":temp['type'],
            "temp":temp['temp'],
            "dt":temp['dt']
        }
        self.mergeJSON(tempMsg)
        
    def jsonStatus(self,msg):
        #Gather all devices status
        self.jsonArray.append(dict(msg))
        
    def jsonSendStatus(self):
        #Call This Function to dump status to queue in json format
        print(self.jsonArray)
        self.convert2JSON()
        
    def mergeJSON(self, msg):
        # merge vital sign into single json message
        if not self.jsonArray:
            self.jsonArray.append(msg)
            return
        for msgJson in self.jsonArray:
            if msg['name'] in msgJson:
                msgJson.update(msg)
        
    def deleteNull(self, msg):
        # delete message key in dictionary which does not have value
        noneListKey=[]
        for key in msg:
            if msg[key] == None or not msg[key]:
                noneListKey.append(key)
        for delKey in noneListKey:
            msg.pop(delKey)
        return msg
