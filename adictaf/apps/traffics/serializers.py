from django.contrib.gis.geoip2 import GeoIP2
from rest_framework import serializers
from user_agents import parse

from .models import Traffic

g = GeoIP2()

default_location = {
    'city': 'Undefined',
    'country_code': 'ud',
    'country_name': 'Undefined',
    'dma_code': None,
    'latitude': 0.0,
    'longitude': 0.0,
    'postal_code': 'N/A',
    'region': 'N/A',
    'time_zone': 'UTC'
}

def parse_user_agent(ua_string):
    user_agent = parse(ua_string)
    agent = {
        'browser': user_agent.browser,
        'os': user_agent.os.family
    }
    return agent

class TrafficSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    user_agent = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Traffic
        fields = ('id', 'user', 'location', 'user_agent')

    def get_location(self, obj):
        try:
            loc = g.city(obj.ip)
        except Exception:
            loc = default_location
        loc['flag'] = 'flag-icon flag-icon-'+ loc['country_code'] +' h4 mb-0'
        return loc

    def get_user_agent(self, obj):
        return parse_user_agent(obj.user_agent)

    def get_user(self, obj):
        try:
            user= {
                'name': obj.user.first_name + obj.user.last_name,
                'email': obj.user.email,
                'username': obj.user.username
            }
        except:
            user = {
                'name': 'Annonimous',
                'email': 'annonimous@email.co',
                'username': 'annonimous'
            }
        return user
