import pickle
import joblib
from datetime import datetime, timedelta, timezone
import time
import requests
import pandas as pd
import os
import pybitflyer
import traceback
import math
import ta

from features import features,calc_features

from apscheduler.schedulers.blocking import BlockingScheduler


#BitFlyerからOHLCVデータを取得
def get_bitflyer_ohlcv(target_coin,time_scale):
    #OHLCV取得
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
    unixtime = datetime.now().timestamp() * 1000
    ohlc_list=[]
    #1000本以上の1分足を取得
    while len(ohlc_list) < 1000:
        response = requests.get( f"https://lightchart.bitflyer.com/api/ohlc?symbol={target_coin}&period=m&before={unixtime}", headers= headers).json()
        ohlc_list.extend(response)
        current_after = datetime.fromtimestamp(response[-1][0]/1000)
        next_before = current_after - timedelta(minutes=1)
        unixtime = int(next_before.timestamp() * 1000)

    df_1m = pd.DataFrame(ohlc_list,columns=['timestamp', 'op', 'hi', 'lo', 'cl', 'volume','volume_buy_sum','volume_sell_sum','volume_buy','volume_sell'])
    df_1m["timestamp"] = pd.to_datetime(df_1m["timestamp"]/1000,unit='s', utc=True)
    df_1m.set_index("timestamp",inplace=True)
    df_1m.sort_index(inplace=True)

    #指定したタイムスケールに分足を変換
    df = pd.DataFrame()
    rule = time_scale
    df["op"] = df_1m["op"].resample(rule).first()
    df["hi"] = df_1m["hi"].resample(rule).max()
    df["lo"] = df_1m["lo"].resample(rule).min()
    df["cl"] = df_1m["cl"].resample(rule).last()
    df["volume"] = df_1m["volume"].resample(rule).sum()
    df["volume_buy"] = df_1m["volume_buy"].resample(rule).sum()
    df["volume_sell"] = df_1m["volume_sell"].resample(rule).sum()
    df = df.dropna()
    return df

def get_bitflyer_position(bitflyer): 
    poss = bitflyer.getpositions(product_code="FX_BTC_JPY")
    size= pnl = 0
    for p in poss:
        if p['side'] == 'BUY':
            size += p['size']
            pnl += p['pnl']
        if p['side'] == 'SELL':
            size -= p['size']
            pnl -= p['pnl']
    if size == 0: 
        side = 'NONE'
    elif size > 0:
        side = 'BUY'
    else:
        side = 'SELL'
    return {'side':side, 'size':size, 'pnl':pnl}

def order_bitflyer(exchange,order_side,order_price,order_size):
    order = exchange.sendchildorder(
        product_code = "FX_BTC_JPY",
        child_order_type = 'LIMIT',
        side = order_side,
        price = order_price,
        size = order_size
    )
    print(order)


def order_bitflyer_exit(exchange,order_side,order_size):
    order = exchange.sendchildorder(
        product_code = "FX_BTC_JPY",
        child_order_type = 'MARKET',
        side = order_side,
        #price = order_price,
        size = order_size
    )
    print(order)


global doten_ON
doten_ON =False

