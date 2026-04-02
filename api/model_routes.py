from flask import Blueprint, jsonify, request
from models import trainer, predictor
from pipelines.training_pipeline import run_training_pipeline	
from pipelines.evaluation_pipeline import run_evaluation
from core import security
import threading
import time

model_bp = Blueprint('models', __name__, url_prefix='/api/models')


# ─────────────────────────────
# 🚀 START TRAINING
# ─────────────────────────────
@model_bp.route('/train', methods=['POST'])
@security.require_auth
def start_training():
    """Start model training (async)"""
    config = request.json or {}

    def training_job():
        print("[+] Training job started")
        run_training_pipeline(config)
        print("[+] Training job finished")

    thread = threading.Thread(target=training_job)
    thread.start()

    return jsonify({
        'status': 'started',
        'message': 'Training started in background'
    })


# ─────────────────────────────
# 📊 TRAINING STATUS (OPTIONAL)
# ─────────────────────────────
@model_bp.route('/status/<task_id>')
@security.require_auth
def training_status(task_id):
    """Get training status"""
    status = trainer.get_status(task_id)
    return jsonify(status)


# ─────────────────────────────
# 🤖 PREDICTION
# ─────────────────────────────
@model_bp.route('/predict', methods=['POST'])
@security.require_auth
def predict_action():
    """Get model prediction"""
    telemetry = request.json

    action, confidence = predictor.predict(telemetry)

    return jsonify({
        'action': action,
        'confidence': confidence,
        'timestamp': time.time()
    })


# ─────────────────────────────
# 🧪 EVALUATION
# ─────────────────────────────
@model_bp.route('/evaluate', methods=['POST'])
@security.require_auth
def evaluate_model():
    """Run evaluation"""
    try:
        result = run_evaluation()

        return jsonify({
            'status': 'success',
            'result': result
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
