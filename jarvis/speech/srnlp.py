import os
import time
import numpy as np
import apiai
import pyaudio
import pocketsphinx
from pause import PauseDetector


class PocketSphinx:
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    MODELDIR = "/usr/local/share/pocketsphinx/model"
    config = pocketsphinx.Decoder.default_config()
    config.set_string('-hmm', os.path.join(MODELDIR, 'en-us/en-us'))
    config.set_string('-lm', os.path.join(MODELDIR, 'en-us/en-us.lm.bin'))
    config.set_string('-dict', os.path.join(MODELDIR, 'en-us/cmudict-en-us.dict'))
    decoder = pocketsphinx.Decoder(config)
    pause_detector = PauseDetector()

    # Decode streaming data.
    decoder = pocketsphinx.Decoder(config)

    @staticmethod
    def reset():
        PocketSphinx.pause_detector.reset()

    @staticmethod
    def capture_and_process(pa):
        PocketSphinx.reset()
        PocketSphinx.decoder.start_utt()
        stream = pa.open(format=PocketSphinx.FORMAT,
                         channels=PocketSphinx.CHANNELS,
                         rate=PocketSphinx.RATE,
                         input=True,
                         output=False,
                         frames_per_buffer=PocketSphinx.CHUNK)

        while True:
            buf = stream.read(PocketSphinx.CHUNK)

            # Check if utterance is over
            is_pause = PocketSphinx.pause_detector.process(buf, dtype=np.int16)
            if is_pause:
                print "Detected pause"
                break

            PocketSphinx.decoder.process_raw(buf, False, False)

        print "Done capturing."
        stream.stop_stream()
        stream.close()
        PocketSphinx.decoder.end_utt()
        return [seg.word for seg in PocketSphinx.decoder.seg()]


class APIAI:
    CHUNK = 512
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CLIENT_ACCESS_TOKEN = 'f720d62e62ef452a85525c816a4e5428'
    SUBSCRIBTION_KEY = '5f4a1f26-e151-4b7e-b97f-ce4a6c34b1f6'
    ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIBTION_KEY)
    pause_detector = PauseDetector()
    resampler = apiai.Resampler(source_samplerate=RATE)
    request = ai.voice_request()

    @staticmethod
    def callback(in_data, frame_count, time_info, status):
        frames, data = APIAI.resampler.resample(in_data, frame_count)
        is_pause = APIAI.pause_detector.process(data, dtype=np.int16)
        APIAI.request.send(data)

        if not is_pause:
            return in_data, pyaudio.paContinue
        else:
            return in_data, pyaudio.paComplete

    @staticmethod
    def reset():
        APIAI.pause_detector.reset()
        APIAI.request = APIAI.ai.voice_request()

    @staticmethod
    def capture_and_process(pa):
        # Using API.ai
        APIAI.reset()
        stream = pa.open(format=APIAI.FORMAT,
                         channels=APIAI.CHANNELS,
                         rate=APIAI.RATE,
                         input=True,
                         output=False,
                         frames_per_buffer=APIAI.CHUNK,
                         stream_callback=APIAI.callback)

        stream.start_stream()
        try:
            while stream.is_active():
                time.sleep(0.1)
        except Exception:
            raise e
        except KeyboardInterrupt:
            pass

        stream.stop_stream()
        stream.close()

        print ("Wait for response...")
        response = APIAI.request.getresponse()

        return response.read()
