import pymongo

import config

current_mongo = config.mongo

client = pymongo.MongoClient("mongodb://localhost:{}/".format(config.pymongo_clientport))
db = client[config.pymongo_client_name]
data_collection = db[config.projects_db]

project_list = current_mongo.get_complete_project_list()
for project in project_list:
    changed = False
    if "esa_results" in project:
        new_project = {
            "project_name": project["project_name"],
            "project_link": project["project_link"],
            "description": project["description"]
        }

        for i in ["ner_results", "esa_results"]:
            if i in project:
                new_project[i.replace("esa", "ra")] = project[i]
            if config.user_prefix + i in project:
                new_project[config.user_prefix + i.replace("esa", "ra")] = project[config.user_prefix + i]

        project = new_project
        changed = True

    if "ra_results" in project and "top_research_areas_with_sim" in project["ra_results"]:
        top = project["ra_results"]["top_research_areas_with_sim"]
        all = project["ra_results"]["research_areas_with_sim_list"]
        tokens = project["ra_results"]["used_tokens"]
        project["ra_results"] = {
            "top_classification_areas_with_sim": top,
            "classification_areas_with_sim_list": all,
            "used_tokens": tokens
        }
        changed = True

    if config.user_prefix + "ra_results" in project and "top_research_areas_with_sim" in project["ra_results"]:
        top = project[config.user_prefix + "ra_results"]["top_research_areas_with_sim"]
        all = project[config.user_prefix + "ra_results"]["research_areas_with_sim_list"]
        tokens = project[config.user_prefix + "ra_results"]["used_tokens"]
        project[config.user_prefix + "ra_results"] = {
            "top_classification_areas_with_sim": top,
            "classification_areas_with_sim_list": all,
            "used_tokens": tokens,
            "classification_scheme": "research_areas"
        }
        changed = True

    if changed:
        project_id = project["_id"]
        project.pop("_id")
        data_collection.delete_one({"_id": project_id})

        data_collection.insert_one(project)
