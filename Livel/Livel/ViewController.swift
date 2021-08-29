//
//  ViewController.swift
//  Livel
//
//  Created by Nattapong Ounanong on 22/7/2564 BE.
//

import UIKit
import CoreBluetooth
import SwiftMQTT

import Alamofire

class ViewController: UIViewController, CBCentralManagerDelegate, CBPeripheralDelegate{
    var centralManager: CBCentralManager!
    var myPeripheral: CBPeripheral!
    var mqttSession: MQTTSession!
    var tokenHTTP: String! = ""
    var gattCollection: Array<CBPeripheral>!
    @IBOutlet weak var tempVal: UILabel!
    @IBOutlet weak var pressureVal: UILabel!
    @IBOutlet weak var pressurePulseVal: UILabel!
    @IBOutlet weak var spo2Val: UILabel!
    @IBOutlet weak var spo2PulseVal: UILabel!
    
    let spo2UUID = CBUUID(string: "49535343-1E4D-4BD9-BA61-23C647249616")
    let tempUUID = CBUUID(string: "FE10")
    let pressureUUID = CBUUID(string: "FFF1")
    let serializer = Serializer()
    let api = RestAPI()
    let topic = "vitalSign"
    
    var payload: Array<Dictionary<String,Any>>!
    var jsonTemp: Dictionary<String,Any>!
    var jsonPressure: Dictionary<String,Any>!
    var jsonSpo2: Dictionary<String,Any>!
    var jsonHr: Dictionary<String,Any>!
    
    var thermalGunLabel: UILabel!
    var spo2Label: UILabel!
    var pressureLabel: UILabel!
    
