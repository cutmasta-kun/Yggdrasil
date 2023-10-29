# api_server.py
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import requests
import yaml

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

# Enable CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/logo.png", include_in_schema=False)
def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
def plugin_manifest():
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(content=text, media_type="application/json")

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    # Konvertieren der 'AnyUrl'-Objekte in Strings
    if "servers" in openapi_schema:
        for server in openapi_schema["servers"]:
            if hasattr(server["url"], "__str__"):  # Prüfen, ob das Objekt in einen String umgewandelt werden kann
                server["url"] = server["url"].__str__()

    order = ['openapi', 'info', 'servers', 'paths', 'components']

    yaml_output = ""
    for key in order:
        if key in openapi_schema:
            section = {key: openapi_schema[key]}
            yaml_output += yaml.dump(section, sort_keys=False)  # sort_keys=False behält die Reihenfolge der Schlüssel bei

    return Response(yaml_output, media_type="text/yaml")

from typing import Optional, List

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
