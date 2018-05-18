from django.db import models
from adictaf.utilities.crypto import SafiCrypto

class Project(models.Model):
    name = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=25)
    password = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=False)
    requests = models.PositiveIntegerField(default=0)

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


class Advert(models.Model):
    title = models.CharField(max_length=50)
    text = models.CharField(max_length=300)
    image = models.URLField()

    def __str__(self):
        return self.title
