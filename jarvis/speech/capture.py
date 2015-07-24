import time
import atexit
import pocketsphinx
import pyaudio
from jarvis.speech.srnlp import PocketSphinx

class Borg:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class JarvisAudio(Borg):
    def __init__(self):
        Borg.__init__(self)

        if not hasattr(self, 'pyaudio'):
            self.pyaudio = pyaudio.PyAudio()


@atexit.register
def terminate_audio():
    aud = JarvisAudio()
    aud.pyaudio.terminate()


def listen_for(keyphrase,
               callback=None,
               threshold=1e-30,
               hmm="/usr/local/share/pocketsphinx/model/en-us/en-us",
               dic="/usr/local/share/pocketsphinx/model/en-us/cmudict-en-us.dict",
               timeout=None):

        # Create a decoder with certain model
        config = pocketsphinx.Decoder.default_config()
        config.set_string('-hmm', hmm)
        config.set_string('-dict', dic)
        config.set_string('-keyphrase', keyphrase)
        config.set_float('-kws_threshold', threshold)

        decoder = pocketsphinx.Decoder(config)
        pa = JarvisAudio().pyaudio

        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        decoder.start_utt()

        # Create stream
        stream = pa.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         output=False,
                         frames_per_buffer=CHUNK)

        start_time = time.time()
        while True:
            if timeout is not None and (time.time() - start_time) > timeout:
                break

            buf = stream.read(CHUNK)
            if not buf:
                break

            decoder.process_raw(buf, False, False)
            if decoder.hyp() is not None and \
               decoder.hyp().hypstr == keyphrase:
                decoder.end_utt()
                stream.stop_stream()
                if callback is not None:
                    callback()
                decoder.start_utt()
                stream.start_stream()


def capture_utterance():
    utt = PocketSphinx.capture_and_process(JarvisAudio().pyaudio)
    return utt
