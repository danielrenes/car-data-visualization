import json

from flask import g, jsonify, abort, request, url_for

from . import api
from ..queries import query_all_parking_spaces

@api.route('/maps/init', methods=['GET'])
def init_map():
    sensors = query_all_parking_spaces(g.current_user.id)
    avg_latitude = avg_longitude = 0
    min_latitude = min_longitude = 1000
    max_latitude = max_longitude = 0
    for sensor in sensors:
        latitude, longitude = sensor.location.split(',')
        latitude, longitude = float(latitude), float(longitude)
        avg_latitude += latitude
        avg_longitude += longitude
        if latitude < min_latitude:
            min_latitude = latitude
        if latitude > max_latitude:
            max_latitude = latitude
        if longitude < min_longitude:
            min_longitude = longitude
        if longitude > max_longitude:
            max_longitude = longitude
    avg_latitude /= len(sensors)
    avg_longitude /= len(sensors)
    radius = max([avg_latitude - min_latitude, max_latitude - avg_latitude, avg_longitude - min_longitude, max_longitude - avg_longitude])
    return jsonify({'center': {'latitude': avg_latitude, 'longitude': avg_longitude}, 'zoom': int(0.05 / radius)})

@api.route('/maps/refresh', methods=['GET'])
def refresh_map():
    last_index = int(request.args.get('map'))
    sensors = query_all_parking_spaces(g.current_user.id)
    refresh_data = {}
    for sensor in sensors:
        refresh_data[sensor.location] = [data.to_dict() for data in sensor.datas[last_index:]]
    return jsonify(refresh_data)
