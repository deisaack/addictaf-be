

URLS = [
    "https://www.instagram.com/explore/tags/football/?__a=1"
]
import requests
from adictaf.apps.posts.models import Post
from django.conf import settings
import os
import shutil
import boto3


class WebBot(object):
    def __init__(self, category="SPORTSMEME"):
        self.post_detail_url = "https://www.instagram.com/p/{0}/?__a=1"
        self.category = category
        self.s = requests.Session()
        self.posts = []

    def crawl(self):
        self.posts = []
        for url in URLS:
            self.fetch(url)
        for post in self.posts:
            self.save(post['node'])

    def fetch(self, url):
        r = self.s.get(url)
        if r.status_code == 200:
            data = r.json()
            self.posts += data['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            self.posts += data['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges']

    def save(self, post):
        is_video = post['is_video']
        try:
            img = post['thumbnail_resources'][-1]['src']
        except:
            img = None
        try:
            caption = post['edge_media_to_caption']['edges'][0]['node']['text']
        except:
            caption = ""
        p, created = Post.objects.get_or_create(
            id = post['id'],
            defaults={
                "is_video": is_video,
                "caption_tmp": caption,
                "shortcode": post['shortcode'],
                'category': self.category,
                'image': img
            }
        )
        p.create_tags_and_caption()
        if is_video:
            self.get_single_video(p)

    def get_single_video(self, instance):
        r = self.s.get(self.post_detail_url.format(instance.shortcode))
        if not r.status_code == 200:
            return
        data = r.json()
        try:
            video= data['graphql']['shortcode_media']['video_url']
        except:
            return
        response = self.s.get(video, stream=True)
        if not response.status_code == 200:
            return
        dir = str(os.path.join(settings.NOIRE['MEDIA_DIR'])) + "/videos/"
        if os.path.exists(dir):
            pass
        else:
            os.makedirs(dir)
        filename = dir + str(instance.id) + ".mp4"
        with open(filename, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        upload = self.upload_to_s3(filename)
        instance.video = upload
        instance.save()


    def upload_to_s3(self, filename):
        s3 = boto3.client('s3')
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        upload_location = filename.split('live')[-1][1:]
        try:
            s3.upload_file(filename, bucket_name, upload_location)
        except Exception as e:
            return None
        try:
            os.remove(filename)
        except FileNotFoundError:
            return None
        return upload_location


bot = WebBot()

if __name__ == '__main__':
    bot.crawl()

