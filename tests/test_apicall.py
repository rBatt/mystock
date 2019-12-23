import unittest
from unittest.mock import patch

import re
import os

from mystock.apicall import ApiCall

class TestEmployee(unittest.TestCase):

    def setUp(self):
        self.call1 = ApiCall()
        # self.call1.api_key = 'testKey'
        self.call1.keyfile = re.sub(r"apikey.txt", "apikey_test.txt", self.call1.keyfile)

        self.call2 = ApiCall()

    def tearDown(self):
        os.remove(self.call1.keyfile)

    @patch('mystock.apicall.input')
    def test_get_key(self, mock_input):
        # test getting user input and writing to file
        mock_input.return_value = "testKey"
        self.assertFalse(os.path.exists(self.call1.keyfile)) # test key file should not exist
        self.assertEqual(self.call1._get_key(), 'testKey') # mock prompt for key and retrieval
        self.assertTrue(os.path.exists(self.call1.keyfile)) # test that apikey file exists
        self.assertEqual(self.call1._get_key(), 'testKey') # test reading key from file (not the best test, depends on previous 2 ...)


if __name__ == '__main__':
    unittest.main()