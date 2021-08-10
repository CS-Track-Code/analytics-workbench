import pymongo


class MongoInterface:
    def __init__(self, pymongo_clientport, pymongo_client_name, db_name="projects", user_prefix="user_"):

        self.client = pymongo.MongoClient("mongodb://localhost:{}/".format(pymongo_clientport))
        self.db = self.client[pymongo_client_name]
        self.data_collection = self.db[db_name]

        self.user_prefix = user_prefix

    def check_for_description(self, project_name, project_link, user_generated=True):
        description, link, ra_res, ner_res = self.get_project_data(project_name, project_link,
                                                                    user_generated=user_generated)
        return description

    def get_analysis_results(self, project_name, project_link, project_description, user_generated=True):
        description, link, ra_res, ner_res = self.get_project_data(project_name, project_link, project_description,
                                                                    user_generated=user_generated)
        return ra_res, ner_res

    def get_project_data(self, project_name, project_link="", project_description=None, user_generated=True,
                         whole_data=False):
        result = self.data_collection.find_one({"project_name": project_name})
        if result is None:
            result = self.data_collection.find_one({"project_link": project_link})
        # TODO: change to similar instead of equal
        if result is None:
            if project_description is not None:
                self.save_new_project(project_name, project_link, project_description)
            return None, None, None, None
        elif result["description"] != project_description and not whole_data:
            if project_description is not None and project_description != "":
                self.update_project_data(None, project_link, False, project_description)
            return result["description"], result["project_link"], None, None
        else:
            if user_generated and self.user_prefix + "ra_results" in result:
                ra_res = result[self.user_prefix + "ra_results"]
            elif "ra_results" in result:
                ra_res = result["ra_results"]
            else:
                ra_res = None
            if user_generated and self.user_prefix + "ner_results" in result:
                ner_res = result[self.user_prefix + "ner_results"]
            elif "ner_results" in result:
                ner_res = result["ner_results"]
            else:
                ner_res = None
            return result["description"], result["project_link"], ra_res, ner_res

    def save_new_project_with_results(self, project_name, project_link, description, ra_results, ner_results):
        if self.data_collection.find_one({"project_name": project_name}) is None and self.data_collection.\
                find_one({"project_link": project_link}) is None:
            mongo_item = {
                "project_name": project_name,
                "project_link": project_link,
                "description": description,
                "ra_results": ra_results,
                "ner_results": ner_results
            }

            self.data_collection.insert_one(mongo_item)

    def save_new_project(self, project_name, project_link, description):
        condition = self.data_collection.find_one({"project_link": project_link}) is None
        if project_name is not None:
            condition = condition and self.data_collection.find_one({"project_name": project_name}) is None
        if condition:
            mongo_item = {
                "project_name": project_name,
                "project_link": project_link,
                "description": description
            }

            self.data_collection.insert_one(mongo_item)

    def update_project_data(self, project_name, project_link, user_generated, project_description=None,
                            ra_results=None, ner_results=None):
        existing_project_data = self.data_collection.find_one({"project_name": project_name})
        if existing_project_data is None:
            existing_project_data = self.data_collection.find_one({"project_link": project_link})
        if existing_project_data is None:
            self.save_new_project(project_name, project_link, project_description)
            existing_project_data = self.data_collection.find_one({"project_link": project_link})
        project_id = existing_project_data["_id"]
        prefix = ""
        if user_generated and project_description == existing_project_data["description"]:
            prefix = self.user_prefix

        if project_description is not None and project_description != existing_project_data["description"]:
            self.data_collection.update_one({"_id": project_id}, {'$set': {"description": project_description}})

        if ra_results is not None and ner_results is not None:
            self.data_collection.update_one({"_id": project_id}, {'$set': {prefix + "ra_results": ra_results,
                                                                           prefix + "ner_results": ner_results}})
        elif ra_results is not None:
            self.data_collection.update_one({"_id": project_id}, {'$set': {prefix + "ra_results": ra_results}})
        elif ner_results is not None:
            self.data_collection.update_one({"_id": project_id}, {'$set': {prefix + "ner_results": ner_results}})

    def get_projects_with_user_generated_data(self):
        project_list = self.data_collection.find()
        filtered_list = []
        for project in project_list:
            if "project_name" in project and project["project_name"] is not None:
                project_name = project["project_name"]
            else:
                project_name = project["project_link"]
            if self.user_prefix + "ra_results" in project:
                ra_res = project[self.user_prefix + "ra_results"]
            elif "ra_results" in project:
                ra_res = project["ra_results"]
            else:
                ra_res = None
            if self.user_prefix + "ner_results" in project:
                ner_res = project[self.user_prefix + "ner_results"]
            elif "ner_results" in project:
                ner_res = project["ner_results"]
            else:
                ner_res = None

            simplified_project = {
                "project_name": project_name,
                "ra_results": ra_res,
                "ner_results": ner_res
            }

            filtered_list.append(simplified_project)
        return filtered_list

    def get_complete_projects_with_user_generated_data(self):
        project_list = self.data_collection.find()
        filtered_list = []
        for project in project_list:
            if self.user_prefix + "ra_results" in project or self.user_prefix + "ner_results" in project:
                filtered_list.append(project)
        return filtered_list

    def get_complete_project_list(self):
        return self.data_collection.find()

    def delete_project(self, project_name, project_link):
        existing_project_data = self.data_collection.delete_one({"project_name": project_name,
                                                                 "project_link": project_link})
