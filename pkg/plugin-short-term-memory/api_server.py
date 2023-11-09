from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import os
from memory_client import MemoryClient
from fast_api_boilerplate import setup_app

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:5006')
PORT = int(os.getenv('PORT', 5030))
memory_client = MemoryClient(MEMORY_HOST)

app = FastAPI(
    title="Short Term Memory Interface Plugin",
    description="A plugin interface to interact with the short term memory service. It allows adding and retrieving memories based on UUIDs.",
    version="1.0.0",
    openapi_tags=[{
        "name": "ShortTermMemory",
        "description": "Operations related to adding and retrieving short term memories.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

setup_app(app)

class AddMemoryPayload(BaseModel):
    message: str = Field(..., description="The message to be added to the short term memory.")

class GetMemoryParams(BaseModel):
    uuid: str = Field(None, description="The UUID of the memory to retrieve. If not provided, all memories are returned.")
    limit: int = Field(10, description="Limit the number of memories returned. Ignored if UUID is provided.")

class MemoryResponse(BaseModel):
    ok: bool
    message: str
    redirect: str = Field(None)

@app.post(
    "/add_memory", 
    summary="Add to Short Term Memory", 
    description="Adds a message to the short term memory.",
    operation_id="addToShortTermMemory",
    response_model=MemoryResponse,
    tags=["ShortTermMemory"]
)
async def add_to_short_term_memory(request: Request, payload: AddMemoryPayload):
    response_content, status_code, headers = await memory_client.post_action(request, "messages/add_memory.json")
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.get(
    "/get_memory", 
    summary="Retrieve Short Term Memory", 
    description="Retrieves a specific memory by its UUID or all memories if no UUID is provided.",
    operation_id="getShortTermMemory",
    response_model=MemoryResponse,
    tags=["ShortTermMemory"]
)
async def get_short_term_memory(request: Request, params: GetMemoryParams = Depends()):
    try:
        response_content, status_code, headers = await memory_client.get_action(request, "messages/get_memory.json")
        return JSONResponse(content=response_content, status_code=status_code, headers=headers)
    except ValueError as e:
        # Senden einer 400-Antwort, wenn sowohl Such- als auch Filterparameter gesetzt sind
        return JSONResponse(content={"detail": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
