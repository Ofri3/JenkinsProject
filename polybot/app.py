import os
import flask
from flask import request
from bot import Bot, QuoteBot, ImageProcessingBot

app = flask.Flask(__name__)

TELEGRAM_TOKEN = ''
TELEGRAM_APP_URL = 'https://t.me/@Smileythebot'


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    print(req)
    if 'message' in req:
        QuoteBot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    QuoteBot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
