""" Unit test for intents. """
from jarvis.intent import *
import jarvis.memory
from urllib2 import URLError

intent = Intent('smarthome.lights_on',
                location='kitchen',
                person='URI:person/kjchavez')

params = intent.get_params()
assert(params['location'] == 'kitchen')
assert(params['person'] == jarvis.memory.fetch_uri('URI:person/kjchavez'))

try:
    fire_intent(intent)
except URLError:
    pass
except:
    raise AssertionError("fire_intent failed.")

print "All tests passed."
