import os
from logging.config import dictConfig as config_logging

import jinja2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from slackeventsapi import SlackEventAdapter

from bot import Bot

port = int(os.environ.get('PORT', '5000'))
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
signing_secret = os.environ["SIGNING_SECRET"]
cache_path = os.environ.get('AUTH_CACHE_PATH')
db_url = os.environ['SQLALCHEMY_DB_URI']

config_logging({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

flaskapp = Flask(__name__)
events_adapter = SlackEventAdapter(
    signing_secret,
    endpoint="/slack",
    server=flaskapp,
)
logger = flaskapp.logger

bot_args = {
    'client_id': client_id,
    'client_secret': client_secret,
    'logger': logger
}
if cache_path and os.path.isfile(cache_path):
    bot_args['cache_path'] = cache_path

supbot = Bot(**bot_args)
template_loader = jinja2.ChoiceLoader([
                    flaskapp.jinja_loader,
                    jinja2.FileSystemLoader(['templates']),
                ])
flaskapp.jinja_loader = template_loader

flaskapp.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(flaskapp)
