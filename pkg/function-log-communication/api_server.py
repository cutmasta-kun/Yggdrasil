# fastapi_server.py
from fastapi import FastAPI, HTTPException, Request, Body, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import logging
import json
from typing import Any, Dict, List, Optional
import yaml

# Konfiguration der Anwendung
logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="Log API",
    description="API for handling and storing log messages.",
    version="1.0.0",
    openapi_tags=[{
        "name": "logging",
        "description": "Endpoints related to log operations.",
    }],
    servers=[{"url": f"http://localhost:5000", "description": "Local Development Server"}],
)

# CORS aktivieren
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definieren der Pydantic-Modelle
class MessageJson(BaseModel):
    any_field: Optional[Dict[str, Any]]

class Data(BaseModel):
    id: str = Field(..., description="The unique identifier")
    time: int = Field(..., description="The time of the message")
    event: str = Field(..., description="The event type")
    topic: str = Field(..., description="The topic of the message")
    
    # Alle nachfolgenden Felder sind optional
    message: Optional[str] = Field(None, description="The message content")
    expires: Optional[int] = Field(None, description="The expiration time")
    title: Optional[str] = Field(None, description="The title of the message")
    tags: Optional[List[str]] = Field(None, description="Tags for the message")
    priority: Optional[int] = Field(None, description="Priority of the message")
    click: Optional[str] = Field(None, description="Click action for the message")
    actions: Optional[List[Dict[str, Any]]] = Field(None, description="Actions for the message")
    attachment: Optional[Dict[str, Any]] = Field(None, description="Attachment for the message")

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

@app.head("/log", include_in_schema=False)
async def log_status():
    return Response(status_code=200)

@app.post("/log", tags=["logging"], summary="Log a message")
async def log(data: Data):
    message = data.message

    if message is not None:
        try:
            message_json = json.loads(message)
            logging.info(f"Message is valid JSON: {message_json}")
        except json.JSONDecodeError:
            logging.info(f"Message is not valid JSON: {message}")
    else:
        logging.info("No message provided")

    logging.info(data.dict())
    return {'status': 'OK'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
