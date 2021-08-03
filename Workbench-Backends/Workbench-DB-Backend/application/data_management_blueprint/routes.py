import pymongo
from flask import Blueprint, request
from werkzeug.wrappers import BaseResponse
import json

import config

# Blueprint Configuration
data_management_bp = Blueprint(
    'data_management_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@data_management_bp.route('/data_man/drop_current')
def drop_current():
    passphrase_correct = False
    if passphrase_correct:
        current_mongo = config.mongo

        client = pymongo.MongoClient("mongodb://localhost:{}/".format(config.pymongo_clientport))
        db = client[config.pymongo_client_name]
        data_collection = db[config.eval_db]

        project_list = current_mongo.get_complete_projects_with_user_generated_data()
        for project in project_list:
            data_collection.insert_one(project)

        data_collection = db[config.projects_db]
        data_collection.delete_many({})
