"""Form API Calls"""

import os
import datetime
import json
import pandas as pd

class ApiCall:
    call_skele = {
        "real_time_stock": "https://api.worldtradingdata.com/api/v1/stock?{options}" # tckr should be something like 'ATVI,SNAP'
        , "real_time_mf": "https://api.worldtradingdata.com/api/v1/mutualfund?{options}"
        , "intraday": "https://intraday.worldtradingdata.com/api/v1/intraday?{options}"
        , "historical": "https://api.worldtradingdata.com/api/v1/history?{options}"
        , "forex_historical": "https://api.worldtradingdata.com/api/v1/forex_history?{options}"
    }

    defaults = {
        "real_time_stock" : {
            "symbol": None
            , "api_token": None
            , "sort_order": "asc"
            , "sort_by": "symbol"
            , "output": "json"
        }
        , "real_time_mf": {
            "symbol": None
            , "api_token": None
            , "sort_order": "asc"
            , "sort_by": "symbol"
            , "output": "json"
        }
        , "intraday" : {
            "symbol": None
            , "api_token": None
            , "interval": "5" # minutes; 1, 2, 5, 60; maybe also 15?
            , "range": "7" # number of days data is returned for; 1 min intervals limited to 7 days max, all other intervals 30 days max
            , "sort": "desc"
            , "ouput": "json"
            , "formatted": "false" # Alter JSON data format. Does not affect CSV
        }
        , "historical" : {
            "symbol": None
            , "api_token": None
            , "date_from": "2018-01-02"
            , "date_to": "2018-06-01"
            , "sort": "oldest"
            , "output": "json"
            , "formatted": "false"
        }
    }

    def _get_key(self):
        if not self.keydir_exists:
            api_key = input("Enter API Key: ")
            with open(self.keyfile, mode='w+') as f:
                f.write(api_key)
        else:
            with open(self.keyfile) as f:
                api_key = f.read()
        return api_key


    def __init__(self, tckr, token=None):
        path_pieces = (
            os.path.dirname(__file__)
            , '..'
            , '.appdata'
        )
        self.key_path = os.path.join(*path_pieces)
        if not os.path.exists(self.key_path):
            os.makedirs(self.key_path)
        self.keyfile = os.path.join(self.key_path, 'apikey.txt')
        self._api_key = None

    @property
    def keydir_exists(self):
        return os.path.exists(self.keyfile)

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = self._get_key()
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        


