"""In-memory counters for one device."""

from prometheus_client import CollectorRegistry, Counter


class Counters:
    def __init__(self):
        self.registry = CollectorRegistry()
        self._counters = {}
        descriptions = {
            "sent": "Sound classification requests sent to other sensors",
            "processed": "Sound classification requests processed on this device",
        }
        for name, description in descriptions.items():
            self._counters[name] = Counter(
                f"app_requests_{name}_total", description, registry=self.registry
            )

    def increment_sent(self):
        self._counters["sent"].inc()

    def increment_processed(self):
        self._counters["processed"].inc()
