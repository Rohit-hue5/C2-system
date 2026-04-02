from flask import Blueprint, request, jsonify
from core import security, state, logger
from telemetry import collector, parser, dispatcher
from api.middleware import validate_json

telemetry_bp = Blueprint('telemetry', __name__, url_prefix='/api/telemetry')

@telemetry_bp.route('/ingest', methods=['POST'])
@validate_json()
def ingest_telemetry():
    """Ingest raw telemetry data"""
    data = request.json
    
    # Verify signature
    signature = data.get('signature')
    timestamp = data.get('timestamp')
    payload = str(data.get('payload', '')).encode()
    
    if not security.verify_signature(payload, signature, timestamp):
        raise exceptions.SecurityError("Invalid signature")
    
    # Parse and dispatch
    parsed = parser.parse_telemetry(data)
    collector.collect(parsed)
    dispatcher.dispatch(parsed)
    
    state.increment('telemetry:events:total')
    
    return jsonify({'status': 'received', 'id': parsed['id']})

@telemetry_bp.route('/stream')
def stream_telemetry():
    """Get recent telemetry stream"""
    since = request.args.get('since', 0, type=int)
    telemetry = collector.get_recent(since)
    return jsonify({'telemetry': telemetry})
