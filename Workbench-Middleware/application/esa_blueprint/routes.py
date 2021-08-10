from flask import Blueprint, render_template, request
from flask import current_app as app
import requests as py_requests
from werkzeug.wrappers import BaseResponse
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

    url_data = config.backend_data + "data/project-analysis"
    url_new = config.backend_esa + "results"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    data_response = py_requests.post(url_data, data=data)
    content = data_response.content
    content_loaded = json.loads(content)
    if content_loaded["ra_results"] is not None:
        content = json.dumps(content_loaded["ra_results"])

    else:
        backend_response = py_requests.post(url_new, data=data)
        content = backend_response.content

        url_data = config.backend_data + "data/save-updates"
        data = {
            "name": name,
            "link": link,
            "description": description,
            "ra_results": content
        }
        data_response = py_requests.post(url_data, data=data)

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response


@esa_bp.route("/esa/changes", methods=['POST'])
def update_esa_results():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]
    ra_res = request.form["ra_results"]

    url_data = config.backend_data + "data/save-updates"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "ra_results": ra_res,
        "user_generated": True
    }
    data_response = py_requests.post(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response


@esa_bp.route("/esa/research_areas")
def get_research_areas():
    url_data = config.backend_esa + "research_areas"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    response = BaseResponse(content, status=200)
    return response
