#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app restx
Version:
    1.0.2
History:
    Created on 2021/10/17
    Last modified on 2022/01/27
Author:
    kwkw
"""

from flask import Flask
from flask_restx import Api, Resource

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

restx_api = Api(app)
ApiDoc(
    app,
    title="Sample App RESTX",
    version="1.0.0",
    description="A simple app RESTX API",
)


@restx_api.route('/todolist')
class TodoList(Resource):
    """Manage todolist"""

    def put(self):
        """Change the data"""

        return {"todos": "put todolist"}

    def delete(self):
        """Delete the data"""

        return {"todos": "delete todolist"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
