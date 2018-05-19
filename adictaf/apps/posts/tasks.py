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


@shared_task
def load_user_posts(userid):
    logger.info('Loading user posts for {0}'.format(userid))
    proj = Project.objects.filter(active=True).last()
    try:
        bot = NoireBot(proj.username, proj.get_password)
    except AttributeError:
        logger.error("No active project in db")
        print('failed')
        return


    # def getTotalUserFeed(self, usernameId, minTimestamp=None):
    next_max_id = ''
    while 1:
        if not bot.getUserFeed(userid, next_max_id):
            logger.error('Failed to load info')
            break

        if not 'items' in bot.LastJson:
            logger.error('no items from request')
            break

        items = bot.LastJson['items']
        dwnload_path = os.path.join(settings.MEDIA_ROOT + '/noire/')
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
                vid_filename = 'video/{0}_{1}'.format(
                    item['user']['username'], item['pk']
                )
                bot.downloadVideo(item['pk'], vid_filename, media=item, path=dwnload_path)
                video_url = 'noire/'+vid_filename+'.mp4'

            elif media_id == 8:
                img = item["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
                thum = item["carousel_media"][0]["image_versions2"]["candidates"][0]["url"]
            else:
                img = None
                thum = None
                logger.warning('A new media id was found {0!}'.format(media_id))

            img_url = None
            if img is not None:
                img_filename = 'photo/{0}_{1}.png'.format(
                    item['user']['username'], item['pk']
                )
                bot.downloadPhoto(img, img_filename, dwnload_path)
                img_url = 'noire/'+img_filename

            post, created = Post.objects.update_or_create(
                    id = item['pk'],
                    defaults={
                        "is_video": is_video,
                        "video_src": video_src,
                        "image_url": img_url,
                        "shortcode": item["code"],
                        "video_url": video_url,
                        "caption": item["caption"]["text"],
                        "comments": item["comment_count"],
                        "image": img,
                        "thumbnail": thum,
                        "likes": item["like_count"],
                        "owner_id": item["user"]["pk"],
                        "timestamp": datetime.fromtimestamp(item["taken_at"]).isoformat(),
                    }
                )

        if "more_available" not in bot.LastJson or not bot.LastJson["more_available"]:
            break

        next_max_id = bot.LastJson["next_max_id"]
        time.sleep(random.random()*2)

    bot.save_responce()
    proj.requests = bot.total_requests
    proj.save()
