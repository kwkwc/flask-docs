#!/usr/bin/env python
# coding=utf8

'''
Program:
    Flask-Docs
Version:
    0.1.5
History:
    Created on 2018/05/20
    Last modified on 2020/09/12
Author:
    kwkw
'''

from flask import Blueprint, current_app, render_template, json, url_for
from flask_restful import Resource
from flask.views import MethodView
import re

CDN_HOST = 'cdn.staticfile.org'
ELEMENT_VERSION = '2.3.8'
VUE_VERSION = '2.5.17-beta.0'
MARKED_VERSION = '0.3.19'
FILE_SAVER_VERSION = '2014-11-29'


class CDN(object):
    def get_resource_url(self, filename):
        raise NotImplementedError


class StaticCDN(object):
    def __init__(self, static_endpoint='static', rev=False):
        self.static_endpoint = static_endpoint
        self.rev = rev

    def get_resource_url(self, filename):
        extra_args = {}

        return url_for(self.static_endpoint, filename=filename, **extra_args)


class WebCDN(object):
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def get_resource_url(self, filename):
        return self.baseurl + filename


class ConditionalCDN(object):
    def __init__(self, confvar, primary, fallback):
        self.confvar = confvar
        self.primary = primary
        self.fallback = fallback

    def get_resource_url(self, filename):
        if not current_app.config[self.confvar]:
            return self.primary.get_resource_url(filename)
        return self.fallback.get_resource_url(filename)


def find_resource(filename, cdn, use_minified=True, local=True):
    if use_minified:
        filename = '%s.min.%s' % tuple(filename.rsplit('.', 1))

    cdns = current_app.extensions['api_doc']['cdns']
    resource_url = cdns[cdn].get_resource_url(filename)

    if resource_url.startswith('//'):
        resource_url = 'https:%s' % resource_url

    return resource_url


