# sup
Better standup bot for slack

Basic functionality:
- remind people to post their updates in #standup
- Collect responses & send email report to pablo
- start-of-day & end-of-day standups

## Installation

Clone this repo

ensure you're in an environment (virtual or real) with python 3.7+

create a .env file with the following:

```bash
export CLIENT_ID='your_slack_app_client_id'
export CLIENT_SECRET='your_slack_app_client_secret'
export SIGNING_SECRET='your_slack_app_signing_secret'
export SQLALCHEMY_DB_URI='sqlite:///temp.db'
export PORT=7676
```

I assume you've already set up an app in slack. it's pretty easy to do. just
like google it or something.

Then install dependencies

```bash
pip install -r requirements
```

then run the init script

```bash
source .env && python init.py
```

And that should be it.

## Running

do this:

```bash
source .env && python app.py
```

This will start the botappserverthing, listening for http requests on port
7676. If you want it to listen on a different port, put that port number in the
.env file.

If you are running locally, you'll probably want ngrok. Assuming you have it
installed, run it with

```bash
ngrok http 7676
```

this will use up a shell, so use tmux or tabs or whatever.  Make a note of the
forwarding addresses, you'll need them soon

If you used a different port, update this command accordingly, or you can
do like

```bash
ngrok http $PORT
```

and if you sourced .env, it should get the port from there too.

## Revenge of the Install

haha you thought you were done? PSYCH!!!

now you need to install the app in slack.  go to localhost:7676/install in your
browser and follow the buttons.

You'll also have to wire up the events listening in Slack's web ui. Just look
for something like 'events'. Enable it and put in the ngrok forwarding address
plus '/slack'. (e.g. `https://8randoms.ngrok.io/slack`)
