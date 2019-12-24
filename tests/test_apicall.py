import unittest
from unittest.mock import patch

import re
import os

from mystock.apicall import ApiCall

class TestApiCall(unittest.TestCase):

    def setUp(self):
        self.input_patch = patch('mystock.apicall.input')
        self.input_mock = self.input_patch.start()
        self.input_mock.return_value = "testKey"

        self.call1 = ApiCall()
        self.call1.keyfile = re.sub(r"apikey.txt", "apikey_test.txt", self.call1.keyfile)

        self.call2 = ApiCall()

    def tearDown(self):
        os.remove(self.call1.keyfile)
        self.input_patch.stop()

    def test_get_key(self):
        self.assertFalse(os.path.exists(self.call1.keyfile)) # test key file should not exist
        self.assertEqual(self.call1._get_key(), 'testKey') # mock prompt for key and retrieval
        self.assertTrue(os.path.exists(self.call1.keyfile)) # test that apikey file exists
        self.assertEqual(self.call1._get_key(), 'testKey') # test reading key from file (not the best test, depends on previous 2 ...)


if __name__ == '__main__':
    unittest.main()