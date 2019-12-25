"""Form API Calls"""

import os
import datetime
import json
import pandas as pd
import requests

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
            , "formatted": "true" # Alter JSON data format. Does not affect CSV
        }
        , "historical" : {
            "symbol": None
            , "api_token": None
            , "date_from": "2018-01-02"
            , "date_to": "2018-06-01"
            , "sort": "oldest"
            , "output": "json"
            , "formatted": "true"
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

    def __init__(self, call_type="historical"):
        # assertion checks
        assert isinstance(call_type, str), 'call_type must be str'
        call_type_opts = ['historical', 'real_time_stock', 'real_time_mf', 'intraday']
        assert call_type in call_type_opts, f"call type must be one of {', '.join(call_type_opts)}"

        # straightforward attributes
        self.call_type = call_type
        self._today = str(datetime.datetime.today().date())

        # get attr for key and its directory
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

    @staticmethod
    def _format_call_history(x):
        s_dict = json.loads(x)
        tckr = s_dict['name']
        df = pd.DataFrame(s_dict['history']).T
        df.index.name = 'date'
        df.loc[:,"symbol"] = tckr
        df.set_index(['symbol'], append=True, inplace=True)
        return df

    def _format_call_stock_multi(self, x):
        x_dict = json.loads(x)
        df = pd.DataFrame(x_dict['data']).set_index('symbol')
        df.loc[:, "date"] = self._today
        return df

    def _form_api_call(self, options):
        """Gather User Requests to Fashion API Call
        """
        opts = self.defaults[self.call_type].copy() # defaults for this type of call
        assert options.keys() <= opts.keys(), "invalid option keys; all configurable options in defaults"
        opts.update(options)
        opts['api_token'] = self.api_key
        sub_list = [k+"="+v for k,v in opts.items()]
        sub = '&'.join(sub_list)
        api_call = self.call_skele[self.call_type].format(options=sub)
        return api_call

    def execute_call(self, options, output='raw'):
        assert isinstance(output, str), 'output must be str'
        assert output in ['raw', 'df']
        api_call = self._form_api_call(options)
        response = requests.get(api_call)
        if output == 'raw':
            return response
        elif output == 'df':
            formatter = {
                'historical': self._format_call_history
                , "real_time_stock": self._format_call_stock_multi
                , "real_time_mf": None
                , "intraday": None
                , "forex_historical": None
            }.get(self.call_type, None)
            assert formatter, f'call_type={self.call_type} df formatter not yet implemented'
            return formatter(response.text)
