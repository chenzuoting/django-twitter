from django.contrib.auth.models import User
from django.test import TestCase
from tweets.models import Tweet
from datetime import timedelta
from utils.time_helpers import utc_now


class TweetTests(TestCase):

    def test_hours_to_now(self):
        test_user = User.objects.create_user(username='test_user')
        test_tweet = Tweet.objects.create(user=test_user, content='Test tweet content')
        test_tweet.created_at = utc_now() - timedelta(hours=26)
        test_tweet.save()
        self.assertEqual(test_tweet.hours_to_now, 26)