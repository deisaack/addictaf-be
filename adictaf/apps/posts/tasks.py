import atexit
import json
import logging
import os
import random
import shutil
import time
from datetime import datetime

import boto3
from celery import shared_task
from django.conf import settings

from adictaf.apps.core.models import Project
from noire.bot.base import NoireBot

from .models import HashTag, Post, Status, Username

logger = logging.getLogger(__name__)

import random
import requests
# from .models import Post

from django.core.exceptions import MultipleObjectsReturned

def check(gag_id):
    return Post.objects.filter(gag_id__iexact=gag_id).exists()

def get_gags(count, category, url):
    s=requests.session()
    step = 0
    while step < count:
        path = url + '?c=' + str(step)
        resp = s.get(path)
        step += 10
        try:
            data = resp.json()
        except:
            logger.warning('The data.json was not there for {0}'.format(url))
            continue
        try:
            objects = data['data']['posts']
        except:
            logger.error("Posts key is not there")
            continue

        for obj in objects:
            if not check(obj['id']):
                try:
                    isVideo = False
                    video = None
                    if obj['type'] == 'Animated':
                        isVideo= True
                        video = obj['images']['image460sv']['url']
                    post, created = Post.objects.update_or_create(
                        gag_id = obj['id'],
                        defaults={
                            'id': random.randint(1000, 100000000),
                            'caption': obj['title'],
                            'is_video': isVideo,
                            'image': obj['images']['image700']['url'],
                            'video': video,
                            'category': category
                        }
                    )
                except MultipleObjectsReturned: pass
                except: raise

from .models import GagLink
def crawl_gags():
    logger.info('Crawling gags')
    links = GagLink.objects.all()
    logger.info('There are {0} gags'.format(len(links)))
    for link in links:
        get_gags(count=200, category=link.category, url=link.path)
        logger.info('Getting '+ links.path + ' ')

