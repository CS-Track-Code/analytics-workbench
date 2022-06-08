from flask import Blueprint, render_template, request
import requests as py_requests
from werkzeug.wrappers import Response
import json

import config

# Blueprint Configuration
esa_bp = Blueprint(
    'esa_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@esa_bp.route("/esa", methods=['POST'])
def get_esa_results():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"
    if classification_scheme != "research_areas" and classification_scheme != "sdgs":
        pass  # ToDo: error

    url_data = config.backend_data + "data/project-analysis"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    data_response = py_requests.post(url_data, data=data)
    content = data_response.content
    content_loaded = json.loads(content)
    needs_new = True

    if not config.has_version_control:
        config.get_version_control()

    if classification_scheme == "research_areas" and content_loaded["ra_results"] is not None:
        content = json.dumps(content_loaded["ra_results"])
        if "version_control" in content_loaded["ra_results"]:
            if content_loaded["ra_results"]["version_control"] == config.version_control["research_areas"]:
                needs_new = False
        elif config.version_control["research_areas"] is None:
            needs_new = False
    elif classification_scheme == "sdgs" and content_loaded["sdg_results"] is not None:
        content = json.dumps(content_loaded["sdg_results"])
        if "version_control" in content_loaded["sdg_results"]:
            if content_loaded["sdg_results"]["version_control"] == config.version_control["sdgs"]:
                needs_new = False
        elif config.version_control["sdgs"] is None:
            needs_new = False

    if needs_new:
        if classification_scheme == "research_areas":
            url_new = config.backend_esa + "results"
            backend_response = py_requests.post(url_new, data=data, timeout=125)
            content = backend_response.content
            config.version_control["research_areas"] = json.loads(content)["version_control"]
            data["ra_results"] = content
        else:
            url_new = config.backend_esa + "results"
            data["classification_scheme"] = "sdgs"
            backend_response = py_requests.post(url_new, data=data, timeout=125)
            content = backend_response.content
            config.version_control["sdgs"] = json.loads(content)["version_control"]
            data["sdg_results"] = content

        url_data = config.backend_data + "data/save-updates"

        data_response = py_requests.post(url_data, data=data)

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@esa_bp.route("/esa_LITE", methods=['POST'])
def get_esa_results_LITE():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"
    if classification_scheme != "research_areas" and classification_scheme != "sdgs":
        pass  # ToDo: error

    data = {
        "name": name,
        "link": link,
        "description": description
    }

    if classification_scheme == "research_areas":
        url_new = config.backend_esa + "results"
        backend_response = py_requests.post(url_new, data=data, timeout=125)
        content = backend_response.content
        config.version_control["research_areas"] = json.loads(content)["version_control"]
    else:
        url_new = config.backend_esa + "results"
        data["classification_scheme"] = "sdgs"
        backend_response = py_requests.post(url_new, data=data, timeout=125)
        content = backend_response.content
        config.version_control["sdgs"] = json.loads(content)["version_control"]

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@esa_bp.route("/esa/changes", methods=['POST'])
def update_esa_results():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"
    if classification_scheme != "research_areas" and classification_scheme != "sdgs":
        pass  # ToDo: error

    data = {
        "name": name,
        "link": link,
        "description": description,
        "user_generated": True
    }

    if classification_scheme == "research_areas":
        ra_res = request.form["ra_results"]
        data["ra_results"] = ra_res
    else:
        sdg_res = request.form["sdg_results"]
        data["sdg_results"] = sdg_res

    url_data = config.backend_data + "data/save-updates"

    data_response = py_requests.post(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@esa_bp.route("/esa/research_areas")
def get_research_areas():
    url_data = config.backend_esa + "research_areas"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response


@esa_bp.route("/esa/sdgs")
def get_sdgs():
    url_data = config.backend_esa + "SDGs"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response
