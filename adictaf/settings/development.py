from .base import *

ALLOWED_HOSTS = ['*']
CORS_ORIGIN_ALLOW_ALL = True
STATIC_URL='/static/'
STATIC_ROOT=os.path.join(LIVE_DIR, 'static')

MEDIA_URL='/media/'
MEDIA_ROOT=os.path.join(LIVE_DIR, 'media')
