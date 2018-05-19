from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import (api_view, parser_classes,
                                       permission_classes)
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers as sz

User = get_user_model()


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = sz.UserSerializer


@api_view(['POST'])
@permission_classes((AllowAny,))
@parser_classes((JSONParser, ))
def login(request):
    serializer = sz.LoginSerializer(
        data=request.data, context={'request': request}
    )
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(User, username=serializer.validated_data['username'])
    if not user.check_password(serializer.validated_data['password']):
        return Response({'error': 'Incorrect username or password'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = sz.UserLoginSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((AllowAny,))
@parser_classes((JSONParser, ))
def create_user(request):
    serializer = sz.SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    user = serializer.save()
    user.set_password(serializer.data['password'])
    user.save()
    return Response({'success': "user created", "user_id": user.id}, status=201)
