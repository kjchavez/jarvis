import sdk
import socket

def say(message, stream_idx=0):
    """ Global access point to jarvis speech output. """
    if len(jarvis.audio_out) > stream_idx:
        jarvis.audio_out[stream_idx].say(message)
    else:
        print "[OUTPUT %d]: %s" % (stream_idx, message)


def capture(stream_idx=0):
    """Listen to input stream for next utterance. """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = sdk.config.audio_input[stream_idx].host
    port = sdk.config.audio_input[stream_idx].port
    try:
        # Connect to server and send data
        sock.connect((host, port))
        sock.sendall("\n")
        # Receive data from the server and shut down
        received = sock.recv(1024)
    finally:
        sock.close()

    return received
