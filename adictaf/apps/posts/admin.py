from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'shortcode', 'comments', 'likes', 'is_video']

admin.site.register(Post, PostAdmin)
