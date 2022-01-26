#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app restful
Version:
    0.3.8
History:
    Created on 2018/05/20
    Last modified on 2022/01/27
Author:
    kwkw
"""

from flask import Flask
from flask_restful import Api, Resource
from flask_restful.reqparse import RequestParser

from flask_docs import ApiDoc

app = Flask(__name__)

# Using CDN
# app.config["API_DOC_CDN"] = True

# Disable document pages
# app.config["API_DOC_ENABLE"] = False

# SHA256 encrypted authorization password, e.g. here is admin
# echo -n admin | shasum -a 256
# app.config["API_DOC_PASSWORD_SHA2"] = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"

# Methods allowed to be displayed
# app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Custom url_prefix
# app.config["API_DOC_URL_PREFIX"] = "/docs/api"

# RESTful Api class name to exclude
# app.config["API_DOC_RESTFUL_EXCLUDE"] = ["Todo"]

# Auto generating request args markdown
app.config["API_DOC_AUTO_GENERATING_ARGS_MD"] = True

# Disable markdown processing for all documents
# app.config["API_DOC_ALL_MD"] = False

restful_api = Api(app)
ApiDoc(
    app,
    title="Sample App Restful",
    version="1.0.0",
    description="A simple app restful API",
)


class Todo(Resource):
    """Manage todo"""

    def post(self):
        """Add todo

        ### request
        ```json
        {"name": "xx", "type": "code"}
        ```

        ### return
        ```json
        {"code": xxxx, "msg": "xxx", "data": null}
        ```
        """
        parser = RequestParser()
        # fmt: off
        parser.add_argument(
            "name", location="json", type=str, required=True, help="todo name",
        )
        parser.add_argument(
            "type", location="json", type=str, required=True, default="life",
            help="todo type",
        )
        parser.add_argument()
        # fmt: on

        return {"todo": "post todo"}

    def get(self):
        """Get todo

        Extra notes:
        {
            "data":{
                "xx": "xxx"
            }
        }

        @@@
        ### description
        > Get todo

        ### args
        |  args | required | request type | type |  remarks |
        |-------|----------|--------------|------|----------|
        |  name |  true    |    query     | str  | todo name |
        |  type |  false   |    query     | str  | todo type |

        ### request
        ```
        http://127.0.0.1:5000/todo?name=xxx&type=code
        ```

        ### return
        ```json
        {"code": xxxx, "msg": "xxx", "data": null}
        ```
        @@@
        """

        return {"todo": "get todo"}


restful_api.add_resource(Todo, "/todo")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
