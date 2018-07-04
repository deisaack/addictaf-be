from django.contrib import admin

from .models import GagLink, HashTag, Post, TagBlacklist, Username


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', "image_hd", 'is_video', 'gag_id', 'created']
    ordering = ['created']
admin.site.register(GagLink)
admin.site.register(Username)
admin.site.register(HashTag)
admin.site.register(TagBlacklist)
admin.site.register(Post, PostAdmin)
