from . import serializers as sz
from rest_framework import viewsets
from .models import Advert, Project
import random
from rest_framework.response import Response
from rest_framework.decorators import api_view


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