class ApiDoc(object):
    NO_DOC = 'No doc found for this Api'
    METHODS_LIST = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

    def __init__(self, app=None, title='Api Doc', version='1.0.0'):
        if app is not None:
            self.init_app(app, title, version)

    def init_app(self, app, title, version):
        app.config.setdefault('API_DOC_MEMBER', [])
        app.config.setdefault('API_DOC_ENABLE', True)
        app.config.setdefault('API_DOC_CDN', False)
        app.config.setdefault('RESTFUL_API_DOC_EXCLUDE', [])

        with app.app_context():
            if current_app.config['API_DOC_ENABLE']:
                api_doc = Blueprint(
                    'api_doc',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    url_prefix='/docs/api')

                app.jinja_env.globals['find_resource'] =\
                    find_resource
                app.jinja_env.add_extension('jinja2.ext.do')

                local = StaticCDN('api_doc.static', rev=True)
                static = StaticCDN()

                def lwrap(cdn, primary=static):
                    return ConditionalCDN('API_DOC_CDN', primary, cdn)

                elementJs = lwrap(WebCDN('//%s/element-ui/%s/' %
                                         (CDN_HOST, ELEMENT_VERSION)), local)

                elementCss = lwrap(
                    WebCDN('//%s/element-ui/%s/theme-chalk/' % (CDN_HOST, ELEMENT_VERSION)), local)

                vue = lwrap(WebCDN('//%s/vue/%s/' %
                                   (CDN_HOST, VUE_VERSION)), local)

                marked = lwrap(WebCDN('//%s/marked/%s/' %
                                      (CDN_HOST, MARKED_VERSION)), local)

                fileSaver = lwrap(WebCDN('//%s/FileSaver.js/%s/' %
                                         (CDN_HOST, FILE_SAVER_VERSION)), local)

                app.extensions['api_doc'] = {
                    'cdns': {
                        'local': local,
                        'static': static,
                        'elementJs': elementJs,
                        'elementCss': elementCss,
                        'vue': vue,
                        'marked': marked,
                        'fileSaver': fileSaver
                    },
                }

                @api_doc.route('/', methods=['GET'])
                def index():

                    dataDict = {}

                    # Restful Api and MethodView Api
                    for c in self.get_all_subclasses(Resource, MethodView):
                        try:
                            dataList = []
                            name = c.__name__.capitalize()
                            if name not in current_app.config['RESTFUL_API_DOC_EXCLUDE']:
                                flag_rule = True
                                for rule in app.url_map.iter_rules():
                                    if (hasattr(c, 'endpoint') and c.endpoint in str(rule.endpoint).split('.')) or (name.lower() in str(rule).lower()):

                                        c_doc = self.get_api_doc(c)

                                        if flag_rule:
                                            try:
                                                if c_doc != ApiDoc.NO_DOC:
                                                    name = name.capitalize() + '(' + c_doc.split('\n\n')[0].split(
                                                        '\n')[0].strip(' ').strip('\n\n').strip(' ').strip('\n').strip(' ') + ')'
                                            except Exception as e:
                                                name = name.capitalize()
                                            flag_rule = False

                                        for m in c.methods:
                                            if m in ApiDoc.METHODS_LIST:
                                                api = {
                                                    'name': '',
                                                    'name_extra': '',
                                                    'url': '',
                                                    'doc': '',
                                                    'doc_md': '',
                                                    'router': name,
                                                    'api_type': 'restful_api'
                                                }

                                                try:
                                                    name_m = m
                                                    url = str(rule)

                                                    result = filter(
                                                        lambda x: x['name'] == name_m, dataList)
                                                    result_list = list(result)
                                                    if len(result_list) > 0:
                                                        result_list[0]['url'] = result_list[0]['url'] + ' ' + url
                                                        result_list[0]['url'] = ' '.join(
                                                            list(set(result_list[0]['url'].split(' '))))
                                                        raise

                                                    api['name'] = name_m
                                                    api['url'] = url

                                                    doc = eval('c.{}.__doc__'.format(
                                                        m.lower())).replace('\t', '    ')

                                                    doc = doc if doc else ApiDoc.NO_DOC

                                                    api['doc'], api['name_extra'], api['doc_md'] = self.get_doc_name_extra_doc_md(
                                                        doc)

                                                except Exception as e:
                                                    pass
                                                else:
                                                    dataList.append(api)

                            if dataList != []:
                                dataList.sort(key=lambda x: x['name'])
                                dataDict[name] = {'children': []}
                                dataDict[name]['children'] = dataList
                        except Exception as e:
                            pass

                    # Api
                    for f in current_app.config['API_DOC_MEMBER']:
                        dataList = []
                        dataDict[f.capitalize()] = {'children': []}
                        for rule in app.url_map.iter_rules():
                            if re.search(r'^/{}/.+'.format(f), str(rule) + '//'):

                                api = {
                                    'name': '',
                                    'name_extra': '',
                                    'url': '',
                                    'method': '',
                                    'doc': '',
                                    'doc_md': '',
                                    'router': f.capitalize(),
                                    'api_type': 'api'
                                }

                                try:
                                    func = app.view_functions[rule.endpoint]

                                    name = self.get_api_name(func)
                                    url = str(rule)
                                    method = ' '.join(
                                        [r for r in rule.methods if r in ApiDoc.METHODS_LIST])

                                    result = filter(
                                        lambda x: x['name'] == name, dataList)
                                    result_list = list(result)
                                    if len(result_list) > 0:
                                        result_list[0]['url'] = result_list[0]['url'] + ' ' + url
                                        result_list[0]['url'] = ' '.join(
                                            list(set(result_list[0]['url'].split(' '))))
                                        result_list[0]['method'] = result_list[0]['method'] + \
                                            ' ' + method
                                        result_list[0]['method'] = ' '.join(
                                            list(set(result_list[0]['method'].split(' '))))
                                        raise

                                    api['name'] = name
                                    api['url'] = url
                                    api['method'] = method

                                    doc = self.get_api_doc(func)

                                    api['doc'], api['name_extra'], api['doc_md'] = self.get_doc_name_extra_doc_md(
                                        doc)

                                except Exception as e:
                                    pass
                                else:
                                    dataList.append(api)
                                    
                        if dataList != []:
                            dataList.sort(key=lambda x: x['name'])
                            dataDict[f.capitalize()]['children'] = dataList
                        else:
                            dataDict.pop(f.capitalize())

                    dataDict = {'data': dataDict}
                    return render_template(
                        'apidoc/api_doc.html', data=json.dumps(dataDict), title=title, version=version, noDocText=ApiDoc.NO_DOC)

                app.register_blueprint(api_doc)

    def get_api_name(self, func):
        """e.g. Convert 'do_work' to 'Do Work'"""

        words = func.__name__.split('_')
        words = [w.capitalize() for w in words]

        return ' '.join(words)

    def get_api_doc(self, func):
        if func.__doc__:
            return func.__doc__.replace('\t', '    ')
        else:
            return ApiDoc.NO_DOC

    def get_doc_name_extra_doc_md(self, doc_src):
        try:
            doc = doc_src.split('@@@')[0]
        except Exception as e:
            doc = ApiDoc.NO_DOC

        if doc != ApiDoc.NO_DOC:
            name_extra = doc.split('\n\n')[0].split('\n')[0].strip(
                ' ').strip('\n\n').strip(' ').strip('\n').strip(' ')
        else:
            name_extra = ''

        doc = doc.replace(name_extra, '', 1).rstrip(' ').strip(
            '\n\n').rstrip(' ').strip('\n').rstrip(' ')

        if doc == '':
            doc = ApiDoc.NO_DOC

        try:
            doc_md = doc_src.split('@@@')[1].strip(' ')
            try:
                space_count = doc_src.split(
                    '@@@')[0].split('\n')[-1].count(' ')
            except Exception as e:
                space_count = 0
            doc_md = '\n'.join(doc_md.split('\n' + ' ' * space_count))
        except Exception as e:
            doc_md = ''

        return doc, name_extra, doc_md

    def get_all_subclasses(self, cls, clsmv=None):
        if clsmv is None:
            clsmv = []
        else:
            clsmv = clsmv.__subclasses__()[1:]
        all_subclasses = []
        for subclass in cls.__subclasses__() + clsmv:
            all_subclasses.append(subclass)
            tmp = self.get_all_subclasses(subclass, None)
            all_subclasses.extend(tmp)

        return all_subclasses
