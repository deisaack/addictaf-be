from django.contrib.auth.middleware import get_user
from django.contrib.gis.geoip2 import GeoIP2
from django.utils.functional import SimpleLazyObject
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import Traffic


class LogTrafic(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = SimpleLazyObject(lambda: self.__class__.get_jwt_user(request))
        obj = {
            'ip': request.META.get('REMOTE_ADDR', ''),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'user_id': request.user.id,
            'path': request.get_full_path()
        }
        Traffic.objects.create(**obj)
        return self.get_response(request)

    @staticmethod
    def get_jwt_user(request):
        user = get_user(request)
        if user.is_authenticated:
            return user
        jwt_authentication = JSONWebTokenAuthentication()
        if jwt_authentication.get_jwt_value(request):
            user, jwt = jwt_authentication.authenticate(request)
        return user
