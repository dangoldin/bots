#!/usr/bin/python

import requests
import json
import re
import random

import settings

from flask import Flask
from flask import request

from database import Database

app = Flask(__name__)

db = Database()

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

def get_or_create_user(db, username, userid):
    data = db.get('select * from users where userid = ?', (userid,))
    if data is None:
        i = db.insert('INSERT INTO users (username, userid, created_date) VALUES (?, ?, CURRENT_TIMESTAMP)', (username, userid))
        data = (i, username, userid, '')
    return data

chat_id integer UNIQUE, user_id integer, active
def get_or_create_user(db, chatid):
    data = db.get('select * from chats where userid = ?', (userid,))
    if data is None:
        i = db.insert('INSERT INTO chats (chat_id, user_id, active) VALUES (?, ?, 1, CURRENT_TIMESTAMP)', (username, userid))
        data = (i, username, userid, '')
    return data

def get_users(db):
    data = db.get_all('select * from users')
    if data is None:
        return []
    return data

@app.route('/danblogbot', methods=['POST'])
def dan_blog_bot():
    message = request.get_json()

    print message

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_DANBLOG)

    posts = get_posts()

    if '/blogme' in message['message']['text']:
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
        username = message['message']['from']['username']
        userid = message['message']['from']['id']

        chatid = message
        print username, userid

        user = get_or_create_user(db, username, userid)

        user_id = user[0]

        get_or_create_chat(db, )

def send_poll(user):
    telegram_username = user[1]
    telegram_userid = user[2]

    print telegram_userid

    telegram_url = 'https://api.telegram.org/bot{0}/'.format(settings.TELEGRAM_TOKEN_DANBLOG)

    chat_id = '@' + telegram_username
    text = 'How are you doing today?'
    parse_mode = 'HTML'
    r = requests.post(telegram_url + 'sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode})

    print r.status_code
    if r.status_code != 200:
        print r.content

def send_polls():
    users = get_users(db)

    for user in users:
        send_poll(user)

if __name__ == '__main__':
    db.create_table('CREATE TABLE IF NOT EXISTS users (id integer PRIMARY KEY, telegram_username text, telegram_user_id integer UNIQUE, created_date text)')

    db.create_table('CREATE TABLE IF NOT EXISTS chats (id integer PRIMARY KEY, telegram_chat_id integer UNIQUE, user_id integer, active integer, created_date text)')

    # get_or_create_user(db, 'Test Name', 'Test Id')

    # app.run(debug=True)

    test_lifebot()

    # send_polls()
