from accounts.api.serializers import UserSerializerForTweet
from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer
from comments.api.serializers import CommentSerializer
from likes.api.serializers import LikeSerializer
from likes.services import LikeService


class TweetSerializer(serializers.ModelSerializer):
    # Need to declare user serializer here to show full user info, otherwise return an int type id
    # Other fields is taken care of by ModelSerializer
    user = UserSerializerForTweet()
    # Self defined method, implemented by get_<name>
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        # comment_set is defined by django, because there is tweet foreign key in comment
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        # self.context['request'].user: get current user
        return LikeService.has_liked(self.context['request'].user, obj)


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet

class TweetSerializerForDetail(TweetSerializer):
    user = UserSerializer()
    # <HOMEWORK> use serialziers.SerializerMethodField to implement comments
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'comments',
            'created_at',
            'content',
            'likes',
            'comments',
            'likes_count',
            'comments_count',
            'has_liked',
        )
