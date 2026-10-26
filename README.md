# Application metrics prototype

A Python Prometheus exporter for one InnoRenew device per container.
Both counters start at zero and increase through HTTP POST calls.
Scraping does not change them. Values are stored in memory and reset on restart.

All counters share one Prometheus registry and are exposed at `/metrics`:

- `app_requests_sent_total`
- `app_requests_processed_total`

`counters.py` owns the counters and their increment methods. `exporter.py`
serves and increments them over HTTP. `main.py` connects both and optionally
runs dummy increments. Creation timestamps are disabled.

## Run locally

Use Python 3.12 or newer:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/main.py
```

Add `--dummy` to increment both counters by one every five seconds:

```sh
.venv/bin/python src/main.py --dummy
```

HTTP increments are available in both modes and add to dummy increments.

## Run with Docker

```sh
docker build -t app-metrics:prototype .
docker run --rm --name app-metrics -p 9009:9009 app-metrics:prototype
```

For dummy mode:

```sh
docker run --rm --name app-metrics -p 9009:9009 app-metrics:prototype --dummy
```

Stop with Ctrl+C, or `docker stop app-metrics` from another terminal.

## Increment and read metrics

Each POST adds one to its corresponding counter and returns `204 No Content`.
No request body is needed:

```sh
curl -X POST http://localhost:9009/sent
curl -X POST http://localhost:9009/processed
```

Repeated requests each count separately; retries are not deduplicated.
GET requests to `/sent` or `/processed` return `405 Method Not Allowed`.
POST requests to `/metrics` also return `405`; unknown paths return `404`.

Read both counters without changing them:

```sh
curl http://localhost:9009/metrics
```

The SAT uses port 9009 and `/metrics` for both collectors, selecting each
counter by its metric name. Set its `app-metrics`
image reference to your published container image before deploying.
Monitoring identifies each device through its scrape target.

The dummy five-second increments are independent of the SAT's ten-second
collection interval. Window aggregation is performed by monitoring, not this
service. The draft SAT's `MAX - MIN` calculation does not handle counter resets
and measures only between the first and last samples in the window.

## Tests

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```
