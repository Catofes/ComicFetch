#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-19 16:49:40
# Project: TEST

from pyspider.libs.base_handler import *
import re
from pymongo import MongoClient
import copy
import time

path="~/Comic_Fetch/"

class Handler(BaseHandler):
    crawl_config = {
    }

    def get_db(self):
        self.client = MongoClient()
        self.db = self.client.comic
        return self.db

    @every(minutes=6*60)
    def on_start(self):
        self.get_db()
        other_comic_lists = self.db.comic_list.find({})
        for i in other_comic_lists:
            self.update_comic(i['url'])

    def update_comic(self, url):
        if re.match("http://www.dmzj.com/info/", url):
            self.crawl(url, callback=self.new_comic_index)
        elif re.match("http://manhua.dmzj.com/", url):
            self.crawl(url, callback=self.old_comic_index)
        else:
            pass

    @config(priority=1, age= 5 * 60)
    def old_comic_index(self, response):
        self.get_db()
        name = response.doc('h1').text()
        self.db.comic_list.update_one({'url': response.url},
                                     {'$set': {'update_time': time.time(), 'name':name}})
        for each in response.doc('.cartoon_online_border li a').items():
            self.crawl(each.attr.href, callback=self.comic_chapter,save=
                       {'name': name, 'chapter': each.text(), 'pic':{}, 'flag':0}, fetch_type='js')

    @config(priority=1, age= 5 * 60)
    def new_comic_index(self, response):
        self.get_db()
        name = response.doc('title').text().split(" ")[0]
        self.db.comic_list.update_one({'url': response.url},
                                     {'$set': {'update_time': time.time(), 'name':name}})
        for each in response.doc('.zj_list > .tab-content-selected li a').items():
            self.crawl(each.attr.href, callback=self.comic_chapter,save=
                       {'name': name, 'chapter': each.text(), 'pic':{}, 'flag':0}, fetch_type='js')

    @config(priority=2)
    def comic_chapter(self, response):
        data = response.save
        flag = False
        for each in response.doc('option[value^="http"]').items():
            try:
                 if each.attr.value == "":
                        flag = True
                        continue
                 data['pic'][re.findall(r'[\d|.]+',each.text())[0]] = each.attr.value
            except:
                 continue
        if flag or not data['pic'] or not len(response.doc('option[value^="http"]')):
            try:
                info = response.doc('.comic_wraCon a')
                image = response.doc('.comic_wraCon img')
                data['pic'][re.findall(r'[\d|.]+',info.attr.id)[0]] = image.attr.src
            except:
                pass
            next = response.doc('.next_url')
            if next:
                self.crawl(next.attr.href, callback=self.comic_chapter,save=data, fetch_type='js')
            else:
                return self.download_chapter(data)
            return
        return self.download_chapter(data)

    def on_message(self, project, message):
        self.get_db()
        for each in message:
            result = self.db.comic_list.find_one({'url': each['url']})
            if result:
                if result['update_time'] < each['time']:
                    self.update_comic(each['url'])

    def download_chapter(self, data):
        for i in range(0,2):
            try:
                result = self.db.comic.find_one({'name':data['name'],'chapter':data['chapter']})
                if not result or not result['pic']:
                    self.db.comic.insert_one(data)
                    print("Saved:    " + data['name'] +"    "+ data['chapter'])
                break
            except:
                self.get_db()
                if i == 1 :
                    return "FALSE"
        result = copy.copy(data)
        result['_id']=""
        return result
                        