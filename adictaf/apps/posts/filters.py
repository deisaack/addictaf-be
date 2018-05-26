from __future__ import absolute_import

from django_filters import rest_framework as filters

from .models import Post


class PostFilter(filters.FilterSet):
    class Meta:
        model = Post
        fields = {
            'owner_id': ['exact'],
            'is_video': ['exact'],
            'likes': ['lte', 'gte'],
            'timestamp': ['year__gt', 'gte'],
            'comments': ['lte', 'gte'],
            'created': ['exact', 'year__gt'],
        }
