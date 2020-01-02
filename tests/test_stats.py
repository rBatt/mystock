import unittest
from unittest.mock import patch

import ast
import os
import pandas as pd
from pandas.util.testing import assert_frame_equal

from mystock import stats

# pytest --cov-report term-missing --cov=mystock tests/

class TestApiCall(unittest.TestCase):
    def setUp(self):
        with open(os.path.join("static","example_user_txn1.py")) as f:
            user_txn = ast.literal_eval(f.read())
        self.user_txn = pd.DataFrame(user_txn)
        self.user_txn.index.names = ['date', 'symbol', 'txn_type']
        self.user_txn = self.user_txn.groupby(['date','symbol']).sum()

        with open(os.path.join("static","example_user_txn1_stockdata.py")) as f:
            stockdata = ast.literal_eval(f.read())
        self.stockdata = pd.DataFrame(stockdata)
        self.stockdata.index.names = ['date','symbol']

    def test_get_total_shares(self):
        # shuffle dataframe so we can test that _get_total_share sorts
        # (important b/c cummulative sum)
        def assert_monotonic_group(x, assertTrue=True):
            # we only need to check that the index is sorted within a given
            # 'symbol' grouping ... i.e., that it is time-sorted
            if assertTrue:
                check = lambda x: self.assertTrue(x)
            else:
                check = lambda x: self.assertFalse(x)
            grouped = x.groupby('symbol')
            for _, group in grouped:
                check(group.index.is_monotonic)
        user_txn = self.user_txn.copy().sample(frac=1, random_state=42)
        assert_monotonic_group(user_txn, assertTrue=False) # use our grouping
        self.assertFalse(user_txn.index.is_monotonic) # check again to make it isnt sorted (w/o relying on custom check())
        self.assertFalse(user_txn.index.get_level_values('date').is_monotonic) # specifically test that date isn't sorted, which is what check() checks

        # apply the core function that we are testing
        user_txn_total = stats._get_total_shares(user_txn)
        print(user_txn_total)

        # test that _get_total_shares did the sorting
        assert_monotonic_group(user_txn_total, assertTrue=True)

        # construct dataframe of expected output
        dict_output = {
            'shares': {('2019-09-30', 'VTI'): 100.0, ('2019-10-04', 'VTI'): 100.0, ('2019-10-18', 'TSLA'): 0.86, ('2019-10-18', 'VOO'): 88.589, ('2019-10-18', 'VTI'): -136.99099999999999, ('2019-11-01', 'TSLA'): 0.835, ('2019-11-01', 'VOO'): 1.307, ('2019-11-01', 'VTI'): 1.669, ('2019-11-15', 'TSLA'): 0.817, ('2019-11-15', 'VOO'): 1.285, ('2019-11-15', 'VTI'): 1.65, ('2019-11-29', 'TSLA'): 0.809, ('2019-11-29', 'VOO'): 1.273, ('2019-11-29', 'VTI'): 1.644, ('2019-12-13', 'TSLA'): 0.8, ('2019-12-13', 'VOO'): 1.263, ('2019-12-13', 'VTI'): 1.622, ('2019-12-27', 'TSLA'): 0.809, ('2019-12-27', 'VOO'): 1.289, ('2019-12-27', 'VTI'): 1.639},
            'total_shares': {('2019-09-30', 'VTI'): 100.0,('2019-10-04', 'VTI'): 200.0,('2019-10-18', 'TSLA'): 0.86,('2019-10-18', 'VOO'): 88.589,('2019-10-18', 'VTI'): 63.009000000000015,('2019-11-01', 'TSLA'): 1.6949999999999998,('2019-11-01', 'VOO'): 89.896,('2019-11-01', 'VTI'): 64.67800000000001,('2019-11-15', 'TSLA'): 2.5119999999999996,('2019-11-15', 'VOO'): 91.181,('2019-11-15', 'VTI'): 66.32800000000002,('2019-11-29', 'TSLA'): 3.3209999999999997,('2019-11-29', 'VOO'): 92.454,('2019-11-29', 'VTI'): 67.97200000000002,('2019-12-13', 'TSLA'): 4.1209999999999996,('2019-12-13', 'VOO'): 93.717,('2019-12-13', 'VTI'): 69.59400000000002,('2019-12-27', 'TSLA'): 4.93,('2019-12-27', 'VOO'): 95.006,('2019-12-27', 'VTI'): 71.23300000000002}
        }
        output = pd.DataFrame(dict_output)
        output.index.names = ['date', 'symbol']
        output.sort_values(by=['symbol','date'], inplace=True)

        # assert that realized output matches expected output
        self.assertIsNone(assert_frame_equal(output, user_txn_total))

if __name__ == '__main__':
    unittest.main()