# Analytics Workbench Backend - NER

## Setup
First install the Workbench Tool Suite (see README.md in workbench-tools)

Then install modules from requirements.txt by running

`pip install -r requirements.txt`

NER is implemented using spacy and pretrained spacy models which must be downloaded manually via console.
The commando line depends on the language for the model you need.

- English: `python -m spacy download en_core_web_sm`
- Spanish: `python -m spacy download es_core_news_sm`
- French: `python -m spacy download fr_core_news_sm`
- German: `python -m spacy download de_core_news_sm`

for other languages please refer to https://spacy.io/models

## Run
Start of Application: run `wsgi.py`

Available on port 5002