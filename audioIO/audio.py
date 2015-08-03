import os
import time
import subprocess
import pyaudio
import atexit
import json
import pocketsphinx as ps
import apiai

# from pause import PauseDetector
from common.intent import *
import common.sayings
import sdk.speech

def initialize():
    """Initialize Jarvis' audio I/O module.

    Find all connected devices and register them with Jarvis as audio input
    or output streams.
    """
    assert(len(jarvis.audio_in) == 0)
    assert(len(jarvis.audio_out) == 0)

    # TODO: Auto search for connected devices
    jarvis.audio_in = [AudioInputStream()]
    jarvis.audio_out = [AudioOutputStream()]

    for ai in jarvis.audio_in:
        ai.start()

class AudioProcessor:
    def __init__(self):
        pass

    def process(self, in_data, frame_count, time_info, status):
        raise NotImplementedError("Override this.")


class APIaiProcessor(AudioProcessor):
    def __init__(self, audio_stream):
        CLIENT_ACCESS_TOKEN = 'f720d62e62ef452a85525c816a4e5428'
        SUBSCRIBTION_KEY = '5f4a1f26-e151-4b7e-b97f-ce4a6c34b1f6'
        self.ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN, SUBSCRIBTION_KEY)

        # self.pause_detector = PauseDetector()
        self.vad = apiai.VAD()
        self.resampler = apiai.Resampler(
                             source_samplerate=audio_stream.SAMPLE_RATE)
        self.request = self.ai.voice_request()

    def process(self, in_data, frame_count, time_info, status):
        frames, data = self.resampler.resample(in_data, frame_count)
        # is_pause = self.pause_detector.process(data, dtype='int16',
                                                #debug=True)
        state = self.vad.processFrame(frames)
        self.request.send(data)
        #if is_pause:
        if state != 1:
            return True
        else:
            return False

    def interpret(self):
        response = self.request.getresponse()
        apiai_intent = json.loads(response.read())
        result = apiai_intent['result']
        utterance = result.get('resolvedQuery', '')
        response = result['fulfillment']['speech']
        intent = None

        # For the API.ai engine, we only fire an intent if there is no
        # spoken fulfillment for the query
        if 'action' in result and not response:
            action = result['action']
            params = result.get('parameters', {})
            for key in params:
                print key, params[key], type(params[key])

            intent = Intent(action, **params)

        self.request = self.ai.voice_request()
        # self.pause_detector.reset()
        self.vad.reset()
        return utterance, response, intent


class KeyphraseListener(AudioProcessor):
    def __init__(self, audio_stream, keyphrase, threshold,
                 hmm="/usr/local/share/pocketsphinx/model/en-us/en-us",
                 dic="/usr/local/share/pocketsphinx/model/en-us/cmudict-en-us.dict"):
        self.keyphrase = keyphrase
        threshold = 1e-30
        config = ps.Decoder.default_config()
        config.set_string('-hmm', hmm)
        config.set_string('-dict', dic)
        config.set_string('-keyphrase', keyphrase)
        config.set_float('-kws_threshold', threshold)

        self.resampler = apiai.Resampler(
                             source_samplerate=audio_stream.SAMPLE_RATE)
        self.decoder = ps.Decoder(config)
        self.decoder.start_utt()

    def process(self, in_data, frame_count, time_info, status):
        frames, data = self.resampler.resample(in_data, frame_count)
        self.decoder.process_raw(data, False, False)
        if self.decoder.hyp() is not None and \
           self.decoder.hyp().hypstr == self.keyphrase:
            self.decoder.end_utt()
            self.decoder.start_utt()
            return True
        else:
            return False


class AudioInputStream:
    IDLE = 0
    LISTENING = 1
    PROCESSING = 2
    _audio = pyaudio.PyAudio()
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLE_RATE = 44100

    def __init__(self):
        self.state = AudioInputStream.IDLE

        self.stream = AudioInputStream._audio.open(
                     format=AudioInputStream.FORMAT,
                     channels=AudioInputStream.CHANNELS,
                     rate=AudioInputStream.SAMPLE_RATE,
                     input=True,
                     start=False,
                     stream_callback=self.process_audio)

    def process_audio(self, in_data, frame_count, time_info, status):
        raise NotImplementedError("Override this")

    def start(self):
        self.stream.start_stream()

    def stop(self):
        self.stream.stop_stream()

    def __del__(self):
        self.stream.close()


class ActiveAudioInputStream(AudioInputStream):
    def __init__(self):
        AudioInputStream.__init__(self)

        self.idle_processor = KeyphraseListener(self, "jarvis", 1e-30)
        self.listening_processor = APIaiProcessor(self)

    def process_audio(self, in_data, frame_count, time_info, status):
        if self.state == AudioInputStream.IDLE:
            # Listen for keyword to switch state
                triggered = self.idle_processor.process(
                                in_data,
                                frame_count,
                                time_info,
                                status)
                if triggered:
                    print "LISTENING..."
                    os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % ( 0.1, 1000))
                    self.state = AudioInputStream.LISTENING

        elif self.state == AudioInputStream.LISTENING:
            done = self.listening_processor.process(
                              in_data,
                              frame_count,
                              time_info,
                              status)

            if done:
                self.state = AudioInputStream.PROCESSING
                utt, reply, intent = self.listening_processor.interpret()
                self.latest_utt = utt
                self.state = AudioInputStream.IDLE

                # Then we trigger actions
                print "Jarvis IN << %s" % utt
                print "Jarvis OUT >> %s" % reply
                if reply:
                    sdk.speech.say(reply)

                if intent:
                    success = fire_intent(intent)
                    if not success:
                        sdk.speech.say(common.sayings.intent_failed())

        return in_data, pyaudio.paContinue


class PassiveAudioInputStream(AudioInputStream):
    def __init__(self):
        AudioInputStream.__init__(self)

        self.listening_processor = APIaiProcessor(self)
        self.latest_utt = ""

    def process_audio(self, in_data, frame_count, time_info, status):
        if self.state == AudioInputStream.IDLE:
            pass

        elif self.state == AudioInputStream.LISTENING:
            done = self.listening_processor.process(
                              in_data,
                              frame_count,
                              time_info,
                              status)

            if done:
                self.state = AudioInputStream.PROCESSING
                utt, reply, intent = self.listening_processor.interpret()
                self.latest_utt = utt
                self.state = AudioInputStream.IDLE

        return in_data, pyaudio.paContinue

    def get_latest_utterance(self):
        while self.state != AudioInputStream.IDLE:
            time.sleep(0.1)

        return self.latest_utt

    def start_listening(self):
        self.state = AudioInputStream.LISTENING


class AudioOutputStream:
    def __init__(self):
        pass

    def say(self, text):
        subprocess.Popen(['espeak', '"%s"' % text])

    def __del__(self):
        pass


if __name__ == "__main__":
    import time
    initialize()
    while True:
        time.sleep(30)
        print "<Jarvis Audio I/O status>"
