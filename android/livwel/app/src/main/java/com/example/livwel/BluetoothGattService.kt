package com.example.livwel

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.bluetooth.*
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.Intent
import android.content.SharedPreferences
import android.graphics.Color
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.annotation.RequiresApi
import java.util.*
private const val CCC_DESCRIPTOR_UUID = "000002902-0000-1000-8000-00805f9b34fb"
class BluetoothGattService : Service() {

    lateinit var bluetoothGatt: BluetoothGatt
    lateinit var gattObject: BluetoothDevice
    lateinit var preferences: SharedPreferences
    lateinit var editor: SharedPreferences.Editor

    private var serializer= Serializer()

    lateinit var serializeData: String

    @RequiresApi(Build.VERSION_CODES.O)
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {

        val channelId =
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                createNotificationChannel("my_service", "My Background Service")
            } else {
                // If earlier version channel ID is not used
                ""
            }

        val notification: Notification = Notification.Builder(this, channelId)
            .setContentTitle("title")
            .setContentText("text")
            .build()
        startForeground(1, notification)

        gattObject = intent?.getParcelableExtra<BluetoothDevice>("Sensor")!!
        gattObject.connectGatt(applicationContext, true, gattCallback)
//        devType = intent?.getStringExtra("vitalSign").toString()
//        gattSensor.put(devType, gattObject)
        preferences = getSharedPreferences("vitalSign", MODE_PRIVATE)
        editor = preferences.edit()

