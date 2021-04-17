#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
Program:
    Flask-Docs
Version:
    0.2.7
History:
    Created on 2018/05/20
    Last modified on 2021/04/17
Author:
    kwkw
"""

import os

from flask import Blueprint, current_app, jsonify
from flask.views import MethodView
from flask_restful import Resource


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

    def __init__(
        self,
        app=None,
        title="Api Doc",
        version="1.0.0",
        no_doc_text="No doc found for this Api",
    ):
        if app is not None:
            self.init_app(app, title, version, no_doc_text)

    def init_app(
        self,
        app,
        title="Api Doc",
        version="1.0.0",
        no_doc_text="No doc found for this Api",
    ):

        self.no_doc_text = no_doc_text

        app.config.setdefault("API_DOC_MEMBER", [])
        app.config.setdefault("API_DOC_ENABLE", True)
        app.config.setdefault("API_DOC_CDN", False)
        app.config.setdefault("RESTFUL_API_DOC_EXCLUDE", [])
        app.config.setdefault("METHODS_LIST", ["GET", "POST", "PUT", "DELETE", "PATCH"])

        with app.app_context():
            if not current_app.config["API_DOC_ENABLE"]:
                return

            api_doc = Blueprint(
                "api_doc", __name__, static_folder="static", url_prefix="/docs/api"
            )

            @api_doc.route("/", methods=["GET"])
            def index():
                if current_app.config["API_DOC_CDN"]:
                    return ApiDoc.INDEX_HTML.replace(
                        "<!-- ___CSS_TEMPLATE___ -->", ApiDoc.CSS_TEMPLATE_CDN
                    ).replace("<!-- ___JS_TEMPLATE___ -->", ApiDoc.JS_TEMPLATE_CDN)
                else:
                    return ApiDoc.INDEX_HTML.replace(
                        "<!-- ___CSS_TEMPLATE___ -->", ApiDoc.CSS_TEMPLATE_LOCAL
                    ).replace("<!-- ___JS_TEMPLATE___ -->", ApiDoc.JS_TEMPLATE_LOCAL)

            @api_doc.route("/data", methods=["GET"])
            def data():

                dataDict = {}

                # Restful Api and MethodView Api
                c_dict = {}
                class_name_dict = {}
                for c in self.get_all_subclasses(Resource, MethodView):
                    c_dict[c.__name__.lower()] = c
                    class_name_dict[c.__name__.lower()] = c.__name__
                for rule in app.url_map.iter_rules():
                    func = app.view_functions[rule.endpoint]
                    if func.__name__ not in c_dict:
                        continue

                    name = func.__name__
                    if name in current_app.config["RESTFUL_API_DOC_EXCLUDE"]:
                        continue

                    c_doc = self.get_api_doc(func)

                    flag_rule = True
                    if flag_rule:
                        # e.g. Repeat "Todolist(manage todolist)(Manage todolist)"
                        try:
                            if c_doc != self.no_doc_text:
                                name = (
                                    class_name_dict[name]
                                    + "("
                                    + c_doc.split("\n\n")[0]
                                    .split("\n")[0]
                                    .strip(" ")
                                    .strip("\n\n")
                                    .strip(" ")
                                    .strip("\n")
                                    .strip(" ")
                                    + ")"
                                )
                        except Exception as e:
                            name = name.capitalize()
                        flag_rule = False

                    if func.methods is None:
                        continue

                    if name not in dataDict:
                        dataDict[name] = {"children": []}

                    for m in func.methods:
                        if m not in current_app.config["METHODS_LIST"]:
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
                                dataDict[name]["children"],
                            )
                            result_list = list(result)
                            if len(result_list) > 0:
                                result_list[0]["url"] = (
                                    result_list[0]["url"] + " " + url
                                )
                                result_list[0]["url"] = " ".join(
                                    list(set(result_list[0]["url"].split(" ")))
                                )
                                raise

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
                            pass
                        else:
                            dataDict[name]["children"].append(api)

                    if dataDict[name]["children"] == []:
                        dataDict.pop(name)
                    else:
                        dataDict[name]["children"].sort(key=lambda x: x["name"])

                # Api
                for rule in app.url_map.iter_rules():
                    f = str(rule).split("/")[1]
                    if f not in current_app.config["API_DOC_MEMBER"]:
                        continue

                    if f.capitalize() not in dataDict:
                        dataDict[f.capitalize()] = {"children": []}

                    api = {
                        "name": "",
                        "name_extra": "",
                        "url": "",
                        "method": "",
                        "doc": "",
                        "doc_md": "",
                        "router": f.capitalize(),
                        "api_type": "api",
                    }

                    try:
                        func = app.view_functions[rule.endpoint]

                        name = self.get_api_name(func)
                        url = str(rule)
                        method = " ".join(
                            [
                                r
                                for r in rule.methods
                                if r in current_app.config["METHODS_LIST"]
                            ]
                        )

                        result = filter(
                            lambda x: x["name"] == name,
                            dataDict[f.capitalize()]["children"],
                        )
                        result_list = list(result)
                        if len(result_list) > 0:
                            result_list[0]["url"] = result_list[0]["url"] + " " + url
                            result_list[0]["url"] = " ".join(
                                list(set(result_list[0]["url"].split(" ")))
                            )
                            result_list[0]["method"] = (
                                result_list[0]["method"] + " " + method
                            )
                            result_list[0]["method"] = " ".join(
                                list(set(result_list[0]["method"].split(" ")))
                            )
                            raise

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
                        pass
                    else:
                        dataDict[f.capitalize()]["children"].append(api)

                    if dataDict[f.capitalize()]["children"] == []:
                        dataDict.pop(f.capitalize())
                    else:
                        dataDict[f.capitalize()]["children"].sort(
                            key=lambda x: x["name"]
                        )

                return jsonify(
                    {
                        "data": dataDict,
                        "title": title,
                        "version": version,
                        "noDocText": self.no_doc_text,
                    }
                )

            app.register_blueprint(api_doc)

    def get_api_name(self, func):
        """e.g. Convert 'do_work' to 'Do Work'"""

        words = func.__name__.split("_")
        words = [w.capitalize() for w in words]

        return " ".join(words)

    def get_api_doc(self, func):
        if func.__doc__:
            return func.__doc__.replace("\t", "    ")
        else:
            return self.no_doc_text

    def get_doc_name_extra_doc_md(self, doc_src):
        try:
            doc = doc_src.split("@@@")[0]
        except Exception as e:
            doc = self.no_doc_text

        if doc != self.no_doc_text:
            name_extra = (
                doc.split("\n\n")[0]
                .split("\n")[0]
                .strip(" ")
                .strip("\n\n")
                .strip(" ")
                .strip("\n")
                .strip(" ")
            )
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

        try:
            doc_md = doc_src.split("@@@")[1].strip(" ")
            try:
                space_count = doc_src.split("@@@")[0].split("\n")[-1].count(" ")
            except Exception as e:
                space_count = 0
            doc_md = "\n".join(doc_md.split("\n" + " " * space_count))
        except Exception as e:
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
