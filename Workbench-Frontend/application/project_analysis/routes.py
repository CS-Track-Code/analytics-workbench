from flask import Blueprint, render_template, request
from werkzeug.wrappers import Response
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

        response = Response(esa_data, status=200)

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
    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"

    url = config.middleware + "esa"
    data = {
        "name": name,
        "link": link,
        "description": description,
        "classification_scheme": classification_scheme
    }

    middleware_response = py_requests.post(url, data=data, timeout=125)

    esa_data = middleware_response.content

    response = Response(esa_data, status=200)

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
        ra_res = request.form["ra_res"]

        url_data = config.middleware + "esa/changes"
        data = {
            "name": name,
            "link": link,
            "description": description,
            "ra_results": ra_res
        }
        data_response = py_requests.post(url_data, data=data)
        content = data_response.content

        response = Response(content, status=200)
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

    response = Response(ner_data, status=200)
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

        response = Response(content, status=200)
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

    response = Response(content, status=200)
    return response


@project_analysis_bp.route('/analyse/project/sdg_names', methods=['GET'])
def get_sdg_names():
    sdgs = {
        "SDG #1": "SDG #01 - No Poverty",
        "SDG #2": "SDG #02 - Zero Hunger",
        "SDG #3": "SDG #03 - Good Health and Well-Being",
        "SDG #4": "SDG #04 - Quality Education",
        "SDG #5": "SDG #05 - Gender Equality",
        "SDG #6": "SDG #06 - Clean Water and Sanitation",
        "SDG #7": "SDG #07 - Affordable and Clean Energy",
        "SDG #8": "SDG #08 - Decent Work and Economic Growth",
        "SDG #9": "SDG #09 - Industry, Innovation and Infrastructure",
        "SDG #10": "SDG #10 - Reduced Inequalities",
        "SDG #11": "SDG #11 - Sustainable Cities and Communities",
        "SDG #12": "SDG #12 - Responsible Consumption and Production",
        "SDG #13": "SDG #13 - Climate Action",
        "SDG #14": "SDG #14 - Life Below Water",
        "SDG #15": "SDG #15 - Life on Land",
        "SDG #16": "SDG #16 - Peace, Justice and Strong Institutions",
        "SDG #17": "SDG #17 - Partnerships for the Goals"
    }

    json_result = json.dumps(sdgs)
    response = Response(json_result)

    return response
