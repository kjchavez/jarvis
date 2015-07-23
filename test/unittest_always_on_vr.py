""" Always On Voice Recognition Test. """
import os
import pyaudio
from jarvis.speech.listener import Listener
from jarvis.speech.srnlp import APIAI, PocketSphinx

pa = pyaudio.PyAudio()


def callback():
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 0.25, 1000))
    intent = APIAI.capture_and_process(pa)
    print intent

listener = Listener(pa, "jarvis", callback=callback)
listener.start()
pa.terminate()
