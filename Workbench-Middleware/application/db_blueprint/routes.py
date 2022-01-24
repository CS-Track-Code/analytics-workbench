from flask import Blueprint, render_template, request
import requests as py_requests
from werkzeug.wrappers import Response
import json

import config

# Blueprint Configuration
db_bp = Blueprint(
    'db_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@db_bp.route("/db/project-names")
def get_project_names():
    url_data = config.backend_data + "evaluation/project-names"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@db_bp.route("/db/tba-project-names")
def get_tba_project_names():
    url_data = config.backend_data + "evaluation/tba-projects"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@db_bp.route("/db/project-data", methods=['POST'])
def get_project_data():
    project_name = request.form["project_name"]
    url_data = config.backend_data + "data/project"
    data = {
        "project_name": project_name,
        "whole_data": True,
        "link": "",
        "description": ""
    }
    data_response = py_requests.post(url_data, data=data)
    content = data_response.content
    content_loaded = json.loads(content)

    if not config.has_version_control:
        config.get_version_control()

    if content_loaded["ra_results"] is not None:
        needs_new = True
        if "version_control" in content_loaded["ra_results"]:
            if content_loaded["ra_results"]["version_control"] == config.version_control["research_areas"]:
                needs_new = False
        elif config.version_control["research_areas"] is None:
            needs_new = False
        if needs_new:
            data = {
                "name": project_name,
                "link": content_loaded["project_link"],
                "description": content_loaded["project_description"]
            }
            url_new = config.backend_esa + "results"
            backend_response = py_requests.post(url_new, data=data, timeout=125)
            content = backend_response.content
            config.version_control["research_areas"] = json.loads(content)["version_control"]
            content_loaded["ra_results"] = json.loads(content)
            data["ra_results"] = content
            url_data = config.backend_data + "data/save-updates"

            data_response = py_requests.post(url_data, data=data)

    if content_loaded["sdg_results"] is not None:
        if "version_control" in content_loaded["sdg_results"]:
            if content_loaded["sdg_results"]["version_control"] == config.version_control["sdgs"]:
                needs_new = False
        elif config.version_control["sdgs"] is None:
            needs_new = False
        if needs_new:
            data = {
                "name": project_name,
                "link": content_loaded["project_link"],
                "description": content_loaded["project_description"]
            }
            url_new = config.backend_esa + "results"
            data["classification_scheme"] = "sdgs"
            backend_response = py_requests.post(url_new, data=data, timeout=125)
            content = backend_response.content
            config.version_control["sdgs"] = json.loads(content)["version_control"]
            content_loaded["sdg_results"] = json.loads(content)
            data["sdg_results"] = content
            url_data = config.backend_data + "data/save-updates"

            data_response = py_requests.post(url_data, data=data)

    content = json.dumps(content_loaded)

    response = Response(content, status=200)
    return response


@db_bp.route("/db/recommendations", methods=['POST'])
def get_recommendations():
    visited_list = modified_list = fave_list = None
    if "visited_list" in request.form:
        visited_list = request.form["visited_list"]
    if "modified_list" in request.form:
        modified_list = request.form["modified_list"]
    if "fave_list" in request.form:
        fave_list = request.form["fave_list"]

    url_data = config.backend_data + "evaluation/recommendation"
    data = {
        "visited_list": visited_list,
        "modified_list": modified_list,
        "fave_list": fave_list
    }

    data_response = py_requests.post(url_data, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response


@db_bp.route("/db/evaluation_data")
def get_evaluation_data():
    url_data = config.backend_data + "evaluation/data"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response

