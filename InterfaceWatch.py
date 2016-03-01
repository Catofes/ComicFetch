#!/usr/bin/python

import subprocess
import re
import time


class Main:
    def __init__(self):
        self.check_list = [
            "204.79.197.200",
            "123.56.158.109",
            "10.20.0.1",
            "106.185.46.113"
        ]

    def check_one(self, destination):
        try:
            p = subprocess.Popen('timeout 2 ping ' + str(destination) + ' -c 1 -i 0.1 -q', stdout=subprocess.PIPE,
                                 shell=True)
            return_code = p.wait()
            if return_code == 0:
                return True
            return False
        except:
            return False

    def check_all(self):
        for destination in self.check_list:
            if self.check_one(destination):
                return True
            else:
                print("Check IP " + destination + " Failed.")
        print("Check Failed. Try to restart Network.")
        return False

    def loop(self):
        while True:
            result = self.check_all()
            if not result:
                self.failed()
            time.sleep(10)

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
