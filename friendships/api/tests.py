from http.client import responses

from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase

FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@twitter.com')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@twitter.com')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)

        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.user1.id)

        # Error: Need logged in to follow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Error: Use GET
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 405)
        # Error: Cannot follow myself
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)
        # Success:
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('created_at' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(response.data['user']['username'], self.user1.username)
        # Success: duplicated follow
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicated'], True)
        # Check there is a new item when user1 follow user2
        count = Friendship.objects.count()
        response = self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.user1.id)

        # Error: Need logged in to follow
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # Error: Use GET
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 405)
        # Error: Cannot unfollow myself
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)
        # Success:
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)
        # Duplicated unfollow
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)

        # Error: Use POST
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # Success: Use Get
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followings']), 3)
        # Check list ordering
        ts0 = response.data['followings'][0]['created_at']
        ts1 = response.data['followings'][1]['created_at']
        ts2 = response.data['followings'][2]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'user2_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'user2_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'user2_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)

        # Error: Use POST
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)
        # Success: Use Get
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['followers']), 2)
        # Check list ordering
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'user2_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'user2_follower0',
        )



