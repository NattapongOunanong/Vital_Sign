package com.example.livwel

import android.bluetooth.BluetoothDevice
import java.net.NetworkInterface
import java.util.*
import kotlin.experimental.and


class Serializer (){
    private var vitalSignData= ArrayList<String>(3)
    private var thermalGunData= HashMap<String, String>()
    private var spo2Data= HashMap<String, String>()
    private var bloodPressureData= HashMap<String, String>()
    private val address = getMacAddr().toString()

    fun getThermalgunData(data: HashMap<String, Any?>):String{
        thermalGunData["\"name\""]= getName(data["gatt"] as BluetoothDevice)
        thermalGunData["\"dt\""]= getTimeStamp()
        thermalGunData["\"DID\""]= "\"$address\""
        thermalGunData["\"type\""]= getDeviceType(data["type"] as String)
        thermalGunData["\"temp\""]= serializeThermalGun(data["data"] as String)
        return thermalGunData.toString()
    }

    fun getSpo2Data(data: HashMap<String, Any?>):String{
        spo2Data["\"name\""]= getName(data["gatt"] as BluetoothDevice)
        spo2Data["\"dt\""]= getTimeStamp()
        spo2Data["\"DID\""]= "\"$address\""
        spo2Data["\"type\""]= getDeviceType(data["type"] as String)
        spo2Data["\"spo2\""]= serializeSpo2(data["data"] as String)
        return spo2Data.toString()
    }

    fun getBloodPressureData(data: HashMap<String, Any?>):String{
        bloodPressureData["\"name\""]= getName(data["gatt"] as BluetoothDevice)
        bloodPressureData["\"dt\""]= getTimeStamp()
        bloodPressureData["\"DID\""]= "\"$address\""
        bloodPressureData["\"type\""]= getDeviceType(data["type"] as String)
        bloodPressureData["\"pressure\""]= serializeBloodPressure(data["data"] as String)
        return bloodPressureData.toString()
    }

    private fun getName(device: BluetoothDevice): String{
        var name = device.name.toString()
        return "\"$name\""
    }

    private fun getTimeStamp(): String{
        return System.currentTimeMillis().toString()
    }

    private fun getDeviceType(deviceName: String): String {
        var deviceType = deviceName
        return "\"$deviceType\""
    }

    private fun serializeThermalGun(thermalGunData: String): String{
        val hexStringData = thermalGunData.split(" ")
        val temperatureDisplay = hexStringData[6] + hexStringData[5]
        val bodyTemp = Integer.parseInt(temperatureDisplay, 16).toFloat() / 10
        return bodyTemp.toString()

    }

    private fun serializeSpo2(spo2Data: String): String{
        val spo2Data=spo2Data.split(" ")
        val spo2 = isBerryMedValid(spo2Data[4])
        val hr = isBerryMedValid(spo2Data[3])
        return "{\"value\": $spo2, \"hr\": $hr}"
    }

    private fun serializeBloodPressure(presureData: String): String{
        val hexStringData = presureData.split(" ")
//        println(hexStringData)
        val sys = Integer.parseInt(hexStringData[8], 16).toString()
        val dia = Integer.parseInt(hexStringData[10], 16).toString()
        val pulse = Integer.parseInt(hexStringData[11], 16).toString()
        return "{\"sys\":$sys, \"dia\":$dia, \"hr\":$pulse}"
    }

    private fun getMacAddr(): String? {
        try {
            val all: List<NetworkInterface> =
                Collections.list(NetworkInterface.getNetworkInterfaces())
            for (nif in all) {
                if (!nif.name.contains("wlan0", ignoreCase = true)) continue
                val macBytes: ByteArray = nif.hardwareAddress ?: return ""
                val res1 = StringBuilder()
                for (b in macBytes) {
                    res1.append(Integer.toHexString((b and 0xFF.toByte()).toInt()).replace("ffffff","") + ":")
                }
                if (res1.isNotEmpty()) {
                    res1.deleteCharAt(res1.length - 1)
                }
                return res1.toString()
            }
        } catch (ex: Exception) {
        }
        return "02:00:00:00:00:00"
    }

    private fun isBerryMedValid(testVal: String): String {
        return if (testVal.contains("7F")){
            "N/A"
        } else{
            Integer.parseInt(testVal,16).toString()
        }
    }
}