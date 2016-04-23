#!/usr/bin/python

import requests
import json
import re
import random

import settings

from flask import Flask
from flask import request

app = Flask(__name__)

RE_LINK = re.compile('<a.+?\d{4}\/\d{2}\/\d{2}\/.+?a>')
RE_HREF = re.compile('href=\"(.+)\"')
RE_TITLE = re.compile('>(.+)<')

def parse_post_html(base_url, html):
    link = base_url + RE_HREF.findall(html)[0]
    title = RE_TITLE.findall(html)[0]

    return (link, title)

def get_posts(blog_url = 'http://dangoldin.com'):
    r = requests.get(blog_url)
    c = r.content

    raw_posts = RE_LINK.findall(c)
    posts = [parse_post_html(blog_url, x) for x in raw_posts]

    return posts

@app.route('/danblogbot', methods=['POST'])
def dan_blog_bot():
    message = request.get_json()

    print message

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN)

    posts = get_posts()

    if '/blogme' in message['message']['text']:
        post = random.choice(posts)
        chat_id = message['message']['chat']['id']
        text = '<a href="{0}">{1}</a>'.format(post[0], post[1])
        parse_mode = 'HTML'
        r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})
    elif '/help' in message['message']['text'] or '/start' in message['message']['text']:
        chat_id = message['message']['chat']['id']
        text = 'Just reply with /blogme to get a random blog post'
        parse_mode = 'HTML'
        r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})

    return 'Success'

def test():
    r = requests.get(telegram_url + 'getMe')
    print json.dumps(r.json(), indent=2)

    r = requests.get(telegram_url + 'getUpdates')
    print json.dumps(r.json(), indent=2)

    messages = r.json()['result']

    for message in messages:
        if '/blogme' in message['message']['text']:
            post = random.choice(posts)
            chat_id = message['message']['chat']['id']
            text = '<a href="{0}">{1}</a>'.format(post[0], post[1])
            parse_mode = 'HTML'
            r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})

if __name__ == '__main__':
    app.run(debug=True)
