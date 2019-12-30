import unittest
from mystock.utils import count_tdays, get_tdays_per_yr

class TestApiCall(unittest.TestCase):
    def test_count_tdays(self):
        # simple case with missing days b/c weekends
        x1 = ['2019-12-05', '2019-12-10']
        out1_str = ['2019-12-05', '2019-12-06', '2019-12-09', '2019-12-10']
        out1_tday = [0, 1, 2, 3]
        out1 = count_tdays(x=x1)
        self.assertListEqual(out1_str, [str(x.date()) for x in out1.index])
        self.assertListEqual(out1_tday, out1.tday.tolist())

        # multi-year, weekends, holiday
        x2 = ['2018-12-28', '2019-01-02']
        out2_str = ['2018-12-28', '2018-12-31', '2019-01-02']
        out2_tday = [0, 1, 2]
        out2 = count_tdays(x=x2)
        self.assertListEqual(out2_str, [str(x.date()) for x in out2.index])
        self.assertListEqual(out2_tday, out2.tday.tolist())

    def test_get_tdays_per_yr(self):
        x1 = [2018, 2019, 2020]
        out1_dict = {2018: 251, 2019: 252, 2020: 253}
        out1 = get_tdays_per_yr(x=x1)
        self.assertDictEqual(out1_dict, out1)

        x2 = ['2018', '2019', '2020']
        out2_dict = {'2018': 251, '2019': 252, '2020': 253}
        out2 = get_tdays_per_yr(x=x2)
        self.assertDictEqual(out2_dict, out2)

if __name__ == '__main__':
    unittest.main()