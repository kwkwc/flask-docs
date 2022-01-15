#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case config fail
Version:
    0.0.1
History:
    Created on 2022/01/16
    Last modified on 2022/01/16
Author:
    kwkw
"""


import sys

sys.path.append(".")

import unittest

from flask import Flask

from flask_docs import ApiDoc

app = Flask(__name__)
app.config["API_DOC_ENABLE"] = "true"

apidoc = ApiDoc(title="Test App")


class ConfigTestCase(unittest.TestCase):
    def test_api_config_fail(self):

        try:
            apidoc.init_app(app)
        except ValueError as e:
            self.assertEqual(type(e), ValueError)


if __name__ == "__main__":
    unittest.main()
