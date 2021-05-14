#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app restful methodview
Version:
    0.2.8
History:
    Created on 2018/05/20
    Last modified on 2021/05/15
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

# Allowed method
# app.config["METHODS_LIST"] = ["GET", "POST", "PUT", "DELETE", "PATCH"]

# Custom url_prefix
# app.config["API_DOC_URL_PREFIX"] = "/docs/api"

# RESTful Api documents to be excluded
app.config["RESTFUL_API_DOC_EXCLUDE"] = []

ApiDoc(app, title="Sample App Restful Methodview", version="1.0.0")


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
