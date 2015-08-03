import os
import google.protobuf.text_format
import conf_pb2

config = conf_pb2.JarvisConf()

if 'JARVIS_ROOT' not in os.environ:
    raise ImportError('Environment variable JARVIS_ROOT not set')

root = os.environ['JARVIS_ROOT']
with open(os.path.join(root, 'config/conf.prototxt')) as fp:
    google.protobuf.text_format.Merge(fp.read(), config)

