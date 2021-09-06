from collections import Counter
import numpy as np
import mysql.connector
import time

from esa_analysis import esa as esa_class
from esa_analysis.esa import ESA

"""
Renaming -> 
research areas -> classification areas
"""


class ClassificationESA:
    def __init__(self, esa_db_path, db_host, db_user, db_password, db_name, classification_areas=None,
                 classifiaction_area_wikis=None, classification_area_vectors=None, cutoff_in_relation_to_max=0.75,
                 top=None, sort=True, tfidf_proportion=0.2, esa=None, load_all_vectors=True):
        if esa is None:
            self.esa = ESA(esa_db_path)
        else:
            self.esa = esa

        try:
            self.ra_con = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
        except mysql.connector.errors.ProgrammingError:
            mydb = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password
            )

            mycursor = mydb.cursor(buffered=True)

            mycursor.execute("CREATE DATABASE " + db_name)

            self.ra_con = mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )

        self.db_name = db_name

        self.mycursor = self.ra_con.cursor()
        self.classification_areas = classification_areas
        self.classifiaction_area_wikis = classifiaction_area_wikis
        self.classification_area_vectors = classification_area_vectors
        self.load_all_vectors = load_all_vectors

        self.mycursor.execute("SHOW TABLES")

        tables = []
        for x in self.mycursor:
            tables.append(x[0])

        if 'absolute_value' not in tables:
            self.mycursor.execute('CREATE TABLE IF NOT EXISTS absolute_value (area_id INTEGER NOT NULL PRIMARY KEY, '
                                  'abs_val REAL NOT NULL)')

        self.cutoff_in_relation_to_max = cutoff_in_relation_to_max
        self.top = top
        self.sort = sort
        self.tfidf_proportion = tfidf_proportion

    def edit_cutoff(self, cutoff_in_relation_to_max):
        self.cutoff_in_relation_to_max = cutoff_in_relation_to_max

    def edit_top(self, top):
        self.top = top

    def edit_sort(self, sort):
        self.sort = sort

    def edit_tfidf(self, tfidf_proportion):
        self.tfidf_proportion = tfidf_proportion

    def edit_esa(self, esa):
        self.esa = esa

    def get_classification_areas(self, min_row_id=0):
        if self.classification_areas is None:
            start_time = time.time()
            self.mycursor.execute('SELECT id, wos_category, wos_topic FROM research_areas;')
            self.classification_areas = []
            for row in self.mycursor.fetchall():
                self.classification_areas.append([row[0], row[1], row[2]])
            print("~~ got classification areas in: " + str(time.time() - start_time))
        return self.classification_areas[min_row_id:]

    def get_classification_area_vectors(self):
        if self.classification_area_vectors is None:
            start_time = time.time()
            self.classification_area_vectors = {}
            for area in self.get_classification_areas():
                area_id = area[0]
                vec = self.get_vector_for_classification_area_id(area_id)
                self.classification_area_vectors[area_id] = vec
            print("~~ got classification area vecs in: " + str(time.time() - start_time))
        return self.classification_area_vectors

    def get_vector_for_classification_area_id(self, area_id):
        self.mycursor.execute(
            'SELECT article_id, tf_idf FROM research_areas_vec WHERE area_id = ' + str(area_id) + ';')

        vec = {}
        for pair in self.mycursor.fetchall():
            vec[pair[0]] = pair[1]
        return vec

    def get_classification_area_wikis(self, min_row_id=0):
        if self.classifiaction_area_wikis is None:
            start_time = time.time()
            self.mycursor.execute('SELECT id, wos_category, wos_topic, wiki_name FROM research_areas_wiki;')
            self.classifiaction_area_wikis = []
            for row in self.mycursor.fetchall():
                self.classifiaction_area_wikis.append([row[0], row[1], row[2], row[3]])
            print("~~ got classification area wikis in: " + str(time.time() - start_time))
        return self.classifiaction_area_wikis[min_row_id:]

    def get_classification_area_similarities_from_text(self, text, tfidf_extractor):
        start_time = time.time()
        if not self.tfidf_proportion == 0:
            bow, tokens = esa_class.text_to_most_important_tokens(text, tfidf_extractor,
                                                                  minimum_percentage=self.tfidf_proportion,
                                                                  also_return_all_tokens=True)
            text_vec = self.esa.get_text_vector_from_bow(bow)
        else:
            text_vec = self.esa.get_text_vector(text)
            tokens = ""

        if len(text_vec) == 0:
            #ToDO: throw error
            return [], [], [], "", []

        text_vec_abs_val = self.esa.abs_val_of_vec(text_vec)
        print("~~ got text vector in " + str(time.time() - start_time))

        classification_areas_with_sim, classification_areas, categories, top_category = \
            self.get_classification_area_similarities_from_vec(text_vec, text_vec_abs_val)

        return classification_areas_with_sim, classification_areas, categories, top_category, tokens

    def get_classification_area_similarities_from_vec(self, text_vec, text_vec_abs_val, min_row_id_of_ra=0):
        classification_areas_similarity = []
        i = 0
        max_sim = 0

        if self.classification_area_vectors is None and self.load_all_vectors:
            print("how'd i get here?")
            self.get_classification_area_vectors()

        print("calculating similarities")
        for row in self.get_classification_areas(min_row_id_of_ra):
            i += 1
            area_id = row[0]
            classification_area_category = row[1]
            classification_area_topic = row[2]

            if not self.load_all_vectors:
                vec = self.get_vector_for_classification_area_id(area_id)
            else:
                vec = self.classification_area_vectors[area_id]

            classification_area_vec_abs_val = self.get_abs_value_of_ca_vec(row[0], vec)

            # get similarity between text and classification area
            sim = self.esa.cos_of_vectors(text_vec, vec, text_vec_abs_val, classification_area_vec_abs_val)
            if sim > max_sim:
                max_sim = sim

            classification_areas_similarity.append([classification_area_category, classification_area_topic, sim])

        if self.cutoff_in_relation_to_max is not None:
            cutoff = max_sim * self.cutoff_in_relation_to_max
            classification_areas_similarity = [cas for cas in classification_areas_similarity if cas[2] > cutoff]

        categories = [cas[0] for cas in classification_areas_similarity]

        # sort categories by count
        counts = Counter([i for i in categories])
        unique_categories = list({i: i for i in categories}.values())
        sorted_categories = sorted(unique_categories, key=lambda item: counts[item], reverse=True)
        categories = [[item, counts[item]] for item in sorted_categories]
        if len(categories) > 0:
            top_category = categories[0][0]
        else:
            top_category = ""

        print("sorting")
        if self.sort:
            sorted_classification_areas = sorted(classification_areas_similarity, key=lambda x: x[2], reverse=True)
            if self.top is not None:
                sorted_classification_areas = sorted_classification_areas[:self.top]

            classification_areas = [ca[1] for ca in sorted_classification_areas]

            return sorted_classification_areas, classification_areas, categories, top_category
        else:
            classification_areas = [ra[1] for ra in classification_areas_similarity]
            return classification_areas_similarity, classification_areas, categories, top_category

    def get_abs_value_of_ca_vec(self, classification_area_id, vec):
        self.mycursor.execute('SELECT abs_val FROM absolute_value WHERE area_id = ' + str(classification_area_id) + ';')
        value_row = self.mycursor.fetchone()
        if value_row is None:
            classification_area_vec_abs_val = self.esa.abs_val_of_vec(vec)
            self.mycursor.execute('INSERT into absolute_value (area_id, abs_val) VALUES (' +
                                  str(classification_area_id) + ',' + str(classification_area_vec_abs_val) + ');')
            self.ra_con.commit()
        else:
            classification_area_vec_abs_val = value_row[0]
        if classification_area_vec_abs_val == 0:
            classification_area = [line for line in self.get_classification_areas() if line[0] == classification_area_id]
            print("The absolute value of the classification area '" + classification_area[0][2] +
                  "' is 0. This likely means that something went wrong in preprocessing the classification areas. "
                  "If this happened for multiple classification areas you should try to rerun preprocessing. "
                  "(For this you will have to first delete the corresponding database '" + self.db_name + "' manually)")
        return classification_area_vec_abs_val

    def get_classification_area_sim_matrix(self):
        classification_areas = self.get_classification_areas()
        classification_area_index = {}
        classification_area_matrix = np.zeros(shape=(len(classification_areas), len(classification_areas)))

        counter = 0

        for ra_id, category, topic in classification_areas:
            classification_area_index[counter] = topic
            classification_area_index[topic] = counter
            counter += 1

        if self.classification_area_vectors is None:
            self.get_classification_area_vectors()

        done = 0
        for row in classification_areas:
            area_id = row[0]
            classification_area_topic = row[2]
            current_area_matrixid = classification_area_index[classification_area_topic]

            vec = self.classification_area_vectors[area_id]

            classification_area_vec_abs_val = self.get_abs_value_of_ca_vec(row[0], vec)

            classification_area_matrix[current_area_matrixid, current_area_matrixid] = 1

            if len(classification_areas) >= done+1:
                store_sort = self.sort
                self.sort = False
                classification_areas_similarity, classification_areas, categories, top_category = \
                    self.get_classification_area_similarities_from_vec(vec, classification_area_vec_abs_val,
                                                                       min_row_id_of_ra=done + 1)
                self.sort = store_sort

                for category, topic, sim in classification_areas_similarity:
                    second_area_matrix_id = classification_area_index[topic]
                    classification_area_matrix[current_area_matrixid, second_area_matrix_id] = sim
                    classification_area_matrix[second_area_matrix_id, current_area_matrixid] = sim
            done += 1

            print(str(done) + ": " + classification_area_topic)
            line = str([str(r) + "\t" for r in classification_area_matrix[done-1:done, :]])
            print(line.replace("\n", ""))

        return classification_area_matrix, classification_area_index

    def get_classification_areas_with_dbp(self, text, tfidf_extractor, db_results):
        db_classification_areas = []

        wiki_classification_area = {}
        for ca in self.get_classification_area_wikis():
            classification_area = ca[2]
            wiki = ca[3]
            if wiki in wiki_classification_area:
                wiki_classification_area[wiki].append(classification_area)
            else:
                wiki_classification_area[wiki] = [classification_area]

        for db_res in db_results:
            if db_res in wiki_classification_area:
                for entry in wiki_classification_area[db_res]:
                    db_classification_areas.append(entry)

        classification_areas_with_sim, classification_areas, categories, top_category, tokens = \
            self.get_classification_area_similarities_from_text(text, tfidf_extractor)

        return classification_areas_with_sim, classification_areas, categories, top_category, db_classification_areas, \
               tokens
