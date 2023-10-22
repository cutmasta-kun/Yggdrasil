from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ask import validate_messages, send_request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json
import logging
import os
import uuid
from typing import List, Optional
import yaml

# Konfigurieren der Protokollierung
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AI Conversation Service",
    description="Der AI Conversation Service ermöglicht interaktive Gespräche mit KI, unterstützt Wissenssuche und das Speichern von Informationen. Einfach zu integrieren, bietet er menschenähnliche Antworten für diverse Anwendungen.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaubt alle Herkünfte
    allow_credentials=True,
    allow_methods=["*"],  # Erlaubt alle Methoden
    allow_headers=["*"],  # Erlaubt alle Header
)

AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

class AskRequest(BaseModel):
    messages: List

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components']
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")

@app.post('/ask')
async def ask(ask_request: AskRequest):
    messages = ask_request.messages

    if not validate_messages(messages):
        raise HTTPException(status_code=400, detail={'error': 'Invalid messages'})

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {OPENAI_API_KEY}'
    }

    response, error, status_code = send_request(messages, headers, AI_MODEL)

    if error:
        raise HTTPException(status_code=status_code, detail={'error': error})

    return JSONResponse(content=response, status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5022)