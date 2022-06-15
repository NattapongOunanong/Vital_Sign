//
//  RestAPI.swift
//  RestAPI
//
//  Created by Nattapong Ounanong on 16/8/2564 BE.
//

import Alamofire
import Foundation

let Url = "https://apidev.airpresense.tech/api/auth/login"
let tempUrl = "https://apidev.airpresense.tech/api/vitalsign/temperature"
let bloodPressureUrl = "https://apidev.airpresense.tech/api/vitalsign/bloodpressure"
let spo2Url = "https://apidev.airpresense.tech/api/vitalsign/spo2"
let heartRateUrl = "https://apidev.airpresense.tech/api/vitalsign/heartrate"
let rootUserUrl = "https://apidev.airpresense.tech/api/patient/user"
let labTempUrl = "http://api.temperature.bangpra.airpresense.tech/api/kiosk/temperature"

struct authResponse: Decodable {
    let id: Int
    let user: String
    let role: String
    let role_id: Int
    let groupPermission: String
    let subgroupPermission: String
    let locationPermission: String
    var token: String
    
    enum CodingKeys: String, CodingKey {
      case id
      case user
      case role
      case role_id
      case groupPermission
      case subgroupPermission
      case locationPermission
      case token
    }
}

struct patientResponse: Decodable {
    let patientId: Int
    let id: Int
    enum CodingKeys: String, CodingKey{
        case patientId
        case id
    }
}
class RestAPI{
    func login(username: String, password: String, dispatcher: DispatchGroup){
        dispatcher.enter()
        let params = [
            "username": username,
            "password": password
        ]
        AF.request(Url, method: .post, parameters: params).responseDecodable(of: authResponse.self) { (response) in
//            debugPrint(response)
            switch response.result
            {
            case .success:
                guard let loginResponse = response.value else { return }
                tokenSecret.getToken.updateToken(resp: loginResponse)
                tokenSecret.getToken.updateStatus(stat: response.response?.statusCode ?? 400)
                
            case .failure(let error):
                tokenSecret.getToken.updateStatus(stat: response.response?.statusCode ?? 400)
                print(response.response?.statusCode)
                print(error)
            }
            dispatcher.leave()
        }
    }
    
    func getPatientId(dispatcher: DispatchGroup){
        dispatcher.enter()
        let userToken = tokenSecret.getToken.token
        let loginSuccess = tokenSecret.getToken.success
        if userToken == nil || loginSuccess! == false{
            return
        }
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
//        print(tokenSecret.getToken.id!)
        let userId = "\(tokenSecret.getToken.id!)"
        let patientUrl = rootUserUrl + "/" + userId
//        AF.request(patientUrl, method: .get, headers: headers).responseDecodable(of: patientResponse.self){
        
        AF.request(patientUrl, method: .get, headers: headers).responseJSON{
            (response) in
//            debugPrint(response)
            switch response.result
            {
            case .success:
                let data = response.data!
                
                let arrayDict = try? JSONSerialization.jsonObject(with: data, options: .mutableLeaves)
                let wrapDict = arrayDict as? [[String:Any]]
                let unwrapDict = wrapDict?.first
                let patientId = unwrapDict!["patientId"]! as? Int
                let statusCode = response.response?.statusCode
                tokenSecret.getToken.setPatientId(stat: statusCode!, pId: patientId!)
                tokenSecret.getToken.updateStatus(stat: response.response?.statusCode ?? 400)
                
            case .failure(let error):
                print(error)
            }
        }
        dispatcher.leave()
    }
    
    func postTemperature(params: Dictionary<String,Any>){
//        print(params)
        let userToken = tokenSecret.getToken.token
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
        AF.request(tempUrl, method: .post, parameters: params, encoding: JSONEncoding.default, headers: headers).responseJSON{
            (response) in
            debugPrint(response)
            switch response.result
            {
            case .success:
                return
                
            case .failure(let error):
                print(error)
            }
        }
    }
    
    func postPressure(params: Dictionary<String,Any>){
        let userToken = tokenSecret.getToken.token
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
        AF.request(bloodPressureUrl, method: .post, parameters: params, encoding: JSONEncoding.default, headers: headers).responseJSON{
            (response) in
//            debugPrint(response)
            switch response.result
            {
            case .success:
                return
            case .failure(let error):
                print(error)
            }
        }
    }
    
    func postSpo2(params: Dictionary<String,Any>){
        let userToken = tokenSecret.getToken.token
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
        AF.request(spo2Url, method: .post, parameters: params, encoding: JSONEncoding.default, headers: headers).responseJSON{
            (response) in
            debugPrint(response)
            switch response.result
            {
            case .success:
                return
                
            case .failure(let error):
                print(error)
            }
        }
    }
    func postHeartRate(params: Dictionary<String,Any>){
        let userToken = tokenSecret.getToken.token
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
        AF.request(heartRateUrl, method: .post, parameters: params, encoding: JSONEncoding.default, headers: headers).responseJSON{
            (response) in
            debugPrint(response)
            switch response.result
            {
            case .success:
                return
                
            case .failure(let error):
                print(error)
            }
        }
    }
    func postLabTemp(params: Dictionary<String,Any>){
        let userToken = tokenSecret.getToken.token
        let headers: HTTPHeaders = ["Authorization" : "Bearer "+userToken!+"",
                       "Content-Type": "application/json"]
        AF.request(labTempUrl, method: .post, parameters: params, encoding: JSONEncoding.default, headers: headers).responseJSON{
            (response) in
            debugPrint(response)
            switch response.result
            {
            case .success:
                return
                
            case .failure(let error):
                print(error)
            }
        }
    }
}

class tokenSecret {
    var token: String?
    var id: Int?
    var success: Bool? = false
    var patientId: Int?
    static let getToken = tokenSecret()
    private init(){
        
    }
    func updateToken (resp: authResponse){
        token = resp.token
        id = resp.id
    }
    func updateStatus (stat: Int){
        if stat == 200{
            success = true
        }else{
            success = false
        }
    }
    func setPatientId (stat: Int, pId: Int){
        if stat == 200{
            patientId = pId
        }
    }
}
