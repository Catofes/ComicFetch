#!/usr/bin/python

from pymongo import MongoClient
import threading
import queue
import os
import urllib.request, urllib.parse
import time
import argparse


class DownloadManager:
    def __init__(self):
        self.download_path = os.path.abspath(".") + "/Download/"
        self.max_thread = 3
        self._threads = []
        self.data = queue.Queue()
        self.tmp_path = "/tmp"
        self.event = threading.Event()

    def append(self, chapter):
        self.data.put(chapter)
        self.event.set()

    def start(self):
        self._threads = [t for t in self._threads if t.is_alive()]
        if len(self._threads) < self.max_thread:
            for i in range(0, self.max_thread - len(self._threads)):
                self._threads.append(DownloadThread(self))
        for t in self._threads:
            if not t.is_alive():
                t.setDaemon(True)
                t.start()


class DownloadThread(threading.Thread):
    def __init__(self, manager):
        threading.Thread.__init__(self)
        self.manager = manager

    def run(self):
        while True:
            self.manager.event.wait(20)
            chapter = None
            try:
                chapter = self.manager.data.get(False)
            except queue.Empty:
                self.manager.event.clear()
            if not self.download(chapter):
                self.manager.append(chapter)

    def download(self, chapter):
        if not chapter:
            return True
        name = chapter['name']
        chapter_name = chapter['chapter']
        pic = chapter['pic']
        path = self.manager.download_path + name + '/' + chapter_name
        os.makedirs(path, exist_ok=True)
        for (k, v) in pic.items():
            try:
                urllib.request.urlretrieve("http://" + urllib.parse.quote(v[7:]), path + "/" + str(k) + '.jpg')
            except:
                print("Download Error: " + name + " " + chapter_name + " " + str(k))
                return False
            print("Download : " + name + " " + chapter_name + " " + str(k))
        callback = chapter['callback']
        callback(chapter)
        time.sleep(1)
        return True


class MongodbManager:
    def __init__(self, dm=DownloadManager()):
        self.dm = dm
        self.client = MongoClient()
        self.db = self.client.comic
        self.comic_name = None
        self.selector = {}
        self.force = False

    def build_selector(self):
        if not self.force:
            self.selector['flag'] = 0
        if self.comic_name:
            self.selector['name'] = self.comic_name

    def loop_forever(self):
        self.build_selector()
        self.db.test.update_many({'flag': 1},
                                 {'$set': {'flag': 0}})
        while True:
            self.add_data()
            print(self.dm.data.qsize())
            time.sleep(10)

    @staticmethod
    def callback(chapter):
        try:
            self = chapter['self']
            self.db.test.update_one({'_id': chapter['_id']}, {"$set": {"flag": 2}})
        except:
            print("Callback Error.")

    def add_data(self):
        try:
            result = self.db.test.find(self.selector)
            for i in result:
                chapter = dict()
                chapter['_id'] = i['_id']
                chapter['name'] = i['name']
                chapter['pic'] = i['pic']
                chapter['chapter'] = i['chapter']
                chapter['self'] = self
                chapter['callback'] = self.callback
                self.dm.append(chapter)
                self.db.test.update_one({'_id': i['_id']}, {'$set': {'flag': 1}})
        except:
            print("Fetch Data Error.")


def build_arg_parser():
    parser = argparse.ArgumentParser(description='Comic Fetch')
    parser.add_argument('-a', '--all', action='store_true', help="Download All Picture")
    parser.add_argument('-o', '--output', help="Output path.")
    parser.add_argument('-f', '--force', action='store_true', help="Force Re-download")
    parser.add_argument('-n', '--name', help="Name of Comic.")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
    return parser


if __name__ == '__main__':
    args = build_arg_parser().parse_args()
    mm = MongodbManager()
    if args.output:
        mm.dm.download_path = args.output
    if not args.name and not args.all:
        print("Input Name of Comic.")
        exit()
    if args.name:
        mm.comic_name = args.name
    if args.force:
        mm.force = True
    mm.dm.start()
    mm.loop_forever()
