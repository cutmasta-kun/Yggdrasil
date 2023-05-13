# app.py
from flask import Flask, request
import logging
import json
from message_types import Data, Message, MessageJson, Id, Time, Expires, Event, Topic, Title, Tags, Priority, Click, Actions, Attachment

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

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

    app.logger.info(f"Received data: {data}")
    return 'OK', 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
