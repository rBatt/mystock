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
        


