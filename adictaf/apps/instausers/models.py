from django.core.validators import MinValueValidator
from django.db import models
from django.utils.timezone import now

from adictaf.utilities.managers import SafiBaseManager, Status


class InstaUser(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True, validators=[MinValueValidator(1)])
    username = models.CharField(max_length=200, unique=True)
    follower_count = models.PositiveIntegerField(null=True, blank=True)
    following_count = models.PositiveIntegerField(null=True, blank=True)
    full_name = models.CharField(null=True, blank=True, max_length=250)
    biography = models.TextField(null=True, blank=True)
    profile_pic = models.URLField(null=True, blank=True)
    thumbnail = models.URLField(null=True, blank=True)
    posts = models.PositiveIntegerField(null=True, blank=True)
    usertags_count = models.PositiveIntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, blank=True)
    status = models.CharField(max_length=10, default=Status.NEW)
    estimate_location = models.CharField(blank=True, max_length=100)
    estimate_count = models.PositiveIntegerField(default=0)

    objects = SafiBaseManager()

    def __str__(self):
        return str(self.id)

    def delete(self, *args, **kwargs):
        if self.status == Status.IN_THRASH:
            return super(InstaUser, self).delete(*args, **kwargs)
        else:
            self.status = Status.IN_THRASH
            self.save()

class Username(models.Model):
    name = models.CharField(unique=True, primary_key=True, max_length=100)
    created = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def scrapped(self):
        return InstaUser.objects.filter(username__iexact=self.name).exists()
