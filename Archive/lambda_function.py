#lambda_function.py

"""
This file should be called once every 60 seconds.
What is does is it uploads the current price to
the firebase database so the main execution can
use that data fore predictions.

I use AWS lambda to trigger this file every 60 seconds



NON-NATIVE PACKAGE DEPENDENCY:
pyrebase

"""

from oauth2client.service_account import ServiceAccountCredentials
import requests
import json
import time
import pyrebase
import datetime
from threading import Timer

#imports credentials file
import creds

config = creds.config
#When you create a web app, there will be a template given to you following the format below
#config = {
#  "apiKey": "",
#  "authDomain": "",
#  "databaseURL": "",
#  "storageBucket": ""
#}

firebase = pyrebase.initialize_app(config)

#represents the number of hours the data should collect
#Please note, data is collected every 15 seconds
HOURS_TO_LOG = 4



json_file = creds.json_file
#This is the data inside your Firebase service account file
#json_file = {
#  "type": "service_account",
#  "project_id": "",
#  "private_key_id": "",
#  "private_key": "-----BEGIN PRIVATE KEY-----\nBlahBlah\n-----END PRIVATE KEY-----\n",
#  "client_email": "",
#  "client_id": "",
#  "auth_uri": "",
#  "token_uri": "",
#  "auth_provider_x509_cert_url": "",
#  "client_x509_cert_url": ""
#}


def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = ServiceAccountCredentials.from_json_keyfile_dict(
      json_file, ['https://www.googleapis.com/auth/firebase.messaging'])
  access_token_info = credentials.get_access_token()
  return access_token_info.access_token


ref = firebase.database()

check_ct = 0

def checkTimeFunction():
    global check_ct
    tkn1 = ref.child('token').get().val()
    tkn2 = ref.child('token2').get().val()
    engine_stat = ref.child('engine_status').get().val()
    for i in engine_stat:
        key = i
        value = int(engine_stat[i])
        current_date = time.time()
        
        tm = ["_one", "_five"]
        for t in tm:
            snap = ref.child('Time/' + key + t).get().val()
            if snap != None and (current_date - float(snap) > 30) and value == 1:
                tokenArray = []
                if tkn1 != None:
                    tokenArray.append(tkn1)
                if tkn2 != None:
                    tokenArray.append(tkn2)
                if tokenArray != []:
                    sendNotificationMessage([tkn1, tkn2], key)
        
        if key == "gemini_":
            ref.child('engine_status/gemini_').remove()
            ref.child('engine_status/gemini__quit').remove()
            continue
        ticker = str(key).split("_")
        tempSymbol = ""
        if (ticker[len(ticker) - 1] == "quit"):
            continue
        if (ticker[0] != "gemini"):
            tempSymbol = ticker.pop() + "USD"
        else:
            tempSymbol = ticker.pop()
            
        
        current_price = float(get_current_price(tempSymbol))
        l = {}
        l[current_date] = current_price

        forecast_data = ref.child('Forecast/' + key).get().val()
        if forecast_data == None:
            forecast_data = [current_price] * (HOURS_TO_LOG * 60 * 4)
        else:
            forecast_data = forecast_data[1:] + [current_price]
        
        ref.child('Forecast/' + key).set(forecast_data)
    
    check_ct += 1
    if check_ct < 4:
        time.sleep(15)
        checkTimeFunction()
     

def get_current_price(ticker):
    data, err = request_get('https://api.gemini.com/v1/pubticker/' + ticker, None, None)
    return data.json()['bid']


def request_get(url, payload, parse_json):
    response_error = None
    response = None
    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()
    except Exception as e:
        response_error = e
        print(response_error)
    if parse_json and response.status_code == 200:
        return response.json(), response_error
    else:
        return response, response_error


def request_post(url, payload, parse_json, headers):
    response_error = None
    try:
        response = requests.post(url, params=payload, headers=headers)
        response.raise_for_status()
    except Exception as e:
        response_error = e
    if parse_json:
        return response.json(), response_error
    else:
        return response, response_error


def sendNotificationMessage(token, engineType):
    for j in token:
        print(j)
        url = 'https://fcm.googleapis.com/v1/projects/robinstocks-47aa9/messages:send'
        fcm_message = { 'message': {
                            'token': j,
                            'notification': {
                                'title' : "ERROR!!!",
                                'body' : "Something went wrong with " + engineType + "!!"
                            },
                            'apns': {
                                'payload': {
                                    'aps': {
                                        'badge': 1,
                                        'sound': "alert.wav"
                                    }
                                }
                            }
                        }
        }
                
        headers = {
        'Authorization': 'Bearer ' + _get_access_token(),
        'Content-Type': 'application/json; UTF-8',
        }
        #[END use_access_token]
        response_error = None
        try:
            response = requests.post(url, data=json.dumps(fcm_message), headers=headers)
            response.raise_for_status()
        except Exception as e:
            response_error = e
            print(response_error)
            
        if response.status_code == 200:
            print('Message sent to Firebase for delivery, response:')
            print(response.text)
            
        else:
            print('Unable to send message to Firebase')
            print(response.text)



def lambda_function(event, context):
    global check_ct
    check_ct = 0
    checkTimeFunction()
    return("Hello World")

