**********
Input data
**********

Before learning how to setup and run the CSTrack Dash application it is important to have at hand the dataset that the app
is going to work with, the database connection and the BERT model needed in order to provide all the visualizations. This information can be
provided through a .env file that needs to placed in the cstrack_dash folder.

=============
Tweet dataset
=============

The CSTrack Dash application reads a .csv file in which the information of the tweets is written. Although we provide a basic
dataset, it can be completed with more tweets or custom datasets may be used too. The name of the .csv file is defined in the variable
TWEET_DATASET of the .env file.

The .csv file must have the following columns:

* Fecha: The date of the tweet.
* Fuente: The source of the tweet.
* Texto: The text of the tweet.
* Enlace: The link of the tweet.
* Marca: The filter used for extracting the tweet.
* Usuario: The username of the person that wrote the tweet.

====================
Database connections
====================

The Geomap visualizations requires from data that is not present in the tweet dataset. This data has been previously stored in a Mongo
database that is accessed by the Dash application in order to create these visualizations. The link of the connection must be supplied
in the MONGODB_CONNECTION variable of the .env file. There needs to be a cstrack database with a "geomap_full" collection in it.
Each document in that collection must contain the following fields:

* lat: The latitude.
* lon: The longitude.
* tweets: The number of tweets.
* followers: The number of followers.
* country_code: The 2 character country code.
* iso_3: The 3 character country code.
* country: The full name of the country.
* continent: The name of the continent.

==========
BERT model
==========

The application preloads a BERT model created with BERTopic (Bertopic_) in order to carry out Topic Modelling tasks. By filtering tweets and training this model
the Dash application creates visualizations that allow you to determine the themes of the discussions in Twitter (Depending on
the tweet dataset). In order to provide this model to the application the variable BERT_MODEL must be supplied to the .env file.

.. _Bertopic: https://github.com/MaartenGr/BERTopic

In addition it is advisable to provide a .json file that contains two keys:

* topics: A list with the topic assignments.
* documents: The list of tweets.

This information should be saved when calling the fit_transform() method of the BERTopic module. Here you can see an example
of how to use BERTopic to create models for topic modelling and how to create the topics.json file.

.. code:: python

    import pandas as pd
    from bertopic import BERTopic
    import re
    import json

    #Data loading
    df = pd.read_csv("tweets.csv", sep=";", encoding="latin-1", error_bad_lines=False)
    df["Texto"] = df["Texto"].apply(str)
    df["Texto"] = df["Texto"].map(lambda x: re.sub("[,\.!?#]^¿¡", "", x))
    df["Texto"] = df["Texto"].map(lambda x: x.lower())
    documents = df["Texto"].values.tolist()

    #Model creation
    model = BERTopic(verbose=True, language="multilingual")
    topics, probs = model.fit_transform(documents)
    model.save("bert_model")
    with open("topics.json", "w") as f:
        f.write(json.dumps({"topics": topics, "documents": documents}))



This .json file needs to be defined in the variable BERT_TOPICS of the .env file.


====================
Final considerations
====================

The .env file should look as follows:

.. include:: env.txt
   :literal:
