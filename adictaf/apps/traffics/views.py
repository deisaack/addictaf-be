from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from . import filters as ft
from . import serializers as sz
from .models import Traffic


class TrafficViewset(viewsets.ModelViewSet):
    queryset = Traffic.objects.all()
    order_fields = ('created',)
    ordering = ('-created',)
    serializer_class = sz.TrafficSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
