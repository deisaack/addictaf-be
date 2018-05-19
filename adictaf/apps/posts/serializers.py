from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
        fields_to = [
            'id', 'comments', 'likes', 'timestamp', 'owner_id',
            'caption', 'image_url', 'video_url', 'is_video', 'status']
