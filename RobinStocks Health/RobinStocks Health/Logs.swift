//
//  Logs.swift
//  RobinStocks Health
//
//  Created by Yush Raj Kapoor on 9/12/21.
//

import UIKit

class Logs: UIViewController {
    
    @IBOutlet weak var textView: UITextView!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        textView.text = ""
        textView.isEditable = false
        textView.isScrollEnabled = true
        ref.child("Logs/\(tag!)").observe(.childAdded, with: { [self] (snapshot) in
            
            if let str = snapshot.value as? String {
                textView.text = textView.text! + "\n" + str
                scrollTextViewToBottom(textView: textView)
            }
           
        })
    
        
    }
    
    func scrollTextViewToBottom(textView: UITextView) {
        if textView.text.count > 0 {
            let location = textView.text.count - 1
            let bottom = NSMakeRange(location, 1)
            textView.scrollRangeToVisible(bottom)
        }
    }
    
    
    
    
    @IBAction func back_button(_ sender: Any) {
        performSegue(withIdentifier: "LogsToHome", sender: self)
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
}
