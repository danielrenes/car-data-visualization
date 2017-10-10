#!/usr/bin/env python
#-*- coding: utf-8 -*

import httplib
import json
import random
import threading
import time
from base64 import b64encode

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Basic {0}'.format(b64encode('Fake User:fakepassword'))
}

sensors = [
    {
        'name':       'virttemp0',
        'category':   'temp',
        'location':   'Budapest',
        'ipv4_addr':  '127.0.0.1',
        'unit':       '°C',
        'min_value':  -20,
        'max_value':  50,
        'interval':   15
    },
    {
        'name':       'virttemp1',
        'category':   'temp',
        'unit':       '°C',
        'min_value':  -10,
        'max_value':  40,
        'interval':   20
    },
    {
        'name':       'virthumi0',
        'category':   'humi',
        'location':   'Budapest',
        'unit':       '%'
    }
]

views = [
    {
        'name':         'virtview0',
        'count':        1,
        'refresh_time': 20,
        'user_id':      1,
        'type':         'normal'
    },
    {
        'name':         'virtview1',
        'count':        2,
        'refresh_time': 10,
        'user_id':      1,
        'type':         'normal'
    },
    {
        'name':         'virtview2',
        'count':        4,
        'refresh_time': 30,
        'user_id':      1,
        'type':         'normal'
    }
]

subviews = [
    {
        'sensor_id':        1,
        'chartconfig_id':   1,
        'view_id':          1
    },
    {
        'sensor_id':        2,
        'chartconfig_id':   2,
        'view_id':          2
    },
    {
        'sensor_id':        2,
        'chartconfig_id':   3,
        'view_id':          2
    },
    {
        'sensor_id':        3,
        'chartconfig_id':   4,
        'view_id':          3
    },
    {
        'sensor_id':        3,
        'chartconfig_id':   5,
        'view_id':          3
    },
    {
        'sensor_id':        3,
        'chartconfig_id':   6,
        'view_id':          3
    },
    {
        'sensor_id':        3,
        'chartconfig_id':   7,
        'view_id':          3
    }
]

def create_admin_tasks(tasks_dict):
    admin_tasks = []
    for key, value in tasks_dict.iteritems():
        if not isinstance(value, list):
            raise TypeError('{0} is not a list'.format(value))
        for task_dict in value:
            if not isinstance(task_dict, dict):
                raise TypeError('{0} is not a list'.format(task_dict))
            for key2, value2 in task_dict.iteritems():
                if not isinstance(value2, list):
                    raise TypeError('{0} is not a list'.format(value2))
                for item in value2:
                    admin_tasks.append({
                        'method':   key,
                        'path':     key2,
                        'data':     item
                    })
    return admin_tasks

def get(dictionary, key, default=None):
    if key in dictionary.iterkeys():
        return dictionary[key]
    return default

class RegisterException(Exception):
    pass

class VirtualSensor(threading.Thread):
    def __init__(self, category_name, name, location=None, ipv4_addr=None, unit='', min_value=0, max_value=100, interval=10, daemon=True):
        super(VirtualSensor, self).__init__()
        self.setDaemon(daemon)
        self.interval = interval
        self.unit = unit
        self.min = min_value
        self.max = max_value
        conn = self.create_connection()
        try:
            self.id = self.register(conn, category_name, name, location, ipv4_addr)
        except RegisterException:
            conn.close()
            raise

    def next_value(self):
        rand_float = random.uniform(self.min, self.max)
        rand_float_0_001 = float('{0:.3f}'.format(rand_float))
        return rand_float_0_001

    def build_data(self, value):
        return {
            'sensor_id': self.id,
            'value': value
        }

    def create_connection(self):
        return httplib.HTTPConnection(host='localhost', port=5000)

    def register(self, conn, category_name, name, location, ipv4_addr):
        category_id = None

        # search its category
        conn.request('GET', '/user', headers=headers)
        resp = conn.getresponse()
        if resp.status != 200:
            raise RegisterException('Could not fetch categories')
        category_locations = json.loads(resp.read())['links']['categories']
        for category_location in category_locations:
            conn.request('GET', category_location, headers=headers)
            resp = conn.getresponse()
            category = json.loads(resp.read())
            if category['name'] == category_name:
                category_id = category['id']

        if category_id is None:
            # register its category
            conn.request('POST', '/category', \
                json.dumps({'name': category_name, 'unit': self.unit, 'min_value': self.min, 'max_value': self.max, 'user_id': 1}), headers)
            resp = conn.getresponse()
            if resp.status != 201:
                raise RegisterException('Could not register category')
            for tup in resp.getheaders():
                if tup[0].lower() == 'location':
                    category_id = tup[1].split('/')[-1]
                    break

        data = {'name': name, 'category_id': category_id}
        if location is not None:
            data['location'] = location
        if ipv4_addr is not None:
            data['ipv4_addr'] = ipv4_addr

        # register itself
        conn.request('POST', '/sensor', json.dumps(data), headers)
        resp = conn.getresponse()
        if resp.status != 201:
            raise RegisterException('Could not register sensor')
        for tup in resp.getheaders():
            if tup[0].lower() == 'location':
                sensor_id = tup[1].split('/')[-1]
                break
        conn.close()

        return sensor_id

    def send_data(self, endpoint):
        conn = self.create_connection()
        conn.request('POST', endpoint, json.dumps(self.build_data(self.next_value())), headers)
        conn.getresponse()
        conn.close()

    def run(self):
        while True:
            self.send_data('/data')
            time.sleep(self.interval)

class VirtualAdmin(object):
    @staticmethod
    def execute(admin_task):
        method = admin_task['method']
        path = admin_task['path']
        data = json.dumps(admin_task['data'])
        conn = httplib.HTTPConnection(host='localhost', port=5000)
        conn.request(method, path, data, headers)
        conn.getresponse()
        conn.close()

class Runner(object):
    def __init__(self):
        self.sensor_threads = []

    def ping(self):
        conn = httplib.HTTPConnection(host='localhost', port=5000)
        try:
            conn.request('HEAD', '')
        except IOError:
            conn.close()
            return False
        is_available = conn.getresponse().status == 200
        conn.close()
        return is_available

    def create_sensor_threads(self):
        for sensor in sensors:
            name = get(sensor, 'name')
            category = get(sensor, 'category')
            location = get(sensor, 'location')
            ipv4_addr = get(sensor, 'ipv4_addr')
            unit = get(sensor, 'unit', '')
            min_value = get(sensor, 'min_value', 0)
            max_value = get(sensor, 'max_value', 100)
            interval = get(sensor, 'interval', 10)
            self.sensor_threads.append(VirtualSensor(name=name, category_name=category, location=location, \
                ipv4_addr=ipv4_addr, unit=unit, min_value=min_value, max_value=max_value, interval=interval))

    def create_admin_tasks(self):
        return create_admin_tasks({
            'POST': [
                {
                    '/view':    views
                },
                {
                    '/subview': subviews
                }
            ]
        })

    def run(self):
        while not self.ping():
            time.sleep(1)
        time.sleep(1)

        # user is created in app when 'debug-with-datafactory' command is selected

        self.create_sensor_threads()

        for admin_task in self.create_admin_tasks():
            VirtualAdmin.execute(admin_task)

        for sensor_thread in self.sensor_threads:
            sensor_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    runner = Runner()
    runner.run()
