# flask_server.py
from flask import Flask, send_file, request, Response
from flask_cors import CORS

import os
from post_flask_actions import post_action
from get_flask_actions import get_action

# Configurate application
app = Flask(__name__)
CORS(app)  # Enable CORS

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:8001')

@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def plugin_manifest():
    host = request.headers['Host']
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route('/', defaults={'path': ''}, methods=['GET'])
@app.route('/<path:path>', methods=['GET'])
def catch_all_get(path):
    # Überprüfen Sie, ob der Pfad mit '.json' endet und fügen Sie es hinzu, wenn nicht
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = get_action(request, path, MEMORY_HOST)
    response = app.response_class(
        response_content,
        status=status_code,
        headers=headers,
        mimetype='application/json'
    )

    return response

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def catch_all_post(path):
    # Überprüfen Sie, ob der Pfad mit '.json' endet und fügen Sie es hinzu, wenn nicht
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = post_action(request, path, MEMORY_HOST)
    response = app.response_class(
        response_content,
        status=status_code,
        headers=headers,
        mimetype='application/json'
    )

    return response

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5005)
