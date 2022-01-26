#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case
Version:
    0.1.3
History:
    Created on 2020/10/18
    Last modified on 2022/01/27
Author:
    kwkw
"""


import sys

sys.path.append(".")

import unittest

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser
from flask_restful.inputs import int_range

from flask_docs import ApiDoc

app = Flask(__name__)
app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "DELETE"]
app.config["API_DOC_MEMBER"] = ["api", "platform", "callback"]
app.config["API_DOC_MEMBER_SUB_EXCLUDE"] = ["add_data"]
app.config["API_DOC_RESTFUL_EXCLUDE"] = ["TodoListExclude"]
app.config["API_DOC_AUTO_GENERATING_ARGS_MD"] = True
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

    TODO_NUMBER_MIN = 1

    def post(self):
        """Submission of data

        Extra notes:
        {
            "data":{
                "xx": "xxx"
            }
        }
        """

        parser = RequestParser()
        # fmt: off
        parser.add_argument(
            "name", location="json", type=str, required=True, help="todo name",
        )
        parser.add_argument(
            "type", location="json", type=str, required=True, choices=["life", "job"],
            default="life", help="todo type",
        )
        parser.add_argument(
            "number", location="json", type=int_range(TodoList.TODO_NUMBER_MIN, 9),
            required=True, help="todo number",
        )
        parser.add_argument()
        # fmt: on

        pass

    @ApiDoc.change_doc({"markdown": "json"})
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
    def get(self):
        pass


class CoverageTestCase(unittest.TestCase):
    def test_api_route_coverage(self):

        api = Blueprint("api", __name__)
        callback = Blueprint("callback", __name__)

        @api.route("/add_data", methods=["POST", "PATCH"])
        @api.route("/post_data", methods=["POST", "PUT"])
        def add_data():
            pass

        @api.route("/delete_data", methods=["DELETE"])
        def delete_data():
            pass

        @callback.route("/change_data", methods=["PUT"])
        def change_data():
            pass

        app.register_blueprint(api, url_prefix="/api")
        app.register_blueprint(callback, url_prefix="/callback")

        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")
            self.assertNotEqual(res.json["data"], {})

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
