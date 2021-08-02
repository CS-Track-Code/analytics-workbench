import pandas as pd

from db_interaction.mongo_interface import MongoInterface
import config

# analysis of zooniverse project; input as excel table including ProjectName and About text
origin_filepath = input("Enter filepath for excel (press 'enter' or enter 'X' to stop programm): ")

while not origin_filepath == "" and not origin_filepath == 'X':
    projects = pd.read_excel(origin_filepath, usecols=['ProjectName', 'Link', 'About']).values.tolist()
    projects_no_duplicates = []
    for z in projects:
        if z not in projects_no_duplicates:
            projects_no_duplicates.append(z)

    mongo_done_projects = MongoInterface(config.pymongo_clientport, config.pymongo_client_name, config.projects_db)

    for project in projects_no_duplicates:
        name = project[0]
        link = project[1]
        about = project[2]
        if mongo_done_projects.check_for_description(name, link) is None:
            mongo_done_projects.save_new_project(name, link, about)

    origin_filepath = input("Enter filepath for excel (press 'enter' or enter 'X' to stop programm): ")
