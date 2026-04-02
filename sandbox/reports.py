# sandbox/reports.py

from core.logger import log


def store_report(payload_id, detection_score, metadata):
    report = {
        "payload_id": payload_id,
        "detection_score": detection_score,
        "metadata": metadata
    }

    # SAFE STATE INTEGRATION
    try:
        from flask import current_app

        if hasattr(current_app, "state"):
            current_app.state.add_payload({
                "id": payload_id,
                "analysis": report
            })

    except Exception as e:
        log(f"State store error: {e}")

    log(f"Report stored for {payload_id}")

    return report


def format_report(report):
    return {
        "id": report["payload_id"],
        "detection": report["detection_score"],
        "entropy": report["metadata"].get("entropy"),
        "size": report["metadata"].get("size")
    }
