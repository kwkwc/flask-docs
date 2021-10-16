#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case disable
Version:
    0.0.1
History:
    Created on 2021/10/17
    Last modified on 2021/10/17
Author:
    kwkw
"""


import sys

sys.path.append(".")

import unittest

from flask import Flask

from flask_docs import ApiDoc

app = Flask(__name__)
app.config["API_DOC_ENABLE"] = False
ApiDoc(app, title="Test App")


class AcceptTestCase(unittest.TestCase):
    def test_accept_docs_api(self):

        with app.test_client() as client:
            res = client.get("/docs/api/")
            self.assertEqual(res.status_code, 404)
            self.assertEqual(res.content_type, "text/html; charset=utf-8")


if __name__ == "__main__":
    unittest.main()
