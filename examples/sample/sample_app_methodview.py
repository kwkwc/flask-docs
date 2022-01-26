#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app methodview
Version:
    0.3.5
History:
    Created on 2019/07/15
    Last modified on 2022/01/27
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

# SHA256 encrypted authorization password, e.g. here is admin
# echo -n admin | shasum -a 256
# app.config["API_DOC_PASSWORD_SHA2"] = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"

# Methods allowed to be displayed
# app.config["API_DOC_METHODS_LIST"] = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Custom url_prefix
# app.config["API_DOC_URL_PREFIX"] = "/docs/api"

# RESTful Api class name to exclude
# app.config["API_DOC_RESTFUL_EXCLUDE"] = ["TodoList"]

# Disable markdown processing for all documents
# app.config["API_DOC_ALL_MD"] = False

ApiDoc(
    app,
    title="Sample App MethodView",
    version="1.0.0",
    description="A simple app MethodView API",
)


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
