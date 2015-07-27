#!/usr/bin/env python
import sys
import argparse
import state_pb2
import sdk.speech
import sdk.state

parser = argparse.ArgumentParser()
parser.add_argument('--location', type=str)
args = parser.parse_args()

state = state_pb2.State()
sdk.state.load('lightapp', state)

if not args.location:
    resolved_location = sdk.speech.inquire('location', query="Which lights?")
    if resolved_location is None:
        sdk.speech.say("I don't know which lights to turn off.")
        sys.exit(0)
    else:
        args.location = resolved_location

for light in state.light:
    if light.location == args.location:
        light.is_on = False
        sdk.state.update('lightapp', state)
        sdk.speech.say("Turned off %s light" % args.location)
        break
else:
    sdk.speech.say("Couldn't find light in %s" % args.location)
