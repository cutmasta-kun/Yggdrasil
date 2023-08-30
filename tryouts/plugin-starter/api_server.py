# api_server.py
from fastapi import FastAPI, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os
import logging
from typing import Optional
from conversations_repository import create_conversation, SpeechBubble, add_speech_bubble, get_conversation_from_repo, search_in_conversation_from_repo
from enum import Enum

app = FastAPI(
    title="Plugin Starter",
    description="A starting project for chatGPT plugins",
    version="1.0.0",
)

# Enable CORS
origins = [
    f"http://localhost:5009",
    "https://chat.openai.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/.well-known/ai-plugin.json")
def plugin_manifest():
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(content=text, media_type="application/json")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5009)