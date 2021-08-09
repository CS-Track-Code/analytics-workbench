import mysql
from esa_analysis.classification_esa import ClassificationESA

import config_esa

host = config_esa.host
user = config_esa.user
password = config_esa.password

database_research_areas = config_esa.research_area_database
database_sdgs = config_esa.sdg_database

# TFIDF #
tfidf_model_path = config_esa.tfidf_model_path
tfidf_extractor = config_esa.tfidf_extractor

# ESA: #
esa_tf_proportion = config_esa.esa_tf_proportion
esa_sort = config_esa.esa_sort
esa_cutoff_in_relation_to_max = config_esa.esa_cutoff_in_relation_to_max
esa_db_path = config_esa.esa_db_path

esa_cutoffs = config_esa.esa_cutoffs

print("## Setup Research Areas ##")
research_areas_esa = ClassificationESA(esa_db_path, host, user, password, database_research_areas)
research_areas = research_areas_esa.get_classification_areas()
research_area_wikis = research_areas_esa.get_classification_area_wikis()
research_area_vectors = research_areas_esa.get_classification_area_vectors()

print("## Setup SDGs ##")
sdg_esa = ClassificationESA(esa_db_path, host, user, password, database_sdgs)
sdg_areas = sdg_esa.get_classification_areas()
sdg_area_wikis = sdg_esa.get_classification_area_wikis()
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
print("done")
