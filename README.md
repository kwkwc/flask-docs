# Flask-Docs

> Adds Docs support to Flask.

Features
-----

- Automatic generation of markdown documents
- Support Flask-RESTful

Usage
-----

Here is an example:

```
from flask import Flask
from flask_docs import ApiDoc

app = Flask(__name__)

# Local loading
# app.config['API_DOC_CDN'] = False

# Disable document pages
# app.config['API_DOC_ENABLE'] = False

# Api Document needs to be displayed
app.config['API_DOC_MEMBER'] = ['api', 'platform']

# Restful API documents to be excluded
app.config['RESTFUL_API_DOC_EXCLUDE'] = []

ApiDoc(app)
```

How to add markdown documents to the code:
```
@@@
# Write your markdown document here
@@@
```

# Run in /docs/api

Api and document pages
-----

```
@api.route('/add_data', methods=['POST'])
def add_data():
    """Add some data

    Add some data in this routing

    Args:
        pass

    Returns:
        pass
    """
    return jsonify({'api': 'add data'})
```

![sample_app](flask_docs/assets/sample_app_add.png)

```
@api.route('/del_data', methods=['POST'])
def del_data():
    """Del some data

    @@@
    #### args

    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    title    |    false    |    string   |    blog title    |
    |    name    |    true    |    string   |    person's name    |

    #### return
    - ##### json
    > {"msg": "success", "code": 200}
    @@@
    """
    return jsonify({'api': 'del data'})
```

![sample_app](flask_docs/assets/sample_app_del.png)

```
@platform.route('/get_something', methods=['GET'])
def get_something():
    """
    @@@
    #### example
        import requests
        url='http://127.0.0.1:5000/api/get_something'
        try:
            print requests.get(url).text
        except:
            pass
    @@@
    """
    return jsonify({'platform': 'get something'})
```

![sample_app](flask_docs/assets/sample_app_get.png)

Flask-RESTful Api and document pages
-----

```
from flask_restful import Resource, Api

class TodoList(Resource):
    """Get todolist"""

    def post(self):
        """Submission of data

        Args:
            pass

        Returns:
            pass

        """
        return {'todos': 'post todolist'}

    def get(self):
        """
        @@@
        #### args

        | args | nullable | type | remark |
        |--------|--------|--------|--------|
        |    id    |    false    |    int   |    todo id    |

        #### return
        - ##### json
        > {...}
        @@@
        """
        return {'todos': 'get todolist'}


restful_api.add_resource(TodoList, '/todos')
```

![sample_app](flask_docs/assets/sample_app_restful_post.png)

![sample_app](flask_docs/assets/sample_app_restful_get.png)

Examples
-----

[Complete example][examples]

Installation
-----

`pip install Flask-Docs`

Reference
-----

[falsk_api_doc](https://github.com/tobyqin/flask_api_doc/)

[examples]: https://github.com/kwkwc/flask-docs/tree/master/examples