from polyglot.text import Text
from collections import Counter

from concept_extraction.dbpedia_extractor import DBPediaExtractor
from esa_analysis.classification_esa import ClassificationESA


def keyword_extraction_dbpedia(text, lang):
    """
    to extract keywords using dbpedia
    :param text: input text (string)
    :param lang: language of text (string)
    shortened to two letters ("en" for english, "de" for german), limited by the languages dbpedia supports
    :return: list of dbpedia results, per result a list with word, tf, surface_form, types
    """
    dbpedia_ex = DBPediaExtractor(confidence=0.5, lang=lang, chunk_size=300)
    tokenized_words = Text(text).tokens
    token_list = []
    for i, token in enumerate(tokenized_words):
        item = {
            "word": token
        }
        token_list.append(item)
    token_list = [item for item in token_list if item["word"] != "."]

    word_tokenlist = [item["word"] for item in token_list]

    db_result = dbpedia_ex.extract(word_tokenlist)
    dbpedia_list = [[word, tf, surface_form, types] for word, tf, surface_form, types in
                    zip(db_result['word'], db_result['tf'],
                        db_result['surface_form'], db_result['types'])]

    dbpedia_list_unique = []
    for item in dbpedia_list:
        item_not_in_unique_list = True
        for unique_item in dbpedia_list_unique:
            if item[0] == unique_item[0]:
                unique_item[1] = unique_item[1] + item[1]
                item_not_in_unique_list = False
        if item_not_in_unique_list:
            dbpedia_list_unique.append(item)

    sorted_dbpedia_list = sorted(dbpedia_list_unique, key=lambda item: item[1], reverse=True)

    del dbpedia_ex

    # sorted_dbpedia_list -> [word, tf, surface_form, types]
    return sorted_dbpedia_list


def keywords_plain_dbpedia(dbpedia_list):
    """

    :param dbpedia_list: output list from keyword_extraction_dbpedia(..)
    :return: filtered one-dimensional list containing only the found dbpedia words
    """
    db_keywords = [word[0] for word in dbpedia_list]
    return db_keywords


def setup_research_area(research_areas_esa, host, user, password, database, edits, top, cutoff_in_relation_to_max, sort,
                        tfidf_proportion):
    """ deprecated """
    return setup_classification_area_esa(research_areas_esa, host, user, password, database, edits, top,
                                         cutoff_in_relation_to_max, sort, tfidf_proportion)


def setup_classification_area_esa(classification_areas_esa, host, user, password, database, edits, top,
                                  cutoff_in_relation_to_max, sort, tfidf_proportion):
    """

    :param database:
    :param password:
    :param user:
    :param host:
    :param classification_areas_esa: object ClassificationESA (can be reused to not reload classification areas every time)
    :param edits: boolean; True if changes for configuration were made
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched classification areas (return x first classification areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if classification areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: ClassificationESA object with given configuration
    """
    if classification_areas_esa is None:
        classification_areas_esa = ClassificationESA("esa_data/esa.db", host, user, password, database,
                                                     cutoff_in_relation_to_max=cutoff_in_relation_to_max,
                                                     sort=sort, tfidf_proportion=tfidf_proportion, top=None)
    elif edits:
        classification_areas_esa.edit_cutoff(cutoff_in_relation_to_max)
        classification_areas_esa.edit_sort(sort)
        classification_areas_esa.edit_tfidf(tfidf_proportion)
        classification_areas_esa.edit_top(top)

    return classification_areas_esa


def get_research_areas_esa(text, host, user, password, database, tfidf_extractor, research_areas_esa=None, edits=False,
                           top=None, cutoff_in_relation_to_max=None, sort=True, tfidf_proportion=0.2):
    return get_classification_areas_esa(text, host, user, password, database, tfidf_extractor, research_areas_esa, edits,
                                        top, cutoff_in_relation_to_max, sort, tfidf_proportion)


def get_classification_areas_esa(text, host, user, password, database, tfidf_extractor, classification_areas_esa=None,
                                 edits=False, top=None, cutoff_in_relation_to_max=None, sort=True,
                                 tfidf_proportion=0.2):
    """

    :param database:
    :param tfidf_extractor:
    :param password:
    :param host:
    :param user:
    :param text:
    :param classification_areas_esa: object ClassificationESA (can be reused to not reload classification areas every time)
    :param edits: boolean; True if changes for configuration were made
    (if False and classification_areas_esa is given: top, cutoff_in_relation_to_max,
    sort and tfidf_proportion don't have to be set!)
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched classification areas (return x first classification areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if classification areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: classification_areas_with_sim_list (list of matched classification areas, each with category, classification area, similarity),
    classification_areas (list of matched classification areas only),
    categories_with_count (counted how many classification areas per category were matched),
    top_category (category with most matched classification areas),
    bow (used bag of words for esa)
    """
    classification_areas_esa = setup_classification_area_esa(classification_areas_esa, host, user, password, database, edits,
                                                             top, cutoff_in_relation_to_max, sort, tfidf_proportion)

    classification_areas_with_sim_list, classification_areas, categories_with_count, top_category, bow = \
        classification_areas_esa.get_classification_area_similarities_from_text(text, tfidf_extractor)
    print("-- RESEARCH AREAS:")
    print(classification_areas)

    return classification_areas_with_sim_list, classification_areas, categories_with_count, top_category, bow


def get_research_areas_esa_with_dbpedia(text, host, user, password, database, tfidf_extractor, research_areas_esa=None,
                                        edits=False, top=None, cutoff_in_relation_to_max=None, sort=True,
                                        tfidf_proportion=0.25):
    return get_classification_areas_esa_with_dbpedia(text, host, user, password, database, tfidf_extractor, research_areas_esa,
                                                     edits, top, cutoff_in_relation_to_max, sort, tfidf_proportion)


