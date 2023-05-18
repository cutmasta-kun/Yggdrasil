# flask_server.py
from flask import Flask, send_file, request, Response
from flask_cors import CORS
import requests
import json
import logging

# Configurate application
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS

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

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    response = requests.request(
        method=request.method,
        url=f"http://memory:8001/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        allow_redirects=False)

    headers = []
    headers.append(('Transfer-Encoding', 'identity'))  # Disable chunked transfer encoding

    response = app.response_class(response.content, response.status_code, headers)
    logging.info(response)
    return response

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5005)
