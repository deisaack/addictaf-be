import logging

from django.db import transaction
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from adictaf.apps.core.models import Project
from adictaf.utilities.permissions import AdictAFAdminOrReadOnly
from noire.bot.base import NoireBot
from adictaf.apps.activities.models import Activity
from adictaf.utilities.common import request_ip
from . import serializers as sz
from .models import Post
from .tasks import load_user_posts
from django.db import transaction
from rest_framework.decorators import action, api_view, permission_classes
from django.db.models.expressions import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

logger = logging.getLogger(__name__)

class PostViewset(viewsets.ReadOnlyModelViewSet):
    serializer_class = sz.PostSerializer
    queryset = Post.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    ordering_fields = ['created']
    ordering = '-created'
    filter_fields = ['is_video']

    @action(methods=['put'], detail=True)
    def upvote(self, request, pk=None):
        post = self.get_object()
        user = request.user
        ip = request_ip(request)
        if user.is_anonymous:
            user = None
        vote = Activity.objects.filter(
            Q(posts__id=post.id),
            user=user,
            activity_type=Activity.UP_VOTE,
            ip=ip
        ).exists()
        if not vote:
            post.activities.create(
                user=user,
                content_object = post,
                activity_type = Activity.UP_VOTE,
                ip = ip
            )
        post.views+=1
        post.save()
        return Response(not vote, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def down_vote(self, request, pk=None):
        post = self.get_object()
        user = request.user
        ip = request_ip(request)
        if user.is_anonymous:
            user = None
        vote = Activity.objects.filter(
            Q(posts__id__iexact=pk),
            user=user,
            activity_type=Activity.DOWN_VOTE,
            ip=ip
        ).exists()

        if not vote:
            post.activities.create(
                content_object=post,
                user=user,
                activity_type = Activity.DOWN_VOTE,
                ip = ip
            )
        post.views += 1
        post.save()
        return Response(not vote, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        return Response(
            {"error": "Not Allowed"},
            status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self, *args, **kwargs):
        queryset_list = super(PostViewset, self).get_queryset(*args, **kwargs)
        tags = self.request.GET.get('tags', None)
        category = self.request.GET.get('category', None)
        if tags is not None:
            try:
                tags=tags.split(',')
                queryset_list = queryset_list.filter(tags__overlap=tags)
            except:
                pass
        if category == 'hot':
            queryset_list = queryset_list.order_by('-views')
        if category == 'trending':
            queryset_list = queryset_list.order_by('-up_votes')
        return queryset_list

    def retrieve(self, *args, **kwargs):
        obj = self.get_object()
        obj.views +=1
        obj.save()
        return super(PostViewset, self).retrieve(*args, **kwargs)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def retrieve(self, request, pk=None):
        queryset = Post.objects.all()
        post = get_object_or_404(queryset, pk=pk)
        serializer = sz.PostSerializer(post)
        # if serializer.is_valid():
        return Response(serializer.data)
        # return Response(serializer.errors)

    @transaction.atomic()
    def update(self, request, pk=None):
        try:
            post = Post.objects.select_for_update().get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "No such post"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
# @permission_classes([AdictAFAdminOrReadOnly])
@permission_classes([AllowAny])
def crawl_username(request):
    if not 'username' in request.data:
        return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
    count = request.GET.get('count', 100)
    forceLogin = request.GET.get('force', False)
    if forceLogin:
        forceLogin=True
    username=request.data['username']
    logger.info('Loading user posts for {0}'.format(username))
    proj = Project.objects.filter(active=True).last()
    try:
        bot = NoireBot(proj.username, proj.get_password, forceLogin=forceLogin)
    except AttributeError:
        logger.error("No active project in db")
        return
    usernameid = bot.convert_to_user_id(username)
    load_user_posts.delay(usernameid, int(count))
    return Response({"success": "data is being loaded"})

from collections import OrderedDict

@api_view(['GET'])
@permission_classes([AllowAny])
def all_tags(request):
    count= request.GET.get('count', 20)
    if count > 100:
        count=100
    list_all=[]
    for post in Post.objects.all():
        list_all.extend(post.tags)
    list_all=set(list_all)
    obj = {}
    for item in list_all:
        item=item.lower()
        if not item in obj:
            obj[item] = 1
            continue
        obj[item] += 1
    sorted_by_value = OrderedDict(sorted(obj.items(), key=lambda x: x[1]))
    resp_items=[]
    i=0
    for item in reversed(sorted_by_value):
        if i >= count:
            break
        resp_items.append(item)
        i+= 1
    return Response(resp_items)

