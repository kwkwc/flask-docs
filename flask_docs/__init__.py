#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Flask-Docs
Version:
    0.6.4
History:
    Created on 2018/05/20
    Last modified on 2022/01/16
Author:
    kwkw
"""

import copy
import inspect
import logging
import os
from collections import OrderedDict
from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from flask_docs.version import __version__

PROJECT_NAME = "Flask-Docs"
PROJECT_VERSION = __version__

logger = logging.getLogger(__name__)


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

    LOCATIONS = {
        "args": "query",
        "form": "formData",
        "headers": "header",
        "json": "body",
        "values": "query",
        "files": "formData",
    }

    PY_TYPES = {
        int: "integer",
        str: "string",
        bool: "boolean",
        float: "number",
    }

    def __init__(self, app=None, title="Api Doc", version="1.0.0", description=""):
        if app is not None:
            self.init_app(app, title, version, description)

    def init_app(self, app, title="Api Doc", version="1.0.0", description=""):

        app.config.setdefault("API_DOC_CDN_CSS_TEMPLATE", "")
        app.config.setdefault("API_DOC_CDN_JS_TEMPLATE", "")
        app.config.setdefault("API_DOC_URL_PREFIX", "/docs/api")
        app.config.setdefault(
            "API_DOC_NO_DOC_TEXT", "No documentation found for this Api"
        )
        app.config.setdefault("API_DOC_ENABLE", True)
        app.config.setdefault("API_DOC_CDN", False)
        app.config.setdefault("API_DOC_MEMBER", [])
        app.config.setdefault("API_DOC_MEMBER_SUB_EXCLUDE", [])
        app.config.setdefault("API_DOC_RESTFUL_EXCLUDE", [])
        app.config.setdefault(
            "API_DOC_METHODS_LIST", ["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        app.config.setdefault("API_DOC_PASSWORD_SHA2", "")
        app.config.setdefault("API_DOC_AUTO_GENERATING_ARGS_MD", False)

        with app.app_context():
            self._check_value_type(
                {"title": title, "version": version, "description": description},
                str,
                data_type="variable",
            )
            self._check_value_type(
                [
                    "API_DOC_CDN_CSS_TEMPLATE",
                    "API_DOC_CDN_JS_TEMPLATE",
                    "API_DOC_URL_PREFIX",
                    "API_DOC_NO_DOC_TEXT",
                    "API_DOC_PASSWORD_SHA2",
                ],
                str,
            )
            self._check_value_type(
                ["API_DOC_ENABLE", "API_DOC_CDN", "API_DOC_AUTO_GENERATING_ARGS_MD"],
                bool,
            )
            self._check_value_type(
                [
                    "API_DOC_MEMBER",
                    "API_DOC_MEMBER_SUB_EXCLUDE",
                    "API_DOC_RESTFUL_EXCLUDE",
                    "API_DOC_METHODS_LIST",
                ],
                list,
            )

            if not current_app.config["API_DOC_ENABLE"]:
                return

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
            @self._verify_password
            def data():

                url_prefix = current_app.config["API_DOC_URL_PREFIX"]
                referer = request.headers.get("referer", "http://127.0.0.1")
                host = referer.split(url_prefix)[0]

                data_dict = {}

                # Restful Api
                data_dict.update(self._get_restful_api_data())

                # Api
                data_dict.update(self._get_api_data())

                return jsonify(
                    {
                        "PROJECT_NAME": PROJECT_NAME,
                        "PROJECT_VERSION": PROJECT_VERSION,
                        "host": host,
                        "title": title,
                        "version": version,
                        "description": description,
                        "noDocText": current_app.config["API_DOC_NO_DOC_TEXT"],
                        "data": data_dict,
                    }
                )

            app.register_blueprint(api_doc)

    def _get_restful_api_data(self):
        """Restful Api"""

        data_dict = {}

        for rule in current_app.url_map.iter_rules():
            cls = current_app.view_functions[rule.endpoint]

            if not hasattr(cls, "view_class"):
                continue

            if cls.methods is None:
                continue

            c_name = cls.view_class.__name__

            if c_name in current_app.config["API_DOC_RESTFUL_EXCLUDE"]:
                continue

            c_doc = self._clean_doc(self._get_api_doc(cls))

            if c_doc and c_doc != current_app.config["API_DOC_NO_DOC_TEXT"]:
                c_name = "{}({})".format(c_name, c_doc)

            data_dict.setdefault(c_name, {"children": []})

            for method in cls.methods:
                if method not in current_app.config["API_DOC_METHODS_LIST"]:
                    continue

                api_data = {
                    "url": str(rule),
                    "method": method,
                    "router": c_name,
                    "api_type": "restful_api",
                }

                self._add_api_data(
                    data_dict, api_data, getattr(cls.view_class, method.lower())
                )

            if data_dict[c_name]["children"] == []:
                data_dict.pop(c_name)
            else:
                data_dict[c_name]["children"].sort(key=lambda x: x["name"])

        return data_dict

    def _get_api_data(self):
        """Api"""

        data_dict = {}

        for rule in current_app.url_map.iter_rules():
            func = current_app.view_functions[rule.endpoint]

            if hasattr(func, "view_class"):
                continue

            bp_name = rule.endpoint.split(".")[0]
            member_sub_name = rule.endpoint.split(".")[-1]

            if bp_name not in current_app.config["API_DOC_MEMBER"]:
                continue

            if member_sub_name in current_app.config["API_DOC_MEMBER_SUB_EXCLUDE"]:
                continue

            data_dict.setdefault(bp_name, {"children": []})

            url = str(rule)

            method = " ".join(
                [
                    r
                    for r in rule.methods
                    if r in current_app.config["API_DOC_METHODS_LIST"]
                ]
            )
            if not method:
                continue

            url = "{}\t[{}]".format(url, "\t".join(method.split(" ")))

            api_data = {
                "url": url,
                "method": method,
                "router": bp_name,
                "api_type": "api",
            }

            self._add_api_data(data_dict, api_data, func)

        for bp_name in copy.deepcopy(data_dict):
            if data_dict[bp_name]["children"] == []:
                data_dict.pop(bp_name)
            else:
                data_dict[bp_name]["children"].sort(key=lambda x: x["name"])

        return data_dict

    def _add_api_data(self, data_dict, api_data, func):
        if api_data["api_type"] == "restful_api":
            api_name = api_data["method"]
        elif api_data["api_type"] == "api":
            api_name = self._get_api_name(func)

        router = api_data["router"]

        try:
            result = filter(
                lambda x: x["name"] == api_name,
                data_dict[router]["children"],
            )
            result_list = list(result)
            if len(result_list) > 0:
                for k, v in [("url", api_data["url"]), ("method", api_data["method"])]:
                    result_list[0][k] = " ".join(
                        list(set(" ".join([result_list[0][k], v]).split(" ")))
                    )
                raise RuntimeError

            api_data["name"] = api_name

            doc = self._get_api_doc(func)

            (
                api_data["doc"],
                api_data["name_extra"],
                api_data["doc_md"],
            ) = self._get_doc_name_extra_doc_md(doc)

            if current_app.config["API_DOC_AUTO_GENERATING_ARGS_MD"]:
                args_md = self._get_args_md(func)
                if args_md:
                    api_data["doc_md"] = "\n".join([args_md, api_data["doc_md"]])

        except Exception as e:
            logger.error(
                "{} error - {} - {} - {}".format(PROJECT_NAME, e, router, api_name)
            )
        else:
            data_dict[router]["children"].append(api_data)

    def _get_api_name(self, func):
        words = func.__name__.split("_")
        words = [w.capitalize() for w in words]

        return "".join(words)

    def _get_api_doc(self, func):
        func_doc = func.__doc__
        if func_doc:
            return func_doc.replace("\t", " " * 4)
        else:
            return current_app.config["API_DOC_NO_DOC_TEXT"]

    def _clean_str(self, str):
        return str.strip(" ").strip("\n\n").strip(" ").strip("\n").strip(" ")

    def _clean_doc(self, doc_src):
        return self._clean_str(doc_src.split("\n\n")[0].split("\n")[0])

    def _get_doc_name_extra_doc_md(self, doc_src):
        doc = doc_src.split("@@@")[0]

        if doc != current_app.config["API_DOC_NO_DOC_TEXT"]:
            name_extra = self._clean_doc(doc)
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
            doc = current_app.config["API_DOC_NO_DOC_TEXT"]

        if len(doc_src.split("@@@")) >= 2:
            doc_md = doc_src.split("@@@")[1].strip(" ")
            space_count = doc_src.split("@@@")[0].split("\n")[-1].count(" ")
            doc_md = "\n".join(doc_md.split("\n" + " " * space_count))
        else:
            doc_md = ""

        return doc, name_extra, doc_md

    def _check_value_type(self, data_packages, type, data_type="config"):
        for d in data_packages:
            if data_type == "config":
                value = current_app.config[d]
            elif data_type == "variable":
                value = data_packages[d]
            if not isinstance(value, type):
                raise ValueError(
                    "{} is the incorrect type of value, the correct type is {}".format(
                        d, type
                    )
                )

    def _get_argument(self, func):
        func_source = inspect.getsource(func)
        func_doc = func.__doc__
        if func_doc:
            func_source = func_source.replace(func_doc, "")
        func_source = func_source.replace("\t", " " * 4)

        argument_list = func_source.split("add_argument")

        return argument_list

    def _clean_argument(self, argument_source):
        argument_data = ""
        stack = []
        index = 0
        for char in argument_source:
            if char == "(":
                stack.append(char)
            elif char == ")":
                stack.pop()
            index += 1
            if not stack:
                index -= 1
                argument_data = argument_source[1:index]
                break

        return self._clean_str(argument_data)

    def _parse_argument(self, argument_data):
        def _run_eval(eval_str):
            argument_dict = {}
            try:
                argument_dict = eval(eval_str)
            except Exception as e:
                e_str = str(e)
                logger.error(e_str)
                if "is not defined" in e_str:
                    err_str = e_str.split("'")[1]
                    argument_dict = _run_eval(eval_str.replace(err_str, ""))
                else:
                    return argument_dict

            return argument_dict

        args_dict = {}
        arg_list = argument_data.split(",")
        if len(arg_list) < 1 or not arg_list[0].strip():
            return args_dict

        name = arg_list[0].strip("'").strip('"').strip()
        args_dict = OrderedDict(
            name=name,
            location="",
            type="",
            required="",
            nullable="",
            default="",
            help="",
        )
        eval_str = "dict({})".format(",".join(arg_list[1:]).strip())
        argument_dict = _run_eval(eval_str)
        if not argument_dict:
            return args_dict

        args_dict["required"] = "False"
        args_dict["nullable"] = "True"

        for key, value in argument_dict.items():
            if key not in args_dict:
                continue
            if key == "location":
                args_dict[key] = ApiDoc.LOCATIONS.get(value, "")
            elif key == "type":
                args_dict[key] = ApiDoc.PY_TYPES.get(value, "")
            else:
                args_dict[key] = str(value)

        return args_dict

    def _get_args_md(self, func):
        args_md_list = []
        argument_list = self._get_argument(func)
        for argument_source in argument_list:
            argument_data = self._clean_argument(argument_source)
            args_dict = self._parse_argument(argument_data)
            if not args_dict:
                continue
            if not args_md_list:
                args_md_list.append("### args")
                args_md_list.append(
                    "|" + "|".join(arg_key for arg_key in args_dict.keys()) + "|"
                )
                args_md_list.append("|---" * len(args_dict) + "|")
            args_md_list.append(
                "|" + "|".join(arg_value for arg_value in args_dict.values()) + "|"
            )

        return "\n".join(args_md_list)

    def _unauthorized(self):
        response = jsonify({"error": "unauthorized"})
        response.status_code = 401
        return response

    def _verify_password(self, func):
        @wraps(func)
        def decorated_function(*args, **kw):
            API_DOC_PASSWORD_SHA2 = current_app.config["API_DOC_PASSWORD_SHA2"]
            auth_password_sha2 = request.headers.get("Auth-Password-SHA2")

            if API_DOC_PASSWORD_SHA2 and API_DOC_PASSWORD_SHA2 != auth_password_sha2:
                return self._unauthorized()
            return func(*args, **kw)

        return decorated_function

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
