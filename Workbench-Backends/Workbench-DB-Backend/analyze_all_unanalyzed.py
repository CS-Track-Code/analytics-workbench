import pymongo
import requests as py_requests
import json

###########
"""Edit to point to API"""
API_address = "http://localhost:5001/external/analyse"
API_address = "https://workbench.rias-institute.eu/api/getAnalysisResults"
AUTH = ('rias', 'cstrack')

"""Edit According to Database"""
pymongo_clientport = '27017'
pymongo_client_name = "data_collection"

db_name = "projects_22_06_01-zooniverse-List"
###########


def analysis_results_exist(project):
    """
    should check if the project object from the database contains ner and esa result
    and return a corresponding boolean value
    """
    if "ner_results" in project and "ra_results" in project and "sdg_results" in project:
        return True
    return False


def safe_analysis_results(mongo_collection, project, ra_results, sdg_results, ner_results):
    """
    meant to save the newly acquired esa and ner results to the database
    """
    mongo_collection.update_one({"_id": project["_id"]}, {'$set': {"ra_results": ra_results,
                                                                   "sdg_results": sdg_results,
                                                                   "ner_results": ner_results}})
    pass


def get_project_data(project):
    """
    meant to extract project_name, project_link and description from the project object from the database
    """
    return project["project_name"], project["project_link"], project["description"]

###########


client = pymongo.MongoClient("mongodb://localhost:{}/".format(pymongo_clientport))
db = client[pymongo_client_name]
data_collection = db[db_name]

project_list = data_collection.find()

for project in project_list:
    if not analysis_results_exist(project):
        print(project["project_name"])
        project_name, project_link, description = get_project_data(project)
        data = {
            "name": project_name,
            "link": project_link,
            "description": description
        }

        data_response = py_requests.post(API_address, data=data, auth=AUTH)  # Todo: catch 500 error (wait and retry? alert to error?)
        content = json.loads(data_response.content)
        ra_results = content["ra_results"]
        sdg_results = content["sdg_results"]
        ner_results = content["ner_results"]
        safe_analysis_results(data_collection, project, ra_results, sdg_results, ner_results)
