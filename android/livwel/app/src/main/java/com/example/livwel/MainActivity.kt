package com.example.livwel

import android.Manifest
import android.app.Activity
import android.app.AlertDialog
import android.bluetooth.*
import android.bluetooth.le.ScanCallback
import android.bluetooth.le.ScanResult
import android.bluetooth.le.ScanSettings
import android.content.Context
import android.content.DialogInterface
import android.content.Intent
import android.content.pm.PackageManager
import android.net.wifi.WifiManager
import android.os.*
import android.util.Log
import android.view.View
import android.widget.Button
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.recyclerview.widget.SimpleItemAnimator
import kotlinx.android.synthetic.main.activity_main.*
import java.util.*



private const val ENABLE_BLUETOOTH_REQUEST_CODE = 1
private const val LOCATION_PERMISSION_REQUEST_CODE = 1

@RequiresApi(Build.VERSION_CODES.JELLY_BEAN_MR2)
class MainActivity : AppCompatActivity() {
    lateinit var scanTemp: Button
    lateinit var scanSpo2: Button
    lateinit var scanBloodPressure: Button

    private lateinit var vitalSign: MutableList<String>
    private val deviceNameType= mapOf("JXB_TTM" to "TEMP", "BerryMed" to "SPO2", "DBP" to "BLOODPRESSURE")

    lateinit var deviceType: String

    private lateinit var myMqtt: MQTTClient

    private lateinit var vitalSignListenner: VitalSignListener

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setupRecyclerView()
        vitalSignListenner = VitalSignListener()
        vitalSignListenner.init(applicationContext,this)

        myMqtt= MQTTClient(applicationContext,"tcp://devmqtt.airpresense.tech:1883")
        myMqtt.connect(
            "guest",
            "guest",
        )

        vitalSign= arrayListOf()

        scanTemp = findViewById<Button>(R.id.scanTemp)
        scanTemp.setOnClickListener {
            if (vitalSign.contains("Temperature")) {
                vitalSign.remove("Temperature")
                stopBleScan()
            } else {
                vitalSign.add("Temperature")
                startBleScan()
            }
        }


        scanSpo2 = findViewById<Button>(R.id.scanSpo2)
        scanSpo2.setOnClickListener {
            if (vitalSign.contains("Spo2")) {
                vitalSign.remove("Spo2")
                stopBleScan()
            } else {
                vitalSign.add("Spo2")
                startBleScan()
            }
        }


