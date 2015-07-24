from flask import Flask, Response, request
import jarvis.intent

app = Flask(__name__)


@app.route('/')
def index():
    return 'JARVIS router is up and running!'


@app.route('/intent', methods=['POST'])
def route_intent():
    msg = request.data
    intent = jarvis.intent.catch_intent(msg)
    print intent
    response = Response("", status=200)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5500)
