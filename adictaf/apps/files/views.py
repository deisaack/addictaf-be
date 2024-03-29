import base64
import hashlib
import hmac
import os
import time
from datetime import timedelta, timezone

from django.conf import settings
from django.views.generic.edit import CreateView
from rest_framework import authentication, permissions, status
from rest_framework.decorators import (api_view, parser_classes,
                                       permission_classes)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document, FileItem


@api_view(['POST'])
@parser_classes((MultiPartParser, FormParser))
@permission_classes((AllowAny,))
def upload_document(request):
    try: file = request.FILES["file"]
    except: return Response({'error': 'No file selected'}, status=status.HTTP_400_BAD_REQUEST)
    # filename = str(file.name)
    # save_path = os.path.join(os.path.join(settings.MEDIA_ROOT), filename)
    # fs = FileSystemStorage()
    # itemname = fs.save(filename, file)
    # uploaded_file_url = fs.url(filename)
    savedfile =Document.objects.create(
            upload=file
        )
    # savedfile.file = file
    # savedfile.save()
    return Response({'success': 'File uploaded'}, status=201)

class DocumentCreateView(CreateView):
    model = Document
    fields = ['upload', ]
    success_url = '/'
    template_name = 'sample.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = Document.objects.all()
        context['documents'] = documents
        return context


class FilePolicyAPI(APIView):
    """
    This view is to get the AWS Upload Policy for our s3 bucket.
    What we do here is first create a FileItem object instance in our
    Django backend. This is to include the FileItem instance in the path
    we will use within our bucket as you'll see below.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        The initial post request includes the filename
        and auth credientails. In our case, we'll use
        Rest Authentication but any auth should work.
        """
        filename_req = request.data.get('filename')
        if not filename_req:
                return Response({"error": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)
        policy_expires = int(time.time()+5000)
        user = request.user
        username_str = str(request.user.username)
        """
        Below we create the Django object. We'll use this
        in our upload path to AWS. 

        Example:
        To-be-uploaded file's name: Some Random File.mp4
        Eventual Path on S3: <bucket>/username/2312/2312.mp4
        """
        file_obj = FileItem.objects.create(
            user=user, name=filename_req)
        file_obj_id = file_obj.id
        upload_start_path = "{username}/{file_obj_id!s}/".format(
                    username=username_str,
                    file_obj_id=file_obj_id
            )       
        _, file_extension = os.path.splitext(filename_req)
        filename_final = "{file_obj_id}{file_extension}".format(
                    file_obj_id=file_obj_id,
                    file_extension=file_extension

                )
        """
        Eventual file_upload_path includes the renamed file to the 
        Django-stored FileItem instance ID. Renaming the file is 
        done to prevent issues with user generated formatted names.
        """
        final_upload_path = "{upload_start_path}{filename_final}".format(
                                 upload_start_path=upload_start_path,
                                 filename_final=filename_final,
                            )
        if filename_req and file_extension:
            """
            Save the eventual path to the Django-stored FileItem instance
            """
            file_obj.path = final_upload_path
            file_obj.save()

        policy_document_context = {
            "expire": policy_expires,
            "bucket_name": settings.AWS_UPLOAD_BUCKET,
            "key_name": "",
            "acl_name": "private",
            "content_name": "",
            "content_length": 524288000,
            "upload_start_path": upload_start_path,

            }
        policy_document = """
        {"expiration": "2019-01-01T00:00:00Z",
          "conditions": [ 
            {"bucket": "%(bucket_name)s"}, 
            ["starts-with", "$key", "%(upload_start_path)s"],
            {"acl": "%(acl_name)s"},

            ["starts-with", "$Content-Type", "%(content_name)s"],
            ["starts-with", "$filename", ""],
            ["content-length-range", 0, %(content_length)d]
          ]
        }
        """ % policy_document_context
        aws_secret = str.encode(settings.AWS_SECRET_ACCESS_KEY)
        policy_document_str_encoded = str.encode(policy_document.replace(" ", ""))
        url = 'https://{bucket}.s3-{region}.amazonaws.com/'.format(
                        bucket=settings.AWS_UPLOAD_BUCKET,
                        region=settings.AWS_UPLOAD_REGION
                        )
        policy = base64.b64encode(policy_document_str_encoded)
        signature = base64.b64encode(hmac.new(aws_secret, policy, hashlib.sha1).digest())
        data = {
            "policy": policy,
            "signature": signature,
            "key": settings.AWS_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_id": file_obj_id,
            "filename": filename_final,
            "url": url,
            "username": username_str,
        }
        return Response(data, status=status.HTTP_200_OK)


class FileUploadCompleteHandler(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
     file_id = request.POST.get('file')
     size = request.POST.get('fileSize')
     course_obj = None
     data = {}
     type_ = request.POST.get('fileType')
     if file_id:
         obj = FileItem.objects.get(id=int(file_id))
         obj.size = int(size)
         obj.uploaded = True
         obj.type = type_
         obj.save()
         data['id'] = obj.id
         data['saved'] = True
     return Response(data, status=status.HTTP_200_OK)
