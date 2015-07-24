import os
import json
import pyaudio
from urllib2 import URLError

import jarvis.speech
from jarvis.speech.srnlp import APIAI
from jarvis.intent import Intent, fire_intent

pa = pyaudio.PyAudio()


def callback():
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 0.25, 1000))
    apiai_intent = json.loads(APIAI.capture_and_process(pa,timeout=2))
    result = apiai_intent['result']

    print "Jarvis heard: %s" % result['resolvedQuery']
    # Nothing understood
    if 'action' not in result:
        if 'resolvedQuery' in result:
            jarvis.speech.say("Sorry, I don't know what you mean by: %s" %
                result['resolvedQuery'])
        else:
            jarvis.speech.say("Sorry, I didn't get that.")
        return

    # If there's an immediate, verbal fulfillment, do that
    if 'fulfillment' in result and 'speech' in result['fulfillment']:
        speech = result['fulfillment']['speech']
        if speech:
            jarvis.speech.say(speech)
            return

    action = apiai_intent['result']['action']
    params = apiai_intent['result'].get('parameters', {})
    #try:
    intent = Intent(action, **params)
    #except:
    #    say("Sorry, I didn't get that.")
    #    return

    try:
        fire_intent(intent)
    except URLError:
        jarvis.speech.say("I can't do that right now.")


jarvis.speech.listen_for("jarvis", callback=callback)
