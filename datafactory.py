#!/usr/bin/env python

import httplib
import json
import random
import threading
import time

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}

sensors = [
    {
        'name':       'virttemp0',
        'category':   'temp',
        'location':   'Budapest',
        'ipv4_addr':  '127.0.0.1',
        'min_value':  -20,
        'max_value':  50,
        'interval':   15
    },
    {
        'name':       'virttemp1',
        'category':   'temp',
        'min_value':  -30,
        'max_value':  40,
        'interval':   20
    },
    {
        'name':       'virthumi0',
        'category':   'humi',
        'location':   'Budapest'
    }
]

views = [
    {
        'name':         'virtview0',
        'count':        1,
        'refresh_time': 20
    },
    {
        'name':         'virtview1',
        'count':        2,
        'refresh_time': 10
    },
    {
        'name':         'virtview2',
        'count':        4,
        'refresh_time': 30
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
    def __init__(self, category_name, name, location=None, ipv4_addr=None, min_value=0, max_value=100, interval=10, daemon=True):
        super(VirtualSensor, self).__init__()
        self.setDaemon(daemon)
        self.interval = interval
        self.min = min_value
        self.max = max_value
        conn = self.create_connection()
        try:
            self.id = self.register(conn, category_name, name, location, ipv4_addr)
        except RegisterException:
            conn.close()
            raise

    def random_value(self):
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
        conn.request('GET', '/categories', headers=headers)
        resp = conn.getresponse()
        if resp.status != 200:
            raise RegisterException('Could not fetch categories')
        categories = json.loads(resp.read())['categories']
        for category in categories:
            if category['name'] == category_name:
                category_id = category['id']
                break

        if category_id is None:
            # register its category
            conn.request('POST', '/category', json.dumps({'name': category_name, 'min_value': self.min, 'max_value': self.max}), headers)
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

    def send_data(self):
        conn = self.create_connection()
        val = self.random_value()
        conn.request('POST', '/data', json.dumps(self.build_data(self.random_value())), headers)
        conn.getresponse()
        conn.close()

    def run(self):
        while True:
            self.send_data()
            time.sleep(self.interval)

class VirtualAdmin(object):
    @classmethod
    def execute(cls, admin_task):
        method = admin_task['method']
        path = admin_task['path']
        data = json.dumps(admin_task['data'])
        conn = httplib.HTTPConnection(host='localhost', port=5000)
        conn.request(method, path, data, headers)
        conn.getresponse()
        conn.close()

def ping():
    conn = httplib.HTTPConnection(host='localhost', port=5000)
    try:
        conn.request('HEAD', '')
    except IOError:
        conn.close()
        return False
    is_available = conn.getresponse().status == 200
    conn.close()
    return is_available

if __name__ == '__main__':
    while not ping():
        time.sleep(1)

    sensor_threads = []

    for sensor in sensors:
        name = get(sensor, 'name')
        category = get(sensor, 'category')
        location = get(sensor, 'location')
        ipv4_addr = get(sensor, 'ipv4_addr')
        min_value = get(sensor, 'min_value', 0)
        max_value = get(sensor, 'max_value', 100)
        interval = get(sensor, 'interval', 10)
        sensor_threads.append(VirtualSensor(name=name, category_name=category, location=location, \
            ipv4_addr=ipv4_addr, min_value=min_value, max_value=max_value, interval=interval))

    for admin_task in create_admin_tasks({
        'POST': [
            {
                '/view':    views
            },
            {
                '/subview': subviews
            }
        ]
    }):
        VirtualAdmin.execute(admin_task)

    for sensor_thread in sensor_threads:
        sensor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
