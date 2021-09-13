#robinhood_starter.py
# Copyright Yush Raj Kapoor
# Created 08/13/2021



import robin_stocks.robinhood as rs
import os
from time import sleep
from robin_obfuscate import *
import math
import pyrebase
import sys
import time
from threading import Timer
import signal
from numpy import *
from playsound import playsound
import pandas as pd
from pandas import read_csv
from pandas import to_datetime
from pandas import DataFrame
from prophet import Prophet
import numpy as np
import datetime
import robin_creds


config = robin_creds.config

firebase = pyrebase.initialize_app(config)

ref = firebase.database()

buy_price = 0
sell_price = 0

robin_user = robin_creds.robin_user
robin_pass = robin_creds.robin_pass

MAXIMUM_VALUE = 0
MINIMUM_VALUE = 0

prev_action = "none"
target_price = 0

Ticker = ""

coins = 0
cash = 10

data_points = 240
slope_points = 30
slope_tracker = []


golden_ratio = 1.61803398875

ROOT_PERC = 0.004

SELLING_PERCENTAGE_MAIN = ROOT_PERC
BUYING_PERCENTAGE_MAIN = ROOT_PERC

selling_const = ROOT_PERC
buying_const = ROOT_PERC


target_reached = False
safe_reached = False

tracker = []
forecasting_pts = 1000

E_forecast = []
Q_forecast = []
H_forecast = []
F_forecast = [0.25]

first = True

Mock = True

QUIT = False

def reset_High_Lows(min_val, max_val):
    global MAXIMUM_VALUE
    global MINIMUM_VALUE
    MAXIMUM_VALUE = max_val
    MINIMUM_VALUE = min_val
    
    
def get_forecasts():
    #a = ["E_forecast", "Q_forecast", "H_forecast", "F_forecast"]
    a = ["F_forecast"]
    for i in a:
        forecast(i)
        

def forecast(root):
    global E_forecast
    global Q_forecast
    global H_forecast
    global F_forecast
    a = {"E_forecast":8, "Q_forecast":4, "H_forecast":2, "F_forecast":1}
    use_data = tracker[-int(len(tracker)/a[root]):]
    times = []
    cur_time = time.time()
    
    ct = cur_time - (len(use_data) * 15)
    for i in use_data:
        times.append(datetime.datetime.fromtimestamp(ct))
        ct += 15
    
    data = {'Month':times, 'Price':use_data}

    df = pd.DataFrame(data)
    df.columns = ['ds', 'y']
    model = Prophet()
    model.daily_seasonality=True
    model.yearly_seasonality = False
    model.weekly_seasonality = False
    with suppress_stdout_stderr():
        model.fit(df)

        future = list()
        for i in range(1, 20):
            date = time.time() + (i * 15)
            future.append([datetime.datetime.fromtimestamp(date)])

        future = DataFrame(future)
        future.columns = ['ds']

        forecast = model.predict(future)
        
        if root == "E_forecast":
            E_forecast = forecast['yhat'].to_numpy()
        elif root == "Q_forecast":
            Q_forecast = forecast['yhat'].to_numpy()
        elif root == "H_forecast":
            H_forecast = forecast['yhat'].to_numpy()
        elif root == "F_forecast":
            F_forecast = forecast['yhat'].to_numpy()


def calculate_trend_slope(data):
    sum = 0
    av_price = ((buy_price + sell_price)/2)
    for i in range(1, len(data)):
        cur = data[i]
        prev = data[i-1]
        sum += (cur - prev) / av_price
    
    return sum / len(data)
    
    
def current_coins():
    positions = rs.get_crypto_positions()
    for n in positions:
        if n['currency']['code'] == Ticker:
            coins = float(n['cost_bases'][0]['direct_quantity'])
            return coins
        
    return 0
    
    
def get_min_max_of_tracker():
    min = 999999
    max = 0
    max_index = -1
    min_index = -1
    new = tracker[-data_points:]
    for n in list(range(len(new))):
        val = new[n]
        if val > max:
            max = val
            max_index = n
        elif val < min:
            min = val
            min_index = n
            
    return (min, max, min_index, max_index)
    
  

