import json

from tests import BaseTest
from data_visualization.models import User

class MainTest(BaseTest):
    def test_index(self):
        # index page is visible to users who are not logged in
        rv = self.client.get('/', headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        # generate user
        fake_user = {
            'username': 'Fake User',
            'email': 'fakeuser@localhost.loc',
            'password': 'fakepassword'
        }

        User.generate_fake_user(fake_user['username'], fake_user['email'], fake_user['password'])

        # login
        login_data = {
            'username': fake_user['username'],
            'password': fake_user['password']
        }
        self.client.post(path='/forms/login', data=json.dumps(login_data), headers=self.get_headers())

        # index page redirects to userpage
        rv = self.client.get('/', headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # logout
        self.client.get(path='/logout', headers=self.get_headers())

        # index page is visible again after logout
        rv = self.client.get('/', headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

    def test_userpage(self):
        # generate two fake users
        fake_user_1 = {
            'username': 'Fake User 1',
            'email': 'fakeuser1@localhost.loc',
            'password': 'fakepassword1'
        }

        fake_user_2 = {
            'username': 'Fake User 2',
            'email': 'fakeuser2@localhost.loc',
            'password': 'fakepassword2'
        }

        User.generate_fake_user(fake_user_1['username'], fake_user_1['email'], fake_user_1['password'])
        User.generate_fake_user(fake_user_2['username'], fake_user_2['email'], fake_user_2['password'])

        # try to access userpage without being logged in
        rv = self.client.get('/FakeUser1', headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # login FakeUser1
        login_data = {
            'username': fake_user_1['username'],
            'password': fake_user_1['password']
        }
        self.client.post(path='/forms/login', data=json.dumps(login_data), headers=self.get_headers())

        # try to access userpage after login
        rv = self.client.get('/Fake.User.1', headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        # try to access non-exisiting userpage
        rv = self.client.get('/nonexisting', headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # try to access FakeUser2's userpage
        rv = self.client.get('/Fake.User.2', headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
