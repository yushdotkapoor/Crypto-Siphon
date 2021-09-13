//
//  ViewController.swift
//  RobinStocks Health
//
//  Created by Yush Raj Kapoor on 8/17/21.
//

import UIKit
var tag:String?

class ViewController: UIViewController, UITableViewDelegate, UITableViewDataSource {
    @IBOutlet weak var tableView: UITableView!
    
    var labels:[String] = []
    
    var dict:[String:Bool] = [:]
        
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        UIApplication.shared.applicationIconBadgeNumber = 0
        
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "shell")
        tableView.delegate = self
        tableView.dataSource = self
        tableView.estimatedRowHeight = 70
    }
    
    override func viewWillAppear(_ animated: Bool) {
        fetchResults()
        ref.child("engine_status").observe(.childChanged, with: { (snapshot) in
            self.fetchResults()
        })
    }
    
    func fetchResults() {
        ref.child("engine_status").observeSingleEvent(of: .value, with: { [self] snapshot in
            let val = snapshot.value as? [String:Int] ?? [:]
            var lbls:[String] = []
            for i in val.keys {
                let key = i
                let val = val[i]
                if !key.contains("quit") {
                    lbls.append(key)
                    if val == 0 {
                        dict[key] = false
                    }
                    else if val == 1 {
                        dict[key] = true
                    }
                }
            }
            lbls.sort()
            labels = lbls
            tableView.reloadData()
        })
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return labels.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell") as! TableViewCell
        
        cell.controller = self
        let txt = labels[indexPath.row]
        cell.label.text = txt
        cell.sw.setOn(dict[txt]!, animated: true)
        
        return cell
    }
    
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        tag = labels[indexPath.row]
        performSegue(withIdentifier: "toLogs", sender: self)
    }
    
    
}

