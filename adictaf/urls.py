from decouple import config
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from adictaf.apps.posts import urls as post_url
from django.urls import include

admin.site.site_header = 'AdictAF'
admin.site.site_title = 'Adict AF'
admin.site.index_title = 'AdictAF SITE ADMINISTRATION'


urlpatterns = [
    path('developer/', admin.site.urls),
    path('core/', include('adictaf.apps.core.urls', namespace='core')),
    path('posts/', include('adictaf.apps.posts.urls', namespace='posts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
