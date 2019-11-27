import os

import jinja2
from bot import Bot
from flask_sqlalchemy import SQLAlchemy
from slackeventsapi import SlackEventAdapter


port = int(os.environ.get('PORT', '5000'))
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
signing_secret = os.environ["SIGNING_SECRET"]
cache_path = os.environ.get('AUTH_CACHE_PATH')
db_url = os.environ['SQLALCHEMY_DB_URI']

bot_args = {
    'client_id': client_id,
    'client_secret': client_secret,
}
if cache_path and os.path.isfile(cache_path):
    bot_args['cache_path'] = cache_path

supbot = Bot(**bot_args)

events_adapter = SlackEventAdapter(signing_secret, endpoint="/slack")
flaskapp = events_adapter.server
template_loader = jinja2.ChoiceLoader([
                    flaskapp.jinja_loader,
                    jinja2.FileSystemLoader(['templates']),
                ])
flaskapp.jinja_loader = template_loader

flaskapp.config['SQLALCHEMY_DATABASE_URI'] = db_url
db = SQLAlchemy(flaskapp)

logger = flaskapp.logger
