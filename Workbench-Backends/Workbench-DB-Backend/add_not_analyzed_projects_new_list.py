import pandas as pd
import ast
import numpy as np

from db_interaction.mongo_interface import MongoInterface
import config

# analysis of zooniverse project; input as excel table including ProjectName and About text
origin_filepath = input("Enter filepath for excel (press 'enter' or enter 'X' to stop programm): ")

while not origin_filepath == "" and not origin_filepath == 'X':
    # projects = pd.read_excel(origin_filepath, usecols=['ProjectName', 'Link', 'About']).values.tolist()
    projects = pd.read_excel(origin_filepath, usecols=['Description', 'Title', 'URL Platform']).values.tolist()

    projects_no_duplicates = []
    for z in projects:
        if z not in projects_no_duplicates:
            projects_no_duplicates.append(z)

    mongo_done_projects = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)

    for project in projects_no_duplicates:
        has_nan = False
        for elem in project:
            if type(elem) == float and np.isnan(elem):
                has_nan = True
        if not has_nan:
            name = project[1]
            try:
                link = [elem for elem in project[2].split('"') if elem.startswith("http")]
                link = "\n ".join(link)
                if project[0].startswith("["):
                    about = [elem for elem in ast.literal_eval(project[0].replace('" "', '", "')) if type(elem) == str]
                    about = "\n ".join(about)
                else:
                    about = project[0]
                if mongo_done_projects.check_for_description(name, link) is None and len(link) > 0:
                    mongo_done_projects.save_new_project(name, link, about)
            except SyntaxError:
                print("Couldn't process project: \t" + name)

    origin_filepath = input("Enter filepath for excel (press 'enter' or enter 'X' to stop programm): ")
