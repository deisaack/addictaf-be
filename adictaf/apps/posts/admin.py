from django.contrib import admin

from .models import Post, TagBlacklist, Username, HashTag


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', "image_hd", 'is_video']

admin.site.register(Username)
admin.site.register(HashTag)
admin.site.register(TagBlacklist)
admin.site.register(Post, PostAdmin)
