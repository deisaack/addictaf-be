import logging
import os
import random
import time
from datetime import datetime

from celery import shared_task
from django.conf import settings

from adictaf.apps.core.models import Project
from noire.bot.base import NoireBot

from .models import Post

logger = logging.getLogger(__name__)
import boto3
import os
import atexit
import shutil

class LoadUserPosts(object):
    def __init__(self, userid, count):
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
                media_id=item["media_type"]
                is_video = False
                video_src=None
                video_url = None
                if media_id == 1:
                    img = item["image_versions2"]["candidates"][0]["url"]
                    thum = item["image_versions2"]["candidates"][-1]["url"]
                elif media_id == 2:
                    img = item["image_versions2"]["candidates"][0]["url"]
                    thum = item["image_versions2"]["candidates"][-1]["url"]
                    is_video = True
                    video_src = item['video_versions'][0]['url']


                elif media_id == 8:
                    img = item["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
                    thum = item["carousel_media"][0]["image_versions2"]["candidates"][-1]["url"]
                else:
                    img = None
                    thum = None
                    logger.warning('A new media id was found {0!}'.format(media_id))

                post, created = Post.objects.update_or_create(
                        id = item['pk'],
                        defaults={
                            "is_video": is_video,
                            "video_src": video_src,
                            "shortcode": item["code"],
                            "comments": item["comment_count"],
                            "image": img,
                            "thumbnail": thum,
                            "likes": item["like_count"],
                            "owner_id": item["user"]["pk"],
                            "timestamp": datetime.fromtimestamp(item["taken_at"]).isoformat(),
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
                        path = str(d).split('media')
                        video_url = path[-1][1:]
                        post.video_hd = video_url
                        post.video_sm = video_url.replace('videos/', 'videos/sm/')
                        post.save()
                    if img is not None:
                        img_filename = '{0}_{1}.jpg'.format(
                            item['user']['username'], item['pk']
                        )
                        d = self.bot.downloadPhoto(img, img_filename, small_url=thum)
                        path = str(d).split('media')
                        img_url = path[-1][1:]
                        post.image_hd = img_url
                        post.image_sm = img_url.replace('photos/', 'photos/sm/')
                        post.save()

            if not self.more_available:
                break
            time.sleep(random.random()*2)
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
        for key, item in enumerate(all_files):
            if os.path.isdir(item):
                continue
            file_name = item.split('live')[-1][1:]
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            try:
                s3.upload_file(item, bucket_name, file_name)
            except Exception as e:
                logger.error("Failed to upload file upload file due to {0!s}".format(e))

    def close(self):
        self.upload_to_s3()
        self.bot.save_responce()
        self.proj.requests = self.bot.total_requests
        shutil.rmtree(self.bot.mediaDir, ignore_errors=False, onerror=None)
        self.proj.save()

@shared_task
def load_user_posts(userid, count=10):
    LoadUserPosts(userid, count)

