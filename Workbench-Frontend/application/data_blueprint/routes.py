from flask import Blueprint, render_template, request
from werkzeug.wrappers import Response
import requests as py_requests
import json

import config

# Blueprint Configuration
data_bp = Blueprint(
    'data_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@data_bp.route("/data-dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        title="Explore Data - Dashboard"
    )


@data_bp.route("/data/dashboard-data")
def get_dashboard_data():
    url = config.middleware + "db/evaluation_data"
    data = {}
    data_response = py_requests.get(url, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response


@data_bp.route("/data/recommendations", methods=['POST'])
def get_recommendations():
    visited_list = modified_list = fave_list = None
    if "visited_list" in request.form:
        visited_list = request.form["visited_list"]
    if "modified_list" in request.form:
        modified_list = request.form["modified_list"]
    if "fave_list" in request.form:
        fave_list = request.form["fave_list"]

    url = config.middleware + "db/recommendations"
    data = {
        "visited_list": visited_list,
        "modified_list": modified_list,
        "fave_list": fave_list
    }

    data_response = py_requests.post(url, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response


@data_bp.route("/data/generate-recommendation")
def generate_recommendation():
    return render_template(
        "user_gen_recommendation.html",
        title="Find a project like"
    )


@data_bp.route("/data/research_areas")
def get_research_areas():
    url_data = config.middleware + "esa/research_areas"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response


@data_bp.route("/data/sdgs")
def get_sdgs():
    url_data = config.middleware + "esa/sdgs"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    content = data_response.content

    response = Response(content, status=200)
    return response