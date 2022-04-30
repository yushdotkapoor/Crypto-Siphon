# Crypto-Siphon
 Cryptocurrency trading algorithm using gemini and robinhood.
 
 
## Overview
This project is attempting to buy and sell cryptocurrency based on its trends and forecasts to "Siphon" value from the cryptocurrency's volatility.
The main function runs on Python, but there is an iOS/macOS primitive interface that can go along with it. If you choose to integrate with iOS (reccomended), then you will recieve buy/sell notifications and get notified if there are any errors present in the code (network issues, etc.)
Robinhood has a big flaw in that orders can sometimes take hours to execute, so I will not be primarily pushing for robinhood, but the files are there for you to use.
###**PLEASE NOTE: This is NOT a finished project and does NOT guarantee profit increase. Testing has shown that fees and spread of to exchange are causing a profit decrease.**

## Requirements
 You will need a Gemini and Firebase account, and an AWS account is recommended.
 
 There are a few non-native python libraries that will need to be installed:
 ```bash
 #required
 pip install pyrebase
 pip install robin_stocks
 pip install prophet
 #optional
 pip install playsound
 ```
 
 ## Set-Up
 ### Gemini
 Go to your gemini account settings and find the API section to create a Primary scope API. Make sure to note down the API credentials. In the gemini_starter.py file, replace the API_KEY and API_SECRET variables with what you noted down.
 ### Firebase
 Create a Firebase project and set it up as a Web App project. When setting up, take note of the instructions given and make sure to copy down the "firebaseConfig" data. You can always find this in the General tab in the Project Settings of your Firebase project. Copy this configuration data and paste it in gemini_starter.py, replacing the config variable. Do the same thing in the lambda-function.py file in the Archive folder. Now, in your Firebase project settings, create a Firebase Admin SDK private key file and copy its contents. Then paste it in json_file variable in the lambda-function.py file. If you want to set up the iOS ecosystem, go into project overview and select 'Add App'. Then follow the instructions to initialize the iOS integration with Firebase. Make sure you have RobinStocks Health.xcodeproj open. You will be asked to download an GoogleService-Info.plist file, which you will then drag into the RobinStock Health xcode hierarchy next to the likes of alert.wav and Main.storyboard.
 ### General
 #### gemini_starter.py
Let's start with variable 'Mock' being True. This will make sure to jumpstart the data in the database and allow for historical data to start flowing in (more on that later). For a list of valid cryptocurrencies, please take a look at gemini_symbols.py. For example, Bitcoin will be listed as 'BTCUSD'. If you choose not to get notified on your iOS/MacOS device, or if you are not planning on integrating with the iOS ecosystem, you can simply set 'Notify' to False. If you would like to disable the sound updates, set variable Sound to false. You can run the file however you like.
 #### lambda_function.py
 We will need to collect price data for the cryptocurrencies of your choice, so the lambda_function.py file will have to run on a timer. I am using AWS lambda to run this python script, but you can use other scripting options such as Google AppsScript (although the quotas are smaller). Make sure whatever trigger you use triggers every 60 seconds.
 Note that lambda_function.py requires installation of pyrebase before running which means either wherever you run the script needs to have pyrebase installed, or you will have to upload all pyrebase dependancies for access.
 ### iOS
 You should have already been successful in setting up the iOS functionality in the Firebase section above. At this point, all you have to do is connect your iOS device via the cable and run the project. You could also run it directly on your mac as well. The iOS interface is very basic, all it has is the status of the cryptocurrency engines (on/off) and current logs. You can also abort a cryptocurrency engine from the app as well. The most important feature, is the notifications feature. The app will notifiy you whenever there is an error with the code (sometimes there is a network error or something else) and also notifies you of buying and selling of the cryptocurrency.
 

 
 
 
