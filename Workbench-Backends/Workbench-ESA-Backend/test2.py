import pandas as pd
import copy
import pymysql
import nltk
from os import path
import logging

from esa_analysis import esa
from esa_analysis.esa import ESA
from text_extraction import mercury_web_parser as Mercury
import config_esa as config

###
"""Edit to prepare other Comparison Bases (like SDGs)"""
data_base_name = config.research_area_database
table_base_name = "research_areas"  # name currently necessary for analysis!

filepath_base = "application/esa_blueprint/static/esa/esa_data/"
filename = "research_areas.csv"
filepath_csv = filepath_base + filename
###

logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

print("Please have the csv table with wiki-links for each classification area prepared and saved in " + filepath_base)
in_file_name = input("Enter filename for csv (enter for '" + filename + "'): ")
filepath_csv = filepath_base + in_file_name if in_file_name != '' and path.exists(filepath_base + in_file_name) \
    else filepath_base + filename

api_endpoint = "http://192.168.2.30:8888/myapp/"

data_dir = "application/esa_blueprint/static/esa/esa_data/"

esa_db = ESA(data_dir + "esa.db")

# use prepared list of research areas (includes: category, topic, wikipedia page name, wikipedia link)
research_areas = pd.read_csv(filepath_csv, header=None, encoding='utf8', delimiter=";")
research_areas = research_areas.values.tolist()

last_category = ""
last_topic = ""
topic_vec = []

old_wiki = {
    "SDG #1": "https://en.wikipedia.org/w/index.php?title=Sustainable_Development_Goal_1&oldid=1047535389",
    "SDG #2": "https://en.wikipedia.org/w/index.php?title=Sustainable_Development_Goal_2&oldid=1047844687",
    "SDG #3": "https://en.wikipedia.org/w/index.php?title=Sustainable_Development_Goal_3&oldid=1043645976"
}

for area in research_areas:
    wos_category = area[0]
    wos_topic = area[1]
    wiki_name = area[2]
    wiki_link = area[3]

    path_to_file = filepath_base + "ref_dump/" + wos_category.replace(" ", "")[:5] + \
                   "/" + wos_topic.replace(" ", "_") + "/" + wiki_name.replace(" ", "") + ".txt"

    # fetch wikipedia text for wiki_name
    with open(path_to_file, "r") as f:
        text = f.read()
        print("Pulled text for: '" + wiki_name + "'")
        logging.debug("Pulled text for %s from ref_dump", wiki_name.upper())
        f.close()

    tokens = esa.text_to_most_important_tokens(text, config.tfidf_extractor, minimum_percentage=0.20)  # extract tokens from text
    save_file = "test" + "/current_" + wiki_name.replace(" ", "") + ".txt"
    with open(save_file, "a") as f:
        f.write(str(tokens))
        f.close()

    text = Mercury.extract_wiki_without_ref(api_endpoint, old_wiki[wos_topic])
    tokens = esa.text_to_most_important_tokens(text, config.tfidf_extractor,
                                               minimum_percentage=0.20)  # extract tokens from text
    save_file = "test" + "/oct_" + wiki_name.replace(" ", "") + ".txt"
    with open(save_file, "a") as f:
        f.write(str(tokens))
        f.close()


