from flask import Blueprint, render_template, request
from flask import current_app as app
import requests as py_requests
from werkzeug.wrappers import BaseResponse
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
    response = BaseResponse(content, status=200, headers=header)
    return response


@db_bp.route("/db/tba-project-names")
def get_tba_project_names():
    url_data = config.backend_data + "evaluation/tba-projects"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
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

    response = BaseResponse(content, status=200)
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

    response = BaseResponse(content, status=200)
    return response


@db_bp.route("/db/evaluation_data")
def get_evaluation_data():
    url_data = config.backend_data + "evaluation/data"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response

