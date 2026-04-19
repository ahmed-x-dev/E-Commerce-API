# app/core/redis.py
import redis
from app.core.config import settings

# Create a single, shared connection pool for the whole app
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True # Best practice so Redis returns strings instead of bytes
)

def get_redis_client():
    return redis_client
