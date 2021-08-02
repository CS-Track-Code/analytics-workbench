import spacy
from os import path
import pickle as pkl

import random
from spacy.util import minibatch, compounding


class SpacyNer:
    def __init__(self, lang, spacy_trained_model_path="", training_data_path=""):
        self.spacy_model = ""
        self.spacy_model = lang + "_core_web_sm"
        try:
            if path.exists(spacy_trained_model_path + self.spacy_model):
                self.nlp = spacy.load(spacy_trained_model_path + self.spacy_model)
            else:
                self.nlp = spacy.load(self.spacy_model)
        except OSError:
            self.spacy_model = lang + "_core_news_sm"
            try:
                self.nlp = spacy.load(self.spacy_model)
            except OSError:
                self.spacy_model = "xx_ent_wiki_sm"
                try:
                    self.nlp = spacy.load(self.spacy_model)
                    print("No language specific spacy model available. Using default model. "
                          "Check on https://spacy.io/models how to get a model for this language.")
                except OSError:
                    self.nlp = spacy.blank(lang)
                    print("Couldn't load spacy model")

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

        self.training_data_file = lang + "_core_web_sm_training_data.pkl"
        self.training_data_file = lang + "_core_web_sm_training_data.pkl"
        self.training_data_path = training_data_path
        if path.exists(training_data_path + self.training_data_file):
            with open(training_data_path + self.training_data_file, "rb") as in_file:
                self.training_data = pkl.load(in_file)
        else:
            self.training_data = []

    def get_descriptors(self):
        return self.lab_desc

    def get_descriptors_list(self):
        list = []
        for key in self.lab_desc:
            list.append((key, self.lab_desc[key]))
        return list

    def get_labels(self, text):
        labels = []
        doc = self.nlp(text)

        for d in doc.ents:
            labels.append((d.text, d.label_, d.start_char, d.end_char))

        return labels

    def process_text(self, text):
        labels_and_descriptions = []
        labels = self.get_labels(text)

        for lab in labels:
            if lab[1] in self.lab_desc:
                labels_and_descriptions.append((lab[0], lab[1], self.lab_desc[lab[1]], lab[2], lab[3]))
            else:
                labels_and_descriptions.append((lab[0], lab[1], ""))
        return labels_and_descriptions

    def process_text_get_filtered_results(self, text):
        results = self.process_text(text)
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
