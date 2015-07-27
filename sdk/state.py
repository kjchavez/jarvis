import redis
import os
import sdk

r = redis.StrictRedis(host=sdk.config.state.host,
                      port=sdk.config.state.port, db=0)

def load(appname, state):
    msg_str = r.get(appname)
    state.ParseFromString(msg_str)

def update(appname, new_state):
    msg_str = state.SerializeToString()
    r.set(appname, msg_str)
