import spacy
from os import path
import pickle as pkl


class SpacyTrainer:
    def __init__(self, lang, spacy_trained_model_path="", training_data_path=""):
        self.training_data_file = lang + "_core_web_sm_training_data.pkl"
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
        self.training_data_path = training_data_path


def add_to_training(sentence, entities, training_data_path, lang="en"):
    new_training_data = (sentence, {"entities": entities})
    training_data_file = lang + "_core_web_sm_training_data.pkl"
    if path.exists(training_data_path + training_data_file):
        with open(training_data_path + training_data_file, "rb") as in_file:
            training_data = pkl.load(in_file)
    else:
        training_data = []
    training_data.append(new_training_data)

    with open(training_data_path + training_data_file, "wb") as out_file:
        pkl.dump(training_data, out_file)


