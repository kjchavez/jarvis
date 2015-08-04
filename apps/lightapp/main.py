#!/usr/bin/env python
import sys
import argparse
import state_pb2
import sdk.speech
import sdk.state

state = state_pb2.State()
sdk.state.load('lightapp', state)

def get_location():
    return sdk.speech.inquire('location', query="Which lights?")


def turn_lights(new_state, location=None):
    if not location:
        location = get_location()

    if location is None:
        sdk.speech.say("I don't know which lights to turn %s." % new_state)
        return

    for light in state.light:
        if light.location == location:
            light.is_on = True
            sdk.state.update('lightapp', state)
            sdk.speech.say("Turned %s %s light" % (new_state, location))
            break
    else:
        sdk.speech.say("Couldn't find light in %s" % location)


# action
def lights_on(location=None):
    turn_lights("on", location=location)


# action
def lights_off(location=None):
    turn_lights("off", location=location)
