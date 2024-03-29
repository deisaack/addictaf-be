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

__all__ = ['NoireBot',]

class NoireLoginException(RuntimeError):
    pass

class NoireBot(object):
    def __init__(self,
                 username,
                 password=None,
                 maxSessionTime=60 * 60 * 24 * 10,
                 forceLogin=False,
                 proxy=None,
                 max_likes_to_like=100,
                 ):
        self.start_time = datetime.datetime.now()
        self.proxy = proxy
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
        self.csrf_token = ''
        now_time = datetime.datetime.now()
        log_string = 'GetInfo v1.2.0 started at %s:' % \
                     (now_time.strftime("%d.%m.%Y %H:%M"))
        self.logger.info(log_string)
        self.username = username.lower()
        self.password = password
        self.maxSessionTime = maxSessionTime  # default 10 days
        self.forceLogin = forceLogin
        if forceLogin and password is None:
            raise LookupError('password is required for a login')
        self.s = requests.Session()
        self.total_requests = 0
        self.isLoggedIn = False
        self.LastResponse = None
        self.LastJson = None
        self.uuid = self.generateUUID(True)
        # self.login()
        self.baseDir = str(os.path.join(settings.NOIRE['BASE_DIR']))
        self.mediaDir = str(os.path.join(settings.NOIRE['MEDIA_DIR']))
        self.userDir = self.baseDir+'/users/{0!s}/'.format(self.username)
        self.sessionFile = self.userDir+'jar'
        self.userInfoFile = self.userDir+'userinfo.json'
        self.testDir = self.baseDir+'/test/'

        self.photosDir = self.mediaDir+'/photos/'
        self.smPhotosDir = self.mediaDir+'/photos/sm/'
        self.videosDir = self.mediaDir+'/videos/'
        self.smVideosDir = self.mediaDir+'/videos/sm/'
        self.token = None
        self.max_likes_to_like = max_likes_to_like
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
            # except FileExistsError:
            #     pass

    def close(self):
        self.__save_cache()
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
                self.csrf_token = self.s.cookies.get('csrftoken', path='i.instagram.com')
            except requests.cookies.CookieConflictError:
                raise
            self.s.headers.update({'X-CSRFToken': self.csrf_token})
            if self.__load_user():
                self.token = self.csrf_token
                self.isLoggedIn = True
                self.user_id = self.LastJson["logged_in_user"]["pk"]
                log_string = 'Successfully logedin from cookies only'
                self.logger.info(log_string)
                self.rank_token = "%s_%s" % (self.user_id, self.uuid)
                return True

        m = hashlib.md5()
        m.update(self.username.encode('utf-8') + self.password.encode('utf-8'))
        self.proxy = proxy
        self.device_id = self.generateDeviceId(m.hexdigest())
        self.logger.info('Device Id is : {0!s}'.format(self.device_id))
        self.uuid = self.generateUUID(True)

        if (not self.isLoggedIn or force):
            if self.proxy is not None:
                parsed = urllib.parse.urlparse(self.proxy)
                scheme = 'http://' if not parsed.scheme else ''
                proxies = {
                    'http': scheme + self.proxy,
                    'https': scheme + self.proxy,
                }
                self.s.proxies.update(proxies)
            if (
                    self.SendRequest('si/fetch_headers/?challenge_type=signup&guid=' + self.generateUUID(False),
                                     None, True)):

                data = {'phone_id': self.generateUUID(True),
                        '_csrftoken': self.LastResponse.cookies['csrftoken'],
                        'username': self.username,
                        'guid': self.uuid,
                        'device_id': self.device_id,
                        'password': self.password,
                        'login_attempt_count': '0'}

                if self.SendRequest('accounts/login/', self.generateSignature(json.dumps(data)), True):
                    self.isLoggedIn = True
                    self.user_id = self.LastJson["logged_in_user"]["pk"]
                    self.rank_token = "%s_%s" % (self.user_id, self.uuid)
                    self.token = self.LastResponse.cookies["csrftoken"]

                    self.logger.info("Login success as %s!", self.username)
                    self.__save_user()
                    self.__save_cookies()
                    return True
                else:
                    self.logger.info("Login or password is incorrect.")
                    # return False
                    raise NoireLoginException

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
            self.total_requests += 1
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
            return True
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
            return False


    def generateDeviceId(self, seed):
        volatile_seed = "12345"
        m = hashlib.md5()
        m.update(seed.encode('utf-8') + volatile_seed.encode('utf-8'))
        return 'android-' + m.hexdigest()[:16]

    def generateUUID(self, uuid_type):
        generated_uuid = str(uuid.uuid4())
        if (uuid_type):
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

    def generateSignature(self, data):
        try:
            parsedData = urllib.parse.quote(data)
        except AttributeError:
            parsedData = urllib.parse.quote(data)

        return 'ig_sig_key_version=' + settings.NOIRE['SIG_KEY_VERSION'] + '&signed_body=' + hmac.new(
            settings.NOIRE['IG_SIG_KEY'].encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest() + '.' + parsedData

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
        if self.forceLogin: return 'A new login is a must when ForceLogin', False
        if not os.path.isfile(self.sessionFile): return 'cookie file not found', False
        modTime = self.__modification_date(self.sessionFile)
        lastModification = (datetime.datetime.now() - modTime)
        if lastModification.seconds > self.maxSessionTime:
            return 'File too old, Last access {0}m ago) '.format(lastModification.min), False
        with open(self.sessionFile, 'rb') as f:
            cookies = pickle.load(f)
            if not cookies: return 'Cookies not found', False
            jar = requests.cookies.RequestsCookieJar()
            jar._cookies = cookies
            self.s.cookies = jar
        return 'Cookies successfully loaded', True

    def __load_user(self):
        try:
            with open(self.userInfoFile) as json_file:
                self.LastJson = json.load(json_file)
            data = self.LastJson.get('local_cache')
            # self.total_requests = data['total_requests']
            self.uuid = data['uuid']
            self.device_id = data['device_id']
            return True
        except:
            return False

    def __save_cookies(self):
        with open(self.sessionFile, 'wb') as f:
            f.truncate()
            pickle.dump(self.s.cookies._cookies, f)

    def __save_user(self, data=None):
        if data is None: data=self.LastJson
        with open(self.userInfoFile, 'w') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)

    def save_responce(self, filename='last.json'):
        filename = str(self.testDir)+filename
        with open(filename, 'w') as f:
            json.dump(self.LastJson, f, ensure_ascii=False, sort_keys=True, indent=4)

    def __save_cache(self):
        with open(self.userInfoFile) as json_file:
            data = json.load(json_file)
        data['local_cache'] = {
            'total_requests': self.total_requests,
            'uuid': self.uuid,
            'device_id': self.device_id
        }
        self.__save_user(data=data)

    
    def uploadPhoto(self, photo, caption=None, upload_id=None):
        return uploadPhoto(self, photo, caption, upload_id)

    def configurePhoto(self, upload_id, photo, caption=''):
        return configurePhoto(self, upload_id, photo, caption)

    def expose(self):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'id': self.user_id,
            '_csrftoken': self.token,
            'experiment': 'ig_android_profile_contextual_feed'
        })
        return self.SendRequest('qe/expose/', self.generateSignature(data))

    def get_your_medias(self, as_dict=False):
        """
        Returns your media ids. With parameter as_dict=True returns media as dict.
        :type as_dict: bool
        """
        return get_your_medias(self, as_dict)

    def getSelfUserFeed(self, maxid='', minTimestamp=None):
        return self.getUserFeed(self.user_id, maxid, minTimestamp)

    def getUserFeed(self, usernameId, maxid='', minTimestamp=None):
        url = 'feed/user/{username_id}/?max_id={max_id}&min_timestamp={min_timestamp}&rank_token={rank_token}&ranked_content=true'.format(
            username_id=usernameId,
            max_id=maxid,
            min_timestamp=minTimestamp,
            rank_token=self.rank_token
        )
        return self.SendRequest(url)


    def get_archived_medias(self, as_dict=False):
        """
        Returns your archived media ids. With parameter as_dict=True returns media as dict.
        :type as_dict: bool
        """
        return get_archived_medias(self, as_dict)

    def getTimelineFeed(self):
        """ Returns 8 medias from timeline feed of logged user """
        return self.SendRequest('feed/timeline/')

    def getPopularFeed(self):
        popularFeed = self.SendRequest(
            'feed/popular/?people_teaser_supported=1&rank_token={rank_token}&ranked_content=true&'.format(
                rank_token=self.rank_token
            ))
        return popularFeed

    def get_user_medias(self, user_id, filtration=True, is_comment=False):
        return get_user_medias(self, user_id, filtration, is_comment)

    def get_total_user_medias(self, user_id):
        return get_total_user_medias(self, user_id)

    def syncFeatures(self):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'id': self.user_id,
            '_csrftoken': self.token,
            'experiments': settings.NOIRE['EXPERIMENTS']
        })
        return self.SendRequest('qe/sync/', self.generateSignature(data))

    def autoCompleteUserList(self):
        return self.SendRequest('friendships/autocomplete_user_list/')

    def megaphoneLog(self):
        return self.SendRequest('megaphone/log/')

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
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token
        })
        return self.SendRequest('media/' + str(mediaId) + '/remove/', self.generateSignature(data))

    def mediaInfo(self, mediaId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'media_id': mediaId
        })
        return self.SendRequest('media/' + str(mediaId) + '/info/', self.generateSignature(data))

    def archiveMedia(self, media, undo=False):
        action = 'only_me' if not undo else 'undo_only_me'
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'media_id': media['id']
        })
        url = 'media/{media_id}/{action}/?media_type={media_type}'.format(
            media_id=media['id'],
            action=action,
            media_type=media['media_type']
        )
        return self.SendRequest(url, self.generateSignature(data))

    def deleteMedia(self, media):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'media_id': media.get('id')
        })
        return self.SendRequest('media/' + str(media.get('id')) + '/delete/', self.generateSignature(data))

    def changePassword(self, newPassword):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'old_password': self.password,
            'new_password1': newPassword,
            'new_password2': newPassword
        })
        return self.SendRequest('accounts/change_password/', self.generateSignature(data))

    def explore(self):
        return self.SendRequest('discover/explore/')

    def comment(self, mediaId, commentText):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'comment_text': commentText
        })
        return self.SendRequest('media/' + str(mediaId) + '/comment/', self.generateSignature(data))

    def deleteComment(self, mediaId, commentId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token
        })
        return self.SendRequest('media/' + str(mediaId) + '/comment/' + str(commentId) + '/delete/',
                                self.generateSignature(data))

    def removeProfilePicture(self):
        return removeProfilePicture(self)

    def setPrivateAccount(self):
        return setPrivateAccount(self)

    def setPublicAccount(self):
        return setPublicAccount(self)

    def getProfileData(self):
        return getProfileData(self)

    def editProfile(self, url, phone, first_name, biography, email, gender):
        return editProfile(self, url, phone, first_name, biography, email, gender)

    def getUsernameInfo(self, usernameId):
        return self.SendRequest('users/' + str(usernameId) + '/info/')

    def getSelfUsernameInfo(self):
        return self.getUsernameInfo(self.user_id)

    def getRecentActivity(self):
        activity = self.SendRequest('news/inbox/?')
        return activity

    def getFollowingRecentActivity(self):
        activity = self.SendRequest('news/?')
        return activity

    def getv2Inbox(self):
        inbox = self.SendRequest('direct_v2/inbox/?')
        return inbox

    def getUserTags(self, usernameId):
        url = 'usertags/{username_id}/feed/?rank_token={rank_token}&ranked_content=true&'.format(
            username_id=usernameId,
            rank_token=self.rank_token
        )
        tags = self.SendRequest(url)
        return tags

    def getSelfUserTags(self):
        return self.getUserTags(self.user_id)

    def tagFeed(self, tag):
        userFeed = self.SendRequest(
            'feed/tag/' + str(tag) + '/?rank_token=' + str(self.rank_token) + '&ranked_content=true&')
        return userFeed

    def getMediaLikers(self, media_id):
        likers = self.SendRequest('media/' + str(media_id) + '/likers/?')
        return likers

    def getGeoMedia(self, usernameId):
        locations = self.SendRequest('maps/user/' + str(usernameId) + '/')
        return locations

    def getSelfGeoMedia(self):
        return self.getGeoMedia(self.user_id)

    def fbUserSearch(self, query):
        return fbUserSearch(self, query)

    def searchUsers(self, query):
        return searchUsers(self, query)

    def searchUsername(self, username):
        return searchUsername(self, username)

    def searchTags(self, query):
        return searchTags(self, query)

    def searchLocation(self, query='', lat=None, lng=None):
        return searchLocation(self, query, lat, lng)

    def syncFromAdressBook(self, contacts):
        return self.SendRequest('address_book/link/?include=extra_display_name,thumbnails',
                                "contacts=" + json.dumps(contacts))

    def getTimeline(self):
        query = self.SendRequest(
            'feed/timeline/?rank_token=' + str(self.rank_token) + '&ranked_content=true&')
        return query

    def getArchiveFeed(self):
        query = self.SendRequest(
            'feed/only_me_feed/?rank_token=' + str(self.rank_token) + '&ranked_content=true&')
        return query


    def getHashtagFeed(self, hashtagString, maxid=''):
        return self.SendRequest('feed/tag/' + hashtagString + '/?max_id=' + str(
            maxid) + '&rank_token=' + self.rank_token + '&ranked_content=true&')

    def getLocationFeed(self, locationId, maxid=''):
        return self.SendRequest('feed/location/' + str(locationId) + '/?max_id=' + str(
            maxid) + '&rank_token=' + self.rank_token + '&ranked_content=true&')

    def getUserFollowings(self, usernameId, maxid=''):
        url = 'friendships/{username_id}/following/?max_id={max_id}&ig_sig_key_version={sig_key}&rank_token={rank_token}'.format(
            username_id=usernameId,
            max_id=maxid,
            sig_key=settings.NOIRE['SIG_KEY_VERSION'],
            rank_token=self.rank_token
        )
        return self.SendRequest(url)

    def getSelfUsersFollowing(self):
        return self.getUserFollowings(self.user_id)

    def getUserFollowers(self, usernameId, maxid=''):
        if maxid == '':
            return self.SendRequest('friendships/' + str(usernameId) + '/followers/?rank_tp.ref oken=' + self.rank_token)
        else:
            return self.SendRequest(
                'friendships/' + str(usernameId) + '/followers/?rank_token=' + self.rank_token + '&max_id=' + str(
                    maxid))

    def getSelfUserFollowers(self):
        return self.getUserFollowers(self.user_id)

    def like(self, mediaId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'media_id': mediaId
        })
        return self.SendRequest('media/' + str(mediaId) + '/like/', self.generateSignature(data))

    def unlike(self, mediaId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'media_id': mediaId
        })
        return self.SendRequest('media/' + str(mediaId) + '/unlike/', self.generateSignature(data))

    def getMediaComments(self, mediaId):
        return self.SendRequest('media/' + str(mediaId) + '/comments/?')

    def setNameAndPhone(self, name='', phone=''):
        return setNameAndPhone(self, name, phone)

    def getDirectShare(self):
        return self.SendRequest('direct_share/inbox/?')

    def follow(self, userId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'user_id': userId,
            '_csrftoken': self.token
        })
        return self.SendRequest('friendships/create/' + str(userId) + '/', self.generateSignature(data))

    def unfollow(self, userId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'user_id': userId,
            '_csrftoken': self.token
        })
        return self.SendRequest('friendships/destroy/' + str(userId) + '/', self.generateSignature(data))

    def block(self, userId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'user_id': userId,
            '_csrftoken': self.token
        })
        return self.SendRequest('friendships/block/' + str(userId) + '/', self.generateSignature(data))

    def unblock(self, userId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'user_id': userId,
            '_csrftoken': self.token
        })
        return self.SendRequest('friendships/unblock/' + str(userId) + '/', self.generateSignature(data))

    def userFriendship(self, userId):
        data = json.dumps({
            '_uuid': self.uuid,
            '_uid': self.user_id,
            'user_id': userId,
            '_csrftoken': self.token
        })
        return self.SendRequest('friendships/show/' + str(userId) + '/', self.generateSignature(data))

    def _prepareRecipients(self, users, threadId=None, useQuotes=False):
        if not isinstance(users, list):
            return False
        result = {'users': '[[{}]]'.format(','.join(users))}
        if threadId:
            result['thread'] = '["{}"]'.format(threadId) if useQuotes else '[{}]'.format(threadId)
        return result

    def sendDirectItem(self, itemType, users, **options):
        data = {
            '_uuid': self.uuid,
            '_uid': self.user_id,
            '_csrftoken': self.token,
            'client_context': self.generateUUID(True),
            'action': 'send_item'
        }
        url = ''
        if itemType == 'links':
            data['link_text'] = options.get('text')
            data['link_urls'] = json.dumps(options.get('urls'))
            url = 'direct_v2/threads/broadcast/link/'
        elif itemType == 'message':
            data['text'] = options.get('text', '')
            url = 'direct_v2/threads/broadcast/text/'
        elif itemType == 'media_share':
            data['media_type'] = options.get('media_type', 'photo')
            data['text'] = options.get('text', '')
            data['media_id'] = options.get('media_id', '')
            url = 'direct_v2/threads/broadcast/media_share/'
        elif itemType == 'like':
            url = 'direct_v2/threads/broadcast/like/'
        elif itemType == 'hashtag':
            url = 'direct_v2/threads/broadcast/hashtag/'
            data['text'] = options.get('text', '')
            data['hashtag'] = options.get('hashtag', '')
        elif itemType == 'profile':
            url = 'direct_v2/threads/broadcast/profile/'
            data['profile_user_id'] = options.get('profile_user_id')
            data['text'] = options.get('text', '')
        recipients = self._prepareRecipients(users, threadId=options.get('thread'), useQuotes=False)
        if not recipients:
            return False
        data['recipient_users'] = recipients.get('users')
        if recipients.get('thread'):
            data['thread_ids'] = recipients.get('thread')
        return self.SendRequest(url, data)

    def getLikedMedia(self, maxid=''):
        return self.SendRequest('feed/liked/?max_id=' + str(maxid))

    def getTotalFollowers(self, usernameId, amount=None):
        sleep_track = 0
        followers = []
        next_max_id = ''
        self.getUsernameInfo(usernameId)
        if "user" in self.LastJson:
            if amount:
                total_followers = amount
            else:
                total_followers = self.LastJson["user"]['follower_count']
            if total_followers > 200000:
                pass
                # print("Consider temporarily saving the result of this big operation. This will take a while.\n")
        else:
            return False
        with tqdm(total=total_followers, desc="Getting followers", leave=False) as pbar:
            while True:
                self.getUserFollowers(usernameId, next_max_id)
                temp = self.LastJson
                try:
                    pbar.update(len(temp["users"]))
                    for item in temp["users"]:
                        followers.append(item)
                        sleep_track += 1
                        if sleep_track >= 20000:
                            sleep_time = randint(120, 180)
                            # print("\nWaiting %.2f min. due to too many requests." % float(sleep_time / 60))/
                            time.sleep(sleep_time)
                            sleep_track = 0
                    if len(temp["users"]) == 0 or len(followers) >= total_followers:
                        return followers[:total_followers]
                except Exception:
                    return followers[:total_followers]
                if temp["big_list"] is False:
                    return followers[:total_followers]
                next_max_id = temp["next_max_id"]

    def getTotalFollowings(self, usernameId, amount=None):
        sleep_track = 0
        following = []
        next_max_id = ''
        self.getUsernameInfo(usernameId)
        self.logger.debug('aaaaaaaaaa')
        if "user" in self.LastJson:
            if amount:
                total_following = amount
            else:
                total_following = self.LastJson["user"]['following_count']
            if total_following > 200000:
                pass
                # print("Consider temporarily saving the result of this big operation. This will take a while.\n")
        else:
            return False
        self.logger.debug('bbbbbbbbbbbbbbbbbbbb')
        with tqdm(total=total_following, desc="Getting following", leave=False) as pbar:
            self.logger.debug('ccccccccccccccccccc')
            while True:
                self.getUserFollowings(usernameId, next_max_id)
                temp = self.LastJson
                self.logger.debug('ddddddddddddddddd')
                try:
                    pbar.update(len(temp["users"]))
                    for item in temp["users"]:
                        self.logger.debug('eeeeeeeee')
                        following.append(item)
                        sleep_track += 1
                        if sleep_track >= 20000:
                            self.logger.debug('ffffffffffffff')
                            sleep_time = randint(120, 180)
                            # print("\nWaiting %.2f min. due to too many requests." % float(sleep_time / 60))
                            time.sleep(sleep_time)
                            sleep_track = 0
                    if len(temp["users"]) == 0 or len(following) >= total_following:
                        self.logger.debug('gggggggg')
                        return following[:total_following]
                except Exception:
                    self.logger.debug('hhhhhhhhhhhhhhhhhhhh')
                    return following[:total_following]
                if temp["big_list"] is False:
                    self.logger.debug('iiiiiiiiiiiiiiiiii')
                    return following[:total_following]
                self.logger.debug('jjjjjjjjjjjjjjjjjj')
                next_max_id = temp["next_max_id"]

    def getTotalUserFeed(self, usernameId, minTimestamp=None):
        user_feed = []
        next_max_id = ''
        while 1:
            self.getUserFeed(usernameId, next_max_id, minTimestamp)
            temp = self.LastJson
            if "items" not in temp:  # maybe user is private, (we have not access to posts)
                return []
            for item in temp["items"]:
                user_feed.append(item)
            if "more_available" not in temp or temp["more_available"] is False:
                return user_feed
            next_max_id = temp["next_max_id"]

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

    def getTotalSelfUserFeed(self, minTimestamp=None):
        return self.getTotalUserFeed(self.user_id, minTimestamp)

    def getTotalSelfFollowers(self):
        return self.getTotalFollowers(self.user_id)

    def getTotalSelfFollowings(self):
        return self.getTotalFollowings(self.user_id)

    def getTotalLikedMedia(self, scan_rate=1):
        next_id = ''
        liked_items = []
        for _ in range(0, scan_rate):
            temp = self.getLikedMedia(next_id)
            temp = self.LastJson
            next_id = temp["next_max_id"]
            for item in temp["items"]:
                liked_items.append(item)
        return liked_items

    def filter_medias(self, media_items, filtration=True, quiet=False, is_comment=False):
        return filter_medias(self, media_items, filtration, quiet, is_comment)

    def convert_to_user_id(self, usernames):
        return convert_to_user_id(self, usernames)

    def get_userid_from_username(self, username):
        return get_userid_from_username(self, username)
