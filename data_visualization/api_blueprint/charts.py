from flask import g, render_template, jsonify, abort, request

from . import api
from .. import chartjs
from ..models import Category, ChartConfig, Sensor, View
from ..queries import query_get_category_by_id, query_get_sensor_by_id, query_get_sensor_by_name, query_get_view_by_id, query_get_chartconfig_by_id, query_get_predefined_config_by_id

@api.route('/charts/<view_id>', methods=['GET'])
def get_charts_skeleton(view_id):
    view = query_get_view_by_id(view_id, g.current_user.id)
    number_of_subviews = view.number_of_subviews();
    width = 1200 if number_of_subviews != 4 else 550
    height = 300 if number_of_subviews != 1 else 600
    charts = []
    for subview in view.subviews:
        category_id = query_get_sensor_by_id(subview.sensor_id, g.current_user.id).category_id
        category = query_get_category_by_id(category_id, g.current_user.id)
        chartconfig = query_get_chartconfig_by_id(subview.chartconfig_id)
        canvas = chartjs.Canvas('chart{0}'.format(subview.id), width, height)
        options = chartjs.Options(float(category.min_value), float(category.max_value))
        chart_builder = chartjs.ChartBuilder(chartconfig.type, options)
        chart = chartjs.Chart(canvas, 'ctx{0}'.format(subview.id), chart_builder)
        chart_builder.create_dataset(category.name)
        charts.append(chart.to_dict())
    return render_template('charts.html.j2', charts=charts)

@api.route('/charts/<view_id>/refresh', methods=['GET'])
def refresh_charts(view_id):
    view = query_get_view_by_id(view_id, g.current_user.id)
    if len(request.args) != view.number_of_subviews():
        abort(400)
    refresh_data = {}
    for subview in view.subviews:
        last_index = int(request.args.get('chart{0}'.format(subview.id)))
        datas_since_index = query_get_sensor_by_id(subview.sensor_id, g.current_user.id).datas[last_index:]
        refresh_data['chart{0}'.format(subview.id)] = [data.to_dict() for data in datas_since_index]
    return jsonify(refresh_data)

@api.route('/get_preconfigured_skeleton/<view_id>', methods=['GET'])
def get_preconfigured_skeleton(view_id):
    view = query_get_view_by_id(view_id, g.current_user.id)
    if view.type != 'preconfigured':
        abort(400)
    predefined_config = query_get_predefined_config_by_id(view.predefined_configuration_id).configuration
    return predefined_config

@api.route('/refresh_preconfigured/<view_id>', methods=['GET'])
def refresh_preconfigured(view_id):
    view = query_get_view_by_id(view_id, g.current_user.id)
    if view.type != 'preconfigured':
        abort(400)
    predefined_config = query_get_predefined_config_by_id(view.predefined_configuration_id)
    refresh_data = {}
    for arg in request.args:
        last_index = int(request.args.get(arg))
        datas_since_index = query_get_sensor_by_id(query_get_sensor_by_name(arg, g.current_user.id).id, g.current_user.id).datas[last_index:]
        dataset_size = 60 if len(datas_since_index) > 60 else len(datas_since_index)
        refresh_data[arg] = [data.to_dict() for data in datas_since_index[:dataset_size]]
    return jsonify(refresh_data)
