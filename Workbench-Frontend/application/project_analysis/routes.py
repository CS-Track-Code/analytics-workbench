from flask import Blueprint, render_template, request
from flask import current_app as app
from werkzeug.wrappers import BaseResponse
import requests as py_requests
import json

import config

# Blueprint Configuration
project_analysis_bp = Blueprint(
    'project_analysis_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@project_analysis_bp.route('/analyse')
def analysepage():
    link = request.args.get("link", "")
    description = request.args.get("description", "")
    return render_template(
        "analyse_project.html",
        title="Analyse Project",
        project_link=link,
        project_description=description
    )


@project_analysis_bp.route('/analyse/description', methods=['POST'])
def get_description():
    name = request.form["name"]
    link = request.form["link"]
    if link != "":
        url = config.middleware + "mercury/get_project_text"
        data = {
            "name": name,
            "link": link
        }

        middleware_response = py_requests.post(url, data=data)

        esa_data = middleware_response.content

        response = BaseResponse(esa_data, status=200)

        return response


@project_analysis_bp.route('/analyse/project')
def start_analysis():
    # link = request.args.get("link", "")
    # description = request.args.get("description", "")
    return render_template(
        "modify_analysis_results.html",
        title="Analyse Project",
        # project_link=link,
        # project_description=description
    )


@project_analysis_bp.route('/analyse/project/esa', methods=['POST'])
def get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "esa"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    middleware_response = py_requests.post(url, data=data)

    esa_data = middleware_response.content

    response = BaseResponse(esa_data, status=200)

    return response


@project_analysis_bp.route('/analyse/project/modify_esa', methods=['GET', 'POST'])
def mod_esa():
    if request.method == 'GET':
        return render_template(
            "modify_esa_results.html",
            title="Analyse Project - Modify ESA Results"
        )
    else:
        name = request.form["name"]
        link = request.form["link"]
        description = request.form["description"]
        esa_res = request.form["esa_res"]

        url_data = config.middleware + "esa/changes"
        data = {
            "name": name,
            "link": link,
            "description": description,
            "esa_results": esa_res
        }
        data_response = py_requests.post(url_data, data=data)
        content = data_response.content

        response = BaseResponse(content, status=200)
        return response


@project_analysis_bp.route('/analyse/project/ner', methods=['POST'])
def get_ner():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "ner"
    data = {
        "name": name,
        "link": link,
        "description": description
    }

    middleware_response = py_requests.post(url, data=data)

    ner_data = middleware_response.content

    response = BaseResponse(ner_data, status=200)
    return response


@project_analysis_bp.route('/analyse/project/modify_ner', methods=['GET', 'POST'])
def mod_ner():
    if request.method == 'GET':
        return render_template(
            "modify_ner_results.html",
            title="Analyse Project - Modify NER Results"
        )
    else:
        name = request.form["name"]
        link = request.form["link"]
        description = request.form["description"]
        ner_res = request.form["ner_res"]

        url_data = config.middleware + "ner/changes"
        data = {
            "name": name,
            "link": link,
            "description": description,
            "ner_results": ner_res
        }
        data_response = py_requests.post(url_data, data=data)
        content = data_response.content

        response = BaseResponse(content, status=200)
        return response


@project_analysis_bp.route('/analyse/project/data', methods=['POST'])
def project_data():
    project_name = request.form["name"]
    url_data = config.middleware + "db/project-data"
    data = {
        "project_name": project_name
    }
    data_response = py_requests.post(url_data, data=data)
    content = data_response.content

    response = BaseResponse(content, status=200)
    return response
