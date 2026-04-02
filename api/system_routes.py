from flask import Blueprint, jsonify
from core import scheduler, state, security
from observability import metrics

system_bp = Blueprint('system', __name__, url_prefix='/api/system')

@system_bp.route('/jobs')
@security.require_auth
def list_jobs():
    return jsonify(scheduler.get_jobs())

@system_bp.route('/metrics')
def prometheus_metrics():
    from prometheus_client import generate_latest
    return generate_latest()

@system_bp.route('/debug')
@security.require_auth
def debug_info():
    return jsonify({
        'redis': state.redis_client.ping(),
        'agents': state.agent_stats(),
        'jobs': len(scheduler.jobs),
        'memory': state.get('system:memory_usage', 0)
    })
