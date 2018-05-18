import logging
import os


class LoggingMixin(object):
    def __init__(self):

        self.logger = logging.getLogger('[instabot_{}]'.format(id(self)))

        fh = logging.FileHandler(filename='instabot.log')
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(message)s')
        fh.setFormatter(formatter)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.DEBUG)
