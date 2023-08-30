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
import yaml

app = FastAPI(
    title="Function Chat",
    description="Function Chat is a service that manages and retrieves chat conversations. It supports adding messages to conversations, and provides the ability to retrieve the latest messages within a conversation. It also offers a simple search functionality within a conversation.",
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

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:8001')

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components']
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")

class Role(str, Enum):
    system = "system"
    assistant = "assistant"
    user = "user"

class ChatRequest(BaseModel):
    content: str = Field(..., example="Hello, how are you?")
    role: Optional[Role] = Field(Role.user, example="user")
    uuid: Optional[str] = Field(None, example="1234-5678-90")

class ConversationRequest(BaseModel):
    uuid: str = Field(..., example="1234-5678-90")
    queryTags: Optional[str] = Field(None, example="Hello")

@app.post("/chat", operation_id="chat")
async def chat(request: ChatRequest):
    # If UUID is not provided, create a new conversation
    if request.uuid is None:
        conversation_uuid = create_conversation(MEMORY_HOST)
        if conversation_uuid is None:
            raise HTTPException(status_code=500, detail="Could not create conversation")
    else:
        conversation_uuid = request.uuid

    user_bubble = SpeechBubble(content=request.content, role=request.role)

    # Add a speech bubble to the conversation
    if not add_speech_bubble(MEMORY_HOST, conversation_uuid, user_bubble):
        raise HTTPException(status_code=500, detail="Could not add speech bubble")
    # If UUID was provided, return HTTP 204 No Content
    if request.uuid is not None:
        return Response(status_code=204)
    # If UUID was not provided, return the UUID of the new conversation
    return {"uuid": conversation_uuid}

@app.post("/conversation", operation_id="get_conversation_by_uuid")
async def get_conversation(request: ConversationRequest):
    # If queryTags is provided, search for the tag in the conversation
    if request.queryTags is not None:
        conversation = search_in_conversation_from_repo(MEMORY_HOST, request.uuid, request.queryTags)

        if conversation is None:
            raise HTTPException(status_code=404, detail="No matches found")

        messages = [bubble.speech_bubble_to_dict() for bubble in conversation]
        
        # Return the search result
        return {"result": messages}
    else:
        print('no queryTags')
        # Get the conversation from the database
        conversation = get_conversation_from_repo(MEMORY_HOST, request.uuid)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Convert SpeechBubble objects to dictionaries
        messages = [bubble.speech_bubble_to_dict() for bubble in conversation]
        
        # Return the converted conversation
        return messages

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5009)