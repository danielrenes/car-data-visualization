def instance_check(obj, clas):
    if not isinstance(obj, clas):
        raise TypeError

class Color(object):
    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def build(self):
        return 'rgba({0},{1},{2},{3})'.format(self.red, self.green, self.blue, self.alpha)

class DataHighlights(object):
    def __init__(self, _from, _to, _color):
        instance_check(_color, Color)
        self.data_highlights = []
        self.add(_from, _to, _color)

    def add(self, _from, _to, _color):
        self.data_highlights.append((_from, _to, _color))

    def build(self):
        return 'data-highlights=\'[{0}]\''.format(''.join(\
            ['{' + '"from": {0}, "to": {1}, "color": "{2}"'.format(data_highlight[0], data_highlight[1], data_highlight[2].build()) + '}' for data_highlight in self.data_highlights]))

class Ticks(object):
    def __init__(self, major_from, major_to, minor, major_step=None, stroke=True):
        major_step = major_step if major_step else self.generate_major_step(major_from, major_to)
        self.major = [i for i in xrange(major_from, major_to + major_step, major_step)]
        self.minor = minor
        self.stroke = stroke

    def generate_major_step(self, _min, _max):
        _range = _max - _min
        ten_pow = 1
        while _range > ten_pow and _range % ten_pow == 0:
            ten_pow *= 10
        ten_pow /= 10
        major_step = ten_pow
        if _range / major_step > 10:
            while _range % major_step == 0:
                major_step += ten_pow
            major_step -= ten_pow
        return major_step

    def build(self):
        return 'data-major-ticks="{0}" data-minor-ticks="{1}" data-stroke-ticks="{2}"'.format(','.join([str(i) for i in self.major]), self.minor, self.stroke)

class BasicConfig(object):
    def __init__(self, width, height, unit, _min, _max):
        self.width = width
        self.height = height
        self.unit = unit
        self.min = _min
        self.max = _max

    def build(self):
        return 'data-width="{0}" data-height="{1}" data-units="{2}" data-min-value="{3}" data-max-value="{4}"'.format(self.width, self.height, self.unit, self.min, self.max)

class CanvasGauge(object):
    def __init__(self, canvas_id, data_type, basic, ticks, data_highlights=None, color_scheme=None):
        instance_check(basic, BasicConfig)
        instance_check(ticks, Ticks)
        if data_highlights:
            instance_check(data_highlights, DataHighlights)
        self.canvas_id = canvas_id
        self.data_type = data_type
        self.basic = basic
        self.ticks = ticks
        self.data_highlights = data_highlights if data_highlights else self.generate_data_highlights()

    def generate_data_highlights(self):
        _from = -len(self.ticks.major) / 3
        _to = -1
        if _from == -1:
            _from = -2
        return DataHighlights(self.ticks.major[_from], self.ticks.major[_to], Color(204, 0, 0, 0.8))

    def build(self):
        config = []
        config.append('<canvas id="{0}" data-type="{1}"'.format(self.canvas_id, self.data_type))
        config.append(self.basic.build())
        config.append(self.ticks.build())
        config.append(self.data_highlights.build())
        config.append('></canvas>')
        return ' '.join(config)
