# api_server.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
import time
import requests
from fast_api_boilerplate import setup_app, setup_healthcheck, ping_host, ServerTimingMiddleware, ServerCostMiddleware, setup_ask
import json

# Define constants
NTFY_HOST = os.environ.get('NTFY_HOST', "https://ntfy.sh")
OPENAI_HOST = os.environ.get('OPENAI_HOST', " https://api.openai.com")
TOPIC = os.environ.get('TOPIC', "mytopic")
PORT = int(os.environ.get('PORT', 5003))

app = FastAPI(
    title="NTFY Plugin",
    description="A plugin that allows the user to send notifications via NTFY.",
    version="1.0.0",
    openapi_tags=[{
        "name": "SendNTFY",
        "description": "Send a notification.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

dependencies = {
    "NTFY_HOST connection": lambda: ping_host(NTFY_HOST)
}

config = {
    "documentation": {
        "api_description.md": f"http://localhost:{PORT}/api_description.md"
#        "openapi.yaml": f"http://localhost:{PORT}/openapi.yaml",
#        "README.md": f"http://localhost:{PORT}/README.md"
    },
    "operations": {
        "send": {"method": "POST", "url": f"http://localhost:{PORT}/send"}
    },
    "context": None,
    "meta": {
#        "healthcheck": f"http://localhost:{PORT}/healthcheck"
    }
}

setup_app(app)
setup_healthcheck(app, dependencies)
setup_ask(app, config, False)

app.add_middleware(ServerTimingMiddleware)
app.add_middleware(ServerCostMiddleware)

from typing import Optional
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class SendNotificationPayload(BaseModel):
    message: str
    tags: Optional[str] = None

@app.post(
        "/send",
        summary="Send a notification",
        operation_id="send",
        tags=["SendNTFY"]
        )
def send_notification(request: Request, sendPayload: SendNotificationPayload):
    if sendPayload.tags:
        tags = [tag.strip() for tag in sendPayload.tags.split(',')]
        data = {
            "message": sendPayload.message,
            "tags": tags,
            "topic": TOPIC
        }
        response = requests.post(f"{NTFY_HOST}", data=json.dumps(data))
        del data['topic']
    else:
        data = sendPayload.message
        response = requests.post(f"{NTFY_HOST}/{TOPIC}", data=data.encode('utf-8'))

    request.state.timing_marks.append(('send-ntfy', time.time()))

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to send notification: " + response.text)
    
    return {'status': 'success', 'message': data}

if __name__ == "__main__":
    import uvicorn
    PORT = int(PORT)
    uvicorn.run(app, host="0.0.0.0", port=PORT)
