#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Sample app
Version:
    0.3.6
History:
    Created on 2018/05/20
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

# Name of the Api blueprint to be displayed
app.config["API_DOC_MEMBER"] = ["api", "platform"]

# Name of the Submembers Api function to be excluded
# app.config["API_DOC_MEMBER_SUB_EXCLUDE"] = ["delete_data"]

# Disable markdown processing for all documents
# app.config["API_DOC_ALL_MD"] = False

ApiDoc(
    app,
    title="Sample App",
    version="1.0.0",
    description="A simple app API",
)

api = Blueprint("api", __name__)
platform = Blueprint("platform", __name__)


@api.route("/add_data", methods=["POST"])
def add_data():
    """Add some data

    @@@
    ### args
    |  args | required | request type | type |  remarks |
    |-------|----------|--------------|------|----------|
    | title |  true    |    body      | str  | blog title    |
    | name  |  true    |    body      | str  | person's name |

    ### request
    ```json
    {"title": "xxx", "name": "xxx"}
    ```

    ### return
    ```json
    {"code": xxxx, "msg": "xxx", "data": null}
    ```
    @@@
    """
    return jsonify({"api": "add data"})


@api.route("/delete_data", methods=["GET"])
def delete_data():
    """Delete some data

    @@@
    ### args
    |  args  | required | request type | type |  remarks     |
    |--------|----------|--------------|------|--------------|
    |  id    |  false   |    query     |  str | blog id    |
    |  name  |  true    |    query     |  str | person's name |

    ### request
    ```
    http://127.0.0.1:5000/api/delete_data?name=xxx
    ```

    ### return
    ```json
    {"code": xxxx, "msg": "xxx", "data": null}
    ```
    @@@
    """

    return jsonify({"api": "delete data"})


@platform.route("/get_something", methods=["GET"])
def get_something():
    """Get some data

    @@@
    ### request example
    ```python
    import requests
    url="http://127.0.0.1:5000/platform/get_something"
    try:
        print(requests.get(url).text)
    except:
        pass
    ```

    ### return
    ```json
    {"code": xxxx, "msg": "xxx", "data": null}
    ```
    @@@
    """

    return jsonify({"platform": "get something"})


app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(platform, url_prefix="/platform")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
