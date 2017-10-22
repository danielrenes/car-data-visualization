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
    "scenario": []
}'''

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--count', type=int, required=True, help='the number of parking space data definitions to create')
    parser.add_argument('-t', '--time', type=int, required=True, help='the time interval in seconds for the data definitions')
    return parser

def generate(time, filename):
    generated = []
    values = ['Free', 'Occupied']
    current_time = 0
    current_value = ''
    sum_time = 0
    while sum_time < time:
        temp_time = random.randint(60, 120)
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
            with open(os.path.join(data_definitions_dir, filename), 'w') as f:
                f.write(json.dumps(base))

def run():
    args = cli().parse_args()
    count, time = args.count, args.time
    for i in xrange(count):
        generate(time, 'parking_space_{0}.json'.format(i))

if __name__ == '__main__':
    run()
