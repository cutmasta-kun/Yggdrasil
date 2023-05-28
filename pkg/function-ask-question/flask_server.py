# flask_server.py
from flask import Flask, request, Response
from flask_cors import CORS
from ask import validate_messages, send_request
import requests
import json
import logging
import os
import uuid

# Configurate application
logging.basicConfig(level=logging.WARNING)
app = Flask(__name__)
CORS(app)  # Enable CORS

AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    messages = data.get('messages', None)

    if not validate_messages(messages):
        return 'Invalid messages', 400

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    response, error, status_code = send_request(messages, headers, AI_MODEL)

    if error:
        return error, status_code

    return response, status_code

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5022)
