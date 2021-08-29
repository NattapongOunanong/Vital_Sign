package com.example.livwel

import android.content.Context
import android.util.Log
import org.eclipse.paho.android.service.MqttAndroidClient
import org.eclipse.paho.client.mqttv3.*

class MQTTClient(context: Context?,
                 serverURI: String,
                 clientID: String = "") {
    private var mqttClient = MqttAndroidClient(context, serverURI, clientID)
    // TAG
    companion object {
        const val TAG = "AndroidMqttClient"
    }

    fun connect(username:   String               = "",
                password:   String               = "") {
        mqttClient.setCallback(object : MqttCallback {
            override fun messageArrived(topic: String?, message: MqttMessage?) {
                Log.d(TAG, "Receive message: ${message.toString()} from topic: $topic")
            }

            override fun connectionLost(cause: Throwable?) {
                Log.d(TAG, "Connection lost ${cause.toString()}")
                connect("guest","guest")
            }

            override fun deliveryComplete(token: IMqttDeliveryToken?) {

            }
        })
        val options = MqttConnectOptions()
        options.userName = username
        options.password = password.toCharArray()

        try {
            mqttClient.connect(options, null, object : IMqttActionListener {
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d(TAG, "Connection successful")
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.d(TAG, "Connection failure")
                    exception?.cause?.printStackTrace()
                    println(exception)
                    connect("guest","guest")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }

    fun publish(topic:      String,
                msg:        String,
                qos:        Int                 = 1,
                retained:   Boolean             = false) {
        try {
            val message = MqttMessage()
            message.payload = msg.toByteArray()
            message.qos = qos
            message.isRetained = retained
            mqttClient.publish(topic, message, null, object: IMqttActionListener{
                override fun onSuccess(asyncActionToken: IMqttToken?) {
                    Log.d(TAG,"Publish $message to server")
                }

                override fun onFailure(asyncActionToken: IMqttToken?, exception: Throwable?) {
                    Log.d(TAG,"Publishing Failed")
                }
            })
        } catch (e: MqttException) {
            e.printStackTrace()
        }
    }

//    fun disconnect(cbDisconnect: IMqttActionListener =  ) {
//        try {
//            mqttClient.disconnect(null, object: IMqttActionListener{
//                override fun onSuccess(asyncActionToken: IMqttToken?) {
//                    Log.v(TAG, "Successfully Disconnect from Server")
//                }
//            })
//        } catch (e: MqttException) {
//            e.printStackTrace()
//        }
//    }

}

