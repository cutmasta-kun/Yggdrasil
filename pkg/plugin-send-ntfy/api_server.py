# api_server.py
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# Enable CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define constants
NTFY_HOST = os.environ.get('NTFY_HOST', "https://ntfy.sh")
TOPIC = os.environ.get('TOPIC', "mytopic")

@app.get("/logo.png")
def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
def plugin_manifest():
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(content=text, media_type="application/json")

@app.get("/openapi.yaml")
def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(content=text, media_type="text/yaml")

from typing import Optional, List

class Message(BaseModel):
    message: str
    tags: Optional[str] = None

@app.post("/send")
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
    uvicorn.run(app, host="0.0.0.0", port=5003)
