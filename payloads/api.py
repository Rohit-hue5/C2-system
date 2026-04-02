from flask import Blueprint, jsonify, request
from payloads import manager
from core.security import require_auth

payload_bp = Blueprint('payloads', __name__, url_prefix='/api/payloads')


@payload_bp.route('/list')
@require_auth
def list_payloads():
    return jsonify({'payloads': manager.list_payloads()})


@payload_bp.route('/compile-all', methods=['POST'])
@require_auth
def compile_all():
    results = manager.compile_all()
    return jsonify({'results': results})


@payload_bp.route('/compile/<name>')
@require_auth
def compile_one(name):
    result = manager.compile_payload(name)
    return jsonify(result)


@payload_bp.route('/deploy', methods=['POST'])
@require_auth
def deploy():
    data = request.json or {}

    agent_id = data.get('agent_id')
    payload = data.get('payload')

    if not agent_id or not payload:
        return jsonify({'error': 'agent_id and payload required'}), 400

    task_id = manager.deploy(agent_id, payload)
    return jsonify({'task_id': task_id})
