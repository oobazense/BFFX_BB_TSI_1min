import os
from os.path import join, dirname
from dotenv import load_dotenv
import main
import pybitflyer

if __name__  == '__main__':

   dotenv_path = join(dirname(__file__), './env/.env-bffx')
   load_dotenv(dotenv_path,verbose=True)

   API_KEY='YXCs4CfzHpkdNJoer9FBpR'
   SECRET_KEY='KpWqttsIqkl9xyciPZM6D3FbgyVC85KLeFrS/SzC31A='
   LOT=0.01
   MAX_LOT=0.01
   INTERVAL=15

   apiKey    = API_KEY
   secretKey = SECRET_KEY
   lot = float(LOT)
   max_lot = float(MAX_LOT)
   interval = int(INTERVAL)

   exchange = pybitflyer.API(api_key=apiKey, api_secret=secretKey)
   main.start(exchange, max_lot, lot, interval)