#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import os
import time
import threading

from data_visualization.chartjs import chart_types

class DataType(object):
    def __init__(self, _name):
        self.name = _name
        self._current = None

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        raise NotImplementedError('Class {0} must implement current(self, value)'.format(self.__class__.__name__))

    def to_json(self):
        raise NotImplementedError('Class {0} must implement to_json()'.format(self.__class__.__name__))

    @classmethod
    def from_json(cls, _json):
        raise NotImplementedError('Class {0} must implement from_json(cls, _json)'.format(self.__class__.__name__))

class NumericDataType(DataType):
    def __init__(self, _name, _min, _max, _unit, _current=None):
        super(NumericDataType, self).__init__(_name)
        self.min = _min
        self.max = _max
        self.unit = _unit
        self.current = _current

    @DataType.current.setter
    def current(self, value):
        if value is None or value >= self.min and value <= self.max:
            self._current = value
        else:
            raise ValueError('{0} is not in range [{1},{2}]'.format(value, self.min, self.max))

    def to_json(self):
        return json.dumps(
            {
                'datatype': self.__class__.__name__,
                'name':     self.name,
                'min':      self.min,
                'max':      self.max,
                'current':  self.current,
                'unit':     self.unit
            }
        )

    @classmethod
    def from_json(cls, _json):
        if type(_json) is str:
            obj = json.loads(_json)
        elif isinstance(_json, NumericDataType):
            obj = _json
        else:
            raise TypeError('Input must be JSON string or a NumericDataType object!')
        datatype = cls(obj['name'], obj['min'], obj['max'], obj['unit'], obj['current'])
        return datatype

class EnumeratedDataType(DataType):
    class Enumeration(object):
        def __init__(self, _enum):
            for number, name in enumerate(_enum):
                setattr(self, name, number)

        @property
        def values(self):
            return [key for key in sorted(self.__dict__, key=self.__dict__.get)]

    def __init__(self, _name, _enum, _current=None):
        super(EnumeratedDataType, self).__init__(_name)
        self.enum = EnumeratedDataType.Enumeration(_enum)
        self.current = _current

    @DataType.current.setter
    def current(self, value):
        if value is None:
            self._current = None
        elif hasattr(self.enum, value):
            self._current = getattr(self.enum, value)
        else:
            raise ValueError('{0} is not in enum: {1}'.format(value, self.enum))

    def to_json(self):
        return json.dumps(
            {
                'datatype': self.__class__.__name__,
                'name':     self.name,
                'enum':     self.enum.values,
                'current':  self.current if self.current is None else self.enum.values[self.current]
            }
        )

    @classmethod
    def from_json(cls, _json):
        if type(_json) is str:
            obj = json.loads(_json)
        elif isinstance(_json, EnumeratedDataType):
            obj = _json
        else:
            raise TypeError('Input must be JSON string or a NumericDataType object!')
        datatype = cls(obj['name'], obj['enum'], obj['current'])
        return datatype

def from_json(_json):
    obj = json.loads(_json)
    datatype = obj['datatype']
    if datatype == 'NumericDataType':
        return NumericDataType.from_json(_json)
    elif datatype == 'EnumeratedDataType':
        return EnumeratedDataType.from_json(_json)
    else:
        raise TypeError('The given datatype is not defined: {0}'.format(datatype))

class Scenario(object):
    def __init__(self, descriptors):
        self.descriptors = descriptors

    @staticmethod
    def from_json(_json):
        scenario = Scenario(json.loads(_json))
        return scenario

# def create_default():
#     vehicle_speed = NumericDataType('vehicle_speed', 0, 200, 'km/h')
#     engine_rpm = NumericDataType('engine_rpm', 0, 8000, 'rpm')
#     selected_gear = EnumeratedDataType('selected_gear', ['Reverse', 'Neutral', 'First', 'Second', 'Third', 'Forth', 'Fifth', 'Sixth'])
#     coolant_temperature = NumericDataType('coolant_temperature', -30, 150, '°C')
#     oil_temperature = NumericDataType('oil_temperature', -30, 150, '°C')
#     throttle_position = NumericDataType('throttle_position', 0, 45, 'deg')
#     brake_position = NumericDataType('brake_position', 0, 45, 'deg')
#     clutch_position = NumericDataType('clutch_position', 0, 45, 'deg')
#     battery_voltage = NumericDataType('battery_voltage', 11, 14, 'V')

class DataGenerator(object):
    def __init__(self, filepath):
        with open(filepath) as f:
            obj = json.loads(f.read())
        self.name = os.path.splitext(os.path.split(filepath)[1])[0]
        self.datatype = from_json(json.dumps(obj['datatype']))
        self.scenario = Scenario.from_json(json.dumps(obj['scenario']))

    def map_to_sensor(self):
        return {
            'name': self.name,
            'category': self.datatype.name,
            'min_value': self.datatype.min if isinstance(self.datatype, NumericDataType) else 0,
            'max_value': self.datatype.max if isinstance(self.datatype, NumericDataType) else 0,
            'unit': self.datatype.unit if isinstance(self.datatype, NumericDataType) else ''
        }

    def map_to_datas(self):
        return [value for value in self.run(silent=True)]

    def run(self, silent=False):
        elapsed_seconds = 0
        for descriptor in self.scenario.descriptors:
            cnt = 0
            while cnt < descriptor['duration']:
                if isinstance(self.datatype, NumericDataType):
                    self.datatype.current = self.datatype.current + descriptor['step_or_value']
                elif isinstance(self.datatype, EnumeratedDataType):
                    self.datatype.current = descriptor['step_or_value']
                else:
                    raise TypeError('Datatype is not valid!')
                cnt += 1
                elapsed_seconds += 1
                if isinstance(self.datatype, NumericDataType):
                    value = self.datatype.current
                elif isinstance(self.datatype, EnumeratedDataType):
                    value = self.datatype.enum.values[self.datatype.current]
                if silent:
                    yield value
                else:
                    time.sleep(1)
                    print '{0}: {1}'.format(self.datatype.name, value)

def create_datagenerators():
    data_definitions_dir = './data_definitions'
    data_generators = []

    for _file in os.listdir(data_definitions_dir):
        if os.path.splitext(_file)[1] == '.json':
            data_generators.append(DataGenerator(os.path.join(data_definitions_dir, _file)))

    return data_generators

def map_to_models(data_generators):
    sensors = []
    datas = []
    for data_generator in data_generators:
        sensors.append(data_generator.map_to_sensor())
        datas.append(data_generator.map_to_datas())
    return (sensors[0:4], datas[0:4])

if __name__ == '__main__':
    data_generators = create_datagenerators()
    sensors, datas = map_to_models(create_datagenerators())
    print 'sensors'
    print sensors[0]
    print 'datas'
    print datas[0]
