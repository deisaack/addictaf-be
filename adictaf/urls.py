from decouple import config
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from adictaf.apps.posts import urls as post_url

admin.site.site_header = 'AdictAF'
admin.site.site_title = 'Adict AF'
admin.site.index_title = 'AdictAF SITE ADMINISTRATION'
from . import views

urlpatterns = [
    path('developer/', admin.site.urls),
    path('policy/', views.Policy.as_view()),
    path('core/', include('adictaf.apps.core.urls', namespace='core')),
    path('files/', include('adictaf.apps.files.urls', namespace='files')),
    path('posts/', include('adictaf.apps.posts.urls', namespace='posts')),
    path('users/', include('adictaf.apps.users.urls', namespace='users')),
]

handler404 = 'adictaf.views.handler404'
handler500 = 'adictaf.views.handler500'
# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
