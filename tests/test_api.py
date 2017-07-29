import json

from data_visualization.queries import create_chartconfigs

from tests import BaseTest

class ApiTest(BaseTest):
    def test_categories(self):
        # create categories
        categories = self.get_categories()
        locations = []

        for category in categories:
            rv = self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # try to add one of the categories once more
        rv = self.client.post('/category', data=json.dumps(categories[0]))
        self.assertEqual(rv.status_code, 400)

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(path=locations[i], headers=self.get_headers())
            self.assertEqual(json.loads(rv.get_data())['name'], categories[i]['name'])

        # try to get a non-existing category
        location_base = '/'.join(locations[0].split('/')[:-1])
        invalid_location = location_base + '/4'
        rv = self.client.get(path=invalid_location, headers=self.get_headers())
        self.assertEquals(rv.status_code, 400)

        # fetch all the categories
        categories_location = 'http://localhost/categories'
        rv = self.client.get(path=categories_location, headers=self.get_headers())
        data = json.loads(rv.get_data())
        self.assertTrue('categories' in data.keys())
        data = data['categories']
        self.assertEqual(len(data), len(categories))
        for i in xrange(len(data)):
            self.assertEqual(data[i]['name'], categories[i]['name'])

        # create a sensor with foreign key to categories[0]
        sensor = self.get_sensors()[0]
        rv = self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)
        sensor_location = rv.headers['Location']

        # get the sensors for categories[0]
        rv = self.client.get(path=locations[0], headers=self.get_headers())
        sensors_location = json.loads(rv.get_data())['links']['sensors']
        self.assertTrue(len(sensors_location), 1)
        self.assertEqual(sensors_location[0].split('/')[-2:], sensor_location.split('/')[-2:])
        rv = self.client.get(path=sensor_location, headers=self.get_headers())
        data = json.loads(rv.get_data())
        self.assertEqual(data['name'], sensor['name'])

        # modify categories[0]
        category_mod = {'name': 'humi'}
        rv = self.client.put(path=locations[0], data=json.dumps(category_mod), headers=self.get_headers())
        data = json.loads(rv.get_data())
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data['id'], int(locations[0].split('/')[-1]))
        self.assertEqual(data['name'], category_mod['name'])

        # delete categories
        for location in locations:
            rv = self.client.delete(path=location, headers=self.get_headers())
            self.assertEqual(rv.status_code, 204)

        # try to get sensor
        rv = self.client.get(path=sensor_location, headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

    def test_sensors(self):
        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # create sensors
        sensors = self.get_sensors()
        locations = []
        category_locations = []

        for sensor in sensors:
            rv = self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])
            category_locations.append(json.loads(rv.get_data())['links']['category'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(path=locations[i], headers=self.get_headers())
            data = json.loads(rv.get_data())
            for key in sensors[i].iterkeys():
                self.assertTrue(key in data.keys())
                self.assertEqual(data[key], sensors[i][key])

        # try to get a non-existing sensor
        invalid_location = '/'.join(locations[0].split('/')[:-1]) + '/non-existing'
        rv = self.client.get(path=invalid_location, headers=self.get_headers())
        self.assertEquals(rv.status_code, 400)

        # fetch sensors in every category
        for category_location in category_locations:
            rv = self.client.get(path=category_location, headers=self.get_headers())
            data = json.loads(rv.get_data())['links']['sensors']
            self.assertEqual(len(data), 1)
            self.assertTrue(('/').join(data[0].split('/')[-2:]) in [('/').join(location.split('/')[-2:]) for location in locations])

        # create a data with foreign key to sensors[0]
        data = self.get_datas()[0]
        rv = self.client.post(path='/data', data=json.dumps(data), headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)
        data_location = rv.headers['Location']

        # modify sensors[0]
        sensors[0]['name'] = 'humi'
        sensors[0]['location'] = 'New York'
        rv = self.client.put(path=locations[0], data=json.dumps(sensors[0]), headers=self.get_headers())
        data = json.loads(rv.get_data())
        self.assertEqual(rv.status_code, 201)
        self.assertEqual(data['id'], int(locations[0].split('/')[-1]))
        self.assertEqual(data['name'], 'humi')
        self.assertEqual(data['location'], 'New York')
        self.assertEqual(data['ipv4_addr'], sensors[0]['ipv4_addr'])

        # delete sensors
        for location in locations:
            rv = self.client.delete(path=location, headers=self.get_headers())
            self.assertEqual(rv.status_code, 204)

        # try to get data
        rv = self.client.get(path=data_location, headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

    def test_datas(self):
        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())

        # create datas
        datas = self.get_datas()
        locations = []
        sensor_locations = []

        for data in datas:
            rv = self.client.post(path='/data', data=json.dumps(data), headers=self.get_headers())
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])
            sensor_locations.append(json.loads(rv.get_data())['links']['sensor'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(path=locations[i], headers=self.get_headers())
            data = json.loads(rv.get_data())
            for key in datas[i].iterkeys():
                self.assertTrue(key in data.keys())
                self.assertEqual(data[key], datas[i][key])

        # try to get a non-existing data
        invalid_location = '/'.join(locations[0].split('/')[:-1]) + '/non-existing'
        rv = self.client.get(path=invalid_location, headers=self.get_headers())
        self.assertEquals(rv.status_code, 400)

        # fetch datas for every sensor
        for sensor_location in sensor_locations:
            rv = self.client.get(path=sensor_location, headers=self.get_headers())
            data = json.loads(rv.get_data())['links']['datas']
            self.assertEqual(len(data), 1)
            self.assertTrue(('/').join(data[0].split('/')[-2:]) in [('/').join(location.split('/')[-2:]) for location in locations])

    def test_chartconfigs(self):
        # create chartconfigs
        create_chartconfigs()

        locations = []

        # fetch all chartconfigs
        rv = self.client.get('/chartconfigs', headers=self.get_headers())
        data = json.loads(rv.get_data())['chartconfigs']

        from data_visualization.chartjs import chart_types

        self.assertEqual(len(data), len(chart_types))
        for i in xrange(len(data)):
            self.assertTrue(data[i]['type'], chart_types[i])
            locations.append(data[i]['links']['self'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(locations[i], headers=self.get_headers())
            data = json.loads(rv.get_data())
            self.assertEqual(data['type'], chart_types[i])

    def test_subviews(self):
        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())

        # create chartconfigs
        create_chartconfigs()

        # create views
        views = self.get_views()
        for view in views:
            rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers())

        # create subviews
        subviews = self.get_subviews()
        locations = []

        for subview in subviews:
            rv = self.client.post(path='/subview', data=json.dumps(subview), headers=self.get_headers())
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # check the returned 'Location' links
        for i in xrange(len(locations)):
            rv = self.client.get(path=locations[i], headers=self.get_headers())
            data = json.loads(rv.get_data())
            self.assertEqual(data['sensor_id'], subviews[i]['sensor_id'])
            self.assertEqual(data['chartconfig_id'], subviews[i]['chartconfig_id'])

        # modify subviews[0]
        subviews[0]['sensor_id'] = 2
        subviews[0]['chartconfig_id'] = 4
        rv = self.client.put(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.get_data())
        self.assertEqual(data['sensor_id'], 2)
        self.assertEqual(data['chartconfig_id'], 4)
        sensor_location = data['links']['sensor']
        chartconfig_location = data['links']['chartconfig']

        # remove subviews[0]
        rv = self.client.delete(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 204)
        rv = self.client.get(path=locations[0], data=json.dumps(subviews[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # check if sensor and chartconfig are still there
        rv = self.client.get(path=sensor_location, headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)
        rv = self.client.get(path=chartconfig_location, headers=self.get_headers())
        self.assertEqual(rv.status_code, 200)

    def test_views(self):
        # create categories
        categories = self.get_categories()
        for category in categories:
            self.client.post(path='/category', data=json.dumps(category), headers=self.get_headers())

        # create sensors
        sensors = self.get_sensors()
        for sensor in sensors:
            self.client.post(path='/sensor', data=json.dumps(sensor), headers=self.get_headers())

        # create chartconfigs
        create_chartconfigs()

        # create views
        views = self.get_views()
        locations = []

        for view in views:
            rv = self.client.post(path='/view', data=json.dumps(view), headers=self.get_headers())
            self.assertEqual(rv.status_code, 201)
            locations.append(rv.headers['Location'])

        # try to create view with 'count' > 4
        rv = self.client.post(path='/view', data=json.dumps({'count': 5}), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # try to create view with 'count' not in [1, 2, 4]
        rv = self.client.post(path='/view', data=json.dumps({'count': 3}), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # create subviews
        subviews = self.get_subviews()
        subview_locations = []

        subviews[2]['view_id'] = 1

        for i in xrange(len(subviews)):
            rv = self.client.post(path='/subview', data=json.dumps(subviews[i]), headers=self.get_headers())
            if i == 2:
                self.assertEqual(rv.status_code, 400)
            else:
                self.assertEqual(rv.status_code, 201)
                subview_locations.append(rv.headers['Location'])

        subviews[2]['view_id'] = 2
        rv = self.client.post(path='/subview', data=json.dumps(subviews[i]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)
        subview_locations.append(rv.headers['Location'])

        subviews[0]['view_id'] = 2
        rv = self.client.put(subview_locations[0], data=json.dumps(subviews[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # check the returned 'Location' links
        expected_icons = ['1x1', '2x1', '2x1']

        for i in xrange(len(locations)):
            rv = self.client.get(path=locations[i], headers=self.get_headers())
            data = json.loads(rv.get_data())
            self.assertEqual(data['count'], views[i]['count'])
            self.assertEqual(len(data['links']['subviews']), views[i]['count'])
            self.assertTrue(expected_icons[i] in data['links']['icon'])

        # modify views[0]
        views[0]['name'] = 'modifiedview'
        views[0]['count'] = 4
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 201)
        data = json.loads(rv.get_data())
        self.assertEqual(data['name'], 'modifiedview')
        self.assertEqual(data['count'], 4)
        self.assertTrue('2x2' in data['links']['icon'])

        # try to modify the 'count' in views[1]
        views[1]['count'] = 1
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        views[1]['count'] = 3
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        views[1]['count'] = 5
        rv = self.client.put(path=locations[1], data=json.dumps(views[1]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # try to modify the 'refresh_time' in views[0]
        views[0]['refresh_time'] = 9
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        views[0]['refresh_time'] = 61
        rv = self.client.put(path=locations[0], data=json.dumps(views[0]), headers=self.get_headers())
        self.assertEqual(rv.status_code, 400)

        # remove views
        for location in locations:
            rv = self.client.delete(path=location, headers=self.get_headers())
            self.assertEqual(rv.status_code, 204)

        # check if subviews were removed
        for subview_location in subview_locations:
            rv = self.client.get(path=subview_location, headers=self.get_headers())
            self.assertEqual(rv.status_code, 400)
