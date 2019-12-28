import os
import re
import pandas as pd
from pandas.util.testing import assert_frame_equal
import unittest
from unittest.mock import patch

from mystock.stockdata import StockData

class TestApiCall(unittest.TestCase):

    def setUp(self):
        self.input_patch = patch('mystock.apicall.input')
        self.input_mock = self.input_patch.start()
        self.input_mock.return_value = "testKey"

        opts = {
            "date_from": "2019-12-05"
            , "date_to": "2019-12-06"
        }
        self.data1 = StockData(options=opts)

        self.execute_patch = patch('mystock.stockdata.ApiCall.execute_call')
        self.execute_mock = self.execute_patch.start()

        test_out_dict = {
            'close': {
                ('VOO', '2019-12-05'): '286.64',
                ('VOO', '2019-12-06'): '289.19',
                ('VTI', '2019-12-05'): '158.88',
                ('VTI', '2019-12-06'): '160.29'},
            'high': {
                ('VOO', '2019-12-05'): '286.83',
                ('VOO', '2019-12-06'): '289.65',
                ('VTI', '2019-12-05'): '159.00',
                ('VTI', '2019-12-06'): '160.54'},
            'low': {
                ('VOO', '2019-12-05'): '285.29',
                ('VOO', '2019-12-06'): '288.55',
                ('VTI', '2019-12-05'): '158.18',
                ('VTI', '2019-12-06'): '159.89'},
            'open': {
                ('VOO', '2019-12-05'): '286.83',
                ('VOO', '2019-12-06'): '288.58',
                ('VTI', '2019-12-05'): '159.00',
                ('VTI', '2019-12-06'): '159.98'},
            'volume': {
                ('VOO', '2019-12-05'): '1597255',
                ('VOO', '2019-12-06'): '1609493',
                ('VTI', '2019-12-05'): '1858086',
                ('VTI', '2019-12-06'): '2021049'}
        }
        test_out = pd.DataFrame(test_out_dict)
        test_out.index.names = ['symbol', 'date']
        test_out = test_out.reorder_levels(['date','symbol'])
        self.execute_mock.return_value = test_out

    def tearDown(self):
        self.input_patch.stop()

    def test_get_data(self):
        test_dat = self.data1.get_data(tckr='asdf')
        self.assertIsNone(assert_frame_equal(test_dat, self.execute_mock()))
        test_dat2 = self.data1.get_data(tckr=['asdf', 'asdff'])
        self.assertIsNone(assert_frame_equal(test_dat2, pd.concat([self.execute_mock()]*2)))

if __name__ == '__main__':
    unittest.main()