import json

from data_visualization.utils import create_chartconfigs
from data_visualization.models import User

from tests import BaseTest

class ApiTest(BaseTest):
    def test_user(self):
        # create users
        users = self.get_users()

        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])
            rv = self.client.get(path='/user', data=json.dumps(user), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 200)

        # create categories
        categories_for_user = {}
        categories = self.get_categories()
        for category in categories:
            categories_for_user[str(category['user_id'])] = []
        for category in categories:
            user = users[category['user_id'] - 1]
            rv = self.client.post('/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))
            categories_for_user[str(category['user_id'])].append(rv.headers['Location'])

        # check the created users
        for i in xrange(len(users)):
            user = users[i]
            rv = self.client.get(path='/user', headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            self.assertEqual(data['username'], user['username'])
            self.assertTrue('email' not in data)
            self.assertTrue('password' not in data)
            self.assertEqual(len(data['links']['categories']), len(categories_for_user[str(i+1)]))
            for j in xrange(len(categories_for_user[str(i+1)])):
                self.assertEqual('/'.join(data['links']['categories'][j].split('/')[-2:]), '/'.join(categories_for_user[str(i+1)][j].split('/')[-2:]))

        # modify users[0]
        username = users[0]['username']
        users[0]['username'] = 'nicholas'
        rv = self.client.put(path='/user', data=json.dumps(users[0]), headers=self.get_headers(username, users[0]['password']))
        data = json.loads(rv.get_data())
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data['username'], users[0]['username'])
        self.assertTrue('email' not in data)
        self.assertTrue('password' not in data)

        # delete users
        for i in xrange(len(users)):
            rv = self.client.delete(path='/user', headers=self.get_headers(users[i]['username'], users[i]['password']))
            self.assertEqual(rv.status_code, 204)

        # try to get users
        for i in xrange(len(users)):
            rv = self.client.get(path='/user', headers=self.get_headers(users[i]['username'], users[i]['password']))
            self.assertEqual(rv.status_code, 302)

    def test_categories(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        locations = []
        for category in categories:
            user = users[category['user_id'] - 1]
            rv = self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # try to add one of the categories once more
        user = users[categories[0]['user_id'] - 1]
        rv = self.client.post('/category', data=json.dumps(categories[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            user = users[categories[i]['user_id'] - 1]
            rv = self.client.get(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(json.loads(rv.get_data())['name'], categories[i]['name'])

        # create a sensor with foreign key to categories[0]
        user = users[categories[0]['user_id'] - 1]
        sensor = self.get_sensors()[0]
        rv = self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 201)
        sensor_location = rv.headers['Location']

        # get the sensors for categories[0]
        rv = self.client.get(path=locations[0], headers=self.get_headers(user['username'], user['password']))
        sensors_location = json.loads(rv.get_data())['links']['sensors']
        self.assertTrue(len(sensors_location), 1)
        self.assertEqual(sensors_location[0].split('/')[-2:], sensor_location.split('/')[-2:])
        rv = self.client.get(path=sensor_location, headers=self.get_headers(user['username'], user['password']))
        data = json.loads(rv.get_data())
        self.assertEqual(data['name'], sensor['name'])

        # modify categories[0]
        category_mod = {'name': 'humi'}
        rv = self.client.put(path=locations[0], data=json.dumps(category_mod), headers=self.get_headers(user['username'], user['password']))
        data = json.loads(rv.get_data())
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data['id'], int(locations[0].split('/')[-1]))
        self.assertEqual(data['name'], category_mod['name'])

        # delete categories
        username = user['username']
        password = user['password']
        for i in xrange(len(locations)):
            user = users[categories[i]['user_id'] - 1]
            rv = self.client.delete(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 204)

        # try to get sensor
        rv = self.client.get(path=sensor_location, headers=self.get_headers(username, password))
        self.assertEqual(rv.status_code, 400)

    def test_sensors(self):
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            user = users[category['user_id'] - 1]
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        locations = []
        category_locations = []

        for sensor in sensors:
            user = users[categories[sensor['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])
            category_locations.append(json.loads(rv.get_data())['links']['category'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            user = users[categories[sensors[i]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.get(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            for key in sensors[i].iterkeys():
                self.assertTrue(key in data.keys())
                self.assertEqual(data[key], sensors[i][key])

        # fetch sensors in every category
        for i in xrange(len(category_locations)):
            user = users[categories[i]['user_id'] - 1]
            rv = self.client.get(path=category_locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())['links']['sensors']
            self.assertEqual(len(data), 1)
            self.assertTrue(('/').join(data[0].split('/')[-2:]) in [('/').join(location.split('/')[-2:]) for location in locations])

        # create a data with foreign key to sensors[0]
        user = users[categories[sensors[0]['category_id'] - 1]['user_id'] - 1]
        data = self.get_datas()[0]
        rv = self.client.post(path='/data', data=json.dumps(data), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 201)
        data_location = rv.headers['Location']

        # modify sensors[0]
        username = user['username']
        password = user['password']
        sensors[0]['name'] = 'humi'
        sensors[0]['location'] = 'New York'
        rv = self.client.put(path=locations[0], data=json.dumps(sensors[0]), headers=self.get_headers(user['username'], user['password']))
        data = json.loads(rv.get_data())
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data['id'], int(locations[0].split('/')[-1]))
        self.assertEqual(data['name'], 'humi')
        self.assertEqual(data['location'], 'New York')
        self.assertEqual(data['ipv4_addr'], sensors[0]['ipv4_addr'])

        # delete sensors
        for i in xrange(len(locations)):
            user = users[categories[sensors[i]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.delete(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 204)

        # try to get data
        rv = self.client.get(path=data_location, headers=self.get_headers(username, password))
        self.assertEqual(rv.status_code, 400)

    def test_datas(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            user = users[category['user_id'] - 1]
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            user = users[categories[sensor['category_id'] - 1]['user_id'] - 1]
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create datas
        datas = self.get_datas()
        locations = []
        sensor_locations = []

        for data in datas:
            user = users[categories[sensors[data['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/data', data=json.dumps(data), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])
            sensor_locations.append(json.loads(rv.get_data())['links']['sensor'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            user = users[categories[sensors[datas[i]['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.get(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            for key in datas[i].iterkeys():
                self.assertTrue(key in data.keys())
                self.assertEqual(data[key], datas[i][key])

        # fetch datas for every sensor
        for i in xrange(len(sensor_locations)):
            user = users[categories[sensors[datas[i]['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.get(path=sensor_locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())['links']['datas']
            self.assertEqual(len(data), 1)
            self.assertTrue(('/').join(data[0].split('/')[-2:]) in [('/').join(location.split('/')[-2:]) for location in locations])

    def test_chartconfigs(self):
        # create a user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])

        # create chartconfigs
        create_chartconfigs()

        locations = []

        # fetch all chartconfigs
        rv = self.client.get('/chartconfigs', headers=self.get_headers(user['username'], user['password']))
        data = json.loads(rv.get_data())['chartconfigs']

        from data_visualization.chartjs import chart_types

        self.assertEqual(len(data), len(chart_types))
        for i in xrange(len(data)):
            self.assertTrue(data[i]['type'], chart_types[i])
            locations.append(data[i]['links']['self'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            self.assertEqual(data['type'], chart_types[i])

    def test_subviews(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            user = users[category['user_id'] - 1]
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            user = users[categories[sensor['category_id'] - 1]['user_id'] - 1]
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create chartconfigs
        create_chartconfigs()

        # create views
        views = self.get_views()
        for view in views:
            user = users[view['user_id'] - 1]
            self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))

        # create subviews
        subviews = self.get_subviews()
        locations = []

        for subview in subviews:
            user = users[categories[sensors[subview['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/subview', data=json.dumps(subview), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            user = users[categories[sensors[subviews[i]['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.get(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            self.assertEqual(data['sensor_id'], subviews[i]['sensor_id'])
            self.assertEqual(data['chartconfig_id'], subviews[i]['chartconfig_id'])

        # modify subviews[0]
        user = users[categories[sensors[subviews[0]['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
        subviews[0]['sensor_id'] = 2
        subviews[0]['chartconfig_id'] = 4
        rv = self.client.put(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.get_data())
        self.assertEqual(data['sensor_id'], 2)
        self.assertEqual(data['chartconfig_id'], 4)
        sensor_location = data['links']['sensor']
        chartconfig_location = data['links']['chartconfig']

        # remove subviews[0]
        rv = self.client.delete(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 204)
        rv = self.client.get(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # check if sensor and chartconfig are still there
        rv = self.client.get(path=sensor_location, headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get(path=chartconfig_location, headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 200)

    def test_views(self):
        # create users
        users = self.get_users()
        for user in users:
            User.generate_fake_user(user['username'], user['email'], user['password'])

        # create categories
        categories = self.get_categories()
        for category in categories:
            user = users[category['user_id'] - 1]
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            user = users[categories[sensor['category_id'] - 1]['user_id'] - 1]
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # create chartconfigs
        create_chartconfigs()

        # create views
        views = self.get_views()
        locations = []

        for view in views:
            user = users[view['user_id'] - 1]
            rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # try to create view with 'count' > 4
        user = users[0]
        view = {
            'name': 'invalidview',
            'count': 5,
            'refresh_time': 10,
            'user_id': 1,
            'type': 'normal'
        }
        rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # try to create view with 'count' not in [1, 2, 4]
        view['count'] = 3
        rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # create subviews
        subviews = self.get_subviews()
        subview_locations = []

        for subview in subviews:
            user = users[categories[sensors[subview['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.post(path='/subview', data=json.dumps(subview), headers=self.get_headers(user['username'], user['password']))
            subview_locations.append(rv.headers['Location'])

        # check the returned 'Location' links
        expected_icons = ['2x1', '1x1']

        for i in xrange(len(locations)):
            user = users[views[i]['user_id'] - 1]
            rv = self.client.get(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            self.assertEqual(data['count'], views[i]['count'])
            self.assertEqual(len(data['links']['subviews']), views[i]['count'])
            self.assertTrue(expected_icons[i] in data['links']['icon'])

        # modify views[0]
        user = users[views[0]['user_id'] - 1]
        views[0]['name'] = 'modifiedview'
        views[0]['count'] = 4
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.get_data())
        self.assertEqual(data['name'], 'modifiedview')
        self.assertEqual(data['count'], 4)
        self.assertTrue('2x2' in data['links']['icon'])

        # try to modify the 'count' in views[1]
        user = users[views[1]['user_id'] - 1]
        views[1]['count'] = 1
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        views[1]['count'] = 3
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        views[1]['count'] = 5
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # try to modify the 'refresh_time' in views[0]
        user = users[views[0]['user_id'] - 1]
        views[0]['refresh_time'] = 9
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        views[0]['refresh_time'] = 61
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers(user['username'], user['password']))
        self.assertEqual(rv.status_code, 400)

        # remove views
        for i in xrange(len(locations)):
            user = users[views[i]['user_id'] - 1]
            rv = self.client.delete(path=locations[i], headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 204)

        # check if subviews were removed
        for i in xrange(len(subview_locations)):
            user = users[categories[sensors[subviews[i]['sensor_id'] - 1]['category_id'] - 1]['user_id'] - 1]
            rv = self.client.get(path=subview_locations[i], headers=self.get_headers(user['username'], user['password']))
            self.assertEqual(rv.status_code, 400)
