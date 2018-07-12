from django.db import models

from adictaf.utilities.crypto import SafiCrypto

from django.contrib.postgres.fields import ArrayField, JSONField

class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=False)
    requests = models.PositiveIntegerField(default=0)
    max_session_time = models.PositiveIntegerField(default=1000000)
    force_login = models.BooleanField(default=False)
    proxy= models.CharField(max_length=1000, blank=True)
    last_json = JSONField(blank=True, null=True)
    uuid = models.UUIDField(blank=True, null=True)
    device_id = models.CharField(blank=True, max_length=100)
    user_id = models.BigIntegerField(default=0)
    max_likes_to_like = models.IntegerField(default=0)

    def set_password(self, password):
        s=SafiCrypto()
        pwd=s.make_token(password)
        self.password = pwd
        self.save()

    @property
    def get_password(self):
        s=SafiCrypto()
        pwd=s.decode_token(self.password)
        return pwd

    def check_password(self, password):
        return self.get_password == password

    @property
    def rank_token(self):
        return "%s_%s" % (self.user_id, self.uuid)

    def get_uuid(self, uuid_type=False):
        generated_uuid = str(self.uuid)
        if (uuid_type):
            return generated_uuid
        else:
            return generated_uuid.replace('-', '')

class Advert(models.Model):
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=300)
    image = models.URLField()

    def __str__(self):
        return self.title
