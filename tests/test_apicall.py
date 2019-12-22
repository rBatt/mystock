import unittest
from unittest.mock import patch

import re
import os

from mystock.apicall import ApiCall

class TestEmployee(unittest.TestCase):

    def setUp(self):
        self.call1 = ApiCall(tckr='ATVI')
        # self.call1.api_key = 'testKey'
        self.call1.keydir = re.sub(r"apikey.txt", "apikey_test.txt", self.call1.keydir)

        self.call2 = ApiCall(tckr='VOO')

    def tearDown(self):
        os.remove(self.call1.keydir)

    @patch('mystock.apicall.input')
    def test_get_key(self, mock_input):
        # test getting user input and writing to file
        mock_input.return_value = "testKey"
        self.assertFalse(os.path.exists(self.call1.keydir)) # test key file should not exist
        self.assertEqual(self.call1._get_key(), 'testKey') # mock prompt for key and retrieval
        self.assertTrue(os.path.exists(self.call1.keydir)) # test that apikey file exists
        self.assertEqual(self.call1._get_key(), 'testKey') # test reading key from file (not the best test, depends on previous 2 ...)


if __name__ == '__main__':
    unittest.main()