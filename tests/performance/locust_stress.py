"""
Locust stress profile for finding degradation/breaking points.

Run:
    locust -f tests/performance/locust_stress.py --host http://127.0.0.1:8000
"""

import random

from locust import HttpUser, LoadTestShape, between, events, task


class EcommerceStressUser(HttpUser):
    """Simulates more aggressive traffic with short think time."""

    wait_time = between(0.05, 0.4)

    @task(1)
    def root(self):
        self.client.get("/", name="GET /")

    @task(2)
    def health(self):
        self.client.get("/api/v1/health", name="GET /api/v1/health")

    @task(6)
    def list_products(self):
        params = {"skip": random.randint(0, 100), "limit": 50}
        self.client.get("/api/v1/products/", params=params, name="GET /api/v1/products/")

    @task(4)
    def search_products(self):
        query = random.choice(["sale", "new", "gaming", "usb", "ssd"])
        params = {"q": query, "skip": random.randint(0, 10), "limit": 20}
        self.client.get("/api/v1/products/search", params=params, name="GET /api/v1/products/search")


class StressProfileShape(LoadTestShape):
    """
    Step-up stress profile:
    progressively increase concurrent users to expose saturation limits.
    """

    stages = [
        {"duration": 60, "users": 50, "spawn_rate": 20},    # 0-1m
        {"duration": 120, "users": 120, "spawn_rate": 30},  # 1-2m
        {"duration": 180, "users": 220, "spawn_rate": 40},  # 2-3m
        {"duration": 240, "users": 320, "spawn_rate": 50},  # 3-4m
        {"duration": 300, "users": 450, "spawn_rate": 60},  # 4-5m
        {"duration": 360, "users": 600, "spawn_rate": 70},  # 5-6m
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
    Stress threshold:
    accept some degradation, but fail when service health drops too far.
    """
    stats = environment.stats.total

    p99 = stats.get_response_time_percentile(0.99) or 0
    fail_ratio = stats.fail_ratio or 0

    if fail_ratio > 0.10:
        environment.process_exit_code = 1
    elif p99 > 2500:
        environment.process_exit_code = 1
    else:
        environment.process_exit_code = 0
