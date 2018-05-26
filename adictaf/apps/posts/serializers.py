from rest_framework import serializers
from adictaf.apps.activities.models import Activity
from .models import Post
# import re


class PostSerializer(serializers.ModelSerializer):
    up_votes = serializers.SerializerMethodField()
    down_votes = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['image_hd', 'image_sm', 'created', 'views', 'video_hd', 'video_sm', 'id', 'up_votes', 'down_votes', 'caption', 'is_video', 'status', 'tags']
        read_only_fields = (
            'id', 'image_url',
        )

    def get_up_votes(self, obj):
        return obj.activities.filter(activity_type=Activity.UP_VOTE).count()

    def get_down_votes(self, obj):
        return obj.activities.filter(activity_type=Activity.DOWN_VOTE).count()
