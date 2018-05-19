#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask, render_template, jsonify, Blueprint
from flask_docs import ApiDoc

app = Flask(__name__)
app.config['API_DOC_MEMBER'] = ['api']
app.config['API_DOC_ENABLE'] = True
# app.config['API_DOC_CDN'] = False

ApiDoc(app)

api = Blueprint('api', __name__)


@api.route('/get_data', methods=['GET'])
def get_data():
    """Get some data
    
    @@@
    ### args

    | args | nullable | type | remark |
    |--------|--------|--------|--------|
    |    title    |    false    |    string   |    blog title    |
    |    name    |    true    |    string   |    person's name    |

    ##### Returns：
    - ##### json
    > {"msg": "success", "code": 200}
    @@@
    """
    return jsonify({'api': 'get data'})


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


@api.route('/del_data', methods=['GET', 'POST'])
def del_data():
    return jsonify({'api': 'del data'})


app.register_blueprint(api, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