        return START_STICKY
    }

    @RequiresApi(Build.VERSION_CODES.O)
    private fun createNotificationChannel(channelId: String, channelName: String): String{
        val chan = NotificationChannel(channelId,
            channelName, NotificationManager.IMPORTANCE_NONE)
        chan.lightColor = Color.BLUE
        chan.lockscreenVisibility = Notification.VISIBILITY_PRIVATE
        val service = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        service.createNotificationChannel(chan)
        return channelId
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    override fun onCreate() {
        // move your service logic here
//        bleScanner.startScan(null, scanSettings, scanCallback)
        isScanning = true
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    override fun onDestroy() {
        isScanning = false
    }

    override fun onBind(intent: Intent?): IBinder? {
        TODO("Not yet implemented")
    }

    private val bluetoothAdapter: BluetoothAdapter by lazy {
        val bluetoothManager = getSystemService(BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }


    //    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private val bleScanner by lazy {
        bluetoothAdapter.bluetoothLeScanner
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private val scanSettings = ScanSettings.Builder()
        .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
        .build()

    private var isScanning = false
        set(value) {
            field = value
        }

    private val gattCallback = @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    object : BluetoothGattCallback() {
        @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
        override fun onConnectionStateChange(gatt: BluetoothGatt, status: Int, newState: Int) {
            val deviceAddress = gatt.device.address

            if (status == BluetoothGatt.GATT_SUCCESS) {
                if (newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.w("BluetoothGattCallback", "Successfully connected to $deviceAddress")
//                    gatt.requestMtu(GATT_MAX_MTU_SIZE)
                    bluetoothGatt = gatt
                    bluetoothGatt.requestConnectionPriority(BluetoothGatt.CONNECTION_PRIORITY_HIGH)
                    editor.putString(getType(), "Connected")
                    editor.commit()
                    Handler(Looper.getMainLooper()).post {
                        bluetoothGatt.discoverServices()
                    }
                } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                    Log.w("BluetoothGattCallback", "Successfully disconnected from $deviceAddress")
                    editor.putString(getType(), "Disconnected")
                    editor.commit()
//                    gatt.close()
                }
            } else {
                Log.w(
                    "BluetoothGattCallback",
                    "Error $status encountered for $deviceAddress! Disconnecting..."
                )
                editor.putString(getType(), "Disconnected")
                editor.commit()
            }
        }

        override fun onServicesDiscovered(gatt: BluetoothGatt, status: Int) {
            with(gatt) {
                Log.w(
                    "BluetoothGattCallback",
                    "Discovered ${services.size} services for ${device.address}"
                )
                findNotifications()
            }
        }

        override fun onMtuChanged(gatt: BluetoothGatt, mtu: Int, status: Int) {
            Log.w("ATT MTU changed to $mtu", "success: ${status == BluetoothGatt.GATT_SUCCESS}")
        }

        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic
        ) {
            val message = characteristic.value.toHexString()
            var data = HashMap<String, Any?>()
            data["gatt"]=gatt.device
            data["data"]=message
            lateinit var devType: String

            if (characteristic.uuid.toString().contains("0000fe10-0000-1000-8000-00805f9b34fb")){
                data["type"]="temp"
                devType = "Temperature"
                serializeData=serializer.getThermalgunData(data)

            }else if(characteristic.uuid.toString().contains("49535343-1e4d-4bd9-ba61-23c647249616")){
                data["type"]="spo2"
                devType = "Spo2"
                serializeData=serializer.getSpo2Data(data)
            }else if(characteristic.uuid.toString().contains("0000fff1-0000-1000-8000-00805f9b34fb")){
                data["type"]="pressure"
                if (message.contains("0xFA")){
                    devType = "BloodPressure"
                    serializeData=serializer.getBloodPressureData(data)
                }else{
                    devType=""
                }
            }else{
                Log.e("Notification","Unidentified")
            }
            transferData(serializeData.replace("=",":"),devType)
            serializeData=""
        }
    }

    // ... somewhere outside BluetoothGattCallback
    fun ByteArray.toHexString(): String =
        joinToString(separator = " ", prefix = "0x") { String.format("%02X", it) }

    private fun transferData(message: String, devType: String) {
        if(devType.isNotEmpty()){
            editor.putString(devType, message)
            editor.commit()
        }
    }

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    fun BluetoothGatt.findNotifications(){
        services.forEach{service ->
            service.characteristics.forEach{characteristic ->
                enableNotifications(characteristic)
            }
        }
    }

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun enableNotifications(characteristic: BluetoothGattCharacteristic) {

        if (characteristic.uuid.toString()=="00002a05-0000-1000-8000-00805f9b34fb"){
            Log.i("Get Characteristic",characteristic.uuid.toString())
            return
        }
        val cccdUuid = UUID.fromString(CCC_DESCRIPTOR_UUID)
        val payload = when {
            characteristic.isIndicatable() -> BluetoothGattDescriptor.ENABLE_INDICATION_VALUE
            characteristic.isNotifiable() -> BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE
            else -> {
//                Log.e("ConnectionManager", "${characteristic.uuid} doesn't support notifications/indications")
                return
            }
        }

            characteristic.getDescriptor(cccdUuid)?.let { cccDescriptor ->
                if (!bluetoothGatt.setCharacteristicNotification(characteristic, true)) {
                    Log.e(
                        "ConnectionManager",
                        "setCharacteristicNotification failed for ${characteristic.uuid}"
                    )
                    return
                }
                Log.v("Descriptor value", "${characteristic.uuid}")
                writeDescriptor(cccDescriptor, payload)
            } ?: Log.e(
                "ConnectionManager",
                "${characteristic.uuid} doesn't contain the CCC descriptor!"
            )
    }

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun BluetoothGattCharacteristic.isIndicatable(): Boolean =
        containsProperty(BluetoothGattCharacteristic.PROPERTY_INDICATE)

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun BluetoothGattCharacteristic.isNotifiable(): Boolean =
        containsProperty(BluetoothGattCharacteristic.PROPERTY_NOTIFY)

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun BluetoothGattCharacteristic.containsProperty(property: Int): Boolean {
        return properties and property != 0
    }

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun writeDescriptor(descriptor: BluetoothGattDescriptor, payload: ByteArray) {
        bluetoothGatt.let { gatt ->
            descriptor.value = payload
            gatt.writeDescriptor(descriptor)
        } ?: error("Not connected to a BLE device!")
    }

    @RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
    private fun getType(): String {
        return if (bluetoothGatt.device.name.contains("JXB_TTM")) {
            "Temperature"
        } else if (bluetoothGatt.device.name.contains("BerryMed")) {
            "Spo2"
        } else if (bluetoothGatt.device.name.contains("DBP")) {
            "BloodPressure"
        } else {
            "Not Found"
        }
    }
}