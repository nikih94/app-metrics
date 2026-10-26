"""HTTP exposure and increment endpoints for the shared counters."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from prometheus_client import CONTENT_TYPE_LATEST, disable_created_metrics, generate_latest

from counters import Counters

disable_created_metrics()


def create_server(counters: Counters, host="0.0.0.0", port=9009):
    increments = {
        "/sent": counters.increment_sent,
        "/processed": counters.increment_processed,
    }

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path in increments:
                self.method_not_allowed("POST")
                return
            if path != "/metrics":
                self.send_error(404, "Unknown endpoint")
                return

            body = generate_latest(counters.registry)
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path == "/metrics":
                self.method_not_allowed("GET")
                return
            increment = increments.get(path)
            if increment is None:
                self.send_error(404, "Unknown endpoint")
                return

            increment()
            self.send_response(204)
            self.end_headers()

        def method_not_allowed(self, allowed):
            self.send_response(405)
            self.send_header("Allow", allowed)
            self.send_header("Content-Length", "0")
            self.end_headers()

        # do not log every request
        def log_message(self, format, *args):
            pass

    return ThreadingHTTPServer((host, port), Handler)
