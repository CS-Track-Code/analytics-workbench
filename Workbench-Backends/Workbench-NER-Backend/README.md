# Analytics Workbench Backend - NER

## Setup
First install the Workbench Tool Suite (see README.md in workbench-tools)

Then install modules from requirements.txt by running

`pip install -r requirements.txt`

NER is implemented using spacy and pretrained spacy models which must be downloaded manually via console.
The command line depends on the language for the model you need.

- English: `python -m spacy download en_core_web_sm`
- Spanish: `python -m spacy download es_core_news_sm`
- French: `python -m spacy download fr_core_news_sm`
- German: `python -m spacy download de_core_news_sm`

for other languages please refer to https://spacy.io/models

## Important Note

Also: as of now the NER Backend **only supports english** in the context of the Analytics Workbench, 
other languages were not supported anyway - due to the limitation given by the ESA Backend - 
this was not a priority in the development. The appropriate place to introduce multilanguage support is 
indicated with a TODO marker in the `application/pacy_blueprint/routes.py` file. 

## Before the first run
Please check if the addresses and user data in all config files are correct
- `config.py`
	- correct host_ip_address (and host_port)

## Run
Start of Application: run `wsgi.py`

Available on port 5002