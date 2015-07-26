import google.protobuf.text_format
import conf_pb2

config = conf_pb2.Jarvis()
with open('conf.prototxt') as fp:
    google.protobuf.text_format.Merge(fp.read(), config)

