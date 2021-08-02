import json

from flask import Blueprint, request
from spacy_ner.spacy_ner import SpacyNer
from werkzeug.wrappers import BaseResponse

import config

# Blueprint Configuration
spacy_bp = Blueprint(
    'spacy_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@spacy_bp.route("/get_ners", methods=['POST'])
def get_ners():
    description = request.form["description"]
    # print(description)

    lang = "en"  # TODO: Language!

    spacy = SpacyNer(lang, config.spacy_model_path, config.training_data_path)
    ner_list = spacy.process_text_get_filtered_results(description)
    all_descriptors = spacy.get_descriptors_list()
    # print(ner_list)

    result = {
        "ner_list": ner_list,
        "all_descriptors": all_descriptors
    }

    json_result = json.dumps(result)
    header = {"Access-Control-Allow-Origin": "http://192.168.2.140:5001"}
    response = BaseResponse(json_result, status=200, headers=header)
    # print(response)

    return response
