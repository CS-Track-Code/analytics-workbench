from os import path
from concept_extraction.tfidf_extractor import TfIdfExtractor

host = "localhost"
user = "esa"
password = "esa_pw"

research_area_database = "esa_research_areas"
sdg_database = "esa_sdgs"

# TFIDF #
tfidf_model_path = path.join(path.dirname(__file__), "application", "esa_blueprint", "static", "concept_extraction", "data", "tfidf_en.tfidf_model")
tfidf_extractor = TfIdfExtractor(model_path=tfidf_model_path, tf_scaling="log")

# ESA: #
esa_tf_proportion = 0.2
esa_sort = True
esa_cutoff_in_relation_to_max = 0.75
esa_db_path = "application/esa_blueprint/static/esa/esa_data/esa.db"
