#!/usr/bin/env python

import httplib
import json
import os
import random
import threading
import time
from base64 import b64encode

from datafactory import create_admin_tasks, get, Runner, VirtualSensor
from local_data import map_to_models as local_map, create_datagenerators as local_create
from data_visualization import canvas_gauges

sensors, datas = local_map(local_create())
predefined_configs = []
views = []

class ReplaySensor(VirtualSensor):
    def __init__(self, category_name, name, datas, location=None, ipv4_addr=None, \
            unit='', min_value=0, max_value=100, interval=10, daemon=True, batch_size=60):
        super(ReplaySensor, self).__init__(category_name, name, location, ipv4_addr, unit, min_value, max_value, interval, daemon)
        self.datas = datas
        self.last_data_index = 0
        self.batch_size = batch_size

    def next_value(self):
        batch = []
        while len(batch) < self.batch_size:
            batch.append(self.datas[self.last_data_index])
            self.last_data_index += 1
            if self.last_data_index == len(self.datas):
                self.last_data_index = 0
        return batch

    def run(self):
        while True:
            self.send_data('/data/batch')
            time.sleep(self.batch_size)

class ReplayRunner(Runner):
    def create_sensor_threads(self):
        for i in xrange(len(sensors)):
            sensor = sensors[i]
            name = get(sensor, 'name')
            category = get(sensor, 'category')
            location = get(sensor, 'location')
            ipv4_addr = get(sensor, 'ipv4_addr')
            unit = get(sensor, 'unit', '')
            min_value = get(sensor, 'min_value', 0)
            max_value = get(sensor, 'max_value', 100)
            interval = get(sensor, 'interval', 10)
            self.sensor_threads.append(ReplaySensor(name=name, category_name=category, datas=datas[i], \
                location=location, ipv4_addr=ipv4_addr, unit=unit, min_value=min_value, max_value=max_value, interval=interval))
        self.create_predefined_views()

    def create_admin_tasks(self):
        return create_admin_tasks({
            'POST': [
                {
                    '/predefinedconfigs':  predefined_configs
                },
                {
                    '/view':                views
                }
            ]
        })

    def create_predefined_views(self):
        global predefined_configs
        global views
        view_definitions_dir = './view_definitions'
        for _file in os.listdir(view_definitions_dir):
            elements = []
            if os.path.splitext(_file)[1] == '.json':
                views.append(
                    {
                        'name': os.path.splitext(_file)[0],
                        'predefined_configuration_id': len(predefined_configs) + 1,
                        'type': 'preconfigured',
                        'user_id': 1
                    }
                )
                with open(os.path.join(view_definitions_dir, _file)) as f:
                    obj = json.loads(f.read())
                for row in obj:
                    position_x = 0
                    max_height = 0
                    for element in row:
                        sensor = self.sensor_for_element(element['data'])
                        if sensor:
                            if element['height'] > max_height:
                                max_height = element['height']
                            basic = canvas_gauges.BasicConfig(element['width'], element['height'],\
                                sensor['unit'], sensor['min_value'], sensor['max_value'])
                            ticks = canvas_gauges.Ticks(sensor['min_value'], sensor['max_value'], 2)
                            canvas = canvas_gauges.CanvasGauge(canvas_id=element['data'], data_type='{0}-{1}'.format(element['subtype'], element['type']), basic=basic, ticks=ticks)
                            canvas_html = self.set_position(canvas.build(), position_x)
                            elements.append(canvas_html)
                            position_x += element['width']
                    try:
                        last_closing_div_index = len(elements) - elements[::-1].index('</div>') - 1
                    except ValueError:
                        last_closing_div_index = -1
                    elements.insert(last_closing_div_index + 1, '<div style="position: relative; height: {0}px">'.format(max_height))
                    elements.append('</div>')
                predefined_configs.append({'configuration': ' '.join(elements)})

    def sensor_for_element(self, element_data_name):
        transformed_data_name = '_'.join(element_data_name.lower().split(' '))
        for sensor in sensors:
            if sensor['name'] == transformed_data_name:
                return sensor
        return None

    def set_position(self, canvas_html, position_x):
        html = ['<canvas style="position: absolute; top: 0px; left: {0}px"'.format(position_x)]
        html.append(canvas_html.split('<canvas ')[1])
        return ' '.join(html)

if __name__ == '__main__':
    runner = ReplayRunner()
    runner.run()
