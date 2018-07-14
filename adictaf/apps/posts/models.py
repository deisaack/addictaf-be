from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models

from adictaf.apps.activities.models import Activity
from adictaf.utilities.common import id_generator
from adictaf.utilities.managers import SafiBaseManager, Status


class Category:
    ADDICTAF = 'ADDICTAF'
    SPORTSMEME = 'SPORTSMEME'


class TagBlacklist(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Username(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.name + ' ' + self.category

class GagLink(models.Model):
    path = models.CharField(max_length=50)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.path + ' > ' + self.category


class BaseObj(models.Model):
    name = models.CharField(max_length=50, primary_key=True, unique=True)
    category = models.CharField(max_length=20)

    def __str__(self):
        return self.name + ' ' + self.category

    class Meta:
        abstract = True

class HashTag(BaseObj):
    pass

class Post(models.Model):
    # id = models.CharField(primary_key=True, unique=True, validators=[MinValueValidator(1)])
    id = models.CharField(primary_key=True, unique=True, max_length=100)
    shortcode = models.CharField(max_length=20, default=id_generator)
    comments = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(null=True, blank=True)
    owner_id = models.BigIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    tags = ArrayField(models.CharField(max_length=500), default=list)
    taged_users = ArrayField(models.CharField(max_length=500), default=list, size=50)
    caption = models.CharField(null=True, blank=True, max_length=5000)
    caption_tmp = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True, max_length=1000)
    image_hd = models.ImageField(null=True, blank=True)
    image_sm = models.ImageField(null=True, blank=True)
    video = models.URLField(null=True, blank=True, max_length=1000)
    video_src = models.URLField(null=True, blank=True, max_length=1000)
    video_hd = models.FileField(null=True, blank=True)
    video_sm = models.FileField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True, max_length=1000)
    is_video = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.CharField(max_length=10, default=Status.NEW)
    source = models.CharField(max_length=25, default='INSTAGRAM')
    activities = GenericRelation(Activity, blank=True, null=True, related_query_name='posts')
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    gag_id = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, default=Category.ADDICTAF)
    is_posted = models.BooleanField(default=False)

    objects = SafiBaseManager()

    def __str__(self):
        return str(self.id)

    def delete(self, *args, **kwargs):
        if self.status==Status.IN_THRASH:
            return super(Post, self).delete(*args, **kwargs)
        else:
            self.status = Status.IN_THRASH
            self.save()

    def publish(self):
        self.status= Status.PUBLISHED
        self.save()

    def create_tags_and_caption(self):
        caption = self.caption_tmp
        if caption is None:
            return
        caption = caption.strip().split()
        tags = []
        text = []
        for word in caption:
            if word[0] != '#':
                if word != '-' and word != '|' and word[0] != '@':
                    text.append(word)
                continue
            tags.append(word[1:])

        v_tags = list(set(self.tags+tags))
        black = [t['name'].lower() for t in TagBlacklist.objects.all().values('name')]
        for b in black:
            while b in v_tags: v_tags.remove(b)
        self.tags=v_tags
        self.caption = ' ' .join(text)
        self.save()
