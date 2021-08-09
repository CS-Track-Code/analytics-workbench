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
    content = response.content
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response


@ex_ac_bp.route("/ex/getResearchAreas", methods=['POST'])
def external_get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    url = config.middleware + "external/esa"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "tfidf_cutoff": tfidf_cutoff,
        "similarity_cutoff": similarity_cutoff
    }

    response = py_requests.post(url, data=data)
    content = response.content
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response


@ex_ac_bp.route("/ex/getSDGs", methods=['POST'])
def external_get_sdgs():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    url = config.middleware + "external/esa"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "classification_scheme": "sdgs"
    }

    response = py_requests.post(url, data=data)
    content = response.content
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response


@ex_ac_bp.route("/ex/getNamedEntities", methods=['POST'])
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
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response


@ex_ac_bp.route("/ex/addProjectsToDatabase", methods=['POST'])
def external_add_to_db():
    project_list = request.form.getlist("projects")
    url = config.middleware + "external/addProjectsToDatabase"
    data = {
        "projects": project_list
    }
    response = py_requests.post(url, data=data)
    content = response.content
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response


@ex_ac_bp.route("/ex/addSingleProjectToDatabase", methods=['POST'])
def external_add_one_to_db():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    url = config.middleware + "external/addSingleProjectToDatabase"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "tfidf_cutoff": tfidf_cutoff,
        "similarity_cutoff": similarity_cutoff
    }
    response = py_requests.post(url, data=data)
    content = response.content
    code = response.status_code

    response = BaseResponse(content, status=code)
    return response
