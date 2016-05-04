#!/usr/bin/python

import sqlite3

class Database:
    def __init__(self):
        self.connect()

    def connect(self):
        self.conn = sqlite3.connect('lifebot.db')

    def get_cursor(self):
        # A bit weird for now but trying to figure out SQLite
        try:
            return self.conn.cursor()
        except Exception, e:
            self.connect()
            return self.conn.cursor()

    def create_table(self, query):
        c = self.get_cursor()
        c.execute(query)
        self.conn.commit()
        self.conn.close()

    def get(self, query, args = None):
        if args is None:
            args = tuple()
        c = self.get_cursor()
        c.execute(query, args)
        return c.fetchone()

    def get_all(self, query, args = None):
        if args is None:
            args = tuple()
        c = self.get_cursor()
        c.execute(query, args)
        return c.fetchall()

    def insert(self, query, args = None):
        if args is None:
            args = tuple()
        c = self.get_cursor()
        c.execute(query, args)
        self.conn.commit()
        return c.lastrowid
