#!/usr/bin/env python
import sys
import state_pb2
from jarvis.state.client import query, update
import jarvis.speech.synthesis as synthesis

if len(sys.argv) != 2:
    print "Usage: lights_off.py <location>"
    sys.exit(1)

location = sys.argv[1]

state = state_pb2.State()
query('lightapp', state)

for light in state.light:
    if light.location == location:
        light.is_on = True
        update('lightapp', state)
        synthesis.say("Turned on %s light" % location)
        break
else:
    synthesis.say("Couldn't find light in %s" % location)
