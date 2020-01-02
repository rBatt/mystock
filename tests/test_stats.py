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

        # small test df
        mind = pd.MultiIndex.from_tuples(
            [
                ("2019-10-01", "XYZ")
                , ("2019-10-02", "ABC")
                , ("2019-10-02", "XYZ")
                , ("2019-10-03", "ABC")
                , ("2019-10-03", "XYZ")
                , ("2019-10-04", "XYZ")
            ]
            , names=['date','symbol']
        )
        # these rX values are the HPR's
        r1 = 1.1
        r2 = 0.9
        r3 = 1.01
        self.r1, self.r2, self.r3 = r1, r2, r3
        self.test_df = pd.DataFrame(
            {
                "shares":         [10, 2,  10,       0.8,      1.7,               1.5]
                , "txn_value":    [20, 1,  20,       0.4,      3.4,               3.0]
                , "tday":         [0,  1,  1,        2,        2,                 3]
                , "end_value_t":  [20, 1,  20+20*r1, 0.4+1*r1, 3.4+(20+20*r1)*r2, 3+(3.4+(20+20*r1)*r2)*r3]
                , "end_value_t1": [0,  0,  20,       1,        20+20*r1,          3.4+(20+20*r1)*r2]
            }
            , index=mind
        ) # TODO should I force all instruments to be present for all dates after 1st non-0 balance?

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

    def test_get_hpr(self):
        output1 = (6-4)/2.5
        output2 = (6.4-7.2)/0.9
        self.assertEqual(output1, stats._get_hpr(M_t=6, flow_t=4, M_t1=2.5))
        self.assertEqual(output2, stats._get_hpr(M_t=6.4, flow_t=7.2, M_t1=0.9))

    def get_hpr_df(self, total=False): # helper
        df = self.test_df.copy()
        if total:
            df = df.groupby('date').sum()
        hpr = stats._get_hpr(M_t=df.end_value_t, flow_t=df.txn_value, M_t1=df.end_value_t1)
        df['hpr'] = df.index.map(hpr)
        return df

    def test_get_twr(self):
        # expected output values (as dictionaries)
        twr_exp_dict = {'twr': {'ABC': 1.1, 'XYZ': 0.9999000000000002}}
        twr_ann_exp_dict = {'twr': {'ABC': 29672172494.534416, 'XYZ': 0.9916017093146073}}
        twr_tot_exp_dict = {'twr': 1.0050674418604653}
        twr_tot_ann_exp_dict = {'twr': 1.5315420616812092}

        # construct by-symbol TWR DF's (annualized and not)
        df = self.get_hpr_df(total=False)
        grouped = df.groupby('symbol')
        twr = grouped.apply(stats._get_twr, annualize=False, ann_tday=253)
        self.assertDictEqual(twr_exp_dict, twr.to_dict())
        twr_ann = grouped.apply(stats._get_twr, annualize=True, ann_tday=253)
        self.assertDictEqual(twr_ann_exp_dict, twr_ann.to_dict())

        # construct total TWR DF's (annualized and not)
        df_tot = self.get_hpr_df(total=True)
        twr_tot = stats._get_twr(df_tot, annualize=False, ann_tday=253)
        self.assertDictEqual(twr_tot_exp_dict, twr_tot.to_dict())
        twr_tot_ann = stats._get_twr(df_tot, annualize=True, ann_tday=253)
        self.assertDictEqual(twr_tot_ann_exp_dict, twr_tot_ann.to_dict())

    def test_get_naive_return(self):
        nr_tot_exp = 0.933305439330544
        nr_tot_ann_exp = 0.0029648783121983048
        nr_exp_dict = {'ABC': 1.0714285714285714, 'XYZ': 0.9614655172413794}
        nr_ann_exp_dict = {'ABC': 6170.889322739344, 'XYZ': 0.03636998546012772}

        df = self.test_df.copy()
        nr_tot = stats._get_naive_return(df)
        self.assertEqual(nr_tot_exp, nr_tot)
        nr_tot_ann = stats._get_naive_return(df, annualize=True)
        self.assertEqual(nr_tot_ann_exp, nr_tot_ann)

        grouped = self.test_df.groupby('symbol')
        nr = grouped.apply(stats._get_naive_return, annualize=False).to_dict()
        self.assertDictEqual(nr_exp_dict, nr)
        nr_ann = grouped.apply(stats._get_naive_return, annualize=True).to_dict()
        self.assertDictEqual(nr_ann_exp_dict, nr_ann)

if __name__ == '__main__':
    unittest.main()