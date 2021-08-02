"""Flask configuration."""
# from os import environ, path
# from dotenv import load_dotenv

from db_interaction.network_safe import Safe
from db_interaction.mongo_interface import MongoInterface

# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))


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
host_port = 5004

pymongo_clientport = '27017'
pymongo_client_name = "data_collection"

projects_db = "projects"

# to save networks for given time before new calculation
# set_save_time = 60  #  10000  # in seconds
mongo = MongoInterface(pymongo_clientport, pymongo_client_name, projects_db)
safe_for_list_and_networks = Safe(0, mongo)
