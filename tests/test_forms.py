import json

from data_visualization.queries import create_chartconfigs

from tests import BaseTest

class FormsTest(BaseTest):
    def test_category_form(self):
        # add a category with form
        category = {
            'name': 'virtcateg',
            'min_value': 10,
            'max_value': 40
        }
        rv = self.client.post(path='/forms/categories/add', data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/categories', headers=self.get_headers())
        data = json.loads(rv.get_data())['categories']
        self.assertEqual(len(data), 1)
        data = data[0]
        for key, value in data.iteritems():
            if key == 'id':
                category_id = value
            elif key != 'links':
                self.assertEqual(value, category[key])
        self.assertTrue(category_id is not None)

        # edit category with form
        category['min_value'] = 30
        category['max_value'] = 70
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/categories', headers=self.get_headers())
        data = json.loads(rv.get_data())['categories'][0]
        self.assertEqual(data['min_value'], 30)
        self.assertEqual(data['max_value'], 70)

        # invalid 'name' length on form
        category['name'] = 'asd'
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        category['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['name'] = 'categ'

        # without 'min_value' on form
        category['min_value'] = ''
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['min_value'] = 10

        # without 'max_value' on form
        category['max_value'] = ''
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        category['max_value'] = 20

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/categories/edit/{0}'.format(category_id), data=json.dumps(category), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

    def test_sensor_form(self):
        # add category
        category = self.get_categories()[0]
        rv = self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # add a sensor with form
        sensor = {
            'name': 'virtsen',
            'category_name': category['name'],
            'location': 'London',
            'ipv4_addr': '192.168.0.2'
        }
        rv = self.client.post(path='/forms/sensors/add', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/sensors', headers=self.get_headers())
        data = json.loads(rv.get_data())['sensors']
        self.assertEqual(len(data), 1)
        data = data[0]
        for key, value in data.iteritems():
            if key == 'id':
                sensor_id = value
            elif key != 'links' and key != 'category_id':
                self.assertEqual(value, sensor[key])
        self.assertTrue(sensor_id is not None)

        # edit category with form
        sensor['location'] = 'Paris'
        sensor['ipv4_addr'] = '192.168.0.1'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/sensors', headers=self.get_headers())
        data = json.loads(rv.get_data())['sensors'][0]
        self.assertEqual(data['location'], 'Paris')
        self.assertEqual(data['ipv4_addr'], '192.168.0.1')

        # invalid 'name' length on form
        sensor['name'] = 'asd'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        sensor['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['name'] = 'sens'

        # invalid 'location' length on form
        sensor['location'] = 'as'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        sensor['location'] = 'qwertyuiopasdfghjklzxqwertyuiopasdfghjklz'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['location'] = 'location'

        # invalid 'ipv4_addr' on form
        sensor['ipv4_addr'] = '192.168.1'
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        sensor['ipv4_addr'] = '192.168.0.1'

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/sensors/edit/{0}'.format(sensor_id), data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)

    def test_subview_form(self):
        # add categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # add sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())
        rv = self.client.get(path='sensors', headers=self.get_headers())
        sensor_names = [sen['name'] for sen in json.loads(rv.get_data())['sensors']]

        # add views
        views = self.get_views()
        for view in views:
            self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers())
        rv = self.client.get(path='views', headers=self.get_headers())
        view_ids = [vie['id'] for vie in json.loads(rv.get_data())['views']]

        # create chartconfigs
        create_chartconfigs()
        rv = self.client.get(path='/chartconfigs', headers=self.get_headers())
        chartconfig_types = [chartconf['type'] for chartconf in json.loads(rv.get_data())['chartconfigs']]

        # get selection for sensor names and chartconfig types from subview form
        rv = self.client.get(path='/forms/subviews/add/{0}'.format(view_ids[0]), headers=self.get_headers())
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
        view = {
            'name': 'view1',
            'count': 1,
            'refresh_time': 10
        }

        # add a view with form
        rv = self.client.post(path='/forms/views/add', data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/views', headers=self.get_headers())
        data = json.loads(rv.get_data())['views']
        self.assertEqual(len(data), 1)
        data = data[0]
        for key, value in data.iteritems():
            if key == 'id':
                view_id = value
            elif key != 'links':
                self.assertEqual(value, view[key])
        self.assertTrue(view_id is not None)

        # edit view with form
        view['count'] = 2
        view['refresh_time'] = 20
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
        rv = self.client.get(path='/views', headers=self.get_headers())
        data = json.loads(rv.get_data())['views'][0]
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['refresh_time'], 20)

        # invalid 'name' length on form
        view['name'] = 'asd'
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['name'] = 'qwertyuiopasdfghjklzx'
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['name'] = 'view'

        # invalid 'count' on form
        view['count'] = 3
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['count'] = 5
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['count'] = 2

        # invalid 'refresh_time' on form
        view['refresh_time'] = 9
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        view['refresh_time'] = 61
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

        view['refresh_time'] = 22

        # check if the set valid datas after the invalid ones are accepted
        rv = self.client.post(path='/forms/views/edit/{0}'.format(view_id), data=json.dumps(view), headers=self.get_headers())
        self.assertEqual(rv.status_code, 302)
