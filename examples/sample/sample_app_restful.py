#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app restful
Version:
    0.2.5
History:
    Created on 2018/05/20
    Last modified on 2021/04/17
Author:
    kwkw
"""

from flask import Flask
from flask_restful import Api, Resource

from flask_docs import ApiDoc

app = Flask(__name__)

# Using CDN
# app.config["API_DOC_CDN"] = True

# Disable document pages
# app.config["API_DOC_ENABLE"] = False

# RESTful Api documents to be excluded
app.config["RESTFUL_API_DOC_EXCLUDE"] = []

restful_api = Api(app)
ApiDoc(app, title="Sample App Restful", version="1.0.0")


class TodoList(Resource):
    """Manage todolist"""

    def post(self):
        """Submission of data

        Args:
            pass

        Returns:
            pass

        """
        return {"todos": "post todolist"}

    def get(self):
        """
        @@@
        ### args

        | args | nullable | type | remark |
        |--------|--------|--------|--------|
        |    id    |    false    |    int   |    todo id    |

        ### return
        - #### json
        > {......}
        @@@
        """
        return {"todos": "get todolist"}


restful_api.add_resource(TodoList, "/todolist")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
