from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Traffic(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    path = models.TextField(blank=True)

    def __str__(self):
        if not self.user:
            return str(self.ip)
        return self.user.username
