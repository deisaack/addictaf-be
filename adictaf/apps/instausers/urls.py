from __future__ import absolute_import

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('instauser', views.InstaUserViewset, base_name='instauser')
router.register('action', views.InstauserActionViewset, base_name='action')


app_name = 'instauser'
urlpatterns = [
    path('', include(router.urls)),
    path('crawl_user/<str:username>/', views.crawl_user, name='crawl_user'),
    path('crawl_usernames/', views.crawl_usernames, name='crawl_usernames'),
    path('export_instausers_xls/', views.export_instausers_xls, name='export_instausers_xls'),
]