def trend(arr):
    lean = 0
    av_price = (buy_price + sell_price) / 2
    for n in arr:
        if av_price > n:
            #support for using min for reference
            lean += 1
        elif av_price < n:
            #support for using max for reference
            lean -= 1
    
    return lean / len(arr)
    

def calculate_immediate_slopes():
    immediate = tracker[-4]
    semi_immediate = tracker[-20]
    
    av_price = (buy_price + sell_price) / 2
    im_slope = (av_price - immediate) / av_price
    s_im_slope = (av_price - semi_immediate) / av_price
    
    return im_slope, s_im_slope
    
    
def volatility(arr):
    prev_tr = 0
    trend_volatility = 0
    for i in arr:
        if i > 0.1:
            if prev_tr == -1:
                trend_volatility += 1
            prev_tr = 1
        elif i < -0.1:
            if prev_tr == 1:
                trend_volatility += 1
            prev_tr = -1
        elif i != 0:
            prev_tr = i/abs(i)
    
    return trend_volatility
    
    
def action():
    global selling_const
    global buying_const
    
    tr1 = trend(tracker[-int(data_points/8):])
    tr2 = trend(tracker[-int(data_points/4):])
    tr3 = trend(tracker[-int(data_points/2):])
    tr4 = trend(tracker[-int(data_points/4*3):])
    tr5 = trend(tracker[-int(data_points):])
    
    a = [tr2, tr3, tr4, tr5]
    trend_volatility = volatility(a)
    is_high_volatility = False
    if trend_volatility > 1:
        is_high_volatility = True
        
    lean = (tr1 * 0.4) + (tr2 * 0.3) + (tr3 * 0.2) + (tr5 * 0.1)
    linear_tr = (tr2 + tr3 + tr4 + tr5) / 4
    
    
    immediate_slope, semi_immediate_slope = calculate_immediate_slopes()
    
#    E_tr = calculate_trend_slope(E_forecast)
#    Q_tr = calculate_trend_slope(Q_forecast)
#    H_tr = calculate_trend_slope(H_forecast)
    F_tr = calculate_trend_slope(F_forecast)
#    scaled_forcasted_slope = (E_tr * 0.1) + (Q_tr * 0.2) + (H_tr * 0.3) + (F_tr * 0.4)
    
    print("date", datetime.datetime.now())
    print("usage_tr",linear_tr)
    print("immediate_slope", immediate_slope)
    print("usage_forecasted_slope", F_tr)
        
    tr_gate = 0
    slope_gate = 0
    forecast_gate = 0
    to_act = "None"
    if prev_action == "buy":
        #looking to sell
        if linear_tr < -0.1:
            tr_gate = linear_tr * 0.1
        if immediate_slope < -0.0002:
            slope_gate = immediate_slope * 0.4
        if F_tr < -0.0001:
            forecast_gate = F_tr * 0.4
        to_act = "sell"
    elif prev_action == "sell":
        #looking to buy
        if linear_tr > 0.1:
            tr_gate = linear_tr * 0.1
        if immediate_slope > 0.0002:
            slope_gate = immediate_slope * 0.4
        if F_tr > 0.0001:
            forecast_gate = F_tr * 0.4
        to_act = "buy"
    
    print("tr_gate", tr_gate)
    print("slope_gate", slope_gate * 200)
    print("forecast_gate", forecast_gate * 2000)
    
    
    min_max = get_min_max_of_tracker()
    min = min_max[0]
    max = min_max[1]
    min_index = min_max[2]
    max_index = min_max[3]
    
    min_delta = buy_price - min
    max_delta = buy_price - max
    
    min_tr = min_delta / buy_price / (data_points - min_index) * 10 * golden_ratio
    max_tr = max_delta / buy_price / (data_points - max_index) * 10 * golden_ratio
    
    print("lean",lean)
   
    tr = max_tr
    if lean > 0:
        tr = min_tr
       
    selling_const = SELLING_PERCENTAGE_MAIN + tr
    buying_const = BUYING_PERCENTAGE_MAIN - tr
    
    if selling_const < 0.002:
        selling_const = 0.002
    if buying_const < 0.002:
        buying_const = 0.002
    
    
    total_gate = (tr_gate + (200 * slope_gate) + (2000 * forecast_gate))
    if to_act == "buy":
        if lean > 0:
            total_gate = total_gate * golden_ratio
    elif to_act == "sell":
        if lean < 0:
            total_gate = total_gate * golden_ratio
        
    print("COMPARE",total_gate)
    if (abs(total_gate) > 0.4):
        if (prev_action == "sell" and total_gate > 0) or (prev_action == "buy" and total_gate < 0) or (first and total_gate > 0):
            first = False
            print(to_act + " FROM COMPARE")
            return to_act
    
    
