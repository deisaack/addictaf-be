from __future__ import absolute_import

from django.db import models

from .constants import Status

__all__ = ['SafiBaseManager']


class SafiBaseQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=Status.IN_THRASH)

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.delete()


class SafiBaseManager(models.Manager):
    def get_queryset(self):
        return SafiBaseQuerySet(self.model, using=self._db)  # Important!

    def active(self):
        return self.get_queryset().active()
