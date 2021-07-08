#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Flask-Docs
Version:
    0.4.8
History:
    Created on 2018/05/20
    Last modified on 2021/07/08
Author:
    kwkw
"""

import logging
import os
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from flask.views import MethodView
from flask_restful import Resource

from flask_docs.version import __version__

PROJECT_NAME = "Flask-Docs"
PROJECT_VERSION = __version__

logger = logging.getLogger(__name__)


def change_doc(doc_dict):
    logger.warning(
        '{} warning - The "change_doc" decorator is deprecated and scheduled for removal \
            in version 0.5.0. Use the "ApiDoc.change_doc" instead'.format(
            PROJECT_NAME
        )
    )
    return ApiDoc.change_doc(doc_dict)


class ApiDoc(object):
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    APP_TEMPLATES = os.path.join(APP_ROOT, "templates")

    with open(os.path.join(APP_TEMPLATES, "index.html"), "r") as h:
        INDEX_HTML = h.read()
    with open(os.path.join(APP_TEMPLATES, "css_template_cdn.html"), "r") as h:
        CSS_TEMPLATE_CDN = h.read()
    with open(os.path.join(APP_TEMPLATES, "css_template_local.html"), "r") as h:
        CSS_TEMPLATE_LOCAL = h.read()
    with open(os.path.join(APP_TEMPLATES, "js_template_cdn.html"), "r") as h:
        JS_TEMPLATE_CDN = h.read()
    with open(os.path.join(APP_TEMPLATES, "js_template_local.html"), "r") as h:
        JS_TEMPLATE_LOCAL = h.read()

    def __init__(self, app=None, title="Api Doc", version="1.0.0", no_doc_text=""):
        if app is not None:
            self.init_app(app, title, version, no_doc_text)

    def init_app(self, app, title="Api Doc", version="1.0.0", no_doc_text=""):

        app.config.setdefault("API_DOC_CDN_CSS_TEMPLATE", "")
        app.config.setdefault("API_DOC_CDN_JS_TEMPLATE", "")
        app.config.setdefault("API_DOC_URL_PREFIX", "/docs/api")
        app.config.setdefault("API_DOC_NO_DOC_TEXT", "No doc found for this Api")
        app.config.setdefault("API_DOC_ENABLE", True)
        app.config.setdefault("API_DOC_CDN", False)
        app.config.setdefault("API_DOC_MEMBER", [])
        app.config.setdefault("RESTFUL_API_DOC_EXCLUDE", [])
        app.config.setdefault("API_DOC_RESTFUL_EXCLUDE", [])
        app.config.setdefault("METHODS_LIST", [])
        app.config.setdefault(
            "API_DOC_METHODS_LIST", ["GET", "POST", "PUT", "DELETE", "PATCH"]
        )

        with app.app_context():
            self.check_variable_type(
                {"title": title, "version": version, "no_doc_text": no_doc_text},
                str,
            )
            self.check_config_type(
                [
                    "API_DOC_CDN_CSS_TEMPLATE",
                    "API_DOC_CDN_JS_TEMPLATE",
                    "API_DOC_URL_PREFIX",
                    "API_DOC_NO_DOC_TEXT",
                ],
                str,
            )
            self.check_config_type(["API_DOC_ENABLE", "API_DOC_CDN"], bool)
            self.check_config_type(
                [
                    "API_DOC_MEMBER",
                    "RESTFUL_API_DOC_EXCLUDE",
                    "API_DOC_RESTFUL_EXCLUDE",
                    "METHODS_LIST",
                    "API_DOC_METHODS_LIST",
                ],
                list,
            )

            if not current_app.config["API_DOC_ENABLE"]:
                return

            # Will be removed in version 0.5.0
            old_conf_warn_template = '{} warning - The "{{}}" setting is deprecated and scheduled for removal \
                in version 0.5.0. Use the "{{}}" instead'.format(
                PROJECT_NAME
            )

            self.no_doc_text = current_app.config["API_DOC_NO_DOC_TEXT"]
            if no_doc_text:
                self.no_doc_text = no_doc_text
                logger.warning(
                    old_conf_warn_template.format("no_doc_text", "API_DOC_NO_DOC_TEXT")
                )

            self.restful_exclude_list = current_app.config["API_DOC_RESTFUL_EXCLUDE"]
            if current_app.config["RESTFUL_API_DOC_EXCLUDE"]:
                self.restful_exclude_list = current_app.config[
                    "RESTFUL_API_DOC_EXCLUDE"
                ]
                logger.warning(
                    old_conf_warn_template.format(
                        "RESTFUL_API_DOC_EXCLUDE", "API_DOC_RESTFUL_EXCLUDE"
                    )
                )

            self.methods_list = current_app.config["API_DOC_METHODS_LIST"]
            if current_app.config["METHODS_LIST"]:
                self.methods_list = current_app.config["METHODS_LIST"]
                logger.warning(
                    old_conf_warn_template.format(
                        "METHODS_LIST", "API_DOC_METHODS_LIST"
                    )
                )
            # Will be removed in version 0.5.0 end

            api_doc = Blueprint(
                "api_doc",
                __name__,
                static_folder="static",
                url_prefix=current_app.config["API_DOC_URL_PREFIX"],
            )

            @api_doc.route("/", methods=["GET"])
            def index():
                if current_app.config["API_DOC_CDN"]:
                    CSS_TEMPLATE = ApiDoc.CSS_TEMPLATE_CDN
                    JS_TEMPLATE = ApiDoc.JS_TEMPLATE_CDN

                    if current_app.config["API_DOC_CDN_CSS_TEMPLATE"]:
                        CSS_TEMPLATE = current_app.config["API_DOC_CDN_CSS_TEMPLATE"]
                    if current_app.config["API_DOC_CDN_JS_TEMPLATE"]:
                        JS_TEMPLATE = current_app.config["API_DOC_CDN_JS_TEMPLATE"]

                    return ApiDoc.INDEX_HTML.replace(
                        "<!-- ___CSS_TEMPLATE___ -->", CSS_TEMPLATE
                    ).replace("<!-- ___JS_TEMPLATE___ -->", JS_TEMPLATE)
                else:
                    return ApiDoc.INDEX_HTML.replace(
                        "<!-- ___CSS_TEMPLATE___ -->", ApiDoc.CSS_TEMPLATE_LOCAL
                    ).replace("<!-- ___JS_TEMPLATE___ -->", ApiDoc.JS_TEMPLATE_LOCAL)

            @api_doc.route("/data", methods=["GET"])
            def data():

                url_prefix = current_app.config["API_DOC_URL_PREFIX"]
                referer = request.headers.get("referer", "http://127.0.0.1")
                host = referer.split(url_prefix)[0]

                data_dict = {}

                # Restful Api and MethodView Api
                data_dict.update(self.get_restful_methodview_api_data())

                # Api
                data_dict.update(self.get_api_data())

                return jsonify(
                    {
                        "data": data_dict,
                        "title": title,
                        "version": version,
                        "noDocText": self.no_doc_text,
                        "PROJECT_NAME": PROJECT_NAME,
                        "PROJECT_VERSION": PROJECT_VERSION,
                        "host": host,
                    }
                )

            app.register_blueprint(api_doc)

    def get_restful_methodview_api_data(self):
        """Restful Api and MethodView Api"""

        data_dict = {}

        c_dict = {}
        class_name_dict = {}

        for c in self.get_all_subclasses(Resource, MethodView):
            c_dict[c.__name__.lower()] = c
            class_name_dict[c.__name__.lower()] = c.__name__

        for rule in current_app.url_map.iter_rules():
            func = current_app.view_functions[rule.endpoint]
            name = func.__name__

            if name not in c_dict:
                continue

            if name in self.restful_exclude_list:
                continue

            c_doc = self.get_api_doc(func)

            if c_doc != self.no_doc_text:
                name = "{}({})".format(class_name_dict[name], self.clean_doc(c_doc))

            if func.methods is None:
                continue

            if name not in data_dict:
                data_dict[name] = {"children": []}

            for m in func.methods:
                if m not in self.methods_list:
                    continue

                api = {
                    "name": "",
                    "name_extra": "",
                    "url": "",
                    "doc": "",
                    "doc_md": "",
                    "router": name,
                    "api_type": "restful_api",
                }

                try:
                    name_m = m
                    url = str(rule)

                    result = filter(
                        lambda x: x["name"] == name_m,
                        data_dict[name]["children"],
                    )
                    result_list = list(result)
                    if len(result_list) > 0:
                        result_list[0]["url"] = result_list[0]["url"] + " " + url
                        result_list[0]["url"] = " ".join(
                            list(set(result_list[0]["url"].split(" ")))
                        )
                        raise RuntimeError

                    api["name"] = name_m
                    api["url"] = url

                    doc = eval(
                        "c_dict[func.__name__].{}.__doc__".format(m.lower())
                    ).replace("\t", "    ")

                    doc = doc if doc else self.no_doc_text

                    (
                        api["doc"],
                        api["name_extra"],
                        api["doc_md"],
                    ) = self.get_doc_name_extra_doc_md(doc)

                except Exception as e:
                    logger.exception("{} error - {}".format(PROJECT_NAME, e))
                else:
                    data_dict[name]["children"].append(api)

            if data_dict[name]["children"] == []:
                data_dict.pop(name)
            else:
                data_dict[name]["children"].sort(key=lambda x: x["name"])

        return data_dict

    def get_api_data(self):
        """Api"""

        data_dict = {}

        for rule in current_app.url_map.iter_rules():
            f = str(rule).split("/")[1]
            if f not in current_app.config["API_DOC_MEMBER"]:
                continue

            f_capitalize = f.capitalize()

            if f_capitalize not in data_dict:
                data_dict[f_capitalize] = {"children": []}

            api = {
                "name": "",
                "name_extra": "",
                "url": "",
                "method": "",
                "doc": "",
                "doc_md": "",
                "router": f_capitalize,
                "api_type": "api",
            }

            try:
                func = current_app.view_functions[rule.endpoint]

                name = self.get_api_name(func)
                url = str(rule)
                method = " ".join([r for r in rule.methods if r in self.methods_list])
                if method:
                    url = "{}\t[{}]".format(url, "\t".join(method.split(" ")))

                result = filter(
                    lambda x: x["name"] == name,
                    data_dict[f_capitalize]["children"],
                )
                result_list = list(result)
                if len(result_list) > 0:
                    result_list[0]["url"] = result_list[0]["url"] + " " + url
                    result_list[0]["url"] = " ".join(
                        list(set(result_list[0]["url"].split(" ")))
                    )
                    result_list[0]["method"] = result_list[0]["method"] + " " + method
                    result_list[0]["method"] = " ".join(
                        list(set(result_list[0]["method"].split(" ")))
                    )
                    raise RuntimeError

                api["name"] = name
                api["url"] = url
                api["method"] = method

                doc = self.get_api_doc(func)

                (
                    api["doc"],
                    api["name_extra"],
                    api["doc_md"],
                ) = self.get_doc_name_extra_doc_md(doc)

            except Exception as e:
                logger.exception("{} error - {}".format(PROJECT_NAME, e))
            else:
                data_dict[f_capitalize]["children"].append(api)

            if data_dict[f_capitalize]["children"] == []:
                data_dict.pop(f_capitalize)
            else:
                data_dict[f_capitalize]["children"].sort(key=lambda x: x["name"])

        return data_dict

    def get_api_name(self, func):
        words = func.__name__.split("_")
        words = [w.capitalize() for w in words]

        return " ".join(words)

    def get_api_doc(self, func):
        if func.__doc__:
            return func.__doc__.replace("\t", "    ")
        else:
            return self.no_doc_text

    def clean_doc(self, doc_src):
        return (
            doc_src.split("\n\n")[0]
            .split("\n")[0]
            .strip(" ")
            .strip("\n\n")
            .strip(" ")
            .strip("\n")
            .strip(" ")
        )

    def get_doc_name_extra_doc_md(self, doc_src):
        doc = doc_src.split("@@@")[0]

        if doc != self.no_doc_text:
            name_extra = self.clean_doc(doc)
        else:
            name_extra = ""

        doc = (
            doc.replace(name_extra, "", 1)
            .rstrip(" ")
            .strip("\n\n")
            .rstrip(" ")
            .strip("\n")
            .rstrip(" ")
        )

        if doc == "":
            doc = self.no_doc_text

        if len(doc_src.split("@@@")) >= 2:
            doc_md = doc_src.split("@@@")[1].strip(" ")
            space_count = doc_src.split("@@@")[0].split("\n")[-1].count(" ")
            doc_md = "\n".join(doc_md.split("\n" + " " * space_count))
        else:
            doc_md = ""

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

    def check_variable_type(self, variable_dict, type):
        for k in variable_dict:
            if not isinstance(variable_dict[k], type):
                raise ValueError(
                    "{} is the incorrect type of value, the correct type is {}".format(
                        k, type
                    )
                )

    def check_config_type(self, config_list, type):
        for c in config_list:
            if not isinstance(current_app.config[c], type):
                raise ValueError(
                    "{} is the incorrect type of value, the correct type is {}".format(
                        c, type
                    )
                )

    @staticmethod
    def change_doc(doc_dict):
        def decorator(func):
            doc = func.__doc__
            for k in doc_dict:
                doc = doc.replace(k, doc_dict[k])
            func.__doc__ = doc

            @wraps(func)
            def decorated_function(*args, **kw):
                return func(*args, **kw)

            return decorated_function

        return decorator
