"""Form API Calls"""

import os

class ApiCall:
    real_time_stock = "https://api.worldtradingdata.com/api/v1/stock?symbol={tckr}&api_token={token}" # tckr should be something like 'ATVI,SNAP'
    real_time_mf = "https://api.worldtradingdata.com/api/v1/mutualfund?symbol={tckr}&api_token={token}"
    intraday = "https://intraday.worldtradingdata.com/api/v1/intraday?symbol={tckr}&range=1&interval=1&api_token={token}"
    historical = "https://api.worldtradingdata.com/api/v1/history?symbol={tckr}&sort=newest&api_token={token}"


    def _get_key(self):
        if not self.keydir_exists:
            api_key = input("Enter API Key: ")
            with open(self.keydir, mode='w+') as f:
                f.write(api_key)
        else:
            with open(self.keydir) as f:
                api_key = f.read()
        return api_key


    def __init__(self, tckr, token=None):
        key_path = (
            os.path.dirname(__file__)
            , '..'
            , '.appdata'
            , 'apikey.txt'
        )
        self.keydir = os.path.join(*key_path)
        self._api_key = None

    @property
    def keydir_exists(self):
        return os.path.exists(self.keydir)

    @property
    def api_key(self):
        if not self._api_key:
            self._api_key = self._get_key()
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value
        


