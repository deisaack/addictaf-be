from django.urls import path

from . import views

app_name = 'files'
urlpatterns = [
    path('policy/', views.FilePolicyAPI.as_view(), name='upload_policy'),
    path('doc/', views.DocumentCreateView.as_view(), name='doc-create'),
    path('complete-upload/', views.FileUploadCompleteHandler.as_view(), name='complete_upload'),
    path('upload-document/', views.upload_document, name='upload-document')
]
