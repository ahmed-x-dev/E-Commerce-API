# app/security/rate_limit.py
from datetime import datetime, timezone
from fastapi import HTTPException, Request, status
from app.core.redis import redis_client

class RateLimiter:
    def __init__(self, key_prefix: str, max_requests: int, window_seconds: int):
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    
    def __call__(self, request: Request):
        # Handle reverse proxy IPs (Standard Best Practice)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host

        key = f"rate:{self.key_prefix}:{client_ip}"
        now = datetime.now(timezone.utc).timestamp()
        window_start = now - self.window_seconds


        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(now): now})
        pipe.expire(key, self.window_seconds)
        results = pipe.execute()

        request_count = results[1]
        
        if request_count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": str(self.window_seconds)}
            )