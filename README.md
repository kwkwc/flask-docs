# Flask-Docs

[![build](https://github.com/kwkwc/flask-docs/actions/workflows/python-build.yml/badge.svg)](https://github.com/kwkwc/flask-docs/actions/workflows/python-build.yml)
[![test](https://github.com/kwkwc/flask-docs/actions/workflows/python-test.yml/badge.svg)](https://github.com/kwkwc/flask-docs/actions/workflows/python-test.yml)
[![codecov](https://codecov.io/gh/kwkwc/flask-docs/branch/master/graph/badge.svg?token=EV69K9WPJ0)](https://codecov.io/gh/kwkwc/flask-docs)
[![PyPI](https://img.shields.io/pypi/v/Flask-Docs)](https://pypi.org/project/Flask-Docs/)

> Adds Docs support to Flask.

[简体中文](README.zh-CN.md)

## Features

- Automatic generation of markdown documentation
- Support for generating offline documentation
- Support Flask-RESTful
- Support Flask-RESTX
- Support flask.views.MethodView
- Support online debugging

## Installation

`pip3 install Flask-Docs`

## Usage

```python
from flask import Flask
from flask_docs import ApiDoc

app = Flask(__name__)


ApiDoc(
    app,
    title="Sample App",
    version="1.0.0",
    description="A simple app API",
)
```

## Configuration

```python
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

# Name of the Api blueprint to be displayed
# app.config["API_DOC_MEMBER"] = ["api", "platform"]

# Name of the Submembers Api function to be excluded
# app.config["API_DOC_MEMBER_SUB_EXCLUDE"] = ["delete_data"]

# Auto generating request args markdown
# app.config["API_DOC_AUTO_GENERATING_ARGS_MD"] = True

# Disable markdown processing for all documents
# app.config["API_DOC_ALL_MD"] = False
```

## Tag @@@

```
# Process all documents in markdown by default
# 1. use the `@@@` wrapper if you want to specify processing
# 2. Turn off `API_DOC_ALL_MD` and remove the `@@@` tag if you want to display the original document

@@@
# Write your markdown document here
@@@
```

## View the documentation page

```
http://127.0.0.1/docs/api/
```

## Api and document pages

````python
@api.route("/add_data", methods=["POST"])
def add_data():
    """Add some data

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
    """
    return jsonify({"api": "add data"})


app.register_blueprint(api, url_prefix="/api")
````

![sample_app](flask_docs/assets/sample_app_add.png)

````python
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


app.register_blueprint(api, url_prefix="/api")
````

![sample_app](flask_docs/assets/sample_app_delete.png)

````python
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


app.register_blueprint(platform, url_prefix="/platform")
````

![sample_app](flask_docs/assets/sample_app_get.png)

## Flask-RESTful Api and document pages

````python
from flask_restful import Resource, Api

class Todo(Resource):
    """Manage todo"""

    def post(self):
        """Add todo

        @@@
        ### description
        > Add todo

        ### args
        |  args | required | request type | type |  remarks |
        |-------|----------|--------------|------|----------|
        |  name |  true    |    body      | str  | todo name |
        |  type |  true    |    body      | str  | todo type |

        ### request
        ```json
        {"name": "xx", "type": "code"}
        ```

        ### return
        ```json
        {"code": xxxx, "msg": "xxx", "data": null}
        ```
        @@@
        """

        return {"todo": "post todo"}

    def get(self):
        """Get todo

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


restful_api = Api(app)
restful_api.add_resource(Todo, "/todo")
````

![sample_app](flask_docs/assets/sample_app_restful_post.png)

![sample_app](flask_docs/assets/sample_app_restful_get.png)

## flask.views.MethodView Api

> **_For the time being, only url_rule with the same class name are supported_**

```python
from flask.views import MethodView

class TodoList(MethodView):
    """Manage todolist"""

    def put(self):
        """Change the data"""

        return jsonify({"todos": "put todolist"})

    def delete(self):
        """Delete the data"""

        return jsonify({"todos": "delete todolist"})


app.add_url_rule("/todolist/", view_func=TodoList.as_view("todolist"))
```

## Decorator @ApiDoc.change_doc

> Reuse comments

````python
from flask_docs import ApiDoc

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
````

## Debugger

![debugger](flask_docs/assets/debugger.png)

## Examples

[Complete example][examples]

## Thanks

[flask_api_doc](https://github.com/tobyqin/flask_api_doc/)

[Flask-Bootstrap](https://github.com/mbr/flask-bootstrap/)

[github-markdown-css](https://github.com/sindresorhus/github-markdown-css/)

[Bytesize Icons](https://github.com/danklammer/bytesize-icons/)

[RESTClient](https://github.com/chao/RESTClient/)

[examples]: https://github.com/kwkwc/flask-docs/tree/master/examples
