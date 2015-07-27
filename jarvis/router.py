import os
import subprocess
from flask import Flask, Response, request
import google.protobuf.text_format

import jarvis.intent
from jarvis.protobuf import Manifest

app = Flask(__name__)
action_routes = {}


@app.route('/')
def index():
    return 'JARVIS router is up and running!'


@app.route('/intent', methods=['POST'])
def route_intent():
    global action_routes
    msg = request.data
    intent = jarvis.intent.catch_intent(msg)
    best_route = find_match(intent, action_routes)
    if best_route is not None:
        execute(best_route, intent)
        response = Response("OK", status=200)
    else:
        response = Response("NO ROUTE", status=501)

    return response


def load_app_manifest(app_dir, global_routes):
    manifest = Manifest()
    with open(os.path.join(app_dir, 'manifest.prototxt')) as fp:
        google.protobuf.text_format.Merge(fp.read(), manifest)

    for route in manifest.route:
        # Specify full path to executables
        prog = os.path.join(app_dir, os.path.join('bin', route.target))
        route.target = prog
        if route.action not in global_routes:
            global_routes[route.action] = []

        global_routes[route.action].append(route)


def load_routes():
    global_routes = {}
    root = os.path.join(os.environ['JARVIS_ROOT'], 'apps')
    for app in os.listdir(root):
        load_app_manifest(os.path.join(root, app), global_routes)

    return global_routes


def find_match(intent, routes):
    best_candidate = None
    if intent.action not in routes:
        return None

    intent_params = set(param.name for param in intent.parameter)
    print "Intent Parameters:", intent_params
    candidates = routes[intent.action]
    for route in candidates:
        for param_name in route.req_parameter:
            if param_name not in intent_params:
                print param_name, "not found."
                break
        else:
            best_candidate = route

    return best_candidate


def execute(route, intent):
    """ Executes the action specified by the route, with given intent."""
    args = [route.target]
    for param in intent.parameter:
        args.append("--%s" % param.name)
        args.append(r"%s" % str(param.data))

    subprocess.Popen(args)

if __name__ == '__main__':
    # Load inverted index of actions to routes
    action_routes = load_routes()
    print action_routes
    app.run(debug=True, port=5500)
