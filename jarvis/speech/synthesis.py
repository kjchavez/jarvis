import subprocess

def say(utterance):
    subprocess.call(['espeak', '"%s"' % utterance])
