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

# Todo: catch connection error from requests to esa (and ner)


@ex_ac_bp.route("/external/analyse", methods=['POST'])
def analyse():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    ner = json.loads(request_ner(name, link, description))
    esa = json.loads(request_esa(name, link, description))

    output_data = {
        "name": name,
        "link": link,
        "description": description,
        "esa_results": esa,
        "ner_results": ner
    }

    # """
    # Save
    # url_data = config.backend_data + "data/save-complete-project"
    # data_response = py_requests.post(url_data, data=output_data)
    # """

    json_data = json.dumps(output_data)
    response = BaseResponse(json_data, status=200)
    return response


@ex_ac_bp.route("/external/esa", methods=['POST'])
def external_get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    content = request_esa(name, link, description)

    # """
    # # Save
    # url_data = config.backend_data + "data/save-updates"
    # data = {
    #     "name": name,
    #     "link": link,
    #     "description": description,
    #     "esa_results": content
    # }
    # data_response = py_requests.post(url_data, data=data)
    # """

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response


@ex_ac_bp.route("/external/ner", methods=['POST'])
def external_get_ner():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    content = request_ner(name, link, description)

    # """
    # # Save
    # url_data = config.backend_data + "data/save-updates"
    # data = {
    #     "name": name,
    #     "link": link,
    #     "description": description,
    #     "ner_results": content
    # }
    # data_response = py_requests.post(url_data, data=data)
    # """

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = BaseResponse(content, status=200, headers=header)
    return response


@ex_ac_bp.route("/external/addProjectsToDatabase", methods=['POST'])
def external_add_to_db():
    project_list = request.form.getlist("projects")
    for project in project_list:
        name = project["name"]
        link = project["link"]
        description = project["description"]

        ner = json.loads(request_ner(name, link, description))
        esa = json.loads(request_esa(name, link, description))

        output_data = {
            "name": name,
            "link": link,
            "description": description,
            "esa_results": esa,
            "ner_results": ner
        }

        url_data = config.backend_data + "data/save-complete-project"
        data_response = py_requests.post(url_data, data=output_data)

    json_result = json.dumps({'success': True})
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000", 'ContentType': 'application/json'}
    response = BaseResponse(json_result, status=200, headers=header)
    return response


def request_ner(name, link, description):
    url_new = config.backend_ner + "get_ners"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    backend_response = py_requests.post(url_new, data=data)
    content = backend_response.content
    return content


def request_esa(name, link, description):
    url_new = config.backend_esa + "results"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    backend_response = py_requests.post(url_new, data=data)
    content = backend_response.content
    return content
