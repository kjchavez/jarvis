import os
import time
import pocketsphinx
import pyaudio


class Listener:
    def __init__(self, pa, keyphrase,
                 callback=None,
                 threshold=1e-30,
                 hmm="/usr/local/share/pocketsphinx/model/en-us/en-us",
                 dic="/usr/local/share/pocketsphinx/model/en-us/cmudict-en-us.dict"):

        # Create a decoder with certain model
        config = pocketsphinx.Decoder.default_config()
        config.set_string('-hmm', hmm)
        config.set_string('-dict', dic)
        config.set_string('-keyphrase', keyphrase)
        config.set_float('-kws_threshold', threshold)

        self.decoder = pocketsphinx.Decoder(config)
        self.pa = pa
        self.keyphrase = keyphrase
        if callback is not None:
            self.callback = callback
        else:
            self.callback = lambda x: "callback"

    def start(self, timeout=None):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        self.decoder.start_utt()

        # Create stream
        stream = self.pa.open(format=FORMAT,
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

            self.decoder.process_raw(buf, False, False)
            if self.decoder.hyp() is not None and \
               self.decoder.hyp().hypstr == self.keyphrase:
                self.decoder.end_utt()
                stream.stop_stream()
                self.callback()
                self.decoder.start_utt()
                stream.start_stream()
