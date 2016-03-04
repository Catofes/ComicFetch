from pymongo import MongoClient
import subprocess
import os
import re
import time


class Convert:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.comic
        self.pic_path = os.path.abspath(".") + "/Download/"
        self.mobi_path = os.path.abspath(".") + "/mobi/"

    def chapter_callback(self, chapter, flag=True):
        if flag:
            print("Converted: " + chapter['name'] + chapter['chapter'])
            self.db.comic.update_one({"_id": chapter['_id']}, {
                "$set": {
                    "mobi_size": chapter['mobi_size'],
                    "mobi": True
                }
            })
            self.db.comic_list.update_one({"name": chapter["name"]}, {"$set": {"mobi": False}})
        else:
            self.db.comic.update_one({"_id": chapter['_id']}, {"$set": {"flag": -1}})

    def comic_callback(self, comic, flag=True):
        if flag:
            print("Converted: " + comic['name'])
            self.db.comic_list.update_one({"_id": comic['_id']}, {
                "$set": {
                    "mobi_size": comic['mobi_size'],
                    "mobi": True
                }
            })
        else:
            pass

    def convert_a_chapter(self, input_chapter):
        name = input_chapter['name']
        chapter = input_chapter['chapter']
        title = name + "-" + chapter
        pic_path = self.pic_path + name + "/" + chapter + "/"
        mobi_path = self.mobi_path + name + "/"
        mobi_file = self.mobi_path + name + "/" + chapter + ".mobi"
        os.makedirs(mobi_path, exist_ok=True)
        try:
            p = subprocess.run(["nice",
                                "-n", "10",
                                "kcc-c2e",
                                "-o", mobi_path,
                                "-t", title,
                                "-f", "MOBI",
                                pic_path
                                ], stdout=subprocess.PIPE)
            if not re.search('MOBI', str(p.stdout)):
                print("Convert " + title + " Failed. STDOUT: " + p.stdout)
                return False
        except:
            print("Convert " + title + " Failed.")
            return False
        size = os.path.getsize(mobi_file)
        input_chapter['mobi_size'] = int(size)
        return True

    def convert_a_comic(self, input_comic):
        name = input_comic['name']
        title = name
        pic_path = self.pic_path + name + "/"
        mobi_path = self.mobi_path
        mobi_file = self.mobi_path + name + ".mobi"
        os.makedirs(mobi_path, exist_ok=True)
        try:
            p = subprocess.run(["nice",
                                "-n", "10",
                                "kcc-c2e",
                                "-o", mobi_path,
                                "-t", title,
                                "-f", "MOBI",
                                pic_path
                                ], stdout=subprocess.PIPE)
            if not re.search('MOBI', str(p.stdout)):
                print("Convert " + title + " Failed. STDOUT: " + p.stdout)
                return False
        except:
            print("Convert " + title + " Failed.")
            return False
        size = os.path.getsize(mobi_file)
        input_comic['mobi_size'] = int(size)
        return True

    def fetch_a_chapter(self):
        result = self.db.comic.find_one({"flag": 2, "mobi": False})
        if result:
            if self.convert_a_chapter(result):
                self.chapter_callback(result)
            else:
                self.chapter_callback(result, False)
            return True
        else:
            return False

    def fetch_a_comic(self):
        result = self.db.comic_list.find_one({"mobi": False})
        if result:
            if self.convert_a_comic(result):
                self.comic_callback(result)
            return True
        else:
            return False

    def loop(self):
        while True:
            while True:
                time.sleep(1)
                if not self.fetch_a_chapter():
                    break
            while True:
                time.sleep(1)
                if not self.fetch_a_comic():
                    break


if __name__ == '__main__':
    convert = Convert()
    convert.loop()
