from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    def setUp(self):
        # This function will call at the beginning of every test function
        # Below steps wrong effect real database, test database is used
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@twitter.com',
            password='correct password',
        )

    def test_login(self):
        # Every function need to start with test_* , so that it can be called for testing
        # Test need to use POST not GET
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # Error: Login failed，http status code return 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # Error: Used post, but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # Check not logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # Success: Use correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@twitter.com')

        # Check logged in successfully
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # Log in user
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # Check user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # Error: Check using GET, expect error
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # Success: Use POST and logged out successfully
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # Check user is logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@testing.com',
            'password': 'any password',
        }
        # Error: Check request failed on GET
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # Error: Check email is valid
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # Error: Check password is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@testing.com',
            'password': '123',
        })
        # print(response.content) print data before parse
        # print(response.data) print data after parse
        self.assertEqual(response.status_code, 400)

        # Error: Check password is too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@testing.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # Success: Signup successfully
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # Check user is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)