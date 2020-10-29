#!/usr/bin/env python
# coding=utf8

'''
Program:
    Test case
Version:
    0.0.3
History:
    Created on 2020/10/18
    Last modified on 2020/10/29
Author:
    kwkw
'''


import sys
sys.path.append('.')

import unittest
from flask import Flask, Blueprint
from flask_restful import Resource, Api
from flask_docs import ApiDoc


app = Flask(__name__)
app.config['API_DOC_MEMBER'] = ['api']
ApiDoc(app, title='Test App')


class AcceptTestCase(unittest.TestCase):

    def test_accept_docs_api(self):

        with app.test_client() as client:
            res = client.get('/docs/api/')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'text/html; charset=utf-8')

    def test_accept_docs_api_data(self):

        with app.test_client() as client:
            res = client.get('/docs/api/data')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


class RestfulApiTestRoute(Resource):
    pass


class TodoList(RestfulApiTestRoute):
    """Manage todolist"""

    def post(self):
        """Submission of data"""
        pass

    def get(self):
        """
        @@@
        ### markdown
        @@@
        """
        pass


class TodoListNone(RestfulApiTestRoute):
    pass


class CoverageTestCase(unittest.TestCase):

    def test_api_route_coverage(self):

        api = Blueprint('api', __name__)

        @api.route('/add_data', methods=['POST'])
        @api.route('/post_data', methods=['POST', 'PUT'])
        def add_data():
            pass

        app.register_blueprint(api, url_prefix='/api')

        with app.test_client() as client:
            res = client.get('/docs/api/data')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')

    def test_restful_api_route_coverage(self):

        restful_api = Api(app)
        restful_api.add_resource(TodoList, '/todolist', '/todo')
        restful_api.add_resource(TodoListNone, '/todolist_none')

        with app.test_client() as client:
            res = client.get('/docs/api/data')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.content_type, 'application/json')


if __name__ == '__main__':
    unittest.main()
