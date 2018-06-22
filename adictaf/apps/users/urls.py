from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('user', views.UserViewset, base_name='users')

app_name = 'users'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('create-user/', views.create_user, name='create_user'),
]

urlpatterns+=router.urls
