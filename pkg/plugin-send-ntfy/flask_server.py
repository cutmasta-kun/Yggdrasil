# main.py
from flask import Flask, send_file, request, Response, jsonify, abort
from flask_cors import CORS
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS

# Define constants
NTFY_HOST = os.environ.get('NTFY_HOST', "https://ntfy.sh")
TOPIC = os.environ.get('TOPIC', "mytopic")

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

@app.route("/send", methods=['POST'])
def send_notification():
    data = request.get_json()
    if data is None or 'message' not in data:
        abort(400, description="Bad Request: 'message' is required.")
    message = data['message']
    # Send the notification
    response = requests.post(f"{NTFY_HOST}/{TOPIC}", data=message.encode(encoding='utf-8'))
    if response.status_code != 200:
        abort(response.status_code, description="Failed to send notification: " + response.text)
    return jsonify({'status': 'success', 'message': message}), 200

def main():
    app.run(debug=False, host="0.0.0.0", port=5003)

if __name__ == "__main__":
    main()
