import datetime
import logging
from django.conf import settings
import os
import requests


class Imgur(object):
    def __init__(self):
        self.logger = logging.getLogger('[imgur_{}]'.format(id(self)))
        fh = logging.FileHandler(filename=settings.NOIRE['LOG_FILE'])
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
        fh.setFormatter(formatter)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch_formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(ch_formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.DEBUG)
        now_time = datetime.datetime.now()
        log_string = 'GetInfo v1.2.0 started at %s:' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.logger.info(log_string)
        self.baseDir = str(os.path.join(settings.NOIRE['BASE_DIR']))
        self.mediaDir = str(os.path.join(settings.NOIRE['MEDIA_DIR']))
        self.s = requests.Session()

    def start(self):
        r = self.s.get("https://imgur.com/")
        return self.s.get("https://imgur.com/t/football")

imgur = Imgur()
