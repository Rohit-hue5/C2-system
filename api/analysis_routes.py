from flask import Blueprint, jsonify, request
from analysis import analyzer, scoring, cache
import time

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/analysis/analyze', methods=['POST'])
def analyze_sample():
    data = request.json
    sample_hash = data.get('hash')

    if cache.is_cached(sample_hash):
        return jsonify(cache.get_analysis(sample_hash))

    result = analyzer.analyze(sample_hash)
    score = scoring.score_analysis(result)

    response = {
        'hash': sample_hash,
        'score': score,
        'details': result,
        'timestamp': time.time()
    }

    cache.store(sample_hash, response)

    return jsonify(response)