#    #Gradient purchase
#    if prev_action == "buy":
#        #Looking for a selling point
#        adjusted_price = sell_price * 1.001
#        percent_difference = ((MAXIMUM_VALUE - adjusted_price) / adjusted_price)
#        print("MAXIMUM_VALUE {} difference {} selling_const {}".format(MAXIMUM_VALUE, percent_difference, selling_const))
#        if percent_difference > selling_const:
#            #SELL SELL SELL
#            print("SELL FROM GRADIENT", percent_difference, ">", selling_const)
#            return "sell"
#    elif prev_action == "sell":
#        #Looking for a buying point
#        adjusted_price = buy_price * 1.001
#        percent_difference = ((adjusted_price - MINIMUM_VALUE) / adjusted_price)
#        print("MINIMUM_VALUE {} difference {} buying_const {}".format(MINIMUM_VALUE, percent_difference, buying_const))
#        if percent_difference > buying_const:
#            #BUY BUY BUY
#            print("BUY FROM GRADIENT", percent_difference, ">", buying_const)
#            return "buy"
    
    
    #Emergency sell
    if safe_reached:
        if sell_price * 0.9995 < target_price:
            print("Emergency sell")
            print("sell_price * 0.9995", sell_price * 0.9995, "target_price",target_price)
            return "sell"
            
    return "None"
    
    
def set_slopes(baseline):
    global slope_tracker
    slope_tracker = []
    for n in list(range(slope_points)):
        slope_tracker.append(baseline)
    
  
def update_min_max():
    global MAXIMUM_VALUE
    global MINIMUM_VALUE
    
    if sell_price > MAXIMUM_VALUE:
        MAXIMUM_VALUE = sell_price
        
    if buy_price < MINIMUM_VALUE:
        MINIMUM_VALUE = buy_price
   
   
def update_slope():
    global slope_tracker
    for n in list(range(1, slope_points)):
        val = slope_tracker[n]
        slope_tracker[n - 1] = val
        
    slope_tracker[slope_points - 1] = buy_price
    
   
def get_min_max_of_slopes():
    min = 999999
    max = 0
    max_index = -1
    min_index = -1
    
    for n in list(range(len(slope_tracker))):
        val = slope_tracker[n]
        if val > max:
            max = val
            max_index = n
        elif val < min:
            min = val
            min_index = n
            
    return (min, max, min_index, max_index)
    


def reset_target_bool():
    global target_reached
    global safe_reached
    target_reached = False
    safe_reached = False
    
    
def check_tresholds():
    global target_reached
    global safe_reached
    target_tag = ""
    safe_tag = ""
    if target_reached:
        target_tag = "REACHED"
    if safe_reached:
        safe_tag = "REACHED"
    print("target price",target_price, target_tag)
    print("safe threshold", target_price * 1.002, safe_tag)
    if prev_action == "buy":
        if buy_price > target_price and not target_reached:
            target_reached = True
            playsound('Crypto-Siphon/target.mp3')
        if buy_price > (target_price * 1.001) and not safe_reached:
            safe_reached = True
            playsound('Crypto-Siphon/safeThreshold.mp3')


