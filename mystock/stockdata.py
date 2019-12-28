"""Stock Data"""
import pandas as pd
from .apicall import ApiCall

class StockData(ApiCall):
    def __init__(self, options=None, call_type='historical'):
        super().__init__(call_type=call_type)
        self.options = options or self.defaults[self.call_type]
        self.data = dict()

    def get_data(self, tckr):
        """Request Instrument Data
        """
        opts = self.options
        if isinstance(tckr, str):
            tckr = [tckr]
        for i in tckr:
            opts['symbol'] = i
            self.data[i] = self.execute_call(options=opts, output='df')
        return pd.concat(self.data.values(), ignore_index=False)