#!/usr/bin/env python
# coding=utf8

'''
Program:
    Test case
Version:
    0.0.1
History:
    Created on 2020/10/18
    Last modified on 2020/10/18
Author:
    kwkw
'''


import sys
sys.path.append('.')

import unittest
from flask import Flask
from flask_docs import ApiDoc


class AcceptTestCase(unittest.TestCase):

    def test_accept_docs_api(self):

        app = Flask(__name__)
        ApiDoc(app, title='Test App')

        with app.test_client() as client:
            res = client.get('/docs/api/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/html; charset=utf-8')


if __name__ == '__main__':
    unittest.main()