def one():
    global prev_action
    global cash
    global coins
    global buy_price
    global sell_price

    buy_price = float(rs.get_crypto_quote(Ticker)['ask_price'])
    sell_price = float(rs.get_crypto_quote(Ticker)['bid_price'])
    
   
    ref.child("Time/robinhood_" + Ticker + "_one").set(time.time())
    quit = ref.child("engine_status/robinhood_" + Ticker + "_quit").get().val()
    if quit == 1:
        quitter()
    ref.child("engine_status/robinhood_" + Ticker).set(1)
    if not Mock:
        coins = current_coins()
    
    update_slope()
    update_min_max()
    
#    least = 0.0000000000001
#    l_rounded = round_up(least, round_quantity()) - least
#    if coins > l_rounded:
#        prev_action = "buy"
#        cash = 0
#    else:
#        prev_action = "sell"
    
    
    
    if QUIT:
        quitter()
    else:
        Timer(1, one).start()
    
    
def five():
    Timer(0.1, get_forecasts).start()
    
    ref.child("Time/robinhood_" + Ticker + "_five").set(time.time())

    todo = action()
    check_tresholds()
    if Mock:
        mock_transaction(todo)
    else:
        make_transaction(todo)
        
    
    if QUIT:
        quitter()
    else:
        Timer(5, five).start()
  
    
#def make_transaction(str):
#    global cash
#    global coins
#    global prev_action
#    global target_price
#    global MINIMUM_VALUE
#    global MAXIMUM_VALUE
#
#    if str == 'buy':
#        coin_to_buy = float(cash / buy_price) * 0.999
#        buy_data = buy(coin_to_buy)
#        prev_action = str
#        data = gem.get_trades_for_crypto(Ticker)[0].json()[0]
#        coins = float(data['amount'])
#        executed_cash = float(data['amount']) * float(data['price'])
#        executed_fee = float(data['fee_amount'])
#        cash -= (executed_cash + executed_fee)
#        MINIMUM_VALUE = buy_price
#        target_price = float(rs.get_crypto_quote(Ticker)['ask_price'])) * 1.002
#        reset_target_bool()
#        reset_High_Lows(sell_price, buy_price)
#        print("status {}\nPrice {}\nProspects {}\n".format(str.upper(), sell_price, coins * sell_price))
#        print("SELL AT ${}".format(target_price))
#    elif str == 'sell':
#        sell_data = sell()
#        data = gem.get_trades_for_crypto(Ticker)[0].json()[0]
#        prev_action = str
#        coins = data['amount']
#        executed_cash = float(data['amount']) * float(data['price'])
#        executed_fee = float(data['fee_amount'])
#        cash += (executed_cash + executed_fee)
#        MAXIMUM_VALUE = float(rs.get_crypto_quote(Ticker)['bid_price']))
#        target_price = float(rs.get_crypto_quote(Ticker)['bid_price'])) * 1.002
#        reset_target_bool()
#        reset_High_Lows(sell_price, buy_price)
#        print("status {}\nPrice {}\nProspects {}\n".format(str.upper(), buy_price, cash))
#    else:
#        status = "NONE"
#        pros = cash
#        price = buy_price
#        if cash == 0:
#            status = "HELD"
#            price = sell_price
#            pros = coins * buy_price
#
#        print("status {}\nPrice {}\nProspects {}\n".format(status, price, pros))
        
        
def mock_transaction(str):
#####THIS IS A MOCK
#####NO MONEY IS USED HERE WHEN GLOBAL VAR 'MOCK' IS TRUE
    global cash
    global coins
    global prev_action
    global target_price
    global MINIMUM_VALUE
    global MAXIMUM_VALUE
    
    if str == 'buy':
        prev_action = str
        executed_cash = cash
        executed_fee = round(cash * 0.001, 2)
        cash -= executed_cash
        coins += (executed_cash - executed_fee) / buy_price
        MINIMUM_VALUE = buy_price
        target_price = buy_price * 1.002
        reset_target_bool()
        reset_High_Lows(sell_price, buy_price)
        print("status {}\nPrice {}\nProspects {}\n".format(str.upper(), sell_price, coins * sell_price))
        playsound('Crypto-Siphon/Buy.mp3')
    elif str == 'sell':
        prev_action = str
        executed_cash = coins * sell_price
        executed_fee = round(executed_cash * 0.001, 2)
        coins -= executed_cash / sell_price
        cash += (executed_cash - executed_fee)
        MAXIMUM_VALUE = sell_price
        target_price = sell_price * 1.002
        reset_target_bool()
        reset_High_Lows(sell_price, buy_price)
        print("status {}\nPrice {}\nProspects {}\n".format(str.upper(), buy_price, cash))
        playsound('Crypto-Siphon/Sell.mp3')
    else:
        status = "NONE"
        pros = cash
        price = buy_price
        if cash == 0:
            status = "HELD"
            price = sell_price
            pros = coins * buy_price
            
        print("status {}\nPrice {}\nProspects {}\n".format(status, price, pros))
    

