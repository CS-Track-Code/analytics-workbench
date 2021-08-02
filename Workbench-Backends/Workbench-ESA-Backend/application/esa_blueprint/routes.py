from flask import Blueprint, request
import requests as py_requests
from werkzeug.wrappers import BaseResponse
import json

from esa_analysis import analyse
from esa_analysis.classification_esa import ClassificationESA
import setup_esa as config


# Blueprint Configuration
esa_bp = Blueprint(
    'esa_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@esa_bp.route("/results", methods=['POST'])
def results():
    name = request.form["name"]
    description = request.form["description"]
    if "classification_scheme" in request.form:
        classification_scheme = request.form["classification_scheme"]
    else:
        classification_scheme = "research_areas"
    print("## ANALYSE ##\n" + name)

    result = get_esa_results(description, classification_scheme)


    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    print(response)

    return response


@esa_bp.route("/getResearchAreas", methods=['POST'])
def esa_results():
    name = request.form["name"]
    description = request.form["description"]
    print("## ANALYSE ##\n" + name)

    result = get_esa_results(description, "research_areas")

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    print(response)

    return response


@esa_bp.route("/getSDGs", methods=['POST'])
def sdg_results():
    name = request.form["name"]
    description = request.form["description"]
    print("## ANALYSE ##\n" + name)

    result = get_esa_results(description, "sdgs")

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    print(response)

    return response


def get_esa_results(description, classification_scheme):
    if classification_scheme == "sdgs":
        database = config.database_sdgs
        classification_areas = config.sdg_areas
        classification_wikis = config.sdg_area_wikis
        classification_area_vectors = config.sdg_area_vectors
        classification_esa = ClassificationESA(config.esa_db_path, config.host, config.user, config.password, database,
                                               classification_areas, classification_wikis, classification_area_vectors)
        classification_areas_similarity_shortlist, classification_areas_with_sim_list, categories_with_count, \
        top_category, db_classification_areas, tokens = \
            analyse.get_classification_areas_esa_with_dbpedia_integrated(description, config.host, config.user,
                                                                         config.password, database,
                                                                         config.tfidf_extractor, classification_esa,
                                                                         config.esa_cutoff_in_relation_to_max)

        result = {
            "top_classification_areas_with_sim": classification_areas_similarity_shortlist,
            "classification_areas_with_sim_list": classification_areas_with_sim_list,
            "used_tokens": tokens
        }
    else:

        research_areas_esa = ClassificationESA(config.esa_db_path, config.host, config.user, config.password,
                                               config.database_research_areas, config.research_areas,
                                               config.research_area_wikis, config.research_area_vectors)
        research_areas_similarity_shortlist, res_areas_with_sim_list, categories_with_count, top_category, \
        db_research_areas, tokens = \
            analyse.get_research_areas_esa_with_dbpedia_integrated(description, config.host, config.user, config.password,
                                                                   config.database_research_areas, config.tfidf_extractor,
                                                                   research_areas_esa, config.esa_cutoff_in_relation_to_max)

        result = {
            "top_research_areas_with_sim": research_areas_similarity_shortlist,
            "research_areas_with_sim_list": res_areas_with_sim_list,
            "used_tokens": tokens
        }

    return result


@esa_bp.route("/research_areas")
def get_research_areas():
    research_area_list = [r[2] for r in config.research_areas]

    json_result = json.dumps(research_area_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    print(response)

    return response


@esa_bp.route("/SDGs")
def get_sdgs():
    sdg_area_list = [r[2] for r in config.sdg_areas]

    json_result = json.dumps(sdg_area_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    print(response)

    return response
