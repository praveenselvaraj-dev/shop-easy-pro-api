import redis
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def cache_set(key: str, value, ttl: int = 300):
    redis_client.set(key, json.dumps(value), ex=ttl)


def cache_get(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None


def cache_delete(key: str):
    redis_client.delete(key)
