import redis
import jarvis

redis_instance = redis.StrictRedis(host=jarvis.MEMORY_HOST, port=jarvis.MEMORY_PORT, db=0)


def fetch_uri(uri):
    return "MemoryError: Jarvis Memory not implemented"


def read(key):
    return redis_instance.get(key)


def write(key, value):
    redis_instance.set(key, value)
