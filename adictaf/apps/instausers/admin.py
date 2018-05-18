from django.contrib import admin

from .models import InstaUser, Username


class InstaUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'posts', 'follower_count', 'estimate_count']
    list_display_links = ['id', 'username']
    ordering = ['estimate_count', 'status', 'following_count']
    list_filter = ['estimate_location']

class UsernameAdmin(admin.ModelAdmin):
    list_display = ['name',]


admin.site.register(InstaUser, InstaUserAdmin)
admin.site.register(Username, UsernameAdmin)
