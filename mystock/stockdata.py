"""Stock Data"""
import pandas as pd
from .apicall import ApiCall

class StockData(ApiCall):
    """Stock Data (and ETF, Bonds, etc)

    Args:
        ApiCall (ApiCall): this class inherits from ApiCall class
    """
    def __init__(self, options=None, call_type='historical'):
        """Initialize StockData
        
        Args:
            options (dict, optional): See ApiCall docs. Defaults to None.
                Note that the value associated with the 'symbol' key of the
                `options` dict will be overwritten. It is intended that this
                particular option will be specified when calling the `get_data`
                method.
            call_type (str, optional): The type of API Call that will be used
                to retrieve data. Defaults to 'historical'.
        """
        super().__init__(call_type=call_type)
        self.options = options or self.defaults[self.call_type]
        self.data = dict()

    def get_data(self, tckr):
        """Get Data

        Args:
            tckr (str, list, tuple): a str or list/ tuple of str specifying
                ticker symbols. Will be passed to the 'symbols' key in the
                `options` dict for each API call.

        Returns:
            DataFrame: a pandas data frame
            self.data: as a side effect, populates a dict of DataFrames
                accessible as instance attributes
        """
        opts = self.options
        if isinstance(tckr, str):
            tckr = [tckr]
        for i in tckr:
            opts['symbol'] = i
            self.data[i] = self.execute_call(options=opts, output='df')
        return pd.concat(self.data.values(), ignore_index=False)