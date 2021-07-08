#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app methodview
Version:
    0.3.1
History:
    Created on 2019/07/15
    Last modified on 2021/07/08
Author:
    kwkw
"""

from flask import Flask, jsonify
from flask.views import MethodView

from flask_docs import ApiDoc

app = Flask(__name__)

# Using CDN
# app.config["API_DOC_CDN"] = True

# Disable document pages
# app.config["API_DOC_ENABLE"] = False

# Methods allowed to be displayed
# app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Custom url_prefix
# app.config["API_DOC_URL_PREFIX"] = "/docs/api"

# RESTful Api documents to be excluded
# app.config["API_DOC_RESTFUL_EXCLUDE"] = ["todolist"]

ApiDoc(app, title="Sample App MethodView", version="1.0.0")


class TodoList(MethodView):
    """Manage todolist"""

    def put(self):
        """Change the data"""

        return jsonify({"todos": "put todolist"})

    def delete(self):
        """Delete the data"""

        return jsonify({"todos": "delete todolist"})


# For the time being, only url_rule with the same class name are supported
app.add_url_rule("/todolist/", view_func=TodoList.as_view("todolist"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
