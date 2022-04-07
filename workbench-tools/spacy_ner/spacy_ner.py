import spacy
from os import path
import pickle as pkl

import random
from spacy.util import minibatch, compounding

from spacy_ner.entity_ruler import SpacyEntity


class SpacyNer:
    def __init__(self, lang, spacy_trained_model_path="", training_data_path=""):
        self.lab_desc = {
            "PERSON": "People, including fictional.",
            "NORP": "Nationalities or religious or political groups.",
            "FAC": "Buildings, airports, highways, bridges, etc.",
            "ORG": "Companies, agencies, institutions, etc.",
            "GPE": "Countries, cities, states.",
            "LOC": "Non-GPE locations, mountain ranges, bodies of water.",
            "PRODUCT": "Objects, vehicles, foods, etc. (Not services.)",
            "EVENT": "Named hurricanes, battles, wars, sports events, etc.",
            "WORK_OF_ART": "Titles of books, songs, etc.",
            "LAW": "Named documents made into laws.",
            "LANGUAGE": "Any named language.",
            "DATE": "Absolute or relative dates or periods.",
            "TIME": "Times smaller than a day.",
            "PERCENT": "Percentage, including ”%“.",
            "MONEY": "Monetary values, including unit.",
            "QUANTITY": "Measurements, as of weight or distance.",
            "ORDINAL": "“first”, “second”, etc.",
            "CARDINAL": "Numerals that do not fall under another type.",
            "PER": "Named person or family.",
            "MISC": "Miscellaneous entities, e.g. events, nationalities, products or works of art."
        }

        self.entity_ruler = SpacyEntity(lang, spacy_trained_model_path)

        self.saved_patterns = [
            {"label": "PER", "pattern": [{"ORTH": "<"},
                                         {"TEXT": {"REGEX": "PER>.{64}</PER"}},
                                         {"ORTH": ">"}]},
            {"label": "PER", "pattern": [{"ORTH": "<"},
                                         {"TEXT": {"REGEX": "PER"}},
                                         {"ORTH": ">"},
                                         {"TEXT": {"REGEX": ".{64}</PER>"}}]},
            {"label": "PER", "pattern": [{"ORTH": "<"},
                                         {"TEXT": {"REGEX": "PER"}},
                                         {"ORTH": ">"},
                                         {"TEXT": {"REGEX": ".{64}</PER"}},
                                         {"ORTH": ">"}]},
            {"label": "PERSON", "pattern": [{"ORTH": "<"},
                                            {"TEXT": {"REGEX": "PERSON>.{64}</PERSON"}},
                                            {"ORTH": ">"}]},
            {"label": "PERSON", "pattern": [{"ORTH": "<"},
                                            {"TEXT": {"REGEX": "PERSON"}},
                                            {"ORTH": ">"},
                                            {"TEXT": {"REGEX": ".{64}</PERSON>"}}]},
            {"label": "PERSON", "pattern": [{"ORTH": "<"},
                                            {"TEXT": {"REGEX": "PERSON"}},
                                            {"ORTH": ">"},
                                            {"TEXT": {"REGEX": ".{64}</PERSON"}},
                                            {"ORTH": ">"}]},
            {"label": "EMAIL", "pattern": [{"ORTH": "<"},
                                           {"TEXT": {"REGEX": "EMAIL>.{64}</EMAIL"}},
                                           {"ORTH": ">"}]},
            {"label": "EMAIL", "pattern": [{"ORTH": "<"},
                                           {"TEXT": {"REGEX": "EMAIL"}},
                                           {"ORTH": ">"},
                                           {"TEXT": {"REGEX": ".{64}</EMAIL>"}}]},
            {"label": "EMAIL", "pattern": [{"ORTH": "<"},
                                           {"TEXT": {"REGEX": "EMAIL"}},
                                           {"ORTH": ">"},
                                           {"TEXT": {"REGEX": ".{64}</EMAIL"}},
                                           {"ORTH": ">"}]},
            {"label": "PERSONAL_ACCOUNT", "pattern": [{"ORTH": "<"},
                                                      {"TEXT": {"REGEX": "PERSONAL_ACCOUNT>.{64}</PERSONAL_ACCOUNT"}},
                                                      {"ORTH": ">"}]},
            {"label": "PERSONAL_ACCOUNT", "pattern": [{"ORTH": "<"},
                                                      {"TEXT": {"REGEX": "PERSONAL_ACCOUNT"}},
                                                      {"ORTH": ">"},
                                                      {"TEXT": {"REGEX": ".{64}</PERSONAL_ACCOUNT>"}}]},
            {"label": "PERSONAL_ACCOUNT", "pattern": [{"ORTH": "<"},
                                                      {"TEXT": {"REGEX": "PERSONAL_ACCOUNT"}},
                                                      {"ORTH": ">"},
                                                      {"TEXT": {"REGEX": ".{64}</PERSONAL_ACCOUNT"}},
                                                      {"ORTH": ">"}]},
            {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "<"},
                                                  {"TEXT": {"REGEX": "PHONE_NUMBER"}},
                                                  {"ORTH": ">"},
                                                  {"TEXT": {"REGEX": ".{64}</PHONE_NUMBER>"}}]},
            {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "<"},
                                                  {"TEXT": {"REGEX": "PHONE_NUMBER"}},
                                                  {"ORTH": ">"},
                                                  {"TEXT": {"REGEX": ".{64}</PHONE_NUMBER>"}},
                                                  {"ORTH": ">"}]},
            {"label": "PHONE_NUMBER", "pattern": [{"ORTH": "<"},
                                                  {"TEXT": {"REGEX": "PHONE_NUMBER>.{64}</PHONE_NUMBER"}},
                                                  {"ORTH": ">"}]}
        ]

        self.entity_ruler.add_pattern(self.saved_patterns)

        self.nlp = self.entity_ruler.get_nlp()

        self.lab_desc["EMAIL"] = "Former email address of a person, organization or institution"
        self.lab_desc["PERSONAL_ACCOUNT"] = "Former link to a personal account e.g. on zooniverse"
        self.lab_desc["PHONE_NUMBER"] = "Former phone number"
        self.lab_desc["PROJECT"] = "Name of a (Citizen Science) project"

        self.training_data_file = lang + "_core_web_sm_training_data.pkl"
        self.training_data_file = lang + "_core_web_sm_training_data.pkl"
        self.training_data_path = training_data_path
        if path.exists(training_data_path + self.training_data_file):
            with open(training_data_path + self.training_data_file, "rb") as in_file:
                self.training_data = pkl.load(in_file)
        else:
            self.training_data = []

    def add_project_name_patterns(self, project_name):
        normal = []
        lower = []
        upper = []
        split_in_words = self.entity_ruler.nlp(project_name)
        for word in split_in_words:
            normal.append({"ORTH": word.text})
            lower.append({"ORTH": word.text.lower()})
            upper.append({"ORTH": word.text.upper()})
        pattern = [{"label": "PROJECT", "pattern": normal},
                   {"label": "PROJECT", "pattern": lower},
                   {"label": "PROJECT", "pattern": upper}]
        self.entity_ruler.add_pattern(pattern)

        for p in pattern:
            if p not in self.saved_patterns:
                self.saved_patterns.append(p)

        for i in range(len(split_in_words)):
            if 1 < i < len(split_in_words):
                for j in range(len(split_in_words) - i + 1):
                    normal = []
                    lower = []
                    upper = []
                    text = ""
                    for word in split_in_words[j:j + i]:
                        text += word.text + " "
                        normal.append({"ORTH": word.text})
                        lower.append({"ORTH": word.text.lower()})
                        upper.append({"ORTH": word.text.upper()})
                    if len(text[:-1]) > 8:
                        pattern = [{"label": "PROJECT", "pattern": normal},
                                   {"label": "PROJECT", "pattern": lower},
                                   {"label": "PROJECT", "pattern": upper}]
                        self.entity_ruler.add_pattern(pattern)

                        for p in pattern:
                            if p not in self.saved_patterns:
                                self.saved_patterns.append(p)

        self.entity_ruler.add_pattern(self.saved_patterns)

    def get_descriptors(self):
        return self.lab_desc

    def get_descriptors_list(self):
        list = []
        for key in self.lab_desc:
            list.append((key, self.lab_desc[key]))
        return list

    def get_labels(self, text, project_name=None):
        labels = []
        if project_name is not None:
            self.add_project_name_patterns(project_name)
            self.nlp = self.entity_ruler.get_nlp()
        doc = self.nlp(text)

        for d in doc.ents:
            labels.append((d.text, d.label_, d.start_char, d.end_char))

        return labels

    def process_text(self, text, project_name=None):
        labels_and_descriptions = []
        labels = self.get_labels(text, project_name)

        for lab in labels:
            if lab[1] in self.lab_desc:
                labels_and_descriptions.append((lab[0], lab[1], self.lab_desc[lab[1]], lab[2], lab[3]))
            else:
                labels_and_descriptions.append((lab[0], lab[1], ""))
        return labels_and_descriptions

    def process_text_get_filtered_results(self, text, project_name=None):
        results = self.process_text(text, project_name)
        shortlist = []
        for res in results:
            if not res in shortlist:
                shortlist.append(res)
        return shortlist

    def process_text_get_filtered_1d_resultlist(self, text):
        results = self.process_text_get_filtered_results(text)
        resultlist = []
        for res in results:
            res_line = res[0] + ", " + res[1] + " (" + res[2] + ")"
            resultlist.append(res_line)
        return resultlist

    def add_training_data(self, sentence, entities):
        new_training_data = (sentence, {"entities": entities})
        self.training_data.append(new_training_data)

        with open(self.training_data_path + self.training_data_file, "wb") as out_file:
            pkl.dump(self.training_data, out_file)

    def training(self, n_iter=20):
        optimizer = self.nlp.begin_trining()
        for itn in range(n_iter):
            random.shuffle(self.training_data)
            losses = {}
            batches = minibatch(self.training_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                self.nlp.update(
                    texts, annotations, drop=0.5, losses=losses, sgd=optimizer
                )
                print("Losses", losses)
