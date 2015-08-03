import argparse
import SocketServer
from audio import *

# Audio stream ready to respond to requests
passive_audio_in = PassiveAudioInputStream()

# Audio stream listening for key-phrase
active_audio_in = ActiveAudioInputStream()


class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        passive_audio_in.start_listening()
        utt = passive_audio_in.get_latest_utterance()
        self.request.sendall(utt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", '-h', default='127.0.0.1')
    parser.add_argument("--port", '-p', type=int, default=9999)

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((args.host, args.port), RequestHandler)
    passive_audio_in.start()
    active_audio_in.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()