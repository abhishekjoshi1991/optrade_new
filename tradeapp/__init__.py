from werkzeug.middleware.proxy_fix import ProxyFix
from flask_restx import Api, Resource
from flask import Flask, render_template
# from flask_restful import Api
from flask_cors import CORS
from .controllers.controller import api as ns1
from flask_sqlalchemy import SQLAlchemy
from .models.models import db
from flask_apscheduler import APScheduler

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object('config')
# app.config['CORS_HEADERS'] = 'Content-Type'
db.init_app(app)
base_url = "/tradeapp/api/v1"
# Using flask_restful
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

api = Api(
    app,
    version="0.1",
    title=' Service APIs',
    description=' titles',
    prefix=base_url,
    doc='/swagger')

api.add_namespace(ns1, path='/option_chain')
# api.add_namespace(ns2, path='/api2')
# api.add_namespace(ns3, path='/api3')

sched = APScheduler()
