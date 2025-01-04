from comments.models import Comment
from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from tweets.models import Tweet
from rest_framework.test import APIClient


class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        # Wrong: this will create an anonymous_client every time it's called
        # return APIClient()
        if hasattr(self, '_anonymous_client'):
            return self._anonymous_client
        self._anonymous_client = APIClient()
        return self._anonymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # Cannot do User.objects.create() because password needs encrypted
        # And username and email need some normalize process
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'Default tweet testing content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'Default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)