import unittest

from data_visualization import create_app, db

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        db.drop_all()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()

    def get_headers(self):
        return {
            'Accept': 'application/json',
            'Content-type': 'application/json'
        }

    def get_categories(self):
        return [
            {
                'name': 'temperature',
                'min_value': -50,
                'max_value': 50
            },
            {
                'name': 'humidity',
                'min_value': 0,
                'max_value': 100
            },
            {
                'name': 'pressure',
                'min_value': 0,
                'max_value': 10000
            }
        ]

    def get_sensors(self):
        return [
            {
                'name': 'temp1',
                'category_id': 1,
                'location': 'London',
                'ipv4_addr': '127.0.0.1'
            },
            {
                'name': 'humi1',
                'category_id': 2
            },
            {
                'name': 'pres1',
                'category_id': 3
            }
        ]

    def get_datas(self):
        return [
            {
                'value': 10.5,
                'sensor_id': 1
            },
            {
                'value': 23.2,
                'sensor_id': 2
            },
            {
                'value': -4.1,
                'sensor_id': 3
            }
        ]

    def get_subviews(self):
        return [
            {
                'sensor_id': 1,
                'chartconfig_id': 1,
                'view_id': 1
            },
            {
                'sensor_id': 2,
                'chartconfig_id': 2,
                'view_id': 2
            },
            {
                'sensor_id': 3,
                'chartconfig_id': 3,
                'view_id': 2
            }
        ]

    def get_views(self):
        return [
            {
                'name': 'view1',
                'count': 1,
                'refresh_time': 10
            },
            {
                'name': 'view2',
                'count': 2,
                'refresh_time': 60
            }
        ]
