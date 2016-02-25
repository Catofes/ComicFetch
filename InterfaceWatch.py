#!/usr/bin/python

import subprocess
import re
import time


class Main:
    def __init__(self):
        self.check_list = [
            "bing.com",
            "8.8.8.8",
            "123.56.158.109",
            "baidu.com"
        ]

    def check_one(self, destination):
        try:
            p = subprocess.Popen('ping ' + str(destination) + ' -c 10 -i 0.1 -q', shell=True,
                                 stdout=subprocess.PIPE)
            p.wait()
            result = p.stdout.read()
            p.kill()
            result = re.findall(r"\d*\s*received", str(result.decode()))
            if result[0].split()[0] == "0":
                return False
            return True
        except:
            return False

    def check_all(self):
        for destination in self.check_list:
            if self.check_one(destination):
                return True
        return False

    def loop(self):
        while True:
            result = self.check_all()
            if not result:
                print(time.ctime() + " : " + str(result))
                self.failed()

    def failed(self):
        p = subprocess.Popen('ip link set eth1 down', shell=True)
        p.wait()
        p = subprocess.Popen('systemctl restart dhcpcd@eth1', shell=True)
        p.wait()
        p = subprocess.Popen('systemctl restart railgun-network', shell=True)
        p.wait()
        time.sleep(10)


if __name__ == '__main__':
    main = Main()
    main.loop()
