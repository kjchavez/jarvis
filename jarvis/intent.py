import urllib2
import jarvis.protobuf
import jarvis.memory


def get_type(data):
    raw_type = type(data)
    if raw_type == str:
        if data[0:4] == 'URI:':
            return jarvis.protobuf.URI
        else:
            return jarvis.protobuf.STRING
    elif raw_type == int:
        return jarvis.protobuf.INT
    elif raw_type == float:
        return jarvis.protobuf.FLOAT
    else:
        raise TypeError("Unknown data type.")


class Intent(object):
    def __init__(self, action, **params):
        self.message = jarvis.protobuf.Intent()
        self.message.action = action
        for name, data in params.items():
            self.add_parameter(name, data)

    def add_parameter(self, name, data):
        param = self.message.parameter.add()
        param.name = name
        param.data = data
        param.type = get_type(data)

    def serialize(self):
        return self.message.SerializeToString()

    def get_params(self):
        """ Returns a dictionary of param names to data. """
        params = {}
        for param in self.message.parameter:
            if param.type != jarvis.protobuf.URI:
                params[param.name] = param.data
            else:
                # Fetch resource from URI
                params[param.name] = jarvis.memory.fetch_uri(param.data)

        return params


def fire_intent(intent, driver='127.0.0.1:5500'):
    """ Hit a particular endpoint with the intent. """
    message = intent.serialize()
    try:
        request = urllib2.Request(
                      'http://%s/intent' % driver,
                      headers={'Content-Type': 'application/jarvis'},
                      data=message)
        response = urllib2.urlopen(request).read()
        print response
    except urllib2.URLError as e:
        print e.message
        raise


def catch_intent(message):
    intent = jarvis.protobuf.Intent()
    intent.ParseFromString(message)
    return intent
