#!/usr/bin/env python
import sys
import state_pb2
from jarvis.state.client import query, update
import jarvis.speech.synthesis as synthesis

"""
Example intent:
{
  "id": "7ff9c35a-3dd5-4eba-a811-0eaaf5319edd",
  "timestamp": "2015-07-23T15:41:36.722Z",
  "result": {
    "source": "domains",
    "resolvedQuery": "jarvis turn on the lights",
    "action": "smarthome.lights_on",
    "metadata": {},
    "fulfillment": {
      "speech": ""
    }
  },
  "status": {
    "code": 200,
    "errorType": "success"
  }
}

{
  "id": "da26c75a-3489-4ee3-bea8-ce60c83e2fc7",
  "timestamp": "2015-07-23T19:50:26.33Z",
  "result": {
    "source": "domains",
    "resolvedQuery": "turn on the kitchen lights",
    "action": "smarthome.lights_on",
    "parameters": {
      "location": "kitchen"
    },
    "metadata": {},
    "fulfillment": {
      "speech": ""
    }
  },
  "status": {
    "code": 200,
    "errorType": "success"
  }
}
"""

if len(sys.argv) != 2:
    print "Usage: lights_on.py <location>"
    sys.exit(1)

location = sys.argv[1]

state_string = query('lightapp')
state = state_pb2.State()
light = state.light.add()
light.is_on = True
print state
if state_string:
    state.ParseFromString(query('lightapp'))

for light in state.light:
    if light.location == location:
        light.is_on = True
        update('lightapp', state)
        synthesis.say("Turned on %s light" % location)
        break
else:
    synthesis.say("Couldn't find light in %s" % location)
