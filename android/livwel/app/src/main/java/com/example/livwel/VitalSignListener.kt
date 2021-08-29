package com.example.livwel

import android.content.Context
import android.content.SharedPreferences
import android.os.Build
import android.util.Log
import android.widget.Button
import android.widget.TextView
import androidx.annotation.RequiresApi
import androidx.core.content.ContextCompat
import java.util.*
import kotlin.collections.ArrayList


@RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
class VitalSignListener {

    lateinit var sharedPreferences: SharedPreferences
    private  val MODE = Context.MODE_PRIVATE
    private lateinit var temperatureListener: SharedPreferences.OnSharedPreferenceChangeListener
    private lateinit var spo2Listener: SharedPreferences.OnSharedPreferenceChangeListener
    private lateinit var bloodPressureListener: SharedPreferences.OnSharedPreferenceChangeListener

    var vitalSignData= ArrayList<String>(3)

    private var thermalGunData=""
    private var spo2Data=""
    private var bloodPressureData=""

    fun init(context: Context, mainActivity: MainActivity) {

        sharedPreferences = context.getSharedPreferences("vitalSign", MODE)

        temperatureListener=
            SharedPreferences.OnSharedPreferenceChangeListener { sharedPreferences, key ->
                if (key.contains("Temperature")) {
                    val preferences = context.getSharedPreferences("vitalSign", MODE)
                    val tempData = preferences.getString("Temperature", null)

                    if (tempData != null) {
                        when {
                            tempData.contains("disconnected", ignoreCase = true) -> {
                                setOnDisconnected(mainActivity, R.id.scanTemp)
                            }
                            tempData.contains("connected", ignoreCase = true) -> {
                                setOnConnected(mainActivity, R.id.scanTemp)
                            }
                            else -> {
                                thermalGunData=tempData.replace("=",":")
                                val regex = Regex("\"temp\":(.*?)[}]")
                                val temperatureData = regex.findAll(thermalGunData)
                                val temperatureDisplay = temperatureData.map { it.groupValues[1] }.joinToString()+" C"
                                mainActivity.findViewById<TextView>(R.id.tempVal).apply {
                                    text = temperatureDisplay
                                }
                            }
                        }
                    }
                }
            }

        spo2Listener =
            SharedPreferences.OnSharedPreferenceChangeListener { sharedPreferences, key ->
                if (key.contains("Spo2")) {
                    val preferences = context.getSharedPreferences("vitalSign", MODE)
                    val spo2PulseData = preferences.getString("Spo2", null)
                    if (spo2PulseData != null) {
                        when {
                            spo2PulseData.contains("disconnected",ignoreCase = true) -> {
                                setOnDisconnected(mainActivity,R.id.scanSpo2)
                            }
                            spo2PulseData.contains("connected",ignoreCase = true) -> {
                                setOnConnected(mainActivity,R.id.scanSpo2)
                                println("disconnect")
                            }
                            else -> {
                                if (!spo2PulseData.contains("N/A")){
                                    spo2Data=spo2PulseData.replace("=",":")

                                    var regex = Regex("\"value\":(.*?)[,]")
                                    val spo2percent = regex.findAll(spo2Data)
                                    val spo2Display = spo2percent.map { it.groupValues[1] }.joinToString()+" %"

                                    regex = Regex("\"hr\":(.*?)[}]")
                                    val pulse = regex.findAll(spo2Data)
                                    val pulseDisplay = pulse.map { it.groupValues[1] }.joinToString()

                                    if (!spo2Display.contains("N/A")){
                                        mainActivity.findViewById<TextView>(R.id.spo2Val).apply {
                                            text = spo2Display
                                        }
                                    }

                                    if(!pulseDisplay.contains("N/A")){
                                        mainActivity.findViewById<TextView>(R.id.pulse_spo2).apply {
                                            text = pulseDisplay
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }

        bloodPressureListener =
            SharedPreferences.OnSharedPreferenceChangeListener { sharedPreferences, key ->
                if (key.contains("BloodPressure")) {
                    val preferences = context.getSharedPreferences("vitalSign", MODE)
                    val bpData = preferences.getString("BloodPressure", null)

                    if (bpData != null) {
                        when {
                            bpData.contains("disconnected", ignoreCase = true) -> {
                                setOnDisconnected(mainActivity, R.id.scanBloodPressure)
                            }
                            bpData.contains("connected", ignoreCase = true) -> {
                                setOnConnected(mainActivity, R.id.scanBloodPressure)
                            }
                            else -> {

                                bloodPressureData=bpData.replace("=",":")

//                                println(bloodPressureData)
                                var regex = Regex("\"sys\":(.*?)[,]")
                                val sysRegex = regex.findAll(bloodPressureData)
                                val sys = sysRegex.map { it.groupValues[1] }.joinToString()

                                regex = Regex("\"dia\":(.*?)[,]")
                                val diaRegex = regex.findAll(bloodPressureData)
                                val dia = diaRegex.map { it.groupValues[1] }.joinToString()

                                regex = Regex("\"hr\":(.*?)[}]")
                                val hrRegex = regex.findAll(bloodPressureData)
                                val hr = hrRegex.map { it.groupValues[1] }.joinToString()
                                mainActivity.findViewById<TextView>(R.id.sys).apply {
                                    text = sys
                                }
                                mainActivity.findViewById<TextView>(R.id.dia).apply {
                                    text = dia
                                }
                                mainActivity.findViewById<TextView>(R.id.pulse).apply {
                                    text = hr
                                }
                            }
                        }
                    }
                }
            }
        registerAllSharedPreferenceListener()
    }

    private fun registerAllSharedPreferenceListener(){
        sharedPreferences.registerOnSharedPreferenceChangeListener(temperatureListener)
        sharedPreferences.registerOnSharedPreferenceChangeListener(spo2Listener)
        sharedPreferences.registerOnSharedPreferenceChangeListener(bloodPressureListener)
    }

    fun getData(mainActivity: MainActivity):ArrayList<String>{
        vitalSignData.clear()
        if (thermalGunData.isNotBlank()){
            vitalSignData.add(thermalGunData)
        }
        if (spo2Data.isNotBlank()){
            vitalSignData.add(spo2Data)
        }
        if (bloodPressureData.isNotBlank()){
            vitalSignData.add(bloodPressureData)
        }
        clearOldData()
        clearUI(mainActivity)
        return vitalSignData
    }

    private fun clearOldData(){
        thermalGunData=""
        spo2Data=""
        bloodPressureData=""
    }

    private fun clearUI(mainActivity: MainActivity){
        val idList= listOf(R.id.spo2Val,R.id.pulse_spo2,R.id.sys,R.id.dia,R.id.pulse,R.id.tempVal)
        for (id in idList){
            mainActivity.findViewById<TextView>(id).apply{
                text="N/A"
            }
        }
    }

    private fun setOnConnected(mainActivity: MainActivity, layout: Int){
        mainActivity.findViewById<Button>(layout).apply {
            setBackgroundColor(ContextCompat.getColor(context,R.color.connectState))
            setTextColor(ContextCompat.getColor(context,R.color.connectText))
        }
    }

    private fun setOnDisconnected(mainActivity: MainActivity, layout: Int){
        mainActivity.findViewById<Button>(layout).apply {
            setBackgroundColor(ContextCompat.getColor(context,R.color.disconnectState))
            setTextColor(ContextCompat.getColor(context,R.color.disconnectText))
        }
    }
}