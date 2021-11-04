"""Flask configuration."""
# from os import environ, path
# from dotenv import load_dotenv

# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

import requests as py_requests
import json


class Config:
    """Base config."""
    # SECRET_KEY = environ.get('SECRET_KEY')
    # SESSION_COOKIE_NAME = environ.get('SESSION_COOKIE_NAME')
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class ProdConfig(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    # DATABASE_URI = environ.get('PROD_DATABASE_URI')


class DevConfig(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    # DATABASE_URI = environ.get('DEV_DATABASE_URI')


host_ip_address = 'localhost'
host_port = 5001

"""Backend Addresses"""
backend_mercury = "http://localhost:8888/myapp/"
backend_ner = "http://localhost:5002/"
backend_esa = "http://localhost:5003/"
backend_data = "http://localhost:5004/"


version_control = {
    "sdgs": None,
    "research_areas": None
}
has_version_control = False


def get_version_control():
    url_data = backend_esa + "version_control"
    data = {}
    data_response = py_requests.get(url_data, data=data)
    if data_response.status_code == 200:
        content = json.loads(data_response.content)
        version_control["sdgs"] = content["sdgs"]
        version_control["research_areas"] = content["research_areas"]
        has_version_control = True
    pass


get_version_control()
