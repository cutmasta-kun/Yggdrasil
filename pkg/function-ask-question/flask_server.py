# flask_server.py
from flask import Flask, request, Response
from flask_cors import CORS
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
    messages = data.get('messages', [])

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    data = {
        'model': AI_MODEL,
        'messages': messages
    }

    logging.debug(data)

    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))

    logging.debug(response)

    if response.status_code == 200:
        return response.json(), 200
    else:
        return 'Error', 400

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5022)
