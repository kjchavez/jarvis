import os
import subprocess
import importlib
from flask import Flask, Response, request
import google.protobuf.text_format

import common.intent
from common.protobuf import Manifest


app = Flask(__name__)
action_routes = {}


class ActionRoute:
    def __init__(self, route, function):
        self.route = route
        self.function = function

    def execute(self, args):
        self.function(**args)


@app.route('/')
def index():
    return 'JARVIS router is up and running!'


@app.route('/intent', methods=['POST'])
def route_intent():
    global action_routes
    msg = request.data
    intent = common.intent.catch_intent(msg)
    best_route = find_match(intent, action_routes)
    if best_route is not None:
        execute(best_route, intent)
        response = Response("OK", status=200)
    else:
        response = Response("NO ROUTE", status=501)

    return response


def load_app_manifest(app_dir, global_routes):
    # Import the app module
    module = importlib.import_module('apps.%s' % app_dir)

    root = os.path.join(os.environ['JARVIS_ROOT'], 'apps')
    full_path = os.path.join(root, app_dir)

    manifest = Manifest()
    with open(os.path.join(full_path, 'manifest.prototxt')) as fp:
        google.protobuf.text_format.Merge(fp.read(), manifest)

    for route in manifest.route:
        function = module.__dict__[route.target]
        if route.action not in global_routes:
            global_routes[route.action] = []

        global_routes[route.action].append(ActionRoute(route, function))


def load_routes():
    global_routes = {}
    root = os.path.join(os.environ['JARVIS_ROOT'], 'apps')
    for app in os.listdir(root):
        if os.path.isdir(os.path.join(root, app)):
            load_app_manifest(app, global_routes)

    return global_routes


def find_match(intent, routes):
    best_candidate = None
    if intent.action not in routes:
        return None

    intent_params = set(param.name for param in intent.parameter)
    print "Intent Parameters:", intent_params
    candidates = routes[intent.action]
    for action_route in candidates:
        for param_name in action_route.route.req_parameter:
            if param_name not in intent_params:
                print param_name, "not found."
                break
        else:
            best_candidate = action_route

    return best_candidate


def execute(route, intent):
    """ Executes the action specified by the route, with given intent."""
    args = {}
    # [route.target]
    for param in intent.parameter:
        args[param.name] = param.data

    route.execute(args)

if __name__ == '__main__':
    # Load inverted index of actions to routes
    action_routes = load_routes()
    print action_routes
    app.run(debug=True, port=5500)
