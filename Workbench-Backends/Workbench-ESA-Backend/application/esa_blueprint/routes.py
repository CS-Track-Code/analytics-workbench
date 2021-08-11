from flask import Blueprint, request
from werkzeug.wrappers import Response
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

    classification_scheme = request.form["classification_scheme"] if "classification_scheme" in request.form \
        else "research_areas"

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    print("## ANALYSE ##\n" + name)

    if similarity_cutoff is not None:
        try:
            similarity_cutoff = float(similarity_cutoff)
        except ValueError:
            similarity_cutoff = None

    if tfidf_cutoff is not None:
        try:
            tfidf_cutoff = float(tfidf_cutoff)
        except ValueError:
            tfidf_cutoff = None

    result = get_esa_results(description, classification_scheme, tfidf_cutoff, similarity_cutoff)


    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, headers=header)
    print(response)

    return response


@esa_bp.route("/getResearchAreas", methods=['POST'])
def esa_results():
    name = request.form["name"]
    description = request.form["description"]

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    print("## ANALYSE ##\n" + name)

    result = get_esa_results(description, "research_areas", tfidf_cutoff, similarity_cutoff)

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, headers=header)
    print(response)

    return response


@esa_bp.route("/getSDGs", methods=['POST'])
def sdg_results():
    name = request.form["name"]
    description = request.form["description"]

    tfidf_cutoff = request.form["tfidf_cutoff"] if "tfidf_cutoff" in request.form else None
    similarity_cutoff = request.form["similarity_cutoff"] if "similarity_cutoff" in request.form else None

    print("## ANALYSE ##\n" + name)

    result = get_esa_results(description, "sdgs", tfidf_cutoff, similarity_cutoff)

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, headers=header)
    print(response)

    return response


def get_esa_results(description, classification_scheme, tfidf_cutoff, similarity_cutoff):
    if classification_scheme == "sdgs":
        database = config.database_sdgs
    else:
        database = config.database_research_areas

    classification_areas = config.preloaded[database]["classification_areas"]
    classification_wikis = config.preloaded[database]["classification_area_wikis"]
    classification_area_vectors = config.preloaded[database]["classification_area_vectors"]
    classification_esa = ClassificationESA(config.esa_db_path, config.host, config.user, config.password, database,
                                           classification_areas, classification_wikis, classification_area_vectors)

    tfidf_cutoff = tfidf_cutoff if isinstance(tfidf_cutoff, float) and 0 <= tfidf_cutoff < 1 \
        else config.esa_cutoffs[database]["esa_tf_proportion"]
    similarity_cutoff = similarity_cutoff if isinstance(similarity_cutoff, float) and 0 <= similarity_cutoff < 1 \
        else config.esa_cutoffs[database]["esa_cutoff_in_relation_to_max"]

    classification_esa = analyse.setup_classification_area_esa(classification_esa, config.host, config.user,
                                                               config.password, database, edits=True, top=None,
                                                               cutoff_in_relation_to_max=similarity_cutoff,
                                                               sort=True, tfidf_proportion=tfidf_cutoff)

    classification_areas_similarity_shortlist, classification_areas_with_sim_list, categories_with_count, \
    top_category, db_classification_areas, tokens = \
        analyse.get_classification_areas_esa_with_dbpedia_integrated(description, config.host, config.user,
                                                                     config.password, database,
                                                                     config.tfidf_extractor, classification_esa,
                                                                     similarity_cutoff)

    result = {
        "top_classification_areas_with_sim": classification_areas_similarity_shortlist,
        "classification_areas_with_sim_list": classification_areas_with_sim_list,
        "used_tokens": tokens,
        "classification_scheme": classification_scheme
    }

    return result


@esa_bp.route("/research_areas")
def get_research_areas():
    research_area_list = [r[2] for r in config.research_areas]

    json_result = json.dumps(research_area_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)
    print(response)

    return response


@esa_bp.route("/SDGs")
def get_sdgs():
    sdg_area_list = [r[2] for r in config.sdg_areas]

    json_result = json.dumps(sdg_area_list)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = Response(json_result, status=200, headers=header)
    print(response)

    return response
