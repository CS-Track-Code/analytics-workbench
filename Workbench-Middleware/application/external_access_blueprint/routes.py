from flask import Blueprint, request
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

    ner, ner_code = request_ner(name, link, description)
    esa, esa_code = request_esa(name, link, description)
    ner = json.loads(ner)
    esa = json.loads(esa)

    code = ner_code if ner_code > esa_code else esa_code

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
    response = BaseResponse(json_data, status=code)
    return response


@ex_ac_bp.route("/external/esa", methods=['POST'])
def external_get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    content, code = request_esa(name, link, description)

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
    response = BaseResponse(content, status=code, headers=header)
    return response


@ex_ac_bp.route("/external/ner", methods=['POST'])
def external_get_ner():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    content, code = request_ner(name, link, description)

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
    response = BaseResponse(content, status=code,  headers=header)
    return response


@ex_ac_bp.route("/external/addProjectsToDatabase", methods=['POST'])
def external_add_to_db():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000", 'ContentType': 'application/json'}

    try:
        project_list = request.form.getlist("projects")
        code = 200
        for project in project_list:
            name = project["name"]
            link = project["link"]
            description = project["description"]

            status_code = add_project_to_database(name, link, description)
            if status_code != 200:
                code = status_code

        response = BaseResponse(status=code, headers=header)
    except ConnectionError:
        response = BaseResponse(headers=header)

    return response


@ex_ac_bp.route("/external/addSingleProjectToDatabase", methods=['POST'])
def external_add_one_to_db():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000", 'ContentType': 'application/json'}

    try:
        name = request.form["name"]
        link = request.form["link"]
        description = request.form["description"]

        code = add_project_to_database(name, link, description)

        response = BaseResponse(status=code, headers=header)
    except ConnectionError:
        response = BaseResponse(headers=header)
    return response


def add_project_to_database(name, link, description):
    ner = request_ner(name, link, description)
    esa = request_esa(name, link, description)

    output_data = {
        "name": name,
        "link": link,
        "description": description,
        "esa_results": esa,
        "ner_results": ner
    }

    url_data = config.backend_data + "data/save-complete-project"
    data_response = py_requests.post(url_data, data=output_data)
    return data_response.status_code


def request_ner(name, link, description):
    url_new = config.backend_ner + "get_ners"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    backend_response = py_requests.post(url_new, data=data)
    content = backend_response.content
    code = backend_response.status_code
    return content, code


def request_esa(name, link, description):
    url_new = config.backend_esa + "results"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    backend_response = py_requests.post(url_new, data=data)
    content = backend_response.content
    code = backend_response.status_code
    return content, code
