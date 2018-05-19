from django.urls import path

from . import views

app_name = 'files'
urlpatterns = [
    path('policy/', views.FilePolicyAPI.as_view(), name='upload_policy'),
    path('complete-upload/', views.FileUploadCompleteHandler.as_view(), name='complete_upload')
]
