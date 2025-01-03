from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetCreateSerializer
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService

# Avoid using ModelViewSet, use other viewset to limit user action
# No need for CreateModelMixin and ListModelMixin, we need to implement them ourselves
class TweetViewSet(viewsets.GenericViewSet,
                   viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.ListModelMixin):
    """
    API endpoint that allows users to create, list tweets
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetCreateSerializer

    def get_permissions(self):
        # self.action is 'list' or 'create' functions below that has request
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        Overwrite list function, only list tweets that matches user_id
        """
        if 'user_id' not in request.query_params:
            return Response('Missing user_id', status=400)

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
        serializer = TweetCreateSerializer(
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