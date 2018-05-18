from decouple import config
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('traffic', views.TrafficViewset, base_name='traffic')

app_name = 'traffic'
urlpatterns=[
    path('', include(router.urls)),
]
