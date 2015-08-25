from flask import jsonify
from . import api


@api.app_errorhandler(404)
def page_not_found(e):
    return jsonify({'message': e}), 404


@api.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({'message': e}), 500
