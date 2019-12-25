import unittest
from unittest.mock import patch
from unittest.mock import PropertyMock

import re
import os
from pandas.util.testing import assert_frame_equal

from mystock.apicall import ApiCall

class TestApiCall(unittest.TestCase):

    def setUp(self):
        self.input_patch = patch('mystock.apicall.input')
        self.input_mock = self.input_patch.start()
        self.input_mock.return_value = "testKey"

        self.call1 = ApiCall("historical")
        self.call1.keyfile = re.sub(r"apikey.txt", "apikey_test.txt", self.call1.keyfile)

    def tearDown(self):
        os.remove(self.call1.keyfile)
        self.input_patch.stop()

    def test_get_key(self):
        self.assertFalse(os.path.exists(self.call1.keyfile)) # test key file should not exist
        self.assertEqual(self.call1._get_key(), 'testKey') # mock prompt for key and retrieval
        self.assertTrue(os.path.exists(self.call1.keyfile)) # test that apikey file exists
        self.assertEqual(self.call1._get_key(), 'testKey') # test reading key from file (not the best test, depends on previous 2 ...)

    def test_form_api_call(self):
        opts = {
            "symbol": 'VOO'
            , "date_from": "2019-12-05"
            , "date_to": "2019-12-05"
        }
        expected_call = """https://api.worldtradingdata.com/api/v1/history?symbol=VOO&api_token=testKey&date_from=2019-12-05&date_to=2019-12-05&sort=oldest&output=json&formatted=true"""
        api_call = self.call1._form_api_call(options=opts)
        self.assertEqual(api_call, expected_call)

    @patch('mystock.apicall.requests.get')
    def test_execute_call(self, mock_get):
        def get_history_example(eg_file='example_history_multiday.json'):
            path_pieces = (
                os.path.dirname(__file__)
                , '..'
                , 'static'
            )
            file_history_multiday = os.path.join(*path_pieces, eg_file)
            with open(file_history_multiday) as f:
                history_multiday = f.read()
            return history_multiday

        mock_get.return_value.text = get_history_example()
        out1 = self.call1.execute_call(options={'symbol':'asdf'}, output='raw')
        self.assertEqual(out1.text, get_history_example())

        out2 = self.call1.execute_call(options={'symbol':'asdf'}, output='df')
        df2 = self.call1._format_call_history(get_history_example())
        self.assertIsNone(assert_frame_equal(out2, df2)) # if pandas test passes, returns None, otherwise raises exception


if __name__ == '__main__':
    unittest.main()