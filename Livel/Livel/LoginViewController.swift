//
//  StartViewController.swift
//  StartViewController
//
//  Created by Nattapong Ounanong on 11/8/2564 BE.
//

import UIKit
//import Siesta
import JWTDecode
import Alamofire

var params = [
    "username": "punkungkub",
    "password": "Punkung.1995"
]
var token: String!

class LoginViewController: UIViewController, UITextFieldDelegate {
    
    @IBOutlet weak var username: UITextField!
    @IBOutlet weak var password: UITextField!
    
    weak var delegate: LoginDelegate?
    
    let api = RestAPI()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "Login"
        self.hideKeyboardWhenTappedAround()
        username.delegate = self
        password.delegate = self
//        print(token)
    }
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        textField.resignFirstResponder()
        return true
    }
    
    @IBAction func login(_ sender: UIButton) {
        params["username"] = username.text!
        params["password"] = password.text!
        let myGroup = DispatchGroup()
        api.login(username: params["username"]!, password: params["password"]!, dispatcher: myGroup)
        let patientIdGroup = DispatchGroup()
        myGroup.notify(queue: .main){
            self.api.getPatientId(dispatcher: patientIdGroup)
        
        patientIdGroup.notify(queue: .main){
            print(tokenSecret.getToken.success!)
            if tokenSecret.getToken.success!{
                let vc = self.storyboard!.instantiateViewController(withIdentifier: "Main") as? ViewController
                self.navigationController?.pushViewController(vc!, animated: true)
            }else{
                print("Login Failure!!!!")
            }
        }
        }
    }
}
    
protocol LoginDelegate: AnyObject {
    func tokenAchieved(_ token: String)
}

extension UIViewController {
    func hideKeyboardWhenTappedAround() {
        let tap = UITapGestureRecognizer(target: self,
                                         action: #selector(UIViewController.dismissKeyboard))
        tap.cancelsTouchesInView = false
        view.addGestureRecognizer(tap)
    }
    @objc func dismissKeyboard(){
        view.endEditing(true)
    }
}


