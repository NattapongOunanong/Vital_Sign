#!/usr/bin/env python
# coding: utf-8

# In[1]:


from configparser import ConfigParser


# # Communication Protocol 

# In[2]:


#Communication Protocol
config_object = ConfigParser()


# In[3]:


config_object["mqtt"]={
    "url": "3.0.54.110",
    "port": "8082",
    "username": "mqtt",
    "password": "12345",
    "topic": {"publisher":["vitalSign", "remoteCtrlReply"],
              "subscriber":["remoteCtrl"]
             }
}
# config_object["restAPI"]={
#     "url":"hello",
#     "port": "world",
#     "username": "from",
#     "password": "HII"
# }


# In[4]:


#Write the above sections to config.ini file
with open('emetWorksCommProtocol.ini', 'w') as conf:
    config_object.write(conf)


# # Hardware

# In[5]:


#Communication Protocol
# Comport for Raspberry Pi
# '/dev/ttyUSB0', '/dev/ttyUSB1'
config_object = ConfigParser()


# In[6]:

config_object["raycomRPD7000"]={
        "name":"raycomRPD7000",
        "baudrate":"9600",
        "command":{
            "status":"CC 80 03 03 01 01 00 00",
            "start" : "CC 80 03 03 01 02 00 03",
            "stop" : "CC 80 03 03 01 03 00 02",
            "lockscreen" : "CC 80 03 03 01 08 00 02",
            "unlockscreen" : "CC 80 03 03 01 08 00 02",
            "read" : "None",
            "calibrate" : "None",
            "reset": "None"
        },
        "comPort":"COM7",
        "timeout": 60,
        "type":["pressure","hr"]
}
config_object["spo2"]={
        "name":"spo2BlackBox",
        "baudrate":"4800",
        "comPort":"/dev/ttyUSB1",
        "stdevTol":3,
        "numMean":3,
        "type":["spo2"]
        }


# In[7]:


#Write the above sections to config.ini file
with open('banbangkhae.ini', 'w') as conf:
    config_object.write(conf)


# In[ ]:

config_object["krKristaz"]={
        "name":"krKristaz",
        "blueAddr": "18:7a:94:73:01:a3",
        "type":["temp"]
        }

config_object["raycomRPD7000"]={
        "name":"raycomRPD7000",
        "baudrate":"9600",
        "command":{
            "status":"CC 80 03 03 01 01 00 00",
            "start" : "CC 80 03 03 01 02 00 03",
            "stop" : "CC 80 03 03 01 03 00 02",
            "lockscreen" : "CC 80 03 03 01 08 00 02",
            "unlockscreen" : "CC 80 03 03 01 08 00 02",
            "read" : "None",
            "calibrate" : "None",
            "reset": "None"
        },
        "comPort":"/dev/ttyUSB0",
        "timeout": 30,
        "type":["pressure","hr"]
}
# In[7]:


#Write the above sections to config.ini file
with open('banbangkhae_Pi.ini', 'w') as conf:
    config_object.write(conf)



# In[ ]:




