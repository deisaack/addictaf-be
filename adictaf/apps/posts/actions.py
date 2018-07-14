from adictaf.apps.posts.models import Post
from noire.bot.custom_base import NoireBot
from adictaf.apps.core.models import Project
import requests
import os
import shutil
from django.conf import settings
import logging
logging.getLogger()
__all__ = ['share_image']

def share_image(objId=None):
    queryset= Post.objects.filter(is_video=False, is_posted=False)
    try:
        if objId is not None:
            post=queryset.get(id=objId)
        else:
            post = Post.objects.order_by('-created').first()
    except Exception as e:
        return False, "Item already posted or {0!s}".format(e)
    filename = settings.LIVE_DIR + '/' + post.image.split('/')[-1]
    response = requests.get(post.image, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

        bot = NoireBot(Project.objects.filter(active=True).first().id)
        post.is_posted=False
        os.remove(filename)
        post.save()
        return bot.uploadPhoto(filename, caption=post.caption)
    return False