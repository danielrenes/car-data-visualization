import json

from data_visualization.queries import create_chartconfigs

from tests import BaseTest
from data_visualization.models import User

class FormsTest(BaseTest):
    def test_user_form(self):
        import re
        from data_visualization import mail

        user = {
            'username': 'virtuser0',
            'email': 'virtuser0@localhost.loc',
            'password': 'virtpass',
            'repeat_password': 'virtpass'
        }

        with mail.record_messages() as outbox:
            # add a user with form
            rv = self.client.post(path='/forms/users/add', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 302)

            # check if confirmation email was sent
            self.assertEqual(len(outbox), 1)
            self.assertEqual(len(outbox[0].recipients), 1)
            self.assertEqual(outbox[0].recipients[0], user['email'])
            self.assertEqual(outbox[0].subject, 'Confirm Your Account')

            # check if public endpoint is availbale without email confirmation
            rv = self.client.get(path='/forms/login', follow_redirects=True)
            self.assertEqual(rv.status_code, 200)

            # confirm email
            link = '/'.join(re.findall(pattern='<a href="(.*?)">', string=outbox[0].html)[0].split('/')[-2:])
            self.client.get(path=link, headers=self.get_headers())
            with self.client.session_transaction() as session:
                self.assertTrue(session.get('_flashes', None) and ('success', 'You have successfully activated your account.') in session['_flashes'])
            rv = self.client.get(path='/{0}'.format(user['username']), headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)

            # logout
            self.client.get(path='/logout', headers=self.get_headers())

            # check if non-public endpoints are unavailable when logged out
            self.client.get(path='/forms/sensors/add', headers=self.get_headers(), follow_redirects=True)
            with self.client.session_transaction() as session:
                self.assertTrue(session.get('_flashes', None) and session['_flashes'][-1] == ('error', 'Unauthorized'))

            # login
            login_data = {
                'username': user['username'],
                'password': user['password']
            }
            self.client.post(path='/forms/login', data=json.dumps(login_data), headers=self.get_headers())

            # check if non-public endpoints are available after login
            rv = self.client.get(path='/forms/sensors/add', headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)

            # edit user with form
            user['username'] = 'virtuser1'
            rv = self.client.post(path='/forms/users/edit', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 302)
            rv = self.client.get(path='/user', headers=self.get_headers(user['username'], user['password']))
            data = json.loads(rv.get_data())
            self.assertTrue('email' not in data.iterkeys())
            self.assertTrue('password' not in data.iterkeys())
            for key, value in data.iteritems():
                if key != 'id' and key != 'links':
                    self.assertEqual(user[key], data[key])

            # invalid 'username' length on form
            user['username'] = 'qwertyu'
            rv = self.client.post(path='/forms/users/edit', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)
            user['username'] = 'qwertyuiopasdfghjklzxqwertyuiopas'
            rv = self.client.post(path='/forms/users/edit', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)

            # invalid 'email' on form
            user['email'] = 'qwerty@qwerty'
            rv = self.client.post(path='/forms/users/edit', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)

            # invalid 'repeat_password' on form
            user['password'] = 'qwerty'
            user['repeat_password'] = 'asdfg'
            rv = self.client.post(path='/forms/users/edit', data=json.dumps(user), headers=self.get_headers())
            self.assertEqual(rv.status_code, 200)

            # create another user
            user2 = {
                'username': 'virtuser2',
                'email': 'virtuser2@localhost.loc',
                'password': 'virtpassword2',
                'repeat_password': 'virtpassword2'
            }
            self.client.post(path='/forms/users/add', data=json.dumps(user2), headers=self.get_headers())

            # logout
            self.client.post(path='/logout', headers=self.get_headers())

            # try to login without email confirmation
            login_data = {
                'username': user2['username'],
                'password': user2['password']
            }

            self.client.post(path='/forms/login', data=json.dumps(login_data), headers=self.get_headers())
            with self.client.session_transaction() as session:
                self.assertTrue(session.get('_flashes', None) and session['_flashes'][-1] == ('warning', 'Please activate your account!'))

    def test_category_form(self):
        # add a user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])
        self.client.post(path='/forms/login', data=json.dumps({'username': user['username'], 'password': user['password']}), headers=self.get_headers())

        # add a category with form
        category = {
            'name': 'virtcateg',
            'min_value': 10,
            'max_value': 40,
            'user_id': 1
        }
        rv = self.client.post(path='/forms/categories/add/{0}'.format(category['user_id']), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # edit category with form
        category['min_value'] = 30
        category['max_value'] = 70
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # invalid 'name' length on form
        category['name'] = 'asd'
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        category['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['name'] = 'categ'

        # without 'min_value' on form
        category['min_value'] = ''
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['min_value'] = 10

        # without 'max_value' on form
        category['max_value'] = ''
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['max_value'] = 20

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/categories/edit/1', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

    def test_sensor_form(self):
        # add a user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])
        self.client.post(path='/forms/login', data=json.dumps({'username': user['username'], 'password': user['password']}), headers=self.get_headers())

        # add category
        category = self.get_categories()[0]
        rv = self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # add a sensor with form
        sensor = {
            'name': 'virtsen',
            'category_name': category['name'],
            'location': 'London',
            'ipv4_addr': '192.168.0.2'
        }
        rv = self.client.post(path='/forms/sensors/add', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # edit category with form
        sensor['location'] = 'Paris'
        sensor['ipv4_addr'] = '192.168.0.1'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # invalid 'name' length on form
        sensor['name'] = 'asd'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        sensor['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['name'] = 'sens'

        # invalid 'location' length on form
        sensor['location'] = 'as'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        sensor['location'] = 'qwertyuiopasdfghjklzxqwertyuiopasdfghjklz'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['location'] = 'location'

        # invalid 'ipv4_addr' on form
        sensor['ipv4_addr'] = '192.168.1'
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['ipv4_addr'] = '192.168.0.1'

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/sensors/edit/1', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

    def test_subview_form(self):
        # add a user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])
        self.client.post(path='/forms/login', data=json.dumps({'username': user['username'], 'password': user['password']}), headers=self.get_headers())

        # add categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers(user['username'], user['password']))

        # add sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers(user['username'], user['password']))

        # add views
        views = self.get_views()
        for view in views:
            self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers(user['username'], user['password']))

        # create chartconfigs
        create_chartconfigs()
        rv = self.client.get(path='/chartconfigs', headers=self.get_headers(user['username'], user['password']))
        chartconfig_types = [chartconf['type'] for chartconf in json.loads(rv.get_data())['chartconfigs']]

        # sensor_names for user
        sensor_names = []
        rv = self.client.get(path='/user', headers=self.get_headers(user['username'], user['password']))
        category_links = json.loads(rv.get_data())['links']['categories']
        for category_link in category_links:
            rv = self.client.get(path=category_link, headers=self.get_headers(user['username'], user['password']))
            sensor_links = json.loads(rv.get_data())['links']['sensors']
            for sensor_link in sensor_links:
                rv = self.client.get(path=sensor_link, headers=self.get_headers(user['username'], user['password']))
                sensor_names.append(json.loads(rv.get_data())['name'])

        # get selection for sensor names and chartconfig types from subview form
        rv = self.client.get(path='/forms/subviews/add/1', headers=self.get_headers())
        data = rv.get_data()

        import re
        matches = re.findall('">(.*?)</option>', data)

        self.assertTrue('sensor' in matches[0])
        for i in xrange(len(sensor_names)):
            self.assertEqual(matches[i+1], sensor_names[i])
        self.assertTrue('chart' in matches[i+2])
        for j in xrange(len(chartconfig_types)):
            self.assertEqual(matches[i+j+3], chartconfig_types[j])

    def test_view_form(self):
        # add a user
        user = self.get_users()[0]
        User.generate_fake_user(user['username'], user['email'], user['password'])
        self.client.post(path='/forms/login', data=json.dumps({'username': user['username'], 'password': user['password']}), headers=self.get_headers())

        view = {
            'name': 'view1',
            'count': 1,
            'refresh_time': 10
        }

        # add a view with form
        rv = self.client.post(path='/forms/views/add', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # edit view with form
        view['count'] = 2
        view['refresh_time'] = 20
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

        # invalid 'name' length on form
        view['name'] = 'asd'
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['name'] = 'view'

        # invalid 'count' on form
        view['count'] = 3
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['count'] = 5
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['count'] = 2

        # invalid 'refresh_time' on form
        view['refresh_time'] = 9
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['refresh_time'] = 61
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['refresh_time'] = 22

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/views/edit/1', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
