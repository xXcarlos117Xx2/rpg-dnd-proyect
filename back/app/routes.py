from flask import Blueprint, jsonify

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong"})
