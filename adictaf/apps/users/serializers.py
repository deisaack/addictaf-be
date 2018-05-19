from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

User = get_user_model()

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'token',
                  'last_name')
        read_only_fields = ('id', 'token')

    def get_token(self, obj):
        return None


class SignupSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'password',
            'last_name'
          )


class UserLoginSerializer(UserSerializer):
    def get_token(self, obj):
        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token
