""" This module provides functionality to create topic modelling models and visualizations.
"""

from nltk.corpus import stopwords
from bertopic import BERTopic
import json
import re


def filter_by_topic(df, keywords, stopwords):
    if keywords:
        df = df[df['Texto'].str.contains("|".join(keywords), case=False).any(level=0)]
        if stopwords:
            df = df[~df['Texto'].str.contains("|".join(stopwords), case=False).any(level=0)]
    return df


def remove_stopwords(texts, stop_words):
    list_texts = []
    for text in texts:
        words = text.split(" ")
        final_str = ""
        for word in words:
            if word not in stop_words and len(word) > 3:
                final_str += word + " "
        final_str = final_str.strip()
        list_texts.append(final_str)
    return list_texts


def get_cleaned_documents(df_original):
    df = df_original.copy()
    df["Texto"] = df["Texto"].apply(str)
    # df["Texto"] = df["Texto"].map(lambda x: re.sub("[,\.!?#]^¿¡","",x))
    df['Texto'] = df['Texto'].str.replace(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ')
    df["Texto"] = df["Texto"].str.replace('[^\w\s]', '')
    df["Texto"] = df["Texto"].map(lambda x: x.lower())
    df["Texto"] = df["Texto"].map(lambda x: re.sub("climate change", "climatechange", x))
    stop_words = stopwords.words("english")
    stop_words.extend(stopwords.words("spanish"))
    stop_words.extend(
        ["from", "citizenscience", "citizen science", "citizen", "science", "ciencia", "need", "thank", "project",
         "projects"])
    documents = df["Texto"].values.tolist()
    documents = remove_stopwords(documents, stop_words)
    return documents


def create_bert_model(documents):
    model = BERTopic(verbose=True, language="multilingual", min_topic_size=100)
    topics, probs = model.fit_transform(documents)
    return model, topics, probs


def get_intertopic_distance(model, top_n_topics=20):
    return model.visualize_topics(height=800, top_n_topics=20)


def get_hierarchical_clusterin(model):
    return model.visualize_hierarchy()


def get_topics_bar(model, top_n_topics=9):
    return model.visualize_barchart(top_n_topics=top_n_topics, height=800)


def get_heatmap(model):
    return model.visualize_heatmap()


def get_topics_over_time(df, model, documents, topics):
    timestamps = df["Fecha"]
    return model.visualize_topics_over_time(documents, topics, timestamps)


def load_model(filename):
    model = BERTopic.load(filename)
    return model


def load_topics(filename):
    with open(filename, "r") as f:
        topics = json.loads(f.read())["topics"]
        return topics
