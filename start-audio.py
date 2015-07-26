import SocketServer
from jarvis.audio import *

audio_in = PassiveAudioInputStream()
audio_in2 = ActiveAudioInputStream()


class RequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        print "Handle triggered"
        audio_in.start_listening()
        utt = audio_in.get_latest_utterance()
        self.request.sendall(utt)


if __name__ == "__main__":
    HOST, PORT = '127.0.0.1', 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), RequestHandler)
    audio_in.start()
    audio_in2.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
