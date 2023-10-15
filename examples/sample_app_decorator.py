#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app decorator
Version:
    1.0.5
History:
    Created on 2021/05/15
    Last modified on 2022/01/27
Author:
    kwkw
"""

from flask import Blueprint, Flask, jsonify

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

# Api Document needs to be displayed
app.config["API_DOC_MEMBER"] = ["api"]

# Disable markdown processing for all documents
# app.config["API_DOC_ALL_MD"] = False

ApiDoc(
    app,
    title="Sample App",
    version="1.0.0",
    description="A simple app decorator demo",
)

api = Blueprint("api", __name__)

return_json_str = '{"code": xxxx, "msg": "xxx", "data": null}'


@api.route("/add_data", methods=["POST"])
@ApiDoc.change_doc({"return_json": return_json_str})
def add_data():
    """Add some data

    @@@
    ### return
    ```json
    return_json
    ```
    @@@
    """
    return jsonify({"api": "add data"})


@api.route("/delete_data", methods=["GET"])
@ApiDoc.change_doc({"return_json": return_json_str})
def delete_data():
    """Delete some data

    return_json
    """

    return jsonify({"api": "delete data"})


app.register_blueprint(api, url_prefix="/api")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
