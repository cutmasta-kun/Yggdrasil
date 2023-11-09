from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ask import send_request
from agents.compress_decompress import compress, decompress
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import json
import logging
import os
import uuid
from typing import List, Optional
import yaml
from fast_api_boilerplate import setup_app

# Konfigurieren der Protokollierung
logging.basicConfig(level=logging.INFO)

AI_MODEL = os.getenv('AI_MODEL', 'gpt-4')
PORT = int(os.getenv('PORT', 5022))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

app = FastAPI(
    title="AI Conversation Service",
    description="Der AI Conversation Service ermöglicht interaktive Gespräche mit KI, unterstützt Wissenssuche und das Speichern von Informationen. Einfach zu integrieren, bietet er menschenähnliche Antworten für diverse Anwendungen.",
    version="1.0.0",
    openapi_tags=[{
        "name": "Conversation",
        "description": "API-Endpunkte für Konversationen mit der KI.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

setup_app(app)

class Message(BaseModel):
    content: str
    role: str

class AskRequest(BaseModel):
    messages: List[Message]

class AskResponse(BaseModel):
    messages: List[Message]

@app.post(
        '/ask',
        summary="Stellt eine Frage an die KI", 
        description="Sendet eine Liste von Nachrichten an die KI und erhält eine Antwort.",
        operation_id="ask_ki",
        response_model=AskResponse,
        tags=["Conversation"]
        )
async def ask(ask_request: AskRequest):
    messages = ask_request.messages

    try:
        response, error, status_code = send_request(messages)
    except Exception as e:
        logging.error(f"Fehler bei der Kommunikation mit der KI: {e}")
        raise HTTPException(status_code=500, detail={'error': 'Internal server error'})

    if error:
        logging.error(f"Fehler in der KI-Antwort: {error}")
        raise HTTPException(status_code=status_code, detail={'error': error})

    return JSONResponse(content=response, status_code=status_code)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
