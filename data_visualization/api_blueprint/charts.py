from flask import render_template, jsonify, request

from . import api
from .. import chartjs
from ..models import Category, ChartConfig, Sensor, View

@api.route('/charts/<view_id>', methods=['GET'])
def get_charts_skeleton(view_id):
    view = all_views().filter(View.id==view_id).first()
    if view is None:
        abort(400)
    number_of_subviews = view.number_of_subviews();
    width = 1200 if number_of_subviews != 4 else 550
    height = 300 if number_of_subviews != 1 else 600
    charts = []
    for subview in view.subviews:
        category = all_categories().filter(Category.id==all_sensors().filter(Sensor.id==subview.sensor_id).first().category_id).first()
        chartconfig = all_chartconfigs().filter(ChartConfig.id==subview.chartconfig_id).first()
        canvas = chartjs.Canvas('chart{0}'.format(subview.id), width, height)
        options = chartjs.Options(float(category.min_value), float(category.max_value))
        chart_builder = chartjs.ChartBuilder(chartconfig.type, options)
        chart = chartjs.Chart(canvas, 'ctx{0}'.format(subview.id), chart_builder)
        chart_builder.create_dataset(category.name)
        charts.append(chart.to_dict())
    return render_template('charts.html.j2', charts=charts)

@api.route('/charts/<view_id>/refresh', methods=['GET'])
def refresh_charts(view_id):
    view = all_views().filter(View.id==view_id).first()
    if view is None or len(request.args) != view.number_of_subviews():
        abort(400)
    refresh_data = {}
    for subview in view.subviews:
        last_index = int(request.args.get('chart{0}'.format(subview.id)))
        datas_since_index = all_sensors().filter(Sensor.id==subview.sensor_id).first().datas[last_index:]
        refresh_data['chart{0}'.format(subview.id)] = [data.to_dict() for data in datas_since_index]
    return jsonify(refresh_data)
