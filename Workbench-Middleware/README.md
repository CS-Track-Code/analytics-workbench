# Analytics Workbench Middleware
## Setup
First install the Workbench Tool Suite (see README.md in workbench-tools)

Then install modules from requirements.txt by running

`pip install -r requirements.txt`

## Before the first run
Please check if the addresses and user data in all config files are correct
- `/Worbench-Middleware/config.py`
	- correct host_ip_address (and host_port)
  	- check if backend addresses and port are correct

## Run
Start the middleware after the Backends!
Start of Application: run `wsgi.py`

Available on port 5001