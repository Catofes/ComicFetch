#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-02-25 09:41:57
# Project: FetchComicUpdate

from pyspider.libs.base_handler import *
import time


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=5)
    def on_start(self):
        self.crawl('http://www.dmzj.com/update', callback=self.dmzj_update_page)

    @config(age=3 * 60)
    def dmzj_update_page(self, response):
        result = []
        for each in response.doc('.comic_list_det').items():
            data = each('h3 > a')
            name = data.attr.title
            url = data.attr.href
            update_time = each('.con_data')
            update_time = update_time.text()
            update_time = time.mktime(time.strptime(update_time, "%Y-%m-%d %H:%M"))
            info = {"name": name, "url": url, "time": update_time}
            result.append(info)
        self.send_message('FetchComicList', result)
