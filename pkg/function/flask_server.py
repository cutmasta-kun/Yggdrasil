# flask_server.py
from flask import Flask, send_file, request, Response
from flask_cors import CORS
import requests
import json
import logging
import uuid
from message_types import Data, Message, MessageJson, Id, Time, Expires, Event, Topic, Title, Tags, Priority, Click, Actions, Attachment

# Configurate application
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route('/log', methods=['HEAD'])
def logStatus():
    return ('', 200)

@app.route('/log', methods=['POST',])
def log():
    data: Data = request.get_json()
    message: Message = data.get('message', '')

    try:
        message_json: MessageJson = json.loads(message)
        app.logger.info(f"Message is valid JSON: {message_json}")
    except json.JSONDecodeError:
        app.logger.info(f"Message is not valid JSON: {message}")

    id_: Id = data['id']
    time: Time = data['time']
    expires: Expires = data.get('expires')
    event: Event = data['event']
    topic: Topic = data['topic']
    title: Title = data.get('title')
    tags: Tags = data.get('tags')
    priority: Priority = data.get('priority')
    click: Click = data.get('click')
    actions: Actions = data.get('actions')
    attachment: Attachment = data.get('attachment')

    app.logger.info(data)
    return 'OK', 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
