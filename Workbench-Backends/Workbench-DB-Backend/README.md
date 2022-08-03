# Analytics Workbench Backend - Database

## Setup
First install the Workbench Tool Suite (see README.md in workbench-tools)

Then install modules from requirements.txt by running

`pip install -r requirements.txt`

Install MongoDB and correct port and client in `config_mongo_db.py` if necessary.

## Before the first run
Please check if the addresses and user data in all config files are correct
- `config.py`
	- correct host_ip_address (and host_port)
- `config_mongo_db.py` 
	- check if port and client for mongodb are correct

## Run
Start of Application: run `wsgi.py`

Available on port 5004