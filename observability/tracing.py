# observability/tracing.py

import time
from contextlib import contextmanager
from typing import Dict
from core.logger import log


class Tracer:
    def __init__(self):
        self.spans = []

    @contextmanager
    def span(self, name: str, attributes: Dict = None):
        start = time.time()
        span_id = f"span_{int(start * 1000)}_{hash(name) % 10000}"

        try:
            yield span_id

        finally:
            duration = time.time() - start

            span_data = {
                "name": name,
                "span_id": span_id,
                "duration": duration,
                "attributes": attributes or {}
            }

            self.spans.append(span_data)

            # aligned with your logger system
            log(f"[TRACE] {name} took {duration:.4f}s")