#ボット起動
def start(exchange,max_lot,lot,interval):
    global doten_ON
    t_delta = timedelta(hours=9)  # 9時間
    JST = timezone(t_delta, 'JST')  # UTCから9時間差の「JST」タイムゾーン

    print("paibot started! max_lot:{0}btc lot:{1}btc interval:{2}min nowtiem:{3}".format(max_lot,lot,interval,datetime.now(JST)))
    '''
    while True:

        dt_now = datetime.now()
        
        #指定した時間間隔ごとに実行
        if dt_now.minute % interval == 0:
    '''
    try:

        #OHLCV情報を取得
        df_bf_fx = get_bitflyer_ohlcv("FX_BTC_JPY","1T")
        df = df_bf_fx.dropna()

        #特徴量計算
        df_features = calc_features(df)
        
        indicator_TSI = ta.momentum.TSIIndicator(close=df["cl"], window_slow=25, window_fast=13, fillna=False)
        df['tsi'] = indicator_TSI.tsi()

        tsi = float(df['tsi'].iloc[-1])
        tsi_minus_1 = float(df['tsi'].iloc[-2])
           
        print('df["tsi"]',df['tsi'].tail(5) )
        #print('TSI_-1:',tsi_minus_1)
        print('TSI:',tsi)

        #TSIによるエントリー許容ゾーン指定
        entry_zone = abs(tsi) < 20
        print('entry_zone:',entry_zone)

        #TSIによる緊急回避シグナル #ドテンするなら22くらい？
        emergency_evacuation = abs(tsi) > 20
        print('emergency_evacuation:',emergency_evacuation)

        #緊急回避後のドテンのエグジット。１本前のTSIより今回のTSIが下がったらエグジット
        emergency_evacuation_doten_exit= abs(tsi_minus_1) - abs(tsi)> 1
        print('emergency_evacuation_doten_exit',emergency_evacuation_doten_exit)

        #モデル読み込み
        #model_y_buy = joblib.load('/home/jovyan/work/model/model_y_buy_bffx.xz')
        #model_y_sell = joblib.load('/home/jovyan/work/model/model_y_sell_bffx.xz')

        #推論
        #df_features["y_predict_buy"] = model_y_buy.predict(df_features[features])
        #df_features["y_predict_sell"] = model_y_sell.predict(df_features[features])

        #ticker1=exchange.ticker(product_code="FX_BTC_JPY")
        #saisyuukakaku

        

        buy_price =  int(df_features['BBANDS_lowerband'].iloc[-1])
        sell_price = int(df_features['BBANDS_upperband'].iloc[-1])

        exit_sell_price =  int(df_features['BBANDS_upperband'].iloc[-1])
        exit_buy_price = int(df_features['BBANDS_lowerband'].iloc[-1])



        #df_features["sell_price"] = ticker['ltp'] + ticker['ltp'] * 0.02#0.0095
        #df_features["buy_price"] = ticker['ltp'] - ticker['ltp'] * 0.02
        

        
        position = get_bitflyer_position(exchange)

        #print("predict_buy:{0} predict_sell:{1}".format(str(predict_buy),str(predict_sell)))
        print("position side:{0} size:{1}".format(str(position["side"]),str(position["size"])))
        print("buy price:{0} sell price:{1}".format(str(buy_price),str(sell_price)))


        #注文処理

        order_side = "NONE"

        #全注文をキャンセル
        exchange.cancelallchildorders(product_code="FX_BTC_JPY")
        
        #緊急回避エグジット
        if doten_ON == False and emergency_evacuation and position["side"] == "BUY" and abs(position["size"]) >= 0.01:
            print('#緊急回避エグジット')
            order_side = "SELL"
            order_size = round(abs(position["size"]),8)
            order_bitflyer_exit(exchange,order_side,order_size)
            def doten(): # 成り行きドテン
                order_side = "SELL"
                order_size = 0.1 #緊急回避ドテンはリスクが少なそうなのでロットを大きくする
                #order_size = round(abs(position["size"]),8)
                order_bitflyer_exit(exchange,order_side,order_size)
                global doten_ON
                doten_ON = True
            doten()
        if doten_ON == False and emergency_evacuation and position["side"] == "SELL" and abs(position["size"]) >= 0.01:
            print('#緊急回避エグジット')
            order_side = "BUY"
            order_size = round(abs(position["size"]),8)
            order_bitflyer_exit(exchange,order_side,order_size)
            def doten(): # 成り行きドテン
                order_side = "BUY"
                order_size = 0.1 #緊急回避ドテンはリスクが少なそうなのでロットを大きくする
                #order_size = round(abs(position["size"]),8)
                order_bitflyer_exit(exchange,order_side,order_size)
                global doten_ON
                doten_ON = True
            doten()

        
        #緊急回避後ドテンエグジット TSIが閾値外かつ、前回TSI絶対値よりも今回TSI絶対値が小さくなったタイミングで成り行きエグジット
        if doten_ON and  emergency_evacuation_doten_exit and emergency_evacuation and position["side"] == "BUY" and abs(position["size"]) >= 0.01:
            print('#緊急回避ドテンエグジット')
            order_side = "SELL"
            order_size = round(abs(position["size"]),8)
            order_bitflyer_exit(exchange,order_side,order_size)
            doten_ON = False
        if doten_ON and emergency_evacuation_doten_exit and emergency_evacuation and position["side"] == "SELL" and abs(position["size"]) >= 0.01:
            print('#緊急回避ドテンエグジット')
            order_side = "BUY"
            order_size = round(abs(position["size"]),8)
            order_bitflyer_exit(exchange,order_side,order_size)
            doten_ON = False
        
        #トレンド順張りのdotenをしたている状況か
        print('doten_ON:',doten_ON)
        
        #エントリー
        if  entry_zone and (position["size"] < max_lot):
            order_side = "BUY"
            order_price = buy_price
            order_size = lot
            order_bitflyer(exchange,order_side,order_price,order_size)
        if  entry_zone  and (position["size"] > -max_lot):
            order_side = "SELL"
            order_price = sell_price
            order_size = lot                    
            order_bitflyer(exchange,order_side,order_price,order_size)
        #エグジット
        if doten_ON == False and position["side"] == "BUY" and abs(position["size"]) >= 0.01:
            order_side = "SELL"
            order_price = exit_sell_price
            order_size = round(abs(position["size"]),8)
            order_bitflyer(exchange,order_side,order_price,order_size)
            #order_bitflyer(exchange,order_side,order_size)
        if doten_ON == False and position["side"] == "SELL" and abs(position["size"]) >= 0.01:
            order_side = "BUY"
            order_price = exit_buy_price
            order_size = round(abs(position["size"]),8)
            order_bitflyer(exchange,order_side,order_price,order_size)
            #order_bitflyer_exit(exchange,order_side,order_size)

    except Exception as e:
        print(traceback.format_exc())
        pass

        #time.sleep(10)

