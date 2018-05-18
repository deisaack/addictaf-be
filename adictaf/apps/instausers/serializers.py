from rest_framework import serializers

from .models import InstaUser


class InstaUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstaUser
        fields = ('id', 'username', 'follower_count', 'following_count',
                  'full_name', 'biography', 'thumbnail', 'profile_pic', 'posts',
                  'usertags_count', 'created'
                  )
        read_only_fields = ('id', 'username',)
