import json

from data_visualization.utils import create_chartconfigs
from data_visualization.models import User

from tests import BaseTest

class QueryTest(BaseTest):
    def test_category_query(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        user_categories = {}
        categories = self.get_categories()
        for category in categories:
            user = users[category['user_id'] - 1]
            rv = self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))
            location = rv.headers['Location']
            if user['username'] not in user_categories.iterkeys():
                user_categories[user['username']] = []
            user_categories[user['username']].append(location)

        # get own categories
        for user in users:
            for category_location in user_categories[user['username']]:
                rv = self.client.get(path=category_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 200)

        # try to get other users' categories
        for user in users:
            other_users_categories = []
            for other_user in users:
                if user == other_user:
                    continue
                other_users_categories.extend(user_categories[other_user['username']])
            for category_location in other_users_categories:
                rv = self.client.get(path=category_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 400)

    def test_sensor_query(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        user_sensors = {}
        sensors = self.get_sensors()
        for sensor in sensors:
            user = users[categories[sensor['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))
            location = rv.headers['Location']
            if user['username'] not in user_sensors.iterkeys():
                user_sensors[user['username']] = []
            user_sensors[user['username']].append(location)

        # get own sensors
        for user in users:
            for sensor_location in user_sensors[user['username']]:
                rv = self.client.get(path=sensor_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 200)

        # try to get other users' sensors
        for user in users:
            other_users_sensors = []
            for other_user in users:
                if user == other_user:
                    continue
                other_users_sensors.extend(user_sensors[other_user['username']])
            for sensor_location in other_users_sensors:
                rv = self.client.get(path=sensor_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 400)

    def test_data_query(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create datas
        user_datas = {}
        datas = self.get_datas()
        for data in datas:
            user = users[categories[sensors[data['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/data', data=json.dumps(data), headers=self.get_headers(user['username'], user['password']))
            location = rv.headers['Location']
            if user['username'] not in user_datas.iterkeys():
                user_datas[user['username']] = []
            user_datas[user['username']].append(location)

        # get own datas
        for user in users:
            for data_location in user_datas[user['username']]:
                rv = self.client.get(path=data_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 200)

        # try to get other users' datas
        for user in users:
            other_users_datas = []
            for other_user in users:
                if user == other_user:
                    continue
                other_users_datas.extend(user_datas[other_user['username']])
            for data_location in other_users_datas:
                rv = self.client.get(path=data_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 400)

    def test_subview_query(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create views
        views = self.get_views()
        for view in views:
            self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))

        # create chartconfigs
        create_chartconfigs()

        # create subviews
        user_subviews = {}
        subviews = self.get_subviews()
        for subview in subviews:
            user = users[categories[sensors[subview['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/subview', data=json.dumps(subview), headers=self.get_headers(user['username'], user['password']))
            location = rv.headers['Location']
            if user['username'] not in user_subviews.iterkeys():
                user_subviews[user['username']] = []
            user_subviews[user['username']].append(location)

        # get own subviews
        for user in users:
            for subview_location in user_subviews[user['username']]:
                rv = self.client.get(path=subview_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 200)

        # try to get other users' subviews
        for user in users:
            other_users_subviews = []
            for other_user in users:
                if user == other_user:
                    continue
                other_users_subviews.extend(user_subviews[other_user['username']])
            for subview_location in other_users_subviews:
                rv = self.client.get(path=subview_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 400)

    def test_view_query(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create views
        user_views = {}
        views = self.get_views()
        for view in views:
            user = users[view['user_id'] - 1]
            rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))
            location = rv.headers['Location']
            if user['username'] not in user_views.iterkeys():
                user_views[user['username']] = []
            user_views[user['username']].append(location)

        # get own views
        for user in users:
            for view_location in user_views[user['username']]:
                rv = self.client.get(path=view_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 200)

        # try to get other users' views
        for user in users:
            other_users_views = []
            for other_user in users:
                if user == other_user:
                    continue
                other_users_views.extend(user_views[other_user['username']])
            for view_location in other_users_views:
                rv = self.client.get(path=view_location, headers=self.get_headers(user['username'], user['password']))
                self.assertEqual(rv.status_code, 400)
