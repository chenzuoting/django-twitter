from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from tweets.models import Tweet


class TestCase(DjangoTestCase):

    def create_user(self, username, email, password=None):
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