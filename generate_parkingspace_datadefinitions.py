#!/usr/bin/env python

import argparse
import json
import os
import random

basedir = (os.path.dirname(os.path.realpath(__file__)))
data_definitions_dir = os.path.join(basedir, 'data_definitions')

template = '''{
    "datatype": {
        "datatype": "EnumeratedDataType",
        "name": "parking space",
        "enum": ["Free", "Occupied"],
        "current": "Free",
        "unit": ""
    },
    "optional": {
        "location": ""
    },
    "scenario": []
}'''

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', type=int, required=True, help='the number of parking space data definitions to create')
    parser.add_argument('-t', '--time', type=int, required=True, help='the time interval in seconds for the data definitions')
    parser.add_argument('-n', '--min', type=int, required=True, help='the minimum seconds when generating random state')
    parser.add_argument('-x', '--max', type=int, required=True, help='the maximum seconds when generating random state')
    parser.add_argument('-a', '--latitude', type=float, required=True, help='the latitude of the center of the circle in degrees')
    parser.add_argument('-o', '--longitude', type=float, required=True, help='the longitude of the center of the circle in degrees')
    parser.add_argument('-r', '--radius', type=float, required=True, help='the radius of the circle in degrees')
    return parser

def random_location(latitude, longitude, radius):
    random_latitude = random.uniform(latitude, latitude + radius)
    random_longitude = random.uniform(longitude, longitude + radius)
    return '{0},{1}'.format(random_latitude, random_longitude)

def generate(time, min_rand, max_rand, latitude, longitude, radius, filename):
    generated = []
    values = ['Free', 'Occupied']
    current_time = 0
    current_value = ''
    sum_time = 0
    while sum_time < time:
        temp_time = random.randint(min_rand, max_rand)
        if sum_time + temp_time > time:
            temp_time = time - sum_time
        temp_value = random.choice(values)
        if current_value == '':
            current_value = temp_value
        if temp_value == current_value:
            current_time += temp_time
        else:
            generated.append({
                'duration': current_time,
                'step_or_value': current_value
            })
            current_time = temp_time;
            current_value = ''
            sum_time += temp_time
            base = json.loads(template)
            base['scenario'] = generated
            base['optional']['location'] = random_location(latitude, longitude, radius)
            with open(os.path.join(data_definitions_dir, filename), 'w') as f:
                f.write(json.dumps(base))

def run():
    args = cli().parse_args()
    count, time, min_rand, max_rand, latitude, longitude, radius = args.count, args.time, args.min, args.max, args.latitude, args.longitude, args.radius
    for i in xrange(count):
        generate(time, min_rand, max_rand, latitude, longitude, radius, 'parking_space_{0}.json'.format(i))

if __name__ == '__main__':
    run()
