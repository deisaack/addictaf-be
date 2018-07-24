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

count = 0
def share_image(objId=None, count=0):
    count +=1
    if count >=5:
        return False
    queryset= Post.objects.exclude(
        is_video=True, is_posted=True)\
        .order_by('-created')
    try:
        if objId is not None:
            post=queryset.get(id=objId)
        else:
            post = Post.objects.order_by('-created')[randint(1, 200)]
    except Exception as e:
        return False, "Item already posted or {0!s}".format(e)
    print('aaaaaaaaaaaaaa')
    filename = settings.LIVE_DIR + '/' + post.image.split('/')[-1]
    response = requests.get(post.image, stream=True)
    if response.status_code == 200:
        print('bbbbbbbbbbbbbbbbb')
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)

        bot = NoireBot(Project.objects.filter(active=True).first().id)
        print('ccccccccccccccccccc')
        post.is_posted=True
        post.save()
        share = bot.uploadPhoto(filename, caption=post.caption)
        print('dddddddddddddddd')
        caption = str(post.caption) + ". To see more, visit https://www.addictaf.com/post?id={0!s}".format(post.id)
        post_with_image(filename, caption=caption)
        os.remove(filename)
        if not share:
            print('eeeeeeeeeeeeee')
            share_image(count=count)
        return True
    return False


from decouple import config
import facebook


def get_page():
    page_id = config('PAGE_ID')
    access_token = config('ACCESS_TOKEN')
    graph = facebook.GraphAPI(access_token=access_token)
    resp = graph.get_object('me/accounts')
    page_access_token = None
    for page in resp['data']:
        if page['id'] == page_id:
            page_access_token=page['access_token']
    graph = facebook.GraphAPI(page_access_token)
    return graph

def post_to_wall():
    graph =get_page()
    attachment = {
        "link": "http://sportsmeme.addictaf.com/post/?id=27663988"
    }
    graph.put_wall_post("Just check this", attachment=attachment)

def post_with_image(filename, caption):
    print('fffffffffffffffffff')
    with open(filename, "rb") as img:
        graph = get_page()
        graph.put_photo(img, message=caption)
        print('ggggggggggggggggggggggggg')


def post_image_to_album():
    album = '287938268420845'
    with open("102.jpeg", "rb") as img:
        graph = get_page()
        graph.put_photo(img, album_path=album+'/photos')

def update_profile_pic():
    album = '287938268420845'
    with open("102.jpeg", "rb") as img:
        graph = get_page()
        graph.put_photo(img, album_path=album+'/photos')



