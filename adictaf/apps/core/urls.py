from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('advert', views.AdvertViewset, base_name='advert')

app_name = 'core'
urlpatterns = [
    path('get-advert/', views.get_advert, name='get_advert'),
]

urlpatterns += router.urls
