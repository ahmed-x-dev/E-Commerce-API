# Locust Performance Tests

These scenarios are implemented with Locust and should run against a live API instance.

## 1) Start the API

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 2) Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

## 3) Run load profile

```bash
locust -f tests/performance/locust_load.py --host http://127.0.0.1:8000
```

Headless example:

```bash
locust -f tests/performance/locust_load.py --host http://127.0.0.1:8000 --headless --run-time 9m
```

## 4) Run stress profile

```bash
locust -f tests/performance/locust_stress.py --host http://127.0.0.1:8000
```

Headless example:

```bash
locust -f tests/performance/locust_stress.py --host http://127.0.0.1:8000 --headless --run-time 6m
```

## CI behavior

Each profile sets a process exit code based on failure ratio and latency percentiles via Locust `events.quitting`.
