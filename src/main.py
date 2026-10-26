"""Run the exporter with optional dummy increments every five seconds."""

import argparse
import signal
from threading import Event, Thread

from counters import Counters
from exporter import create_server


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dummy", action="store_true",
        help="also increment both counters every five seconds",
    )
    args = parser.parse_args(argv)
    stop = Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())

    counters = Counters()
    server = create_server(counters)
    worker = Thread(target=server.serve_forever, name="metrics-http")
    worker.start()
    print("Metrics listening on port 9009: /metrics", flush=True)
    try:
        if args.dummy:
            while not stop.wait(5):
                counters.increment_sent()
                counters.increment_processed()
        else:
            stop.wait()
    finally:
        server.shutdown()
        server.server_close()
        worker.join()


if __name__ == "__main__":
    main()
