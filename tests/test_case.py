#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Test case
Version:
    0.1.8
History:
    Created on 2020/10/18
    Last modified on 2023/02/21
Author:
    kwkw
"""


import os
import sys

sys.path.append(".")

import shutil
import unittest

from flask import Blueprint, Flask
from flask_restful import Api, Resource
from flask_restful.inputs import int_range
from flask_restful.reqparse import RequestParser
from flask_restx import Api as RestxApi
from flask_restx import Resource as RestxResource
from flask_restx.reqparse import RequestParser as RestxRequestParser

from flask_docs import ApiDoc

app = Flask(__name__)
app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "DELETE"]
app.config["API_DOC_MEMBER"] = ["api", "platform", "callback"]
app.config["API_DOC_MEMBER_SUB_EXCLUDE"] = ["add_data"]
app.config["API_DOC_RESTFUL_EXCLUDE"] = ["TodoListExclude"]
app.config["API_DOC_AUTO_GENERATING_ARGS_MD"] = True
ApiDoc(app, title="Test App")


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


# Flask-Restful
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

restful_api = Api(app)
restful_api.add_resource(TodoList, "/todolist", "/todo")
restful_api.add_resource(TodoListNone, "/todolist_none")
restful_api.add_resource(TodoListNoneMethod, "/todolist_none_method")
restful_api.add_resource(TodoListExclude, "/todolist_exclude")

todo = TodoList()
todo.get()
# Flask-Restful end

# Flask-Restx
restx_api = RestxApi(app)
ns = restx_api.namespace("sample", description="Sample RESTX API")

RestxParser = RestxRequestParser()
# fmt: off
RestxParser.add_argument(
    "name", location="json", type=str, required=True, help="todo name",
)
# fmt: on


@restx_api.route("/todolistrestx")
class TodoListRestx(RestxResource):
    @ns.expect(RestxParser)
    def post(self):
        return {"todos": "post todolistrestx"}

    @ns.expect(())
    def get(self):
        return {"todos": "get todolistrestx"}


# Flask-Restx end


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


class CoverageTestCase(unittest.TestCase):
    def test_api_route_coverage(self):
        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")
            self.assertNotEqual(res.json["data"], {})

    def test_restful_api_route_coverage(self):
        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")

    def test_restx_api_route_coverage(self):
        with app.test_client() as client:
            res = client.get("/docs/api/data")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, "application/json")

    def test_offline_html_doc(self):
        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "html"])
        assert result.exit_code == 0
        assert "index.html" in os.listdir("htmldoc")

        shutil.rmtree("htmldoc")

    def test_offline_html_doc_out(self):
        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "html", "--out", "htmldoc2"])
        assert result.exit_code == 0
        assert "index.html" in os.listdir("htmldoc2")

        shutil.rmtree("htmldoc2")

    def test_offline_html_doc_out_short_mode(self):
        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "html", "-o", "htmldoc2"])
        assert result.exit_code == 0
        assert "index.html" in os.listdir("htmldoc2")

        shutil.rmtree("htmldoc2")

    def test_offline_html_doc_should_error_when_exists(self):
        runner = app.test_cli_runner()
        os.mkdir("htmldoc_exists")

        result = runner.invoke(args=["docs", "html", "-o", "htmldoc_exists"])

        assert (
            "Target `htmldoc_exists` exists, use -f or --force to override."
            == result.output.strip()
        )
        assert result.exit_code == 1
        shutil.rmtree("htmldoc_exists")

    def test_offline_html_doc_should_override_when_use_force(self):
        runner = app.test_cli_runner()
        os.mkdir("htmldoc_exists2")

        result = runner.invoke(
            args=["docs", "html", "-o", "htmldoc_exists2", "--force"]
        )

        assert result.exit_code == 0
        assert "index.html" in os.listdir("htmldoc_exists2")

        shutil.rmtree("htmldoc_exists2")

    def test_offline_markdown_doc(self):
        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "markdown"])

        assert result.exit_code == 0
        assert "doc.md" in os.listdir(".")

        shutil.os.remove("doc.md")

    def test_offline_markdown_doc_out(self):
        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "markdown", "--out", "doc2.md"])

        assert result.exit_code == 0
        assert "doc2.md" in os.listdir(".")

        shutil.os.remove("doc2.md")

    def test_offline_markdown_doc_should_error_when_exists(self):
        open("doc_exists.md", "w")

        runner = app.test_cli_runner()
        result = runner.invoke(args=["docs", "markdown", "-o", "doc_exists.md"])

        assert (
            "Target `doc_exists.md` exists, use -f or --force to override."
            == result.output.strip()
        )
        assert result.exit_code == 1

        shutil.os.remove("doc_exists.md")

    def test_offline_markdown_doc_should_override_when_use_force(self):
        open("doc_exists2.md", "w")

        runner = app.test_cli_runner()
        result = runner.invoke(
            args=["docs", "markdown", "-o", "doc_exists2.md", "--force"]
        )

        assert result.exit_code == 0
        assert "doc_exists2.md" in os.listdir(".")

        shutil.os.remove("doc_exists2.md")


if __name__ == "__main__":
    unittest.main()
