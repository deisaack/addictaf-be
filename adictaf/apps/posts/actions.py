from adictaf.apps.posts.models import Post
from noire.bot.custom_base import NoireBot
from adictaf.apps.core.models import Project
import requests
import os
import shutil
from django.conf import settings
import logging
from random import randint


logging.getLogger()
__all__ = ['share_image']

count = 5
def share_image(objId=None, count=0):
    count +=1
    if count >=5:
        return False
    queryset= Post.objects.filter(
        is_video=False, is_posted=False)\
        .order_by('-created')
    try:
        if objId is not None:
            post=queryset.get(id=objId)
        else:
            post = Post.objects.order_by('-created')[randint(1, 200)]
    except Exception as e:
        return False, "Item already posted or {0!s}".format(e)
    filename = settings.LIVE_DIR + '/' + post.image.split('/')[-1]
    response = requests.get(post.image, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

        bot = NoireBot(Project.objects.filter(active=True).first().id)
        post.is_posted=True
        post.save()
        share = bot.uploadPhoto(filename, caption=post.caption)
        os.remove(filename)
        if not share:
            share_image(count=count)
        return True
    return False