def get_classification_areas_esa_with_dbpedia(text, host, user, password, database, tfidf_extractor,
                                              classification_areas_esa=None, edits=False, top=None,
                                              cutoff_in_relation_to_max=None, sort=True, tfidf_proportion=0.25):
    """

    :param tfidf_extractor:
    :param text:
    :param classification_areas_esa: object ClassificationESA (can be reused to not reload classification areas every time)
    :param edits: boolean; True if changes for configuration were made
    (if False and classification_areas_esa is given: top, cutoff_in_relation_to_max,
    sort and tfidf_proportion don't have to be set!)
    :param top: int or None; if not None sort has to be True;
    absolute cutoff for matched classification areas (return x first classification areas)
    :param cutoff_in_relation_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :param sort: boolean; True if classification areas should be sorted by similarity (should be True if top is not None)
    :param tfidf_proportion: float (0 < x < 1); in relation to the highest tfidf score in the text
    how high has a words score to be for the word to be used in the esa calculation
    (used to only include high value words and to reduce calculation time by cutting out low value words)
    :return: classification_areas_with_sim_list (list of matched classification areas, each with category, classification area, similarity),
    classification_areas (list of matched classification areas only),
    categories_with_count (counted how many classification areas per category were matched),
    top_category (category with most matched classification areas),
    db_classification_areas (classification areas that match found dbpedia keywords),
    bow (used bag of words for esa)
    """
    classification_areas_esa = setup_classification_area_esa(classification_areas_esa, host, user, password, database, edits, top,
                                                             cutoff_in_relation_to_max, sort, tfidf_proportion)

    try:
        db_list = keyword_extraction_dbpedia(text, "en")
        db_keywords = keywords_plain_dbpedia(db_list)
    except ConnectionError:
        db_keywords = []
        print("DBpedia is currently not reachable")

    classification_areas_with_sim_list, classification_areas, categories_with_count, top_category, db_classification_areas, bow = \
        classification_areas_esa.get_classification_areas_with_dbp(text, tfidf_extractor, db_keywords)

    return classification_areas_with_sim_list, classification_areas, categories_with_count, top_category, db_classification_areas, bow


def get_research_areas_esa_with_dbpedia_integrated(text, host, user, password, database, tfidf_extractor,
                                                   research_areas_esa, cutoff_in_rel_to_max=0.75):
    return get_classification_areas_esa_with_dbpedia_integrated(text, host, user, password, database, tfidf_extractor,
                                                                research_areas_esa, cutoff_in_rel_to_max)


def get_classification_areas_esa_with_dbpedia_integrated(text, host, user, password, database, tfidf_extractor,
                                                         classification_areas_esa, cutoff_in_rel_to_max=0.75):
    """
    method made specifically for workbench application, returns the complete list of all classification areas additionally
    to the shortened list (using the cutoff). Used to give users the option to modify the results.
    And sorts db results in shortened result list

    assumes that configuration is already set, cutoff_in_relation_to_max is required because it is set to None to get
    all classification areas and then perform the cutoff here to return both lists
    :param tfidf_extractor:
    :param text:
    :param classification_areas_esa: object ClassificationESA (can be reused to not reload classification areas every time)
    :param cutoff_in_rel_to_max: float (0 < x < 1); sets cutoff in relation to the maximal cutoff
    :return:
    classification_areas_similarity_shortlist (list of matched classification areas, each with category, classification area, similarity),
    classification_areas_with_sim_list (list of ALL classification areas, each with category, classification area, similarity),
    categories_with_count(counted how many classification areas per category were matched),
    top_category, (category with most matched classification areas),
    db_classification_areas (classification areas that match found dbpedia keywords),
    unique_words (used bag of words for esa)
    """

    classification_areas_esa.edit_cutoff(cutoff_in_relation_to_max=None)

    classification_areas_with_sim_list, classification_areas, categories_with_count, top_category, db_classification_areas, tokens = \
        get_classification_areas_esa_with_dbpedia(text, host, user, password, database, tfidf_extractor,
                                                  classification_areas_esa=classification_areas_esa)

    if classification_areas_with_sim_list == []:
        #ToDo: throw error
        return [], [], [], "", [], []

    counts = Counter([i for i in tokens])
    unique_words = list({i: i for i in tokens}.values())

    max_sim = classification_areas_with_sim_list[0][2]

    cutoff = max_sim * cutoff_in_rel_to_max
    classification_areas_similarity_shortlist = [ras for ras in classification_areas_with_sim_list if ras[2] > cutoff]

    categories = [ras[0] for ras in classification_areas_similarity_shortlist]

    # sort categories by count
    counts = Counter([i for i in categories])
    unique_categories = list({i: i for i in categories}.values())
    sorted_categories = sorted(unique_categories, key=lambda item: counts[item], reverse=True)
    categories_with_count = [[item, counts[item]] for item in sorted_categories]
    if len(categories_with_count) > 0:
        top_category = categories_with_count[0][0]
    else:
        top_category = ""

    db_classification_throwaway = [d for d in db_classification_areas]
    for ca in classification_areas_similarity_shortlist:
        if ca[1] in db_classification_throwaway:
            db_classification_throwaway.remove(ca[1])

    add_ras = [ra for ra in classification_areas_with_sim_list if ra[1] in db_classification_throwaway]

    for ca in add_ras:
        classification_areas_similarity_shortlist.append(ca)

    return classification_areas_similarity_shortlist, classification_areas_with_sim_list, categories_with_count, top_category, \
           db_classification_areas, unique_words
