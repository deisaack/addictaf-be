from django.contrib import admin

from .models import Traffic


class TraficAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'path', 'created' )

admin.site.register(Traffic, TraficAdmin)
