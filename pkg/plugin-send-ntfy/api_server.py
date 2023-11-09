# api_server.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
from fast_api_boilerplate import setup_app

# Define constants
NTFY_HOST = os.environ.get('NTFY_HOST', "https://ntfy.sh")
TOPIC = os.environ.get('TOPIC', "mytopic")
PORT = int(os.environ.get('PORT', 5003))

app = FastAPI(
    title="NTFY Plugin",
    description="A plugin that allows the user to send notifications via NTFY using ChatGPT.",
    version="1.0.0",
    openapi_tags=[{
        "name": "send_ntfy",
        "description": "Send a notification.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

setup_app(app)

from typing import Optional

class Message(BaseModel):
    message: str
    tags: Optional[str] = None

@app.post(
        "/send",
        summary="Send a notification",
        operation_id="send_ntfy",
        tags=["send_ntfy"]
        )
def send_notification(message: Message):
    # If tags are provided, send the message and tags as JSON
    if message.tags:
        data = {
            "message": message.message,
            "tags": message.tags.split(',')
        }
        response = requests.post(f"{NTFY_HOST}/{TOPIC}", json=data)
    # If no tags are provided, send only the message as data
    else:
        data = message.message
        response = requests.post(f"{NTFY_HOST}/{TOPIC}", data=data.encode('utf-8'))

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to send notification: " + response.text)
    return {'status': 'success', 'message': data}

if __name__ == "__main__":
    import uvicorn
    PORT = int(PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
