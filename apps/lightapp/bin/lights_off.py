#!/usr/bin/env python

import argparse
import state_pb2
from jarvis.state.client import query, update
import jarvis.speech.synthesis as synthesis

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
