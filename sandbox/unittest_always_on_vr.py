""" Always On Voice Recognition Test. """
import os
import pyaudio
from listener import Listener
from srnlp import APIAI, PocketSphinx

pa = pyaudio.PyAudio()


def callback():
    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 0.25, 1000))
    intent = APIAI.capture_and_process(pa)
    print intent

listener = Listener(pa, "jarvis", callback=callback)
listener.start()
pa.terminate()
