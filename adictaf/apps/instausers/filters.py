from __future__ import absolute_import

from django_filters import rest_framework as filters

from .models import InstaUser


class InstaUserFilter(filters.FilterSet):
    min_followers = filters.NumberFilter(name="follower_count", lookup_expr='gte')
    max_followers = filters.NumberFilter(name="follower_count", lookup_expr='lte')
    min_followings = filters.NumberFilter(name="following_count", lookup_expr='gte')
    max_followings = filters.NumberFilter(name="following_count", lookup_expr='lte')
    min_posts= filters.NumberFilter(name="posts", lookup_expr='gte')
    max_posts = filters.NumberFilter(name="posts", lookup_expr='lte')

    class Meta:
        model = InstaUser
        fields = (
            'min_followers', 'max_followers', 'min_followings',
            'max_posts', 'min_posts'
        )