if __name__  == '__main__':

    API_KEY='YXCs4CfzHpkdNJoer9FBpR'
    SECRET_KEY='KpWqttsIqkl9xyciPZM6D3FbgyVC85KLeFrS/SzC31A='
    LOT=0.01
    MAX_LOT=0.15  #MAX_LOTは５minの場合低めの方がいいかも
    INTERVAL=1

    apiKey    = API_KEY
    secretKey = SECRET_KEY
    lot = float(LOT)
    max_lot = float(MAX_LOT)
    interval = int(INTERVAL)

exchange = pybitflyer.API(api_key=apiKey, api_secret=secretKey)
#start(exchange, max_lot, lot, interval)

scheduler = BlockingScheduler(timezone="Asia/Tokyo")
## APSchedulerで実行したい関数を登録(5秒間隔で実行)
scheduler.add_job(start, 'cron', second='00',args=[exchange,max_lot,lot,interval])
#scheduler.add_job(send_mail, 'interval', seconds=60,args=(f'送信時間:{datetime.today()} \n利益合計:{profit} \ntoday(USTの時刻を取得):{today} \n情報取得日数:{days} \n{all_results} \nsignal_buy_entry = 現在の終値:{owarine} > エントリー期間最高値:{saitakane_entry_kikan} \nsignal_sell_entry = 現在の終値:{owarine} < エントリー期間最安値:{saiyasune_entry_kikan} \nlong_position_exit = 現在最安値:{yasune_rosoku_ashi} < 決済期間最安値:{saiyasune_kessai_kikan} \nshort_position_exit = 現在最高値:{takane_rosoku_ashi} > 決済期間最高値:{saitakane_kessai_kikan} \n{data}','GMO-Donchien.py定期報告'))

## APSchedulerを実行
scheduler.start()




