# -*- coding: utf-8 -*-
"""
In this file, we'll create a routing layer to handle incoming and outgoing
requests between our bot and Slack.
"""
from flask import render_template, request

from bot import SupException

from core import db, flaskapp, supbot, logger, events_adapter, port

COMMAND_PREFIX='sup '

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), unique=True, nullable=False)


# We can add an installation page route to the event adapter's server
@flaskapp.route("/install", methods=["GET"])
def before_install():
    """
    This route renders an installation page for our app!
    """
    return render_template(
        "install.html",
        scopes=supbot.scopes,
        client_id=supbot.client_id,
    )


@flaskapp.route("/thanks", methods=["GET"])
def thanks():
    """
    This route renders a page to thank users for installing our app!
    """
    auth_code = request.args.get('code')

    try:
        supbot.auth(auth_code)
        error = None
    except SupException as exc:
        logger.error(f"{exc}")
        error = f"{exc}"

    return render_template("thanks.html", error=error)


@events_adapter.on("message")
def handle_message(event_data):
    """
    Here we'll build a 'message' event handler using the Slack Events Adapter.
    """
    message = event_data['event']

    logger.info(f"message received from channel {message['channel']}")
    if 'hello' in message['text']:
        try:
            supbot.say_hello(message)
        except SupException as exc:
            logger.error(f"{exc}")

    if message['text'].startswith(COMMAND_PREFIX):
        command = message['text'][len(COMMAND_PREFIX):]

        logger.info(f"Sup command received: {command}")

        if command.startswith('report'):
            supbot.report_today(message, command.split())



# Here's some helpful debugging hints for checking that env vars are set
@flaskapp.before_first_request
def before_first_request():
    if not supbot.client_id:
        logger.debug(
            "Can't find Client ID, did you set this env variable?")
    if not supbot.client_secret:
        logger.debug(
            "Can't find Client Secret, did you set this env variable?")


@flaskapp.route('/hello')
def hello():
    return 'hello, world!'


if __name__ == '__main__':
    flaskapp.run(debug=True, port=port)
