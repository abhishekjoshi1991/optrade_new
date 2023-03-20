import os
import sys
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.dirname(BASE_DIR))
CSRF_ENABLED     = True

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
# Enable debug mode.
DEBUG = True
# Connect to the database

# db_name = os.environ["DB_NAME"]
# db_user = os.environ["DB_USERNAME"]
# db_password = os.environ["DB_PASSWORD"]
# db_host = os.environ["DB_HOST"]

# SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://abhishek:abhishek@localhost/tradeapp2'


# Turn off the Flask-SQLAlchemy event system and warning
SQLALCHEMY_TRACK_MODIFICATIONS = False

# FUTURE PRICE
FUTURE_PRICE = 18062