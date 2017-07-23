#!/usr/bin/env python

from functools import wraps

"""
The following example creates a Chart.js chart with id of 'mychart' width and height of 400px.
Two datasets are created for '# of apples' and '# of bananas'. Both are 'bar' charts.
At '17:51' the value for the '# of apples' are 12, and at '17:54' it is 5.
At '17:51' the value for the '# of bananas' are 0, and at '17:54' it is 11.

canvas = Canvas('mychart', 400, 400)
chart_builder = ChartBuilder('bar')
chart = Chart(canvas, 'ctx', chart_builder)
chart_builder.create_dataset('# of apples')
chart_builder.create_dataset('# of bananas')
chart_builder.add_data('17:51', 12)
chart_builder.add_data('17:54', [5, 11])
"""

def encode_unicode(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        unicode_ = f(*args, **kwargs)
        if isinstance(unicode_, dict):
            encoded = {}
            for k, v in unicode_.iteritems():
                try:
                    encoded[k] = v.encode('utf-8')
                except AttributeError:
                    encoded[k] = v
        elif isinstance(unicode_, list):
            encoded = []
            for v in unicode_:
                try:
                    encoded.append(v.encode('utf-8'))
                except AttributeError:
                    encoded.append(v)
        elif isinstance(unicode_, str):
            encoded = unicode_.encode('utf-8')
        elif isinstance(unicode_, (int, long, float)):
            encoded = float(unicode_)
        else:
            encoded = None
        return encoded
    return wrapper

chart_types = [
    'line',
    'bar',
    'radar',
    'doughnut',
    'pie',
    'polarArea',
    'bubble',
    'scatter'
]

class InvalidTypeError(Exception):
    def __init__(self, type, valid_types):
        self.type = type
        self.valid_types = valid_types
    def __str__(self):
        return '{0} is not a valid type. Valid types are: {1}'\
            .format(self.type, ', '.join(self.valid_types))

class Colors(object):
    _colors = [
        (108, 101, 215),
        (212, 210, 9),
        (11, 138, 73),
        (187, 63, 24),
        (135, 165, 162)
    ]

    _coeffs = [7, 11, 19, 15, 6]

    _alpha = 0.2

    _ctr = 0

    _last_color = (0, 0, 0)

    @classmethod
    def alpha(cls, alpha):
        cls._alpha = alpha

    @classmethod
    def next(cls):
        _base_color = cls._colors[cls._ctr]
        _coeff = tuple(cls._coeffs[(cls._ctr + i) % 5] for i in xrange(3))
        _color = tuple(((_base_color[i] + cls._last_color[i]) * _coeff[i]) % 256 for i in xrange(3))
        cls._last_color = _color
        cls._ctr += 1
        if cls._ctr == 4:
            cls._ctr = 0
        return _color + (cls._alpha,)

class Canvas(object):
    def __init__(self, id, width, height):
        self.id = id
        self.width = width
        self.height = height

    @encode_unicode
    def to_dict(self):
        return {
            'id': self.id,
            'width': self.width,
            'height': self.height
        }

class Dataset(object):
    def __init__(self, label):
        self.label = label
        self.data = []
        self.background_color = []

    def add_data(self, dat):
        self.data.append(dat)
        self.background_color.append(Colors.next())

    @encode_unicode
    def to_dict(self):
        return {
            'label': self.label,
            'data': [d for d in self.data],
            'backgroundColor': [bgc for bgc in self.background_color]
        }

class Options(object):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value
        from fractions import gcd
        self.step = gcd(min_value, max_value)

    @encode_unicode
    def to_dict(self):
        return {
            'scales': {
                'yAxes': [{
                    'ticks': {
                        'min': self.min_value,
                        'max': self.max_value,
                        'stepSize': self.step
                    }
                }]
            }
        }

class ChartBuilder(object):
    def __init__(self, type, options=None):
        if type not in chart_types:
            raise InvalidTypeError(type, chart_types)
        if options is not None and not isinstance(options, Options):
            raise TypeError('options must be an instance of {0}'.format(Options))
        self.type = type
        self.labels = []
        self.datasets = []
        self.options = options

    def create_dataset(self, label):
        self.datasets.append(Dataset(label))

    def add_data(self, label, datas):
        self.labels.append(label)
        if not isinstance(datas, list):
            datas = [datas]
        for i in xrange(len(self.datasets)):
            curr_data = datas[i] if i < len(datas) else 0
            self.datasets[i].add_data(curr_data)

    @encode_unicode
    def to_dict(self):
        return {
            'type': self.type,
            'data': {
                'labels': [label for label in self.labels],
                'datasets': [dataset.to_dict() for dataset in self.datasets]
            },
            'options': {} if self.options is None else self.options.to_dict()
        }

class Chart(object):
    def __init__(self, canvas, context, chart_builder):
        self.canvas = canvas
        self.context = context
        self.chart_builder = chart_builder

    @encode_unicode
    def to_dict(self):
        return {
            'canvas': self.canvas.to_dict(),
            'context': self.context,
            'chart': self.chart_builder.to_dict()
        }
