# Tests Structure

This project uses a layered test layout to keep intent clear and test runs fast:

```text
tests/
  conftest.py                 # Shared unit-test fixtures
  unit/
    routers/                  # API route behavior tests
    security/                 # Auth/authorization dependency tests
  performance/
    locust_load.py            # Load profile (Locust)
    locust_stress.py          # Stress profile (Locust)
```

## How to run

- Run all default tests (unit and fast checks):

```bash
pytest
```

- Run only unit tests:

```bash
pytest tests/unit
```

- Run Locust load test:

```bash
locust -f tests/performance/locust_load.py --host http://127.0.0.1:8000
```

- Run Locust stress test:

```bash
locust -f tests/performance/locust_stress.py --host http://127.0.0.1:8000
```

## Notes

- Test fixtures in `tests/conftest.py` isolate tests from external dependencies such as PostgreSQL and Redis.
- Locust scenarios run against a live API server (for example: `uvicorn app.main:app --reload`).
