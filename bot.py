# -*- coding: utf-8 -*-
"""
In this file, we'll create a python Bot Class.
"""
import os
import json

from dataclasses import dataclass

from slack import WebClient

DEFAULT_CACHE_PATH = 'auth_cache.json'


@dataclass
class Bot:
    client_id: str
    client_secret: str
    scope: str = 'bot'

    bot_user_id: str = None
    bot_access_token: str = None
    client: object = None

    cache_path: str = DEFAULT_CACHE_PATH

    """ Instanciates a Bot object to handle Slack interactions."""
    def __post_init__(self):
        if os.path.isfile(self.cache_path):
            with open(self.cache_path) as fp:
                blob = json.load(fp)
                self.bot_user_id = blob['user_id']
                self.bot_access_token = blob['access_token']

        self.client = WebClient(token=self.bot_access_token)

    def auth(self, code):
        """
        Here we'll create a method to exchange the temporary auth code for an
        OAuth token and save it in memory on our Bot object for easier access.
        """
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.client_id,
            client_secret=self.client_secret,
            code=code
        )
        if auth_response['ok']:
            self.bot_user_id = auth_response["bot"]["bot_user_id"]
            self.bot_access_token = auth_response["bot"]["bot_access_token"]

            with open(self.cache_path, 'w') as fp:
                json.dump({
                    'user_id': self.bot_user_id,
                    'access_token': self.bot_access_token
                }, fp)

            self.client = WebClient(token=self.bot_access_token)
        else:
            raise OauthFailedException(auth_response['error'])

    def say_hello(self, message):
        """
        Here we'll create a method to respond when a user DM's our bot
        to say hello!
        """
        channel = message['channel']

        text = f"Sup, <@{message['user']}>."

        response = self.client.chat_postMessage(
            channel=channel,
            text=text,
        )
        if not response['ok']:
            raise SayHelloException(response['error'])

        return response


class SupException(BaseException):
    """
    General exception class for Sup
    """
    unit = 'Some bot operation'

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.unit} failed due to: {self.message}"


class OauthFailedException(SupException):
    unit = 'Oauth'


class SayHelloException(SupException):
    unit = 'say_hello'
