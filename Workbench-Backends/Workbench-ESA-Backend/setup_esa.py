import mysql
from esa_analysis.classification_esa import ClassificationESA
import gc

import config_esa

preload_vectors = False

host = config_esa.host
user = config_esa.user
password = config_esa.password

database_research_areas = config_esa.research_area_database
database_sdgs = config_esa.sdg_database

databases = {
    "esa_research_areas": database_research_areas,
    "esa_sdgs":database_sdgs
}

# TFIDF #
tfidf_model_path = config_esa.tfidf_model_path
tfidf_extractor = config_esa.tfidf_extractor

# ESA: #
esa_tf_proportion = config_esa.esa_tf_proportion
esa_sort = config_esa.esa_sort
esa_cutoff_in_relation_to_max = config_esa.esa_cutoff_in_relation_to_max
esa_db_path = config_esa.esa_db_path

esa_cutoffs = config_esa.esa_cutoffs

research_areas_esa = ClassificationESA(esa_db_path, host, user, password, database_research_areas)
research_areas = research_areas_esa.get_classification_areas()
research_area_wikis = research_areas_esa.get_classification_area_wikis()

sdg_esa = ClassificationESA(esa_db_path, host, user, password, database_sdgs)
sdg_areas = sdg_esa.get_classification_areas()
sdg_area_wikis = sdg_esa.get_classification_area_wikis()

if preload_vectors:
    print("## Setup Research Areas ##")
    research_area_vectors = research_areas_esa.get_classification_area_vectors()

    print("## Setup SDGs ##")
    sdg_area_vectors = sdg_esa.get_classification_area_vectors()

    preloaded = {
        "esa_research_areas": {
            "classification_esa": research_areas_esa,
            "classification_areas": research_areas,
            "classification_area_wikis": research_area_wikis,
            "classification_area_vectors": research_area_vectors
        },
        "esa_sdgs": {
            "classification_esa": sdg_esa,
            "classification_areas": sdg_areas,
            "classification_area_wikis": sdg_area_wikis,
            "classification_area_vectors": sdg_area_vectors
        }
    }
else:
    preloaded = {
        "esa_research_areas": {
            "classification_esa": research_areas_esa,
            "classification_areas": research_areas,
            "classification_area_wikis": research_area_wikis
        },
        "esa_sdgs": {
            "classification_esa": sdg_esa,
            "classification_areas": sdg_areas,
            "classification_area_wikis": sdg_area_wikis
        }
    }
print("done")


def get_classification_esa(classification_scheme):
    gc.collect(generation=2)
    if preload_vectors:
        classification_esa = ClassificationESA(esa_db_path, host, user, password, databases[classification_scheme],
                                               preloaded[classification_scheme]["classification_areas"],
                                               preloaded[classification_scheme]["classification_area_wikis"],
                                               preloaded[classification_scheme]["classification_area_vectors"])
    else:
        classification_esa = ClassificationESA(esa_db_path, host, user, password, databases[classification_scheme],
                                               preloaded[classification_scheme]["classification_areas"],
                                               preloaded[classification_scheme]["classification_area_wikis"],
                                               load_all_vectors=False)
    return classification_esa
