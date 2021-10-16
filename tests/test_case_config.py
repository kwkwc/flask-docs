#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case config
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
app.config["API_DOC_CDN"] = True
app.config["API_DOC_CDN_CSS_TEMPLATE"] = "test_css"
app.config["API_DOC_CDN_JS_TEMPLATE"] = "test_js"
app.config[
    "API_DOC_PASSWORD_SHA2"
] = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
ApiDoc(app, title="Test App")


class AcceptTestCase(unittest.TestCase):
    def test_accept_docs_api(self):

        with app.test_client() as client:
            res = client.get("/docs/api/")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "text/html; charset=utf-8")

    def test_accept_docs_api_data(self):

        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 401)
            self.assertEqual(res.content_type, "application/json")


class CoverageTestCase(unittest.TestCase):
    def test_api_route_coverage(self):

        with app.test_client() as client:
            res = client.get(
                "/docs/api/data",
                headers={
                    "Auth-Password-SHA2": "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"
                },
            )
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
