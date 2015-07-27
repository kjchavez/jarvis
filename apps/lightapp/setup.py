# Start up script, executed when jarvis boots up apps
import state_pb2
import sdk.state

state = state_pb2.State()

light = state.light.add()
light.location = 'kitchen'
light.is_on = False

sdk.state.update('lightapp', state)
