from django.contrib import admin
from .models import FileItem, Document


admin.site.register(Document)
admin.site.register(FileItem)

