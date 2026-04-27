"""
Locust load profile for normal sustained traffic.

Run:
    locust -f tests/performance/locust_load.py --host http://127.0.0.1:8000
"""

import random

from locust import HttpUser, LoadTestShape, between, events, task


class EcommerceLoadUser(HttpUser):
    """
    Simulates normal browsing behavior.
    Uses unauthenticated endpoints so load tests are easy to run in any env.
    """

    wait_time = between(0.2, 1.2)

    @task(2)
    def root(self):
        self.client.get("/", name="GET /")

    @task(2)
    def health(self):
        self.client.get("/api/v1/health", name="GET /api/v1/health")

    @task(5)
    def list_products(self):
        params = {"skip": random.randint(0, 20), "limit": 20}
        self.client.get("/api/v1/products/", params=params, name="GET /api/v1/products/")

    @task(3)
    def search_products(self):
        query = random.choice(["phone", "laptop", "keyboard", "mouse", "monitor"])
        params = {"q": query, "skip": 0, "limit": 10}
        self.client.get("/api/v1/products/search", params=params, name="GET /api/v1/products/search")


class LoadProfileShape(LoadTestShape):
    """
    Steady load profile:
    1. Warm up
    2. Ramp to target
    3. Hold stable traffic
    """

    stages = [
        {"duration": 60, "users": 20, "spawn_rate": 5},    # 0-1m
        {"duration": 180, "users": 80, "spawn_rate": 10},  # 1-3m
        {"duration": 420, "users": 80, "spawn_rate": 5},   # 3-7m hold
        {"duration": 540, "users": 30, "spawn_rate": 10},  # 7-9m cool-down
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]
        return None


@events.quitting.add_listener
def _(environment, **kwargs):
    """
    CI-friendly gate:
    fail process if error ratio or latency is too high during load profile.
    """
    stats = environment.stats.total

    # Locust uses float percentile values in [0, 1].
    p95 = stats.get_response_time_percentile(0.95) or 0
    fail_ratio = stats.fail_ratio or 0

    if fail_ratio > 0.02:
        environment.process_exit_code = 1
    elif p95 > 800:
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0
