//
//  TableViewCell.swift
//  RobinStocks Health
//
//  Created by Yush Raj Kapoor on 8/17/21.
//

import UIKit

class TableViewCell: UITableViewCell {
    @IBOutlet weak var label: UILabel!
    @IBOutlet weak var sw: UISwitch!
    
    var controller:UIViewController?
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }
    
    @IBAction func switchTapped(_ sender: Any) {
        let state = sw.isOn
        let path = "engine_status/" + label.text!
        if state {
            ref.child(path).setValue(1)
            ref.child("\(path)_quit").setValue(0)
        } else {
            let alertController = UIAlertController(title: "Confirm", message: "Are you sure you want to shut off \(label.text!)?", preferredStyle: .alert)
            let yes = UIAlertAction(title: "Yes", style: .default, handler: {_ in
                ref.child(path).setValue(0)
                ref.child("\(path)_quit").setValue(1)
            })
            let no = UIAlertAction(title: "No", style: .cancel, handler: { [self]_ in
                sw.setOn(true, animated: true)
            })
            
            alertController.addAction(no)
            alertController.addAction(yes)
            controller!.present(alertController, animated: true, completion: nil)
            
        }
    }
    

    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)

        // Configure the view for the selected state
    }

}
