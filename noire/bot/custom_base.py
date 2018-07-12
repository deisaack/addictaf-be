#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import atexit
import datetime
import hashlib
import hmac
import json
import logging
import os
import pickle
import sys
import time
import urllib
import urllib.parse
import uuid
from random import randint
from urllib.parse import urlparse

import requests
import requests.cookies
from django.conf import settings
from tqdm import tqdm

from .api_photo import configurePhoto, downloadPhoto, uploadPhoto
from .api_profile import (editProfile, getProfileData, removeProfilePicture,
                          setNameAndPhone, setPrivateAccount, setPublicAccount)
from .api_search import (fbUserSearch, searchLocation, searchTags,
                         searchUsername, searchUsers)
from .api_video import configureVideo, downloadVideo, uploadVideo
from .bot_filter import filter_medias
from .bot_get import (convert_to_user_id, get_archived_medias,
                      get_total_user_medias, get_user_medias,
                      get_userid_from_username, get_your_medias)
from .prepare import delete_credentials, get_credentials

__all__ = ['NoireBot', ]

from adictaf.apps.core.models import Project
from django.db import transaction


class NoireLoginException(RuntimeError):
    pass


class NoireBot(object):
    def __init__(self, projectId,
                 ):
        self.project = Project.objects.get(id=projectId)
        self.start_time = datetime.datetime.now()
        self.logger = logging.getLogger('[noire_{}]'.format(id(self)))
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
        self.token = ''
        now_time = datetime.datetime.now()
        log_string = 'GetInfo v1.2.0 started at %s:' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.logger.info(log_string)
        self.s = requests.Session()
        self.total_requests = 0
        self.isLoggedIn = False
        self.LastResponse = None
        # self.login()
        self.baseDir = str(os.path.join(settings.NOIRE['BASE_DIR']))
        self.mediaDir = str(os.path.join(settings.NOIRE['MEDIA_DIR']))
        self.userDir = self.baseDir + '/users/{0!s}/'.format(self.project.username)
        self.sessionFile = self.userDir + 'jar'
        self.userInfoFile = self.userDir + 'userinfo.json'
        self.testDir = self.baseDir + '/test/'

        self.photosDir = self.mediaDir + '/photos/'
        self.smPhotosDir = self.mediaDir + '/photos/sm/'
        self.videosDir = self.mediaDir + '/videos/'
        self.smVideosDir = self.mediaDir + '/videos/sm/'
        atexit.register(self.close)
        self.make_dirs()
        self.login()

    def make_dirs(self):
        all_dirs = [
            self.baseDir, self.userDir, self.testDir, self.smPhotosDir, self.smVideosDir
        ]
        for dir in all_dirs:
            if os.path.exists(dir): continue
            os.makedirs(dir)

    def close(self):
        now_time = datetime.datetime.now()
        log_string = 'NoireBot Clossed at %s: hurrray' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        if os.path.exists(self.sessionFile): self.__save_cookies()
        self.logger.info(log_string)

    def login(self, force=None, proxy=None):
        if not os.path.exists(self.userDir):
            os.mkdir(self.userDir)
        detail, success = self.__load_cookies()
        self.logger.info(detail)
        if success:
            try:
                self.token = self.s.cookies.get('csrftoken', path='i.instagram.com')
            except requests.cookies.CookieConflictError:
                raise
            self.s.headers.update({'X-CSRFToken': self.token})
            self.isLoggedIn = True
            log_string = 'Successfully logedin from cookies only'
            self.logger.info(log_string)
            return True
        self.logger.error(detail)
        return False


    def SendRequest(self, endpoint, post=None, login=False):
        if (not self.isLoggedIn and not login):
            self.logger.critical("Not logged in.")
            raise Exception("Not logged in!")

        self.s.headers.update({'Connection': 'close',
                               'Accept': '*/*',
                               'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'User-Agent': settings.NOIRE['USER_AGENT']})
        try:
            self.project.requests += 1
            self.project.save()
            if post is not None:  # POST
                response = self.s.post(
                    settings.NOIRE['API_URL'] + endpoint, data=post)
            else:  # GET
                response = self.s.get(
                    settings.NOIRE['API_URL'] + endpoint)
        except Exception as e:
            self.logger.warning(str(e))
            return False

        if response.status_code == 200:
            self.LastResponse = response
            self.LastJson = json.loads(response.text)
            status = True
        else:
            self.logger.error("Request return %s error!", str(response.status_code))
            if response.status_code == 429:
                sleep_minutes = 6
                self.logger.warning("That means 'too many requests'. "
                                    "I'll go to sleep for %d minutes.", sleep_minutes)
                time.sleep(sleep_minutes * 60)
            elif response.status_code == 400:
                response_data = json.loads(response.text)
                self.logger.info("Instagram error message: %s", response_data.get('message'))
                if response_data.get('error_type'):
                    self.logger.info('Error type: %s', response_data.get('error_type'))

            # for debugging
            try:
                self.LastResponse = response
                self.LastJson = json.loads(response.text)
            except Exception:
                pass
            status = False

        self.__save_cookies()
        self.__save_user()
        return status

    def generateSignature(self, data):
        try:
            parsedData = urllib.parse.quote(data)
        except AttributeError:
            parsedData = urllib.parse.quote(data)

        return 'ig_sig_key_version=' + settings.NOIRE['SIG_KEY_VERSION'] + '&signed_body=' + hmac.new(
            settings.NOIRE['IG_SIG_KEY'].encode('utf-8'), data.encode('utf-8'),
            hashlib.sha256).hexdigest() + '.' + parsedData

    def logout(self):
        if not self.isLoggedIn:
            return True
        resp = self.SendRequest('accounts/logout/')
        if resp:
            self.isLoggedIn = not resp
            os.remove(self.sessionFile)
            self.logger.info("Bot stopped. "
                             "Worked: %s", datetime.datetime.now() - self.start_time)
        return not self.isLoggedIn

    def __modification_date(self, filename):
        """generateSignature
        return last file modification date as datetime object
        """
        t = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(t)

    def __load_cookies(self):
        if self.project.force_login: return 'A new login is a must when ForceLogin', False
        if not os.path.isfile(self.sessionFile): return 'cookie file not found', False
        modTime = self.__modification_date(self.sessionFile)
        lastModification = (datetime.datetime.now() - modTime)
        if lastModification.seconds > self.project.max_session_time:
            return 'File too old, Last access {0}m ago) '.format(lastModification.min), False
        with open(self.sessionFile, 'rb') as f:
            cookies = pickle.load(f)
            if not cookies: return 'Cookies not found', False
            jar = requests.cookies.RequestsCookieJar()
            jar._cookies = cookies
            self.s.cookies = jar
        return 'Cookies successfully loaded', True

    def __save_cookies(self):
        with open(self.sessionFile, 'wb') as f:
            f.truncate()
            pickle.dump(self.s.cookies._cookies, f)

    def __save_user(self, data=None):
        if data is None: data = self.LastJson
        with transaction.atomic():
            self.project.requests += 1
            self.project.last_json = data
            self.project.save()

        with open(self.userInfoFile, 'w') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)

    def get_your_medias(self, as_dict=False):
        """
        Returns your media ids. With parameter as_dict=True returns media as dict.
        :type as_dict: bool
        """
        return get_your_medias(self, as_dict)


    def uploadPhoto(self, photo, caption=None, upload_id=None):
        return uploadPhoto(self, photo, caption, upload_id)


    def getSelfUserFeed(self, maxid='', minTimestamp=None):
        return self.getUserFeed(self.project.user_id, maxid, minTimestamp)


    def getUserFeed(self, usernameId, maxid='', minTimestamp=None):
        url = 'feed/user/{username_id}/?max_id={max_id}&min_timestamp={min_timestamp}&rank_token={rank_token}&ranked_content=true'.format(
            username_id=usernameId,
            max_id=maxid,
            min_timestamp=minTimestamp,
            rank_token=self.project.rank_token
        )
        return self.SendRequest(url)


    def filter_medias(self, media_items, filtration=True, quiet=False, is_comment=False):
        return filter_medias(self, media_items, filtration, quiet, is_comment)


    def configurePhoto(self, upload_id, photo, caption=''):
        return configurePhoto(self, upload_id, photo, caption)


    def expose(self):
        data = json.dumps({
            '_uuid': self.project.get_uuid(),
            '_uid': self.project.user_id,
            'id': self.project.user_id,
            '_csrftoken': self.token,
            'experiment': 'ig_android_profile_contextual_feed'
        })
        return self.SendRequest('qe/expose/', self.generateSignature(data))

    def get_user_medias(self, username, filtration=True, is_comment=False):
        return get_user_medias(self, username, filtration, is_comment)


    def convert_to_user_id(self, usernames):
        return convert_to_user_id(self, usernames)

    def get_userid_from_username(self, username):
        return get_userid_from_username(self, username)


    def searchUsername(self, username):
        return searchUsername(self, username)

    def downloadPhoto(self, source_url, filename, **kwargs):
        return downloadPhoto(self, source_url, filename, **kwargs)

    # def downloadPhoto(self, media_id, filename, media=False, path='local/photos/'):
    #     return downloadPhoto(self, media_id, filename, media, path)

    def uploadVideo(self, photo, caption=None, upload_id=None):
        return uploadVideo(self, photo, caption, upload_id)

    def downloadVideo(self, media_id, filename, **kwargs):
        return downloadVideo(self, media_id, filename, **kwargs)

    # def settingsureVideo(self, upload_id, video, thumbnail, caption=''):
    #     return settingsureVideo(self, upload_id, video, thumbnail, caption)

    def configureVideo(self, upload_id, video, thumbnail, caption=''):
        return configureVideo(self, upload_id, video, thumbnail, caption='')

    def editMedia(self, mediaId, captionText=''):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'caption_text': captionText
        })
        return self.SendRequest('media/' + str(mediaId) + '/edit_media/', self.generateSignature(data))

    def removeSelftag(self, mediaId):
        data = json.dumps({
            '_uuid': self.project.get_uuid(),
            '_uid': self.project.get_uuid(),
            '_csrftoken': self.token
        })
        return self.SendRequest('media/' + str(mediaId) + '/remove/', self.generateSignature(data))

    def mediaInfo(self, mediaId):
        data = json.dumps({
            '_uuid': self.project.get_uuid(),
            '_uid': self.project.user_id,
            '_csrftoken': self.project.token,
            'media_id': mediaId
        })
        return self.SendRequest('media/' + str(mediaId) + '/info/', self.generateSignature(data))


    def getTotalHashtagFeed(self, hashtagString, count):
        hashtag_feed = []
        next_max_id = ''

        with tqdm(total=count, desc="Getting hashtag medias", leave=False) as pbar:
            while True:
                self.getHashtagFeed(hashtagString, next_max_id)
                temp = self.LastJson
                try:
                    pbar.update(len(temp["items"]))
                    for item in temp["items"]:
                        hashtag_feed.append(item)
                    if len(temp["items"]) == 0 or len(hashtag_feed) >= count:
                        return hashtag_feed[:count]
                except Exception:
                    return hashtag_feed[:count]
                next_max_id = temp["next_max_id"]

    def getHashtagFeed(self, hashtagString, maxid=''):
        return self.SendRequest('feed/tag/' + hashtagString + '/?max_id=' + str(
            maxid) + '&rank_token=' + self.token + '&ranked_content=true&')