    var deviceUUID: Array<CBUUID> {
        get {
            [spo2UUID,
            tempUUID,
            pressureUUID]
        }
    }
    let deviceNameArray = ["spo2": "BerryMed",
                           "temp": "JXB_TTM",
                           "pressure":"DBP"]
    var deviceCharacteristics: Dictionary<CBUUID,String>!
    
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        if central.state == CBManagerState.poweredOn {
            print("BLE powered on")
//            central.scanForPeripherals(withServices: nil)
            // Turned on
        }
        else {
            print("Something wrong with BLE")
            // Not on, but can have different issues
        }
    }
    
    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String : Any], rssi RSSI: NSNumber) {
        if let pname = peripheral.name {
            for subName in deviceNameArray.values{
                if pname.contains(subName){
//                    print(self.deviceCharacteristics)
                    connectGatt(peripheral: peripheral)
                }
            }
        }
    }
    
    func connectGatt(peripheral: CBPeripheral){
        self.myPeripheral = peripheral
        self.myPeripheral.delegate = self

        self.centralManager.connect(peripheral, options: nil)
        
    }
    
    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        print("Conntected!")
        self.myPeripheral.discoverServices(nil)
        }
    
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let services = self.myPeripheral.services else { return }
        for service in services {
            peripheral.discoverCharacteristics(nil, for: service)
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService,
                    error: Error?) {
        guard let characteristics = service.characteristics else { return }
//        print(peripheral.name)
        for characteristic in characteristics {
            print(characteristic)
            if characteristic.properties.contains(.notify) {
                peripheral.setNotifyValue(true, for: characteristic)
            }
        }
    }
    
    func peripheral(_ peripheral: CBPeripheral,
                        didUpdateNotificationStateFor characteristic: CBCharacteristic,
                        error: Error?) {
      // Perform any error handling if one occurred.
      // It's not necessary to abandon the connection from this kind of error
      if let error = error {
        print("Characteristic update notification error: \(error.localizedDescription)")
        return
      }

      // Check if it is successfully set as notifying
      if characteristic.isNotifying {
        print("Characteristic notifications have begun.")
      } else {
        print("Characteristic notifications have stopped. Disconnecting.")
        centralManager.cancelPeripheralConnection(peripheral)
      }

      // Send any info to the peripheral from the central
    }
    
    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let data = characteristic.value else {
                // no data transmitted, handle if needed
                return
            }
        guard let devType = deviceCharacteristics[characteristic.uuid] else {
            return
        }
        
        switch devType {
            case "temp":
            if data.count < 15{
                return
            }
            case "spo2":
                break
            case "pressure":
            if data.count < 20{
                return
            }
            default:
                break
            }
        
        let tmpDictionary = serializer.serializerManager(deviceType: devType, data: data)
        updateVitalSign(deviceType: devType, data: tmpDictionary)
    }

    func updateVitalSign(deviceType: String, data: Dictionary<String, Any>){
        switch deviceType {
        case "temp":
            jsonTemp = data
//            tempVal.text = "\(data["temp"]!) \u{00b0}C"
            tempVal.text = "\(data["temperature"]!) \u{00b0}C"
        case "spo2":
            print(data)
//            let spo2Tmp = data["spo2"]! as! Dictionary<String, String>
//            if data["spo2"] as! String == "--"{
//                break
//            }
//            if data["heartrate"]! as! String == "--"{
//                break
//            }
            if data["spo2"] as! Int == 127{
                break
            }
            if data["heartrate"] as! Int == 127{
                break
            }
            
            var spo2Data = data
            let heartRate = spo2Data.removeValue(forKey: "heartrate")
            jsonSpo2 = spo2Data
                        
            jsonHr = serializer.serializeHeartRate(data: heartRate as! Int)
//            spo2Val.text = "\(spo2Tmp["value"]!) %"
//            spo2PulseVal.text = "\(spo2Tmp["hr"]!) BPM"
            spo2Val.text = "\(data["spo2"]!) %"
            spo2PulseVal.text = "\(data["heartrate"]!) BPM"
        case "pressure":
            jsonPressure = data
            let pressureTmp = data["bloodPressure"]! as! Dictionary<String, Int>
            pressureVal.text = "\(pressureTmp["systolic"]!) / \(pressureTmp["diastolic"]!)"
            pressurePulseVal.text = "\(pressureTmp["heartrate"]!) BPM"
        default:
            print("Invalid Input")
        }
    }
    
    func updateData(){
        payload = [jsonTemp,jsonPressure,jsonSpo2]
        payload.removeAll(where: {$0.count == 1})
        
    }
    
    func clearData(){
        jsonTemp = ["None":"None"]
        jsonPressure = ["None":"None"]
        jsonSpo2 = ["None":"None"]
        jsonHr = ["None":"None"]
        tempVal.text = "--"
        spo2Val.text = "--"
        spo2PulseVal.text = "--"
        pressureVal.text = "-- / --"
        pressurePulseVal.text = "--"
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        // Create a UILabel object.
        
        centralManager = CBCentralManager(delegate: self, queue: nil)
        deviceCharacteristics=[spo2UUID:"spo2",
                               tempUUID:"temp",
                           pressureUUID:"pressure"]
        // Uncomment Code Below for MQTT Protocol**********************************************
//        mqttSession = MQTTSession(
//            host: "devmqtt.airpresense.tech",
//            port: 1883,
//            clientID: "swiftVitalSign", // must be unique to the client
//            cleanSession: true,
//            keepAlive: 15,
//            useSSL: false
//        )
//        mqttSession.username = "guest"
//        mqttSession.password = "guest"
//        mqttSession.connect() { error in
//            if error == .none {
//                print("Connected! MQTT")
//            } else {
//                print(error.description)
//            }
//        }
        // *************************************************************************************
        clearData()
    }
    
    @IBAction func StartScan(_ sender: UIButton) {
        print("Start Scan")
        centralManager.scanForPeripherals(withServices: nil, options: ["characteristics":deviceUUID])
    }
    @IBAction func StopScan(_ sender: UIButton) {
        centralManager.stopScan()
    }
    
    @IBAction func Send(_ sender: UIButton) {
        tokenHTTP = tokenSecret.getToken.token
        updateData()
        api.postTemperature(params: jsonTemp)
        api.postSpo2(params: jsonSpo2)
        api.postPressure(params: jsonPressure)
        api.postHeartRate(params: jsonHr)
//        Uncomment code below for mqtt protocol **************************************************************
//        let jsonMsg = try! JSONSerialization.data(withJSONObject: payload as Any, options: .prettyPrinted)
//        mqttSession.publish(jsonMsg, in: topic, delivering: .atLeastOnce, retain: false) { error in
//            if error == .none {
//                print("Published data in \(self.topic)!")
//            } else {
//                print(error.description)
//            }
//        }
//        *****************************************************************************************************
        clearData()
    }
}
