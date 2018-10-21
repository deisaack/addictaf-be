from rest_framework import serializers

from adictaf.apps.activities.models import Activity

from .models import Post

# import re



class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['image', 'category', 'id', 'caption', 'is_video',]
        read_only_fields = (
            'id',
        )


class PostSerializer(serializers.ModelSerializer):
    up_votes = serializers.SerializerMethodField()
    down_votes = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            'video', 'image', 'category', 'created', 'views', 'id', 'up_votes',
            'caption', 'is_video', 'status', 'tags', 'related', 'down_votes'
        ]
        read_only_fields = (
            'id',
        )

    def get_up_votes(self, obj):
        return obj.activities.filter(activity_type=Activity.UP_VOTE).count()

    def get_down_votes(self, obj):
        return obj.activities.filter(activity_type=Activity.DOWN_VOTE).count()

    def get_related(self, obj):
        queryset = obj.related_posts[:6]
        serializer = PostListSerializer(queryset, many=True)
        return serializer.data
