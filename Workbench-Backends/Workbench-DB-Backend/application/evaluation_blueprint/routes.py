from flask import Blueprint, request
from werkzeug.wrappers import Response
import json

import config

# Blueprint Configuration
evaluation_bp = Blueprint(
    'evaluation_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@evaluation_bp.route("/evaluation/project-names")
def get_project_names():
    safe = config.safe_for_list_and_networks
    names_list = safe.get_project_name_list()
    json_result = json.dumps(names_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)

    return response


@evaluation_bp.route("/evaluation/tba-projects")
def get_tba_project_names():
    safe = config.safe_for_list_and_networks
    names_list = safe.get_tba_project_names()
    json_result = json.dumps(names_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)

    return response


@evaluation_bp.route("/evaluation/recommendation", methods=['POST'])
def get_recommendations():
    visited_list = modified_list = fave_list = []
    if "visited_list" in request.form:
        visited_list = json.loads(request.form["visited_list"])
    if "modified_list" in request.form:
        modified_list = json.loads(request.form["modified_list"])
    if "fave_list" in request.form:
        fave_list = json.loads(request.form["fave_list"])

    safe = config.safe_for_list_and_networks
    recommendations = safe.get_project_recommendations(fave_list, modified_list, visited_list)
    result = {
        "recommendations": recommendations
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)
    print(response)

    return response


@evaluation_bp.route("/evaluation/data")
def get_evaluation_data():
    safe = config.safe_for_list_and_networks
    safe.check_if_current()

    project_count = safe.get_project_count()
    ra_numbers, sdg_numbers, ne_numbers = safe.get_numbers_of_ra_sdg_ne()
    ra_occurances = safe.get_ra_occurances()
    sdg_occurances = safe.get_sdg_occurances()
    ne_occurances = safe.get_ne_occurances()
    vis_projects = safe.convert_network_to_vis(safe.get_folded_project_network())
    vis_p_ra = safe.convert_network_to_vis(safe.get_ra_network())
    vis_complete = safe.convert_network_to_vis(safe.get_complete_network())
    vis_leafless = safe.convert_network_to_vis(safe.get_leafless_network())

    result = {
        "project_count": project_count,
        "ra_numbers": ra_numbers,
        "sdg_numbers": sdg_numbers,
        "ne_numbers": ne_numbers,
        "ra_occurances": ra_occurances,
        "sdg_occurances": sdg_occurances,
        "ne_occurances": ne_occurances,
        "vis_projects": vis_projects,
        "vis_projects_and_ras": vis_p_ra,
        "vis_complete": vis_complete,
        "vis_leafless": vis_leafless
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)

    return response
