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

in_data_base = input("Enter Database-Name (press enter for '" + data_base_name + "'): ")
data_base_name = in_data_base if in_data_base != '' else data_base_name

print("Please have the csv table with wiki-links for each classification area prepared and saved in " + filepath_base)
in_file_name = input("Enter filename for csv (enter for '" + filename + "'): ")
filepath_csv = filepath_base + in_file_name if in_file_name != '' and path.exists(filepath_base + in_file_name) \
    else filepath_base + filename


def init(data_base_name, table_base_name):

    nltk.download('stopwords')
    nltk.download('punkt')

    try:
        mydb = pymysql.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            database=data_base_name,
            cursorclass=pymysql.cursors.DictCursor
        )

        mycursor = mydb.cursor()
        print("connected")

    except pymysql.ProgrammingError:
        mydb = pymysql.connect(
            host=config.host,
            user=config.user,
            password=config.password,
            cursorclass=pymysql.cursors.DictCursor
        )

        mycursor = mydb.cursor()

        mycursor.execute("CREATE DATABASE " + data_base_name)
        mydb.commit()
        print("created")

    mycursor.execute("SHOW TABLES")

    tables = []
    for x in mycursor:
        tables.append(x["Tables_in_" + data_base_name])
        print(x["Tables_in_" + data_base_name])

    if table_base_name not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas (id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, wos_category TEXT NOT NULL, wos_topic TEXT NOT NULL)")
    if table_base_name + '_vec' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_vec (area_id INTEGER NOT NULL, article_id INTEGER NOT NULL, tf_idf REAL NOT NULL, PRIMARY KEY(area_id, article_id))")
    if table_base_name + '_wiki' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_wiki (id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, wos_category TEXT NOT NULL, wos_topic TEXT NOT NULL, wiki_name TEXT NOT NULL)")
    if table_base_name + '_vec' not in tables:
        mycursor.execute(
            "CREATE TABLE research_areas_wiki_vec (area_id INTEGER NOT NULL, article_id INTEGER NOT NULL, tf_idf REAL NOT NULL, PRIMARY KEY(area_id, article_id))")
    mydb.commit()

    return mydb, mycursor


mydb, mycursor = init(data_base_name, table_base_name)
logging.info("connected to database - all tables available")

api_endpoint = "http://localhost:8888/myapp/"

data_dir = "application/esa_blueprint/static/esa/esa_data/"

esa_db = ESA(data_dir + "esa.db")

# use prepared list of research areas (includes: category, topic, wikipedia page name, wikipedia link)
research_areas = pd.read_csv(filepath_csv, header=None, encoding='utf8', delimiter=";")
research_areas = research_areas.values.tolist()

last_category = ""
last_topic = ""
topic_vec = []

for area in research_areas:
    wos_category = area[0]
    wos_topic = area[1]
    wiki_name = area[2]
    wiki_link = area[3]

    path_to_file = filepath_base + "ref_dump/" + wos_category.replace(" ", "")[:5] + \
                   "/" + wos_topic.replace(" ", "_") + "/" + wiki_name.replace(" ", "") + ".txt"

    # if not path.exists(path_to_file):
    #     import subprocess
    #     subprocess.call(["python", "myscript.py"])

    # research area topic only processed if not saved yet
    mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + wos_topic + '";')
    if mycursor.fetchone() is None:
        # check if wiki text in db
        mycursor.execute('SELECT id FROM research_areas_wiki WHERE wiki_name = "' + wiki_name + '";')

        row_id = mycursor.fetchone()
        if row_id is None:
            # fetch wikipedia text for wiki_name
            with open(path_to_file, "r") as f:
                text = f.read()
                print("Pulled text for: '" + wiki_name + "'")
                logging.debug("Pulled text for %s from ref_dump", wiki_name.upper())
                f.close()

            tokens = esa.text_to_most_important_tokens(text, config.tfidf_extractor, minimum_percentage=0.30)  # extract tokens from text
            vec = esa_db.get_text_vector_from_bow(tokens)  # calculate vec for text

            # add topic to db (wiki!)
            sql = 'INSERT into research_areas_wiki (wos_category, wos_topic, wiki_name) VALUES (%s, %s, %s)'
            val = (wos_category, wos_topic, wiki_name)
            mycursor.execute(sql, val)
            mydb.commit()

            mycursor.execute('SELECT id FROM research_areas_wiki WHERE wiki_name = "' + wiki_name + '";')
            row_id = mycursor.fetchone()["id"]

            # add every vec line to db (wiki)
            print("saving vec -- DO NOT STOP")
            logging.debug("saving wiki-vec for %s .... stand by", wiki_name.upper())
            for key in vec:
                mycursor.execute('INSERT into research_areas_wiki_vec (area_id, article_id, tf_idf) VALUES (' +
                                 str(row_id) + ', ' + str(key) + ', ' + str(vec[key]) + ');')
            mydb.commit()
            print("saving vec: " + wiki_name + " -- DONE")
            logging.debug("saved wiki-vec for %s", wiki_name.upper())
        else:
            print("Already in db: " + wiki_name)
            logging.info("Already in wiki db: %s", wiki_name.upper())

            mycursor.execute('SELECT article_id, tf_idf FROM research_areas_wiki_vec WHERE area_id = ' + str(row_id["id"]) + ';')
            vec = {}
            for pair in mycursor.fetchall():
                vec[pair["article_id"]] = pair["tf_idf"]

        if last_topic == wos_topic:
            # add wiki vectors if they belong to the same wos topic
            topic_vec = esa_db.add_vectors(topic_vec, vec)
        else:
            if not last_topic == "":
                # save computed wos topic to db
                mycursor.execute('INSERT into research_areas (wos_category, wos_topic) VALUES ("' +
                                 last_category + '", "' + last_topic + '");')
                mydb.commit()

                mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + last_topic + '";')
                row_id = mycursor.fetchone()["id"]

                print("saving vec -- DO NOT STOP")
                logging.debug("saving vec for %s .... stand by", last_topic.upper())
                for key in topic_vec:
                    mycursor.execute("INSERT into research_areas_vec (area_id, article_id, tf_idf) VALUES (" +
                                     str(row_id) + ", " + str(key) + ", " + str(topic_vec[key]) + ");")
                mydb.commit()
                print("saving vec: " + last_topic + " -- DONE")
                logging.debug("saved vec for %s", last_topic.upper())
            topic_vec = copy.deepcopy(vec)
            last_topic = wos_topic
            last_category = wos_category

    else:
        print("-- " + wos_topic + " already in db")
        logging.info("Already in RA db: %s", wos_topic.upper())

# save last wos topic
mycursor.execute('INSERT into research_areas (wos_category, wos_topic) VALUES ("' +
                 last_category + '", "' + last_topic + '");')
mydb.commit()

mycursor.execute('SELECT id FROM research_areas WHERE wos_topic = "' + last_topic + '";')
row_id = mycursor.fetchone()["id"]

print("saving vec -- DO NOT STOP")
logging.debug("saving vec for %s .... stand by", last_topic.upper())
for key in topic_vec:
    mycursor.execute("INSERT into research_areas_vec (area_id, article_id, tf_idf) VALUES (" +
                     str(row_id) + ", " + str(key) + ", " + str(topic_vec[key]) + ");")
mydb.commit()
print("saving vec: " + last_topic + " -- DONE")
logging.debug("saved vec for %s", last_topic.upper())
print("ALL DONE")
