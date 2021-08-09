# Analytics Workbench

Includes Frontend, Middleware and Backends for a Webbased Application to analyse Citizen Science projects.

Tips and Tricks on how to set up:
- Every part has to be started individually (most cases by running wsgi.py) and some require additional setup work 
  -> see readme files in frontend, middleware and individual backend applications
- Open in seperate Workspaces:
	- Frontend (PyCharm)
		- `/Worbench-Frontend/`
	- Middleware (PyCharm)
		- `/Worbench-Middleware/`
	- Backends (PyCharm)
		- `/Worbench-Backends/Workbench-DB-Backend`
		- `/Worbench-Backends/Workbench-ESA-Backend`
		- `/Worbench-Backends/Workbench-NER-Backend`
	- Backend - Mercury (WebStorm)
		- `/Worbench-Backends/Workbench-WMP-Backend`
		

## Setup

If you want to run all APIs on the same machine please follow all following instructions on that machine. 
If you want to split the APIs on multiple machines please refer to the README.md files in 
- `/Worbench-Frontend/`
- `/Worbench-Middleware/`
- `/Worbench-Backends/Workbench-DB-Backend`
- `/Worbench-Backends/Workbench-ESA-Backend`
- `/Worbench-Backends/Workbench-NER-Backend`
- `/Worbench-Backends/Workbench-WMP-Backend`

### First step
Install the Workbench Tool Suite from /workbench-tools 
- navigate to the directory
- install the requirements by running `pip install -r requirements.txt`
- install the tool suite by running `python setup.py install`

ESA uses polyglot, which can be hard to install depending on your operating system.
This usually stems from problems installing pyicu (and then also pycld).
If that is the case for you on a windows system, you can try installing that by downloading the appropriate whl file(s) for your system from:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyicu (& https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycld2)
(for example for 64bit Windows Python3.6 that's PyICU‑2.6‑cp36‑cp36m‑win_amd64.whl and pycld2‑0.41‑cp36‑cp36m‑win_amd64.whl)
and installing it with

`python -m pip install *path*/*filename*`

after that installing polyglot should work by either running

`pip install -r requirements.txt` again oder specifically installing polyglot with

`pip install polyglot`


### Frontend
Please install modules from /Workbench-Frontend/requirements.txt by navigating to the directory and running

`pip install -r requirements.txt`

### Middleware
Please install modules from /Workbench-Middleware/requirements.txt by navigating to the directory and running

`pip install -r requirements.txt`

### Backend Database
Please install modules from /Worbench-Backends/Workbench-DB-Backend/requirements.txt by navigating to the directory and running

`pip install -r requirements.txt`

Install MongoDB and correct port and client in `/Worbench-Backends/Workbench-DB-Backend/config_mongo_db.py` if necessary.

### Backend ESA
Please install modules from /Worbench-Backends/Workbench-ESA-Backend/requirements.txt by navigating to the directory and running

`pip install -r requirements.txt`

ESA requires esa.db to be placed in `/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/esa/esa_data/` 
which you can download from https://cloud.innowise.de/index.php/s/ajoCKxy6Bi6FB6K
and you need to download the [tfidf model](https://cloud.innowise.de/index.php/s/NAQbmiFcaBYePAw) 
as well which is to be placed in `/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/concept_extraction/data/`.
Additionally you will need a running MySQL service. The host of which you need to enter in the `/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/esa/config.py`
file in addition to the user and password which the esa module should use.

To set up ESA (for usage of assigning research areas to texts) previous to the first application it is necessary to run 
`/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/esa/prep/prepare_research_areas.py`,
which in turn needs the [Backend - Mercury Web Parser](#text_extraction) to run. In the setup the program will need to have a
database "esa_research_areas", which it will try to create if there isn't one. Thus the given user should either be
given the right to create a database or it should be created manually.
The setup will take a few hours depending on the machine you are using. During this time the text vectors for all
research areas are pre calculated using the table in `/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/esa/esa_data/research_areas.csv` this table maps the
research areas of [web of science](https://images.webofknowledge.com/images/help/WOS/hp_research_areas_easca.html) to
wikipedia articles. If you wanted to use a different taxonomy. You could do that by changing the table.
Be advised though that the current code is not equipped to switch between taxonomies and you would have to facilitate
that manually.

### Backend NER
Please install modules from /Worbench-Backends/Workbench-NER-Backend/requirements.txt by navigating to the directory and running

`pip install -r requirements.txt`

NER is implemented using spacy and pretrained spacy models which must be downloaded manually via console.
The commando line depends on the language for the model you need 
(As of now english is the only language supported by the workbench).

- English: `python -m spacy download en_core_web_sm`


### Backend Mercury Web Parser <a name="text_extraction"></a>
The text extraction is facilitated using the Mercury Web Parser.
For this you need to run a local server with Node.js

You need to have node.js installed on your machine (https://nodejs.org/en/).
Next you will have to install the required modules via the console. For this you navigate to this projects folder
`/web_text_extraction/mercury_web_parser` and run `npm i`.
As soon as this is done you can run the server by running `node app.js` in the same directory.

### Dash visualizations

When starting the Frontend of the analytics workbench the Dash application is also started. In order for Dash to work properly you need to add the inputs to the **analytics-workbench/Workbench-Frontend/application/cstrack_dash/** [(Input documentation)](davidrol6.github.io/CSTrack_Docs/inputs.html).

Once the frontend starts, you can access the visualizations by navigating to **http://frontend_url/dashapp/**.

## First Run
Please check if the addresses and user data in all config files are correct
- `/Worbench-Frontend/config.py` 
	- correct host_ip_address (and host_port)
	- check if middleware address and port are correct
- `/Worbench-Middleware/config.py`
	- correct host_ip_address (and host_port)
  	- check if backend addresses and port are correct
- `/Worbench-Backends/Workbench-DB-Backend/config.py`
	- correct host_ip_address (and host_port)
- `/Worbench-Backends/Workbench-DB-Backend/config_mongo_db.py` 
	- check if port and client for mongodb are correct
- `/Worbench-Backends/Workbench-ESA-Backend/config.py`
	- correct host_ip_address (and host_port)
- `/Worbench-Backends/Workbench-ESA-Backend/application/esa_blueprint/static/esa/config.py` 
	- check if user, password and database for MySQL are
- `/Worbench-Backends/Workbench-NER-Backend/config.py`
	- correct host_ip_address (and host_port)



## Runtime
Start MySQL and MongoDB Databases (if not running)

Start APIs:
- Frontend (PyCharm)
	- navigate to `/Worbench-Frontend/` -> run `wsgi.py` (port: 5000)
- Middleware (PyCharm)	  
	- navigate to `/Worbench-Middleware/` -> run `wsgi.py` (port: 5001)
- Backends (PyCharm)	  
	- navigate to `/Worbench-Backends/Workbench-DB-Backend/` -> run `wsgi.py` (port: 5004)
	  
	- navigate to `/Worbench-Backends/Workbench-ESA-Backend/` -> run `wsgi.py` (port: 5003)

	- navigate to `/Worbench-Backends/Workbench-NER-Backend/` -> run `wsgi.py` (port: 5002)
- Backend - Mercury (WebStorm)	  
	- navigate to `/Worbench-Backends/Workbench-WMP-Backend/` -> run `node app.js` (port: 8888)
