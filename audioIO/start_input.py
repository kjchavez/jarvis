import argparse
import SocketServer
import audio


# Audio stream ready to respond to requests
passive_audio_in = audio.PassiveAudioInputStream()

# Audio stream listening for key-phrase
active_audio_in = audio.ActiveAudioInputStream()


class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        passive_audio_in.start_listening()
        utt = passive_audio_in.get_latest_utterance()
        self.request.sendall(utt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default='127.0.0.1')
    parser.add_argument("--port", type=int, default=9999)

    args = parser.parse_args()

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((args.host, args.port), RequestHandler)
    passive_audio_in.start()
    active_audio_in.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
