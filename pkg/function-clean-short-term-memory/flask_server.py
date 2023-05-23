# flask_server.py
from flask import Flask, request, Response
from flask_cors import CORS
import requests
import json
import logging
import uuid
import os

# Configurate application
logging.basicConfig(level=logging.WARNING)
app = Flask(__name__)
CORS(app)  # Enable CORS

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:8001')
GET_MEMORY_PATH = 'messages/get_memories.json'

TASK_CREATOR_HOST = os.getenv('TASK_CREATOR_HOST', 'http://plugin-task-creator:5010')
TASK_CREATOR_PATH = 'queue_task'

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route('/create_task_clean', methods=['POST'])
def create_task_clean():
    try:
        url = f"{MEMORY_HOST}/{GET_MEMORY_PATH}"
        data = requests.get(url).json()

        logging.debug(url)
        logging.debug(data)
    except Exception as e:
        logging.error(f"Failed to get data from Memory Service: {e}")
        return 'Failed to get data from Memory Service', 500

    # Lese den Task-Text aus der Datei
    with open('task_text.txt', 'r') as file:
        task_text = file.read()

    # Erstelle den taskData-String
    task_data = task_text + '\n```json\n' + json.dumps(data) + '\n```\n'

    # Erstelle die URL und die Anforderungsdaten für den Task Creator
    task_creator_url = f"{TASK_CREATOR_HOST}/{TASK_CREATOR_PATH}"
    task_creator_data = {"taskData": task_data}

    try:
        # Füge den Task zur Warteschlange hinzu
        response = requests.post(task_creator_url, json=task_creator_data)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to queue task: {e}")
        return 'Failed to queue task', 500

    return 'Task successfully queued', 200

@app.route('/get_task_text', methods=['GET'])
def get_task_text():
    try:
        url = f"{MEMORY_HOST}/{GET_MEMORY_PATH}"
        data = requests.get(url).json()

        logging.debug(url)
        logging.debug(data)
    except Exception as e:
        logging.error(f"Failed to get data from Memory Service: {e}")
        return 'Failed to get data from Memory Service', 500

    # Lese den Task-Text aus der Datei
    with open('task_text.txt', 'r') as file:
        task_text = file.read()

    # Erstelle den taskData-String
    task_data = task_text + '\n```json\n' + json.dumps(data) + '\n```\n'

    return json.dumps(task_data)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5021)