def set_tracker(baseline):
    global tracker
    tracker = []
    for n in list(range(forecasting_pts)):
        tracker.append(baseline)


def fill_tracker_fast(ct):
    av_price = (float(rs.get_crypto_quote(Ticker)['ask_price'])) + float(rs.get_crypto_quote(Ticker)['bid_price']) / 2
    update_trackers(av_price)
    for n in list(range(1, len(tracker))):
        val = tracker[n]
        tracker[n - 1] = val
        
    tracker[len(tracker) - 1] = av_price
    if ct > 0:
        Timer(1, fill_tracker_fast(ct - 1)).start()
        
    
def start():
    global tracker
    global MINIMUM_VALUE
    global MAXIMUM_VALUE
    global target_price
    rs.login(username=robin_user, password=robin_pass, expiresIn=86400, by_sms=True)
    
#    if current_coins() > 1:
#        data = gem.get_trades_for_crypto(Ticker)[0].json()[0]
#        p = float(data['price'])
#        target_price = p * 1.001
        
    print("STARTING ROBINHOOD ENGINE FOR", Ticker)
    
    buy_price = float(rs.get_crypto_quote(Ticker)['ask_price'])
    sell_price = float(rs.get_crypto_quote(Ticker)['bid_price'])
    set_tracker(buy_price)
    set_slopes(buy_price)
    MAXIMUM_VALUE = buy_price
    MINIMUM_VALUE = sell_price
    
    prev_fore = ref.child("Forecast/robinhood_" + Ticker).get().val()
    if prev_fore != None:
        tracker = prev_fore
    else:
        ref.child("Forecast/robinhood_" + Ticker).set(tracker)
        fill_tracker_fast(data_points)
       
        
    ref.child("Time/robinhood_" + Ticker + "_one").set(time.time())
    ref.child("Time/robinhood_" + Ticker + "_five").set(time.time())
    ref.child("engine_status/robinhood_" + Ticker + "_quit").set(0)
    
    Timer(5, five).start()
    Timer(1, one).start()
  
  
 
def buy(price):
    rs.orders.order_buy_crypto_by_price(Ticker, price, timeInForce='gtc')
    print("Buying " + str(price) + " of " + Ticker)
    playsound('Crypto-Siphon/Buy.mp3')


def sell():
    coins = current_coins()
    bid_price = float(rs.get_crypto_quote(Ticker)['bid_price'])
    price_to_sell = bid_price * coins
    rs.order_sell_crypto_by_quantity(Ticker, coins)
    print("Selling $" + str(price_to_sell) + " of " + Ticker + " at " + str(bid_price) + " each")
    playsound('Crypto-Siphon/Sell.mp3')
                 
    
    
def quitter():
    global QUIT
    QUIT = True
    if Ticker != None:
        ref.child("engine_status/robinhood_" + Ticker).set(0)
        ref.child("engine_status/robinhood_" + Ticker + "_quit").set(0)
    os._exit(os.EX_OK)
    
    
def handler(signum, frame):
    print('KeyboardInturrupt')
    print('Process Manually Stopped')
    quitter()

signal.signal(signal.SIGINT, handler)
    
    
if __name__ == '__main__':
    Ticker = input('Enter Crypto Symbol: ').upper()
    start()
       



class suppress_stdout_stderr(object):
    '''
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


