from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from utils.decorators import required_params

# Avoid using ModelViewSet, ModelViewSet allows all actions: Create, Read, Update, Delete
# Use other viewset to limit user action
# No need for CreateModelMixin and ListModelMixin, we need to implement them ourselves
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    # queryset: used by self.get_object(), as Tweet.objects.all().get(id=?)
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializerForCreate

    # Pre-defined functions
    # POST /api/tweets/ -> create()
    # GET /api/tweets/ -> list()
    # GET /api/tweets/1/ -> retrieve()
    # DELETE /api/tweets/1/ -> destroy()
    # PATCH /api/tweets/1/ -> partial_update()
    # PUT /api/tweets/1/ -> update()

    def get_permissions(self):
        # self.action is 'list' or 'create' functions below that has request
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        # <HOMEWORK 1> Use query argument with_all_comments to decide whether include comments
        # <HOMEWORK 2> Use query argument with_preview_comments to decide whether include first 3 comments
        tweet = self.get_object()
        return Response(TweetSerializerWithComments(tweet).data)

    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        Overwrite list function, only list tweets that matches user_id
        """

        # Below part is moved to required_params using decorator
        # if 'user_id' not in request.query_params:
        #     return Response('Missing user_id', status=400)

        # Below statement will be translated to
        # select * from twitter_tweets
        # where user_id = xxx
        # order by created_at desc
        # This is a composite index of user and created_at
        tweets = Tweet.objects.filter(
            user_id=request.query_params['user_id']
        ).order_by('-created_at')

        # many=True returns list of dict, each dict is one TweetSerializer
        serializer = TweetSerializer(tweets, many=True)

        # Response is using hash by default
        return Response({'tweets': serializer.data})

    def create(self, request, *args, **kwargs):
        """
        Overwrite create function, use current user as tweet.user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            # Pass other request info as well, for example user
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)