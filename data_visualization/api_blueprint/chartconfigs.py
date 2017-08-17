from flask import jsonify, abort

from . import api
from ..models import ChartConfig
from ..queries import query_all_chartconfigs, query_get_chartconfig_by_id

@api.route('/chartconfigs', methods=['GET'])
def get_chartconfigs():
    chartconfigs = query_all_chartconfigs()
    return jsonify({'chartconfigs': [chartconfig.to_dict() for chartconfig in chartconfigs]})

@api.route('/chartconfig/<id>', methods=['GET'])
def get_chartconfig(id):
    chartconfig = query_get_chartconfig_by_id(id)
    return jsonify(chartconfig.to_dict())
