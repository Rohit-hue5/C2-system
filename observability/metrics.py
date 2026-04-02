# observability/metrics.py

from prometheus_client import Counter, Gauge, Histogram
import time


class Metrics:
    def __init__(self):
        self.agent_count = Gauge("c2lab_agents_total", "Total agents")
        self.active_agents = Gauge("c2lab_agents_active", "Active agents")
        self.telemetry_events = Counter("c2lab_telemetry_events_total", "Telemetry events")
        self.model_score = Gauge("c2lab_model_score", "Current model score")
        self.request_duration = Histogram("c2lab_request_duration_seconds", "Request duration")

    def init_app(self, app):
        app.metrics = self
        app.wsgi_app = MetricsMiddleware(app.wsgi_app, self)

    # ───────── HELPERS ─────────
    def increment_telemetry(self):
        self.telemetry_events.inc()

    def update_agent_count(self, count):
        self.agent_count.set(count)

    def update_model_score(self, score):
        self.model_score.set(score)


class MetricsMiddleware:
    def __init__(self, app, metrics):
        self.app = app
        self.metrics = metrics

    def __call__(self, environ, start_response):
        start_time = time.time()

        def metrics_start_response(status, headers, exc_info=None):
            try:
                self.metrics.request_duration.observe(time.time() - start_time)
            except Exception:
                pass
            return start_response(status, headers, exc_info)

        return self.app(environ, metrics_start_response)
