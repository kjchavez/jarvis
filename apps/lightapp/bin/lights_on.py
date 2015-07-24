#!/usr/bin/env python
import sys
import argparse
import state_pb2
from jarvis.state.client import query, update
import jarvis.speech.synthesis as synthesis

"""
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
parser = argparse.ArgumentParser()
parser.add_argument('--location', type=str, required=True)
args = parser.parse_args()

state = state_pb2.State()
query('lightapp', state)

for light in state.light:
    if light.location == args.location:
        light.is_on = True
        update('lightapp', state)
        synthesis.say("Turned on %s light" % args.location)
        break
else:
    synthesis.say("Couldn't find light in %s" % args.location)
