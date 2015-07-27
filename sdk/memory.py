import redis
import sdk

host = sdk.config.memory.host
port = sdk.config.memory.port
redis_instance = redis.StrictRedis(host=host, port=port, db=0)


def fetch_uri(uri):
    if uri[0:4] == 'uri:':
        data = redis_instance.get(uri)
    else:
        data = None

    return data


def read(key):
    return redis_instance.get(key)


def write(key, value):
    redis_instance.set(key, value)
