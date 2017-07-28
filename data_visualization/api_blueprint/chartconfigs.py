from flask import jsonify, abort

from . import api
from ..models import ChartConfig
from ..queries import all_chartconfigs

@api.route('/chartconfigs', methods=['GET'])
def get_chartconfigs():
    chartconfigs = all_chartconfigs().order_by(ChartConfig.id).all()
    return jsonify({'chartconfigs': [chartconfig.to_dict() for chartconfig in chartconfigs]})

@api.route('/chartconfig/<id>', methods=['GET'])
def get_chartconfig(id):
    chartconfig = all_chartconfigs().filter(ChartConfig.id==id).first()
    if chartconfig is None:
        abort(400)
    return jsonify(chartconfig.to_dict())
