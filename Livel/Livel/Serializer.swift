//
//  Serializer.swift
//  Serializer
//
//  Created by Nattapong Ounanong on 30/7/2564 BE.
//


import Foundation
import UserNotifications

struct Serializer{
    func serializerManager(deviceType: String, data: Data) -> Dictionary<String,Any>{
        let dataArray = Array(data)
        let json: Dictionary<String,Any>
        switch deviceType {
        case "temp":
            json = serializeTemp(data: dataArray)
        case "spo2":
            json = serializeSpo2(data: dataArray)
        case "pressure":
            json = serializePressure(data: dataArray)
        default:
            print("Invalid Input")
            return ["None":"None"]
        }
        return json
    }
    func serializeTemp(data: Array<UInt8>)->Dictionary<String,Any>{
        let temp = decodeJXB_TTM(data: data)
//        let jsonMsg=["name":"JXB_TTM",
//                     "temp":temp,
//                     "type":"temp",
////                     "RID":"",
//                     "DID":getIPAddress(),
//                     "dt":getTimestamp()] as [String : Any]
        let jsonMsg = ["patientId":tokenSecret.getToken.patientId!,
//        let jsonMsg = ["patientId":494,
                       "temperature":temp,
                       "createdDate":getDateTime()
        ] as [String : Any]
        return jsonMsg
    }
    func serializeLabTemp(data: Array<UInt8>, sensorName: String, kioskSerial: String)->Dictionary<String,Any>{
        let temp = decodeJXB_TTM(data: data)
        let jsonMsg = ["kioskSerial":tokenSecret.getToken.patientId!,
                       "sensorSerial":sensorName,
                       "sensorName":"Rycom",
                       "temperature":temp,
                       "timestamp":getTimestamp()
        ] as [String : Any]
        return jsonMsg
    }
    func serializeSpo2(data: Array<UInt8>) -> Dictionary<String,Any>{
        let result = decodeBerrryMed(data: data)!
//        guard let cellularIp = getAddress(for: .cellular) else { return }
//        let jsonMsg = ["name":"BerryMed",
//                     "spo2":["value": result.spo2,
//                             "heartrate": result.hr],
//                     "type": "spo2",
//                       "DID": getIPAddress(),
//                       "dt": getTimestamp()] as [String : Any]
        let jsonMsg = ["patientId":tokenSecret.getToken.patientId!,
                       "spo2":Int(result.spo2)!,
                       "heartrate":Int(result.hr)!,
                       "createdDate":getDateTime()
        ] as [String : Any]
        return jsonMsg
    }
    
    func serializeHeartRate(data: Int) -> Dictionary<String,Any>{
//        let result = decodeBerrryMed(data: data)!
        let jsonMsg = ["patientId":tokenSecret.getToken.patientId!,
                       "heartrate":data,
                       "createdDate":getDateTime()
        ] as [String : Any]
        return jsonMsg
    }
    
    func serializePressure(data: Array<UInt8>) -> Dictionary<String,Any>{
//        8,10,11
        let result = decodeDBP(data: data)!
//        let jsonMsg = ["name":"DBP",
//                     "type":"pressure",
//                     "pressure":["sys":result.sys,
//                                 "dia":result.dia,
//                                 "hr":result.hr],
//                     "DID": "IP Address",
//                     "dt": getTimestamp()] as [String : Any]
        let jsonMsg = ["patientId":tokenSecret.getToken.patientId!,
                       "bloodPressure":["systolic":result.sys,
                                    "diastolic":result.dia,
                                    "heartrate":result.hr],
                       "createDate":getDateTime()
        ] as [String : Any]
        return jsonMsg
    }
    func decodeJXB_TTM(data: Array<UInt8>) -> String{
//        if data.count < 15{
//            return 0
//        }
        let hexTemp = String(format:"%02x",data[6])+String(format:"%02x",data[5])
        let decodeTemp = Int(String(hexTemp),radix: 16)
        let temp = Float(decodeTemp!)/10
        let roundTemp = String(round(temp*10)/10.0)
//        let roundTemp = temp.rounded(.to)
        return roundTemp
    }
    func decodeBerrryMed(data: Array<UInt8>) -> (spo2: String, hr: String)?{
        let spo2 = String(Int(exactly: data[4])!)
        let hr = String(Int(exactly:data[3])!)
//        if spo2.contains("127"){
//            spo2 = "--"
//        }
//        if hr.contains("127"){
//            hr = "--"
//        }
        return (spo2, hr)
    }
    func decodeDBP(data: Array<UInt8>) -> (sys: Int, dia: Int, hr: Int)?{
//        if data.count < 20{
//            return (0, 0, 0)
//        }
        let sys = Int(data[8])
        let dia = Int(data[10])
        let hr = Int(data[11])
        return (sys, dia, hr)
    }
    
    func getTimestamp()->CLongLong{
        let timeInterval: TimeInterval = Date().timeIntervalSince1970
        let millisecond = CLongLong(round(timeInterval*1000))
        return millisecond
    }
    
    func getDateTime() -> String{
        let now = Date()
        let cal = Calendar(identifier: .gregorian)
        let formatter = DateFormatter()
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        formatter.calendar = cal
        let dateString = formatter.string(from: now)
        return dateString
    }
    
    func getIPAddress() -> String {
        var address: String?
                var ifaddr: UnsafeMutablePointer<ifaddrs>?
                
                if getifaddrs(&ifaddr) == 0 {
                    
                    var ptr = ifaddr
                    while ptr != nil {
                        defer { ptr = ptr?.pointee.ifa_next } // memory has been renamed to pointee in swift 3 so changed memory to pointee
                        
                        guard let interface = ptr?.pointee else {
                            return "nil"
                        }
                        let addrFamily = interface.ifa_addr.pointee.sa_family
                        if addrFamily == UInt8(AF_INET) || addrFamily == UInt8(AF_INET6) {
                            
                            guard let ifa_name = interface.ifa_name else {
                                return "nil"
                            }
                            let name: String = String(cString: ifa_name)
                            
                            if name == "en0" {  // String.fromCString() is deprecated in Swift 3. So use the following code inorder to get the exact IP Address.
                                var hostname = [CChar](repeating: 0, count: Int(NI_MAXHOST))
                                getnameinfo(interface.ifa_addr, socklen_t((interface.ifa_addr.pointee.sa_len)), &hostname, socklen_t(hostname.count), nil, socklen_t(0), NI_NUMERICHOST)
                                address = String(cString: hostname)
                            }
                            
                        }
                    }
                    freeifaddrs(ifaddr)
                }
                
                return address!
            }
}
