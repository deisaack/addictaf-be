import atexit
import json
import logging
import os
import random
import shutil
import time
from datetime import datetime

import boto3
import requests
from celery import shared_task
from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned

from adictaf.apps.core.models import Project
from noire.bot.custom_base import NoireBot

from .models import GagLink, HashTag, Post, Status, Username

logger = logging.getLogger(__name__)

# from .models import Post


def processObj(obj, category):
    if Post.objects.filter(gag_id__iexact=obj['id']).exists():
        return False
    try:
        isVideo = False
        video = None
        tags = []
        for tag in obj['tags']:
            tags.append(tag['key'])
        if obj['type'] == 'Animated':
            isVideo = True
            video = obj['images']['image460sv']['url']
        post, created = Post.objects.get_or_create(
            gag_id=obj['id'],
            defaults={
                'id': random.randint(1000, 100000000),
                'caption': obj['title'],
                'is_video': isVideo,
                'image': obj['images']['image460']['url'],
                'video': video,
                'category': category,
                'tags': tags
            }
        )
    except MultipleObjectsReturned:
        pass
    except:
        raise

BASE = str(os.path.join(settings.NOIRE['MEDIA_DIR']))
VIDEO_DIR = BASE + "/video/"
def download_meedia(url):
    r = requests.get(url)
    filename = url.split("/")[-1]
    if r.status_code == 200:
        import urllib3
        f = open('00000001.jpg', 'wb')
        f.write(urllib3.connection_from_url('http://www.gunnerkrigg.com//comics/00000001.jpg').read())
        f.close()
        # with open(VIDEO_DIR + filename, 'wb') as f:
        #     r.raw.decode_content = True
        #     shutil.copyfileobj(r.raw, f)
        # return os.path.abspath(VIDEO_DIR + filename)

def processImgur(obj, category):
    if Post.objects.filter(gag_id=obj['id']).exists():
        return False

    isVideo = False
    tags = []
    for tag in obj['tags']:
        tags.append(tag['name'])
    try:
        image_obj = obj['images'][-1]
    except:
        return False, "No images"
    try:
        isVideo = image_obj['animated']
    except KeyError:
        pass
    if isVideo:
        video = image_obj['gifv']
    else:
        video = None
    try:
        post, created = Post.objects.get_or_create(
            gag_id=obj['id'],
            defaults={
                "id": random.randint(100000, 10000000000),
                "caption": obj["title"],
                "is_video": isVideo,
                "image": image_obj['link'],
                "video": video,
                "category": category,
                "tags": tags
            }
        )
        if video is None:
            download_meedia(post.image)


    except MultipleObjectsReturned:
        return  False, "Multiple obj"
    except Exception as e:
        return False, str(e)
    return True, post

def find_gag():
    r = requests.get('https://m.9gag.com/football/hot',
                     headers={"Accept": "application/json", 'X-Requested-With': 'XMLHttpRequest'}
                     )
    data = r.json()['data']['posts']
    for obj in data:
        processObj(obj, category='SPORTSMEME')
    return True


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
            processObj(obj, category)
    return True

def crawl_gags():
    logger.info('Crawling gags')
    links = GagLink.objects.all()
    logger.info('There are {0} gags'.format(len(links)))
    for link in links:
        get_gags(count=200, category=link.category, url=link.path)
        logger.info('Getting '+ link.path + ' ')

class LoadUserPosts(object):
    def __init__(self, userid, category, count):
        self.category = category
        self.userId = userid
        self.count = count
        self.item_count = 0
        self.next_max_id = ''
        self.proj = Project.objects.filter(active=True).last()
        self.bot = NoireBot(self.proj.id)
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
        # shutil.rmtree(self.bot.mediaDir, ignore_errors=False, onerror=None)

class LoadTagPosts(object):
    def __init__(self, tag, category, count):
        self.category = category
        self.tag = tag
        self.count = count
        # self.next_max_id = ''
        self.proj = Project.objects.filter(active=True).last()
        self.bot = NoireBot(self.proj.id)
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
            bot = NoireBot(proj.id)
        except AttributeError:
            logger.error("No active project in db")
            return
        usernameid = bot.get_userid_from_username(username)
        logger.info("user id is + " + str(usernameid))
        LoadUserPosts(userid=usernameid, category=category, count=self.count)
        # load_user_posts(userid=usernameid, category=category, count=self.count)
        # load_user_posts.delay(userid=usernameid, category=category, count=self.count)


def imgur():
    r = requests.get(
        "https://api.imgur.com/3/gallery/t/soccer/",
        headers={
            "Authorization": "Client-ID 748ccbb88149c61"
        }
    )
    data = r.json()['data']['items']
    count = 0
    for obj in  data:
        o = processImgur(obj, "SPORTSMEME")
        print(count)
        print(o)
        count+=1
    return count


from .actions import share_image
# def daily_task():
#     crawl_gags()

# from .actions import share_image
from noire.bot.web import bot

@shared_task
def daily_task():
    bot.crawl()

    try: crawl_gags()
    except: pass
    try:find_gag()
    except: pass
