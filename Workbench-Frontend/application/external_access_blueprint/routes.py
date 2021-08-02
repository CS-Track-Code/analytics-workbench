from flask import Blueprint, render_template, request
from flask import current_app as app
import requests as py_requests
from werkzeug.wrappers import BaseResponse
import json

import config

# Blueprint Configuration
ex_ac_bp = Blueprint(
    'ex_ac_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@ex_ac_bp.route("/ex/getAnalysisResults", methods=['POST'])
def analyse():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "external/analyse"

    input_data = {
        "name": name,
        "link": link,
        "description": description
    }

    response = py_requests.post(url, data=input_data)
    result = response.content

    response = BaseResponse(result, status=200)
    return response


@ex_ac_bp.route("/getResearchAreas", methods=['POST'])
def external_get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "external/esa"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    response = py_requests.post(url, data=data)
    content = response.content

    response = BaseResponse(content, status=200)
    return response


@ex_ac_bp.route("/external/ner", methods=['POST'])
def external_get_ner():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "external/ner"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    response = py_requests.post(url, data=data)
    content = response.content
    ner = content

    url_data = config.backend_data + "data/save-updates"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "ner_results": content
    }
    data_response = py_requests.post(url_data, data=data)

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response