        scanBloodPressure = findViewById<Button>(R.id.scanBloodPressure)
        scanBloodPressure.setOnClickListener {
            if (vitalSign.contains("BloodPressure")) {
                vitalSign.remove("BloodPressure")
                stopBleScan()
            } else {
                vitalSign.add("BloodPressure")
                startBleScan()
            }
        }
    }

    fun sendMQTT(view: View){

//        for (vs in vitalSignListenner.getData()){
//            myMqtt.publish("vitalSign", vs)
//        }
        myMqtt.publish("vitalSign", vitalSignListenner.getData(this).toString())

    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private fun startBleScan() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !isLocationPermissionGranted) {
            requestLocationPermission()
        } else {
            scanResults.clear()
            scanResultAdapter.notifyDataSetChanged()
            bleScanner.startScan(null, scanSettings, scanCallback)
            isScanning = true
        }
    }

    override fun onResume() {
        super.onResume()
        if (!bluetoothAdapter.isEnabled) {
            promptEnableBluetooth()
        }
//        registerAllSharedPreferenceListener()
    }

    override fun onPause() {
        super.onPause()
        stopService(Intent(this, BluetoothGattService::class.java))
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private fun stopBleScan() {
        bleScanner.stopScan(scanCallback)
        isScanning = false
    }
    //
    private val bluetoothAdapter: BluetoothAdapter by lazy {
        val bluetoothManager = getSystemService(BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }



    private fun promptEnableBluetooth() {
        if (!bluetoothAdapter.isEnabled) {
            val enableBtIntent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            startActivityForResult(enableBtIntent, ENABLE_BLUETOOTH_REQUEST_CODE)
        }
    }

    //    keep alerting user until bluetooth is enable
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        when (requestCode) {
            ENABLE_BLUETOOTH_REQUEST_CODE -> {
                if (resultCode != RESULT_OK) {
                    promptEnableBluetooth()
                }
            }
        }
    }

    //    Need location permission when performing blescan
    private val isLocationPermissionGranted
        get() = hasPermission(Manifest.permission.ACCESS_FINE_LOCATION)

    private fun Context.hasPermission(permissionType: String): Boolean {
        return ContextCompat.checkSelfPermission(this, permissionType) ==
                PackageManager.PERMISSION_GRANTED
    }

    private fun requestLocationPermission() {
        if (isLocationPermissionGranted) {
            return
        }
        val dialogBuilder = AlertDialog.Builder(this)
        dialogBuilder.setMessage(
            "Starting from Android M (6.0), the system requires apps to be granted " +
                    "location access in order to scan for BLE devices."
        )
            // if the dialog is cancelable
            .setCancelable(false)
            // positive button text and action
            .setPositiveButton("OK", DialogInterface.OnClickListener { dialog, id ->
                requestPermission(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    LOCATION_PERMISSION_REQUEST_CODE
                )
            }
            )
        val alert = dialogBuilder.create()
        // set title for alert dialog box
        alert.setTitle("Location permission required")
        alert.show()
    }

    private fun Activity.requestPermission(permission: String, requestCode: Int) {
        ActivityCompat.requestPermissions(this, arrayOf(permission), requestCode)
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            LOCATION_PERMISSION_REQUEST_CODE -> {
                if (grantResults.firstOrNull() == PackageManager.PERMISSION_DENIED) {
                    requestLocationPermission()
                } else {
                    startBleScan()
                }
            }
        }
    }

    private var isScanning = false
        set(value) {
            field = value
//            runOnUiThread {button.text = if (value) "Stop Scan" else "Start Scan" }
        }

    //    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private val bleScanner by lazy {
        bluetoothAdapter.bluetoothLeScanner
    }

    //    // From the previous section:
    private val bluetoothA: BluetoothAdapter by lazy {
        val bluetoothManager = getSystemService(BLUETOOTH_SERVICE) as BluetoothManager
        bluetoothManager.adapter
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private val scanSettings = ScanSettings.Builder()
        .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
        .build()

    private val scanResults = mutableListOf<ScanResult>()
    private val scanResultAdapter: ScanResultAdapter by lazy {
        ScanResultAdapter(scanResults) { result ->
            // User tapped on a scan result
            @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
            if (isScanning) {
                stopBleScan()
            }
            var resultDevice = result.device
            with(resultDevice) {
                Log.w("ScanResultAdapter", "Connecting to $address")
                if(name.contains("JXB_TTM")) {
                    deviceType = deviceNameType["JXB_TTM"].toString()
                }else if (name.contains("BerryMed")){
                    deviceType = deviceNameType["BerryMed"].toString()
                }else if (name.contains("DBP")){
                    deviceType = deviceNameType["DBP"].toString()
                }
            }
            var gattIntent = Intent(this, BluetoothGattService::class.java)
            gattIntent.putExtra("Sensor",resultDevice)
            gattIntent.putExtra("vitalSign", deviceType)
            startService(gattIntent)

            scanResults.clear()
            scanResultAdapter.notifyDataSetChanged()
        }
    }

    @RequiresApi(Build.VERSION_CODES.LOLLIPOP)
    private val scanCallback = object : ScanCallback() {
        @RequiresApi(Build.VERSION_CODES.Q)
        override fun onScanResult(callbackType: Int, result: ScanResult) {
            val indexQuery = scanResults.indexOfFirst { it.device.address == result.device.address }
            if (indexQuery != -1) { // A scan result already exists with the same address
                scanResults[indexQuery] = result
                scanResultAdapter.notifyItemChanged(indexQuery)
            } else {
                with(result.device){
//                    println(name)
                    name?.let {
                        if (vitalSign.contains("Temperature") && name.contains("JXB_TTM")){
                            scanResults.add(result)
                            scanResultAdapter.notifyItemInserted(scanResults.size - 1)
                        }else if(vitalSign.contains("Spo2") && name.contains("BerryMed")){
                            scanResults.add(result)
                            scanResultAdapter.notifyItemInserted(scanResults.size - 1)
                        }
                        else if(vitalSign.contains("BloodPressure") && name.contains("DBP")){
                            scanResults.add(result)
                            scanResultAdapter.notifyItemInserted(scanResults.size - 1)
                        }
                    }
                }
            }

        }
        override fun onScanFailed(errorCode: Int) {
            Log.e("ScanCallback", "onScanFailed: code $errorCode")
        }
    }


    private fun setupRecyclerView() {
        scan_results_recycler_view.apply {
            adapter = scanResultAdapter
            layoutManager = LinearLayoutManager(
                this@MainActivity,
                RecyclerView.VERTICAL,
                false
            )
            isNestedScrollingEnabled = false
        }

        val animator = scan_results_recycler_view.itemAnimator
        if (animator is SimpleItemAnimator) {
            animator.supportsChangeAnimations = false
        }
    }
}





