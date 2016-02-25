#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-24 12:21:22
# Project: FetchComicRank

from pyspider.libs.base_handler import *
import re
from pymongo import MongoClient
import copy
import time

class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://www.dmzj.com/rank', callback=self.rank_page)

    @config(age=12 * 60 * 60)
    def rank_page(self, response):
        self.get_db()
        for each in response.doc('h3 > a').items():
            if re.match("^http\:\/\/www\.dmzj\.com\/info\/\w*\.html$", each.attr.href):
                print(each.attr.href)
                if not self.db.comic_list.find_one({'url':each.attr.href}):
                    self.db.comic_list.insert_one({'url':each.attr.href})
        self.crawl(response.doc('.pg_next').attr.href, callback=self.rank_page)

    def get_db(self):
        self.client = MongoClient()
        self.db = self.client.comic
        return self.db
    