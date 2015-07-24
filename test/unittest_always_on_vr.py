""" Always On Voice Recognition Test. """
import os
import pyaudio
import jarvis.speech
from jarvis.speech.srnlp import APIAI

pa = pyaudio.PyAudio()


def callback():
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 0.25, 1000))
    intent = APIAI.capture_and_process(pa)
    print intent

jarvis.speech.listen_for("jarvis", callback=callback)