class LoadUserPosts(object):
    def __init__(self, userid, category, count):
        self.category = category
        self.userId = userid
        self.count = count
        self.item_count = 0
        self.next_max_id = ''
        self.proj = Project.objects.filter(active=True).last()
        self.bot = NoireBot(self.proj.username, self.proj.get_password)
        self.more_available = False
        self.load()
        self.close()
        # atexit.register(self.close)
        # atexit.register(self.upload_to_s3)

    def load(self):
        logger.info('Loading user posts for {0}'.format(self.userId))
        while self.item_count < self.count:
            if not self.bot.getUserFeed(self.userId, self.next_max_id):
                logger.error('Failed to load info')
                break
            if not 'items' in self.bot.LastJson:
                logger.error('no items from request')
                break
            items = self.bot.LastJson['items']
            if "more_available" not in self.bot.LastJson or not self.bot.LastJson["more_available"]:
                self.more_available = False
            else:
                self.next_max_id = self.bot.LastJson["next_max_id"]
                self.more_available = True
            for item in items:
                try:
                    media_id = item["media_type"]
                    is_video = False
                    video_src = None
                    if media_id == 1:
                        img = item["image_versions2"]["candidates"][0]["url"]
                    elif media_id == 2:
                        img = item["image_versions2"]["candidates"][0]["url"]
                        is_video = True
                        video_src = item['video_versions'][-1]['url']
                    elif media_id == 8:
                        img = item["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
                    else:
                        img = None
                        logger.warning('A new media id was found {0!}'.format(media_id))

                    post, created = Post.objects.update_or_create(
                        id=item['pk'],
                        defaults={
                            "is_video": is_video,
                            "video_src": video_src,
                            "shortcode": item["code"],
                            "comments": item["comment_count"],
                            "likes": item["like_count"],
                            "owner_id": item["user"]["pk"],
                            "timestamp": datetime.fromtimestamp(item["taken_at"]).isoformat(),
                            'category': self.category
                        }
                    )

                    try:
                        post.caption_tmp = item["caption"]["text"]
                        post.save()
                        post.create_tags_and_caption()
                    except:
                        logger.warning('Probably Item has no caption')
                    if created:
                        if is_video:
                            vid_filename = '{0}_{1}'.format(
                                item['user']['username'], item['pk']
                            )
                            d = self.bot.downloadVideo(item['pk'], vid_filename, media=item)
                            path = str(d).split('live')
                            video_url = path[-1][1:]
                            post.video = settings.CDN_URL + video_url
                            post.video_sm = video_url.replace('videos/', 'videos/sm/')
                            post.save()
                        if img is not None:
                            img_filename = '{0}_{1}.jpg'.format(
                                item['user']['username'], item['pk']
                            )
                            d = self.bot.downloadPhoto(img, img_filename)
                            path = str(d).split('live')
                            img_url = path[-1][1:]
                            post.image = settings.CDN_URL + img_url
                            post.image_sm = img_url.replace('photos/', 'photos/sm/')
                            post.save()
                except: pass

            if not self.more_available:
                break
            time.sleep(random.random() * 2)
            self.item_count += len(items)
            # break

    def upload_to_s3(self):
        all_files = set()
        items = os.walk(settings.LIVE_DIR)
        for path, folders, files in items:
            all_files.add(path)

            for file in files:
                filename = path + '/' + file
                all_files.add(filename)

        all_files = list(all_files)
        s3 = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        for key, item in enumerate(all_files):
            if os.path.isdir(item):
                continue
            file_name = item.split('live')[-1][1:]
            try:
                s3.upload_file(item, bucket_name, file_name)
            except Exception as e:
                logger.error("Failed to upload file upload file due to {0!s}".format(e))
                continue
            if 'media' in item:
                try:
                    os.remove(item)
                    logger.info('Item deleted')
                except FileNotFoundError:
                    logger.warning('Failed to deleteitem')

    def close(self):
        self.upload_to_s3()
        self.bot.save_responce()
        self.proj.requests += self.bot.total_requests
        # shutil.rmtree(self.bot.mediaDir, ignore_errors=False, onerror=None)
        self.proj.save()


class LoadTagPosts(object):
    def __init__(self, tag, category, count):
        self.category = category
        self.tag = tag
        self.count = count
        # self.next_max_id = ''
        self.proj = Project.objects.filter(active=True).last()
        self.bot = NoireBot(self.proj.username, self.proj.get_password)
        # self.more_available = False
        self.load()
        self.close()
        # atexit.register(self.close)
        # atexit.register(self.upload_to_s3)

    def load(self):
        tag_posts = self.bot.getTotalHashtagFeed(self.tag, count=20)
        logger.info('Loading tag posts for {0}'.format(self.tag))

        with open(self.tag + '.json', 'w') as f:
            json.dump(tag_posts, f, ensure_ascii=False, sort_keys=True, indent=4)

        for item in tag_posts:
            try:
                media_id = item["media_type"]
                is_video = False
                if media_id == 1:
                    img = item["image_versions2"]["candidates"][0]["url"]
                elif media_id == 2:
                    img = item["image_versions2"]["candidates"][0]["url"]
                    is_video = True
                elif media_id == 8:
                    img = item["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
                else:
                    img = None
                    logger.warning('A new media id was found {0!}'.format(media_id))

                post, created = Post.objects.update_or_create(
                    id=item['pk'],
                    defaults={
                        "is_video": is_video,
                        "shortcode": item["code"],
                        "comments": item["comment_count"],
                        "likes": item["like_count"],
                        "owner_id": item["user"]["pk"],
                        "timestamp": datetime.fromtimestamp(item["taken_at"]).isoformat(),
                        'category': self.category
                    }
                )

                if created:
                    try:
                        post.caption_tmp = item["caption"]["text"]
                        post.save()
                        post.create_tags_and_caption()
                    except:
                        logger.warning('Probably Item has no caption')

                    if is_video:
                        vid_filename = '{0}_{1}'.format(
                            item['user']['username'], item['pk']
                        )
                        d = self.bot.downloadVideo(item['pk'], vid_filename, media=item)
                        path = str(d).split('live')
                        video_url = path[-1][1:]
                        post.video = settings.CDN_URL + video_url
                        post.video_sm = video_url.replace('videos/', 'videos/sm/')
                        post.save()
                    if img is not None:
                        img_filename = '{0}_{1}.jpg'.format(
                            item['user']['username'], item['pk']
                        )
                        d = self.bot.downloadPhoto(img, img_filename)
                        path = str(d).split('live')
                        img_url = path[-1][1:]
                        post.image = settings.CDN_URL + img_url
                        post.image_sm = img_url.replace('photos/', 'photos/sm/')
                        post.save()

            except: pass



    def upload_to_s3(self):
        all_files = set()
        items = os.walk(settings.LIVE_DIR)
        for path, folders, files in items:
            all_files.add(path)

            for file in files:
                filename = path + '/' + file
                all_files.add(filename)

        all_files = list(all_files)
        s3 = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        for key, item in enumerate(all_files):
            if os.path.isdir(item):
                continue
            file_name = item.split('live')[-1][1:]
            try:
                s3.upload_file(item, bucket_name, file_name)
            except Exception as e:
                logger.error("Failed to upload file upload file due to {0!s}".format(e))
                continue
            if 'media' in item:
                try:
                    os.remove(item)
                    logger.info('Item deleted')
                except FileNotFoundError:
                    logger.warning('Failed to deleteitem')

    def close(self):
        self.upload_to_s3()
        self.bot.save_responce()
        self.proj.requests += self.bot.total_requests
        # shutil.rmtree(self.bot.mediaDir, ignore_errors=False, onerror=None)
        self.proj.save()


@shared_task
def load_user_posts(userid, category, count):
    LoadUserPosts(userid=userid, category=category, count=count)


class DailyTask:
    def __init__(self, **kwargs):
        self.count = int(kwargs.get('count', 10))
        self.forceLogin = kwargs.get('forceLogin', False)
        self.category = kwargs.get('category', 'a')

    def periodicCrawl(self):
        names = Username.objects.all()
        for user in names:
            logger.info("The username is : " + user.name)
            self.crawl_single_username(user.name, user.category)

        tags = HashTag.objects.all()
        for tag in tags:
            logger.info("The #tag is {0}".format(tag))
            self.crawl_single_tag(tag=tag.name, category=tag.category, count=self.count)


    def crawl_single_tag(self, tag, category, count):
        logger.info('Loading user posts for {0}'.format(tag))
        LoadTagPosts(tag=tag, category=category, count=count)

    def crawl_single_username(self, username, category):
        logger.info('Loading user posts for {0}'.format(username))
        proj = Project.objects.filter(active=True).last()
        try:
            bot = NoireBot(proj.username, proj.get_password, forceLogin=self.forceLogin)
        except AttributeError:
            logger.error("No active project in db")
            return
        usernameid = bot.convert_to_user_id(username)
        logger.info("user id is + " + str(usernameid))
        LoadUserPosts(userid=usernameid, category=category, count=self.count)
        # load_user_posts(userid=usernameid, category=category, count=self.count)
        # load_user_posts.delay(userid=usernameid, category=category, count=self.count)

@shared_task
def daily_task():
    # dT = DailyTask(count=50)
    # dT.periodicCrawl()
    crawl_gags()
