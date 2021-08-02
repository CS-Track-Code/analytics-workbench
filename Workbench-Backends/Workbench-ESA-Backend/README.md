# Analytics Workbench Backend - ESA

## Setup
First install the Workbench Tool Suite (see README.md in workbench-tools)

Then install modules from requirements.txt by running

`pip install -r requirements.txt`

ESA requires esa.db to be placed in `/application/esa_blueprint/static/esa/esa_data/`
which you can download from https://cloud.innowise.de/index.php/s/ajoCKxy6Bi6FB6K
and you need to download the [tfidf model](https://cloud.innowise.de/index.php/s/NAQbmiFcaBYePAw)
as well which is to be placed in `/application/esa_blueprint/static/concept_extraction/data/`.
Additionally you will need a running MySQL service. The host of which you need to enter in the `/application/esa_blueprint/static/esa/config.py`
file in addition to the user and password which the esa module should use.

To set up ESA (for usage of assigning research areas to texts) previous to the first application it is necessary to run 
`/application/esa_blueprint/static/esa/prep/prepare_research_areas.py`,
which in turn needs the Backend - Mercury Web Parser to run. In the setup the program will need to have a
database "esa_research_areas", which it will try to create if there isn't one. Thus the given user should either be
given the right to create a database or it should be created manually.
The setup will take a few hours depending on the machine you are using. During this time the text vectors for all
research areas are pre calculated using the table in `/application/esa_blueprint/static/esa/esa_data/research_areas.csv` this table maps the
research areas of [web of science](https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html) to
wikipedia articles. If you wanted to use a different taxonomy. You could do that by changing the table.
Be advised though that the current code is not equipped to switch between taxonomies and you would have to facilitate
that manually.

## Run
Start of Application: run `wsgi.py`

Available on port 5003