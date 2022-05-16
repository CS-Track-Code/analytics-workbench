import pandas as pd
import copy
import pymysql
import nltk
from os import path, mkdir

from esa_analysis import esa
from esa_analysis.esa import ESA
from text_extraction import mercury_web_parser as Mercury
import config_esa as config

###
"""Edit to prepare other Comparison Bases (like SDGs)"""
filepath_base = "application/esa_blueprint/static/esa/esa_data/"
filename = "research_areas.csv"
filepath_csv = filepath_base + filename
###


print("Please have the csv table with wiki-links for each classification area prepared and saved in " + filepath_base)
in_file_name = input("Enter filename for csv (enter for '" + filename + "'): ")
filepath_csv = filepath_base + in_file_name if in_file_name != '' and path.exists(filepath_base + in_file_name) \
    else filepath_base + filename

# use prepared list of research areas (includes: category, topic, wikipedia page name, wikipedia link)
research_areas = pd.read_csv(filepath_csv, header=None, encoding='utf8', delimiter=";")
research_areas = research_areas.values.tolist()

api_endpoint = "http://192.168.2.30:8888/myapp/"

last_category = ""
last_topic = ""
topic_vec = []

for area in research_areas:
    wos_category = area[0]
    wos_topic = area[1]
    wiki_name = area[2]
    wiki_link = area[3]

    path_to_file = filepath_base + "ref_dump/" + wos_category.replace(" ", "")[:5]
    if not path.exists(path_to_file):
        mkdir(path_to_file)
    path_to_file += "/" + wos_topic.replace(" ", "_")
    if not path.exists(path_to_file):
        mkdir(path_to_file)
    save_file = path_to_file + "/" + wiki_name.replace(" ", "") + ".txt"

    if not path.exists(save_file):
        # fetch wikipedia text for wiki_name
        text = Mercury.extract_wiki_without_ref(api_endpoint, wiki_link)

        with open(save_file, "a") as f:
            f.write(text)
            print("Pulled text for: '" + str(area) + "'")
            f.close()



