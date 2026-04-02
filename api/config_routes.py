from flask import Blueprint, jsonify, request

config_bp = Blueprint('config', __name__)

CONFIG = {}

@config_bp.route('/config/get')
def get_config():
    return jsonify(CONFIG)

@config_bp.route('/config/update', methods=['POST'])
def update_config():
    data = request.json
    CONFIG.update(data)
    return jsonify({'status': 'updated', 'config': CONFIG})
