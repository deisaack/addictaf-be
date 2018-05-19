import random

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import serializers as sz
from .models import Advert, Project


class AdvertViewset(viewsets.ModelViewSet):
    serializer_class = sz.AdvertSerializer
    queryset = Advert.objects.all()


@api_view(['GET'])
def get_advert(request):
    adds = Advert.objects.all()
    index = random.randint(0, len(adds)-1)
    obj = adds[index]
    serializer = sz.AdvertSerializer(obj)
    return Response(serializer.data)
