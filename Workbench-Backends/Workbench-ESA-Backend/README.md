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

To set up ESA (for usage of assigning research areas to texts) previous to the first application it is necessary to prepare the comparison bases. 
Which can be done in two ways: 

### Prepare reference base 
In the setup the program will need to have a MySQL database "esa_research_areas", 
which it will try to create if there isn't one. Thus the given user should either be
given the right to create a database or it should be created manually.
The setup will take a few hours depending on the machine you are using. During this time the text vectors for all
research areas are pre calculated using the table in `/application/esa_blueprint/static/esa/esa_data/research_areas.csv` 
this table maps the research areas of [web of science](https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html) to
wikipedia articles. If you wanted to use a different taxonomy. You could do that by changing the table.
Be advised though that the current code is not equipped to switch between taxonomies, and you would have to facilitate
that manually.

Since the ESA-Backend in its current setup supports the assignment of research areas *and* SDGs it is necessary 
to prepare the reference bases **for both**. Which means you will have to run whichever route you choose **twice**; 
in the first run using `research_areas.csv` as the file input name on request and in the second `sdgs.csv` (or vice versa).

#### ... *without* saving (and modifying the reference texts)
Run the Backend - Mercury Web Parser (refer to corresponding README file).
Then run `prepare_research_areas.py`. 

#### ... *with* saving (and modifying the reference texts)
Run the Backend - Mercury Web Parser (refer to corresponding README file).
Then run `create_ref_dump.py`. 

Modify the reference texts as needed/wanted.

Then run `prepare_classification_area_vectors_from_dump.py`

## Before the first run
Please check if the addresses and user data in all config files are correct
- `config.py`
	- correct host_ip_address (and host_port)
- `config_esa.py` 
	- check if user, password and database for MySQL are

## Run
Start of Application: run `wsgi.py`

Available on port 5003