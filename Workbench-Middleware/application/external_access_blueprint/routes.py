from flask import Blueprint, request
import requests as py_requests
from werkzeug.wrappers import Response
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

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    ner, ner_code = request_ner(name, link, description)
    res_areas, res_areas_code = request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, "research_areas")
    sdg, sdg_code = request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, "sdgs")
    ner = json.loads(ner)
    res_areas = json.loads(res_areas)
    sdg = json.loads(sdg)

    code = ner_code if ner_code > res_areas_code else res_areas_code

    output_data = {
        "name": name,
        "link": link,
        "description": description,
        "ra_results": res_areas,
        "sdg_results": sdg,
        "ner_results": ner
    }

    # """
    # Save
    # url_data = config.backend_data + "data/save-complete-project"
    # data_response = py_requests.post(url_data, data=output_data)
    # """

    json_data = json.dumps(output_data)
    response = Response(json_data, status=code)
    return response


@ex_ac_bp.route("/external/esa", methods=['POST'])
def external_get_esa():
    name = request.form["name"]
    link = request.form["link"]
    description = request.form["description"]

    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    content, code = request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, classification_scheme)

    # """
    # # Save
    # url_data = config.backend_data + "data/save-updates"
    # data = {
    #     "name": name,
    #     "link": link,
    #     "description": description,
    #     "ra_results": content
    # }
    # data_response = py_requests.post(url_data, data=data)
    # """

    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000"}
    response = Response(content, status=code, headers=header)
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
    response = Response(content, status=code,  headers=header)
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

            classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
                else "research_areas"

            tfidf_cutoff = project["tfidf_cutoff"] if "tfidf_cutoff" in project else None
            similarity_cutoff = project["similarity_cutoff"] if "similarity_cutoff" in project else None

            status_code = add_project_to_database(name, link, description, tfidf_cutoff, similarity_cutoff,
                                                  classification_scheme)
            if status_code != 200:
                code = status_code

        response = Response(status=code, headers=header)
    except ConnectionError:
        response = Response(headers=header)

    return response


@ex_ac_bp.route("/external/addSingleProjectToDatabase", methods=['POST'])
def external_add_one_to_db():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5000", 'ContentType': 'application/json'}

    try:
        name = request.form["name"]
        link = request.form["link"]
        description = request.form["description"]

        classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
            else "research_areas"

        tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
        similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

        code = add_project_to_database(name, link, description, tfidf_cutoff, similarity_cutoff, classification_scheme)

        response = Response(status=code, headers=header)
    except ConnectionError:
        response = Response(headers=header)
    return response


def add_project_to_database(name, link, description, tfidf_cutoff, similarity_cutoff):
    ner = request_ner(name, link, description)
    res_areas = request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, "research_areas")
    sdgs = request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, "sdgs")

    output_data = {
        "name": name,
        "link": link,
        "description": description,
        "ra_results": res_areas,
        "sdg_results": sdgs,
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


def request_esa(name, link, description, tfidf_cutoff, similarity_cutoff, classification_scheme):
    url_new = config.backend_esa + "results"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "tfidf_cutoff": tfidf_cutoff,
        "similarity_cutoff": similarity_cutoff,
        "classification_scheme": classification_scheme
    }

    backend_response = py_requests.post(url_new, data=data)
    content = backend_response.content
    code = backend_response.status_code
    return content, code
