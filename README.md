# Application metrics prototype

A Python Prometheus exporter for one InnoRenew device per container.
It exposes `app_requests_sent_total` at `/metrics` to count sound classification
requests sent to other sensors. The counter starts at zero, stays in memory,
and resets on restart. Scraping leaves its value unchanged.
Creation timestamps are disabled.

## Run locally

Use Python 3.12 or newer:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/main.py
```

Add `--dummy` to increment the sent counter by one every five seconds:

```sh
.venv/bin/python src/main.py --dummy
```

HTTP increments are available in both modes and add to dummy increments.

## Run with Docker

```sh
docker build -t app-metrics:latest .
docker run --rm --name app-metrics -p 9009:9009 app-metrics:latest
```

For dummy mode:

```sh
docker run --rm --name app-metrics -p 9009:9009 app-metrics:latest --dummy
```


## Run with Docker Compose

Example of the docker compose in --dummy mode.

```yaml
services:
  app-metrics:
    build: .
    image: app-metrics:latest
    command: ["--dummy"]
    ports:
      - "9009:9009"
```

Start it with `docker compose up --build`. The counter increments every five
seconds, and you can read it at `http://localhost:9009/metrics`. Stop with Ctrl+C
and remove the container with `docker compose down`.

## Increment and read metrics

Each POST to `/sent` adds one to the sent counter and returns `204 No Content`.
No request body is needed:

```sh
curl -X POST http://localhost:9009/sent
```

Repeated requests each count separately; retries are not deduplicated.
GET requests to `/sent` return `405 Method Not Allowed`.
POST requests to `/metrics` also return `405`; unknown paths return `404`.

Read the current count:

```sh
curl http://localhost:9009/metrics
```


