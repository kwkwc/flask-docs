#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case
Version:
    0.0.8
History:
    Created on 2020/10/18
    Last modified on 2021/05/24
Author:
    kwkw
"""


import sys

sys.path.append(".")

import unittest

from flask import Blueprint, Flask
from flask_restful import Api, Resource

from flask_docs import ApiDoc, change_doc

app = Flask(__name__)
app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "DELETE"]
app.config["API_DOC_MEMBER"] = ["api", "platform"]
app.config["API_DOC_RESTFUL_EXCLUDE"] = ["todolistexclude"]
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
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")


class RestfulApiTestRoute(Resource):
    pass


class TodoList(RestfulApiTestRoute):
    """Manage todolist"""

    def post(self):
        """Submission of data"""
        pass

    @change_doc({"markdown": "json"})
    def get(self):
        """
        @@@
        ### markdown
        @@@
        """
        pass


class TodoListNone(RestfulApiTestRoute):
    pass


class TodoListNoneMethod(RestfulApiTestRoute):
    def put(self):
        pass


class TodoListExclude(RestfulApiTestRoute):
    pass


class CoverageTestCase(unittest.TestCase):
    def test_api_route_coverage(self):

        api = Blueprint("api", __name__)

        @api.route("/add_data", methods=["POST", "PATCH"])
        @api.route("/post_data", methods=["POST", "PUT"])
        def add_data():
            pass

        app.register_blueprint(api, url_prefix="/api")

        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")

    def test_restful_api_route_coverage(self):

        restful_api = Api(app)
        restful_api.add_resource(TodoList, "/todolist", "/todo")
        restful_api.add_resource(TodoListNone, "/todolist_none")
        restful_api.add_resource(TodoListNoneMethod, "/todolist_none_method")
        restful_api.add_resource(TodoListExclude, "/todolist_exclude")

        todo = TodoList()
        todo.get()

        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")


if __name__ == "__main__":
    unittest.main()
