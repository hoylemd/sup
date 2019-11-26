# -*- coding: utf-8 -*-
"""
In this file, we'll create a routing layer to handle incoming and outgoing
requests between our bot and Slack.
"""
import os
import json
import jinja2
from flask import render_template, request, make_response
from slackeventsapi import SlackEventAdapter

from bot import Bot, SupException

port = int(os.environ.get('PORT', '5000'))
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
signing_secret = os.environ["SIGNING_SECRET"]
cache_path = os.environ.get('AUTH_CACHE_PATH')

bot_args = {
    'client_id': client_id,
    'client_secret': client_secret,
}
if cache_path and os.path.isfile(cache_path):
    bot_args['cache_path'] = cache_path

supbot = Bot(**bot_args)

events_adapter = SlackEventAdapter(signing_secret, endpoint="/slack")
template_loader = jinja2.ChoiceLoader([
                    events_adapter.server.jinja_loader,
                    jinja2.FileSystemLoader(['templates']),
                  ])
events_adapter.server.jinja_loader = template_loader

logger = events_adapter.server.logger


# We can add an installation page route to the event adapter's server
@events_adapter.server.route("/install", methods=["GET"])
def before_install():
    """
    This route renders an installation page for our app!
    """
    return render_template("install.html", client_id=supbot.client_id)


@events_adapter.server.route("/thanks", methods=["GET"])
def thanks():
    """
    This route renders a page to thank users for installing our app!
    """
    auth_code = request.args.get('code')

    # Now that we have a classy new Bot Class, let's build and use an auth
    # method for authentication.
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

    if 'hello' in message['text']:
        try:
            supbot.say_hello(message)
        except SupException as exc:
            logger.error(f"{exc}")


# Here's some helpful debugging hints for checking that env vars are set
@events_adapter.server.before_first_request
def before_first_request():
    if not supbot.client_id:
        logger.debug(
            "Can't find Client ID, did you set this env variable?")
    if not supbot.client_secret:
        logger.debug(
            "Can't find Client Secret, did you set this env variable?")


def ok_response(message):
    return make_response(json.dumps(message), 200,
                         {'Content-Type': 'application/json'})


@events_adapter.on('action')
def action_handler(action_value):
    if action_value == 'yes':
        return ok_response(supbot.yes_frend())
    if action_value == 'no':
        return ok_response(supbot.no_frend())
    if action_value == 'maybe':
        return ok_response(supbot.maybe_frend())

    return f"No handler found for '{action_value}' answer."


@events_adapter.server.route("/after_button", methods=["GET", "POST"])
def respond():
    """
    This route listens for incoming message button actions from Slack.
    """
    slack_payload = json.loads(request.form["payload"])
    # get the value of the button press
    action_value = slack_payload["actions"][0]["value"]
    # handle the action
    return action_handler(action_value)


if __name__ == '__main__':
    events_adapter.start(debug=True, port=port)
