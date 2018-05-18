from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db import models

from adictaf.utilities.managers import SafiBaseManager, Status


class Post(models.Model):
    id = models.BigIntegerField(primary_key=True, unique=True, validators=[MinValueValidator(1)])
    shortcode = models.CharField(max_length=20, null=True, blank=True)
    comments = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(null=True, blank=True)
    owner_id = models.BigIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    tag = models.CharField(null=True, blank=True, max_length=20)
    other_tags = ArrayField(models.CharField(max_length=50), default=list)
    taged_users = ArrayField(models.CharField(max_length=50), default=list, size=50)
    caption = models.TextField(null=True, blank=True)
    image = models.URLField(null=True, blank=True, max_length=1000)
    image_url = models.ImageField(null=True, blank=True)
    video_src = models.URLField(null=True, blank=True, max_length=1000)
    video_url = models.FileField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True, max_length=1000)
    is_video = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.CharField(max_length=10, default=Status.NEW)

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
