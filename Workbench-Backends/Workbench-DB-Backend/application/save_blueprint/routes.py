from flask import Blueprint, request
from werkzeug.wrappers import BaseResponse
import json

from db_interaction.mongo_interface import MongoInterface
import config

# Blueprint Configuration
save_bp = Blueprint(
    'save_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@save_bp.route('/data/project', methods=['POST'])
def get_project_data():
    project_name = request.form["project_name"]
    mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
    if "whole_data" in request.form:
        whole_data = request.form["whole_data"]
        project_description, project_link, ra_res, ner_res = mongo.get_project_data(project_name,
                                                                                     whole_data=whole_data)
    else:
        project_link = request.form["link"]
        project_description = None
        if "description" in request.form:
            project_description = request.form["description"]
        project_description, project_link, \
        ra_res, ner_res = mongo.get_project_data(project_name, project_link=project_link,
                                                  project_description=project_description)

    result = {
        "project_name": project_name,
        "project_link": project_link,
        "project_description": project_description,
        "ra_results": ra_res,
        "ner_results": ner_res
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)

    return response


@save_bp.route('/data/project-description', methods=['POST'])
def get_project_description():
    project_name = request.form["name"]
    project_link = request.form["link"]
    mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
    project_description = mongo.check_for_description(project_name, project_link)

    result = {
        "name": project_name,
        "project_link": project_link,
        "project_description": project_description
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)

    return response


@save_bp.route('/data/project-analysis', methods=['POST'])
def get_project_analysis_results():
    project_name = request.form["name"]
    project_link = request.form["link"]
    project_description = request.form["description"]
    mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
    ra_res, ner_res = mongo.get_analysis_results(project_name, project_link, project_description)

    result = {
        "name": project_name,
        "project_link": project_link,
        "project_description": project_description,
        "ra_results": ra_res,
        "ner_results": ner_res
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)

    return response


@save_bp.route('/data/save-new-project', methods=['POST'])
def save_new_project():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001", 'ContentType': 'application/json'}

    try:
        project_name = request.form["name"]
        project_link = request.form["link"]
        project_description = request.form["description"]

        mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
        mongo.save_new_project(project_name, project_link, project_description)

        response = BaseResponse(status=200, headers=header)
    except OSError:
        response = BaseResponse(headers=header)

    return response


@save_bp.route('/data/save-updates', methods=['POST'])
def update_project_data():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001", 'ContentType': 'application/json'}

    try:
        project_name = request.form["name"]
        project_link = request.form["link"]
        project_description = request.form["description"]
        user_generated = False
        if "user_generated" in request.form:
            user_generated = request.form["user_generated"]
        ra_results = None
        if "ra_results" in request.form:
            ra_results = json.loads(request.form["ra_results"])
        ner_results = None
        if "ner_results" in request.form:
            ner_results = json.loads(request.form["ner_results"])

        mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
        mongo.update_project_data(project_name, project_link, user_generated, project_description,
                                  ra_results, ner_results)

        response = BaseResponse(status=200, headers=header)
    except OSError:
        response = BaseResponse(headers=header)

    return response


@save_bp.route('/data/save-complete-project', methods=['POST'])
def save_complete_project():
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001", 'ContentType': 'application/json'}

    try:
        project_name = request.form["name"]
        project_link = request.form["link"]
        project_description = request.form["description"]
        ra_results = json.loads(request.form["ra_results"])
        ner_results = json.loads(request.form["ner_results"])

        mongo = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)
        mongo.save_new_project_with_results(project_name, project_link, project_description, ra_results, ner_results)

        response = BaseResponse(status=200, headers=header)
    except OSError:
        response = BaseResponse(headers=header)

    return response
