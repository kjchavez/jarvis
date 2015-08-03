import urllib2
import common.protobuf


def get_type(data):
    raw_type = type(data)
    if raw_type in (str, unicode):
        if data[0:4] == 'uri:':
            return common.protobuf.URI
        else:
            return common.protobuf.STRING
    elif raw_type == int:
        return common.protobuf.INT
    elif raw_type == float:
        return common.protobuf.FLOAT
    else:
        raise TypeError("Unknown data type: " + str(raw_type) + " for " +
                str(data))


class Intent(object):
    def __init__(self, action, **params):
        self.message = common.protobuf.Intent()
        self.message.action = action
        for name, data in params.items():
            self.add_parameter(name, data)

    def add_parameter(self, name, data):
        param = self.message.parameter.add()
        param.name = name
        param.data = str(data)
        param.type = get_type(data)

    def serialize(self):
        return self.message.SerializeToString()

    @staticmethod
    def from_string(string):
        intent_msg = common.protobuf.Intent()
        intent_msg.ParseFromString(string)
        intent = Intent("")
        intent.message = intent_msg
        return intent


def fire_intent(intent, driver='127.0.0.1:5500'):
    """ Hit a particular endpoint with the intent. 
    
    Returns:
        boolean indicating whether or not intent was successfully
        handled.
    """
    message = intent.serialize()

    try:
        request = urllib2.Request(
                      'http://%s/intent' % driver,
                      headers={'Content-Type': 'application/jarvis'},
                      data=message)
        response = urllib2.urlopen(request).read()
        return True

    except urllib2.HTTPError as e:
        if e.code == 501:
            return False

    except urllib2.URLError as e:
        return False



def catch_intent(message):
    intent = common.protobuf.Intent()
    intent.ParseFromString(message)
    return intent


# A few utilities for common intents
def speak_intent(message):
    return Intent('jarvis.say', message=message)
