#!/usr/bin/python

import requests
import json
import re
import random

import settings

from flask import Flask, request, Response

import twilio.twiml

from database import Database

app = Flask(__name__)

# db = Database()

RE_LINK = re.compile('<a.+?\d{4}\/\d{2}\/\d{2}\/.+?a>')
RE_HREF = re.compile('href=\"(.+)\"')
RE_TITLE = re.compile('>(.+)<')

MAX_POSTS = 10

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

def get_quotes(quote_url = 'https://raw.githubusercontent.com/dangoldin/quotes/master/quotes.txt'):
    r = requests.get(quote_url)
    c = r.content

    lines = c.split("\n")
    quotes = []
    curr_quote = {
        'lines': []
    }
    for line in lines:
        # Add the quote
        if line.strip() == '':
            if 'who' not in curr_quote:
                curr_quote['who'] = 'Unattributed'

            quotes.append(curr_quote)
            curr_quote = {
                'lines': []
            }
            continue

        # Attribution
        if line.strip().startswith('-'):
            curr_quote['who'] = line.strip().strip('-').strip()
            continue

        # Actual quote
        curr_quote['lines'].append(line)

    return quotes

def parse_num_posts(msg):
    pieces = msg.split(' ')
    if len(pieces) == 0:
        return 1
    else:
        try:
            return min(MAX_POSTS, int(pieces[1]))
        except Exception as e:
            print 'Failed to parse msg', e
            return 1

def get_or_create_user(db, telegram_username, telegram_user_id):
    data = db.get('select * from users where telegram_user_id = ?', (telegram_user_id,))
    if data is None:
        i = db.insert('INSERT INTO users (telegram_username, telegram_user_id, created_date) VALUES (?, ?, CURRENT_TIMESTAMP)', (telegram_username, telegram_user_id))
        data = (i, telegram_username, telegram_user_id, '')
    return data

def get_or_create_chat(db, telegram_chat_id, user_id):
    data = db.get('select * from chats where telegram_chat_id = ?', (telegram_chat_id,))
    if data is None:
        i = db.insert('INSERT INTO chats (telegram_chat_id, user_id, active, created_date) VALUES (?, ?, 1, CURRENT_TIMESTAMP)', (telegram_chat_id, user_id))
        data = (i, telegram_chat_id, user_id, '')
    return data

def get_users(db):
    data = db.get_all('select * from users')
    if data is None:
        return []
    return data

def get_chats(db):
    data = db.get_all('select * from chats where active')
    if data is None:
        return []
    return data

def to_flask_response(twilio_response):
    print 'Response', str(twilio_response)
    resp = Response(str(twilio_response))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

@app.route('/')
def index():
    return '<html><head>Bots</head><body>It works</body></html>'

@app.route('/quoteme', methods=['POST', 'GET'])
def quote_me():
    quotes = get_quotes()
    quote = random.choice(quotes)
    return '<br/'.join(quote['lines']) + '<br/>- ' + quote['who']

@app.route('/twilio-danblogpost', methods=['POST'])
def twilio_dan_blog_bot():
    print request, request.form, request.data

    msg = request.form.get('Body','')
    fro = request.form.get('From','')

    if 'blog' in msg.lower():
        posts = get_posts()
        posts = random.sample(posts, 1)

        body = ''
        for post in posts:
            body += "{0}: {1}\n".format(post[1], post[0])

        response = twilio.twiml.Response()
        response.message(body)
        return to_flask_response(response)
    else:
        response = twilio.twiml.Response()
        response.message('Unable to process msg {0} and number {1}'.format(str(msg), str(fro)))
        return to_flask_response(response)

@app.route('/danblogbot', methods=['POST'])
def dan_blog_bot():
    message = request.get_json()

    print message

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_DANBLOG)

    if '/blogme' in message['message']['text']:
        posts = get_posts()
        num_posts = parse_num_posts(message['message']['text'])
        posts = random.sample(posts, num_posts)
        for post in posts:
            chat_id = message['message']['chat']['id']
            text = '<a href="{0}">{1}</a>'.format(post[0], post[1])
            parse_mode = 'HTML'
            r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})
    elif '/help' in message['message']['text'] or '/start' in message['message']['text']:
        chat_id = message['message']['chat']['id']
        text = 'Just reply with /blogme to get a random blog post. For more fun do /blogme X where X is a number to get multiple posts (up to 10)'
        parse_mode = 'HTML'
        r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})

    return 'Success'

@app.route('/lifebot', methods=['POST'])
def life_bot():
    message = request.get_json()

    print message

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_LIFE)

    # Get/create user

    # Update user records

    # Randomly cron + run something

    return 'Success'

def test_blogme():
    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_DANBLOG)

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

def test_lifebot():
    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_LIFE)

    r = requests.get(telegram_url + 'getMe')
    print json.dumps(r.json(), indent=2)

    r = requests.get(telegram_url + 'getUpdates')
    print json.dumps(r.json(), indent=2)

    messages = r.json()['result']

    for message in messages:
        telegram_username = message['message']['from']['username']
        telegram_userid = message['message']['from']['id']
        telegram_chatid = message['message']['chat']['id']

        # telegram_chatid = message
        print telegram_username, telegram_userid

        user = get_or_create_user(db, telegram_username, telegram_userid)

        user_id = user[0]

        get_or_create_chat(db, telegram_chatid, user_id)

def send_poll(chat):
    telegram_chat_id = chat[1]

    print telegram_chat_id

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_LIFE)

    text = 'How are you doing today?'
    parse_mode = 'HTML'
    reply_markup = {'resize_keyboard': False, 'one_time_keyboard': True, 'keyboard': [['Great', 'Eh', 'Terrible']]}
    r = requests.post(telegram_url + 'sendMessage', json={'chat_id': telegram_chat_id, 'text': text, 'parse_mode': parse_mode, 'reply_markup': reply_markup})

    if r.status_code != 200:
        print r.content

def send_polls():
    chats = get_chats(db)

    for chat in chats:
        send_poll(chat)

if __name__ == '__main__':
    # db.create_table('CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, telegram_username text, telegram_user_id integer UNIQUE, created_date text)')
    # db.create_table('CREATE TABLE IF NOT EXISTS chats (id integer PRIMARY KEY, telegram_chat_id integer UNIQUE, user_id integer, active integer, created_date text)')

    # get_or_create_user(db, 'Test Name', 'Test Id')

    app.run(debug=True)

    # test_lifebot()
    # send_polls()
