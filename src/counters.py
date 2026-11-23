"""In-memory request counter for one device."""

from prometheus_client import CollectorRegistry, Counter


class Counters:
    def __init__(self):
        self.registry = CollectorRegistry()
        self._sent = Counter(
            "app_requests_sent_total",
            "Sound classification requests sent to other sensors",
            registry=self.registry,
        )

    def increment_sent(self):
        self._sent.inc()
