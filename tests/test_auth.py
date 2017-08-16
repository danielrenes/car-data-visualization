import json
import time

from data_visualization.models import User

from tests import BaseTest

class AuthTest(BaseTest):
    def test_verify_password(self):
        # create user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])

        # get user with API
        rv = self.client.get('/user', headers=self.get_headers(user['username'], user['password']))

        # verify response code is 200
        self.assertEqual(rv.status_code, 200)

    def test_get_token(self):
        # create user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])

        # get token
        rv = self.client.get('/token', headers=self.get_headers(user['username'], user['password']))
        token = json.loads(rv.get_data())['token']

        # get user with API, then wait for 1 second
        for request_counter in xrange(19):
            rv = self.client.get('/user', headers=self.get_headers(token=token))
            self.assertEqual(rv.status_code, 200)
            time.sleep(1)

        # verify the token expires after 20 seconds when testing
        rv = self.client.get('/token', headers=self.get_headers(token=token))
        self.assertEqual(rv.status_code, 403)
