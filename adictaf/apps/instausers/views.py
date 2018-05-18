from __future__ import absolute_import

from django.contrib.auth.models import User
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from . import filters as ft
from . import serializers as sz
# from . import tasks
from .models import InstaUser, Username


class InstaUserViewset(viewsets.ModelViewSet):
    queryset = InstaUser.objects.active()
    serializer_class = sz.InstaUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ft.InstaUserFilter
    search_fields = ('biography', 'username',)
    ordering_fields = (
            'follower_count', 'following_count', 'posts', 'created'
        )
    ordering = ('-created', )
