from flask import Blueprint, render_template, request
import requests as py_requests
from werkzeug.wrappers import Response
import json

import config

# Blueprint Configuration
ner_bp = Blueprint(
    'ner_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@ner_bp.route("/ner", methods=['POST'])
def get_ner_results():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url_data = config.backend_data + "data/project-analysis"
    url_new = config.backend_ner + "get_ners"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    data_response = py_requests.post(url_data, data=data)
    content = data_response.content
    content_loaded = json.loads(content)
    if content_loaded["ner_results"] is not None:
        content = json.dumps(content_loaded["ner_results"])
    else:
        backend_response = py_requests.post(url_new, data=data)
        content = backend_response.content
        ner = json.loads(content)

        url_data = config.backend_data + "data/save-updates"
        data = {
            "name": name,
            "link": link,
            "description": description,
            "ner_results": content
        }
        data_response = py_requests.post(url_data, data=data)

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response


@ner_bp.route("/ner/changes", methods=['POST'])
def update_ner_results():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]
    ner_res = request.form["ner_results"]

    url_data = config.backend_data + "data/save-updates"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "ner_results": ner_res,
        "user_generated": True
    }
    data_response = py_requests.post(url_data, data=data)
    content = data_response.content

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=200, headers=header)
    return response

