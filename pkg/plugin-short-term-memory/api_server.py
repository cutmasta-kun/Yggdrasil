from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional
import os
import time
from memory_client import MemoryClient
from fast_api_boilerplate import setup_app, setup_healthcheck, setup_ask, ping_host, ServerTimingMiddleware, ServerCostMiddleware

#MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:5006')
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')
OPENAI_HOST = os.environ.get('OPENAI_HOST', " https://api.openai.com")
PORT = int(os.getenv('PORT', 5030))
SERVICE_NAME = f"plugin-short-term-memory:{PORT}"
memory_client = MemoryClient(MEMORY_HOST, SERVICE_NAME)

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

dependencies = {
    "MEMORY_HOST connection": lambda: ping_host(MEMORY_HOST)
}

config = {
    "documentation": {
        "api_description.md": f"http://localhost:{PORT}/api_description.md"
#        "openapi.yaml": f"http://localhost:{PORT}/openapi.yaml",
#        "ai_plugin.json": f"http://localhost:{PORT}/.well-known/ai-plugin.json"
    },
    "operations": {
        "addToShortTermMemory": {"method": "POST", "url": f"http://localhost:{PORT}/add_memory"},
        "getShortTermMemory": {"method": "GET", "url": f"http://localhost:{PORT}/get_memory"},
        "deleteShortTermMemorybyUUID": {"method": "DELETE", "url": f"http://localhost:{PORT}/delete_memory"}
    },
    "context": None,
    "meta": {
#        "healthcheck": f"http://localhost:{PORT}/healthcheck"
    }
}

setup_app(app)
setup_healthcheck(app, dependencies)
setup_ask(app, config)

app.add_middleware(ServerTimingMiddleware)
app.add_middleware(ServerCostMiddleware)

class AddMemoryPayload(BaseModel):
    message: str = Field(..., description="The message to be added to the short term memory.")

class GetMemoryParams(BaseModel):
    uuid: Optional[str] = Field(None, description="The UUID of the memory to retrieve. If not provided, all memories are returned.")
    limit: int = Field(10, description="Limit the number of memories returned. Ignored if UUID is provided.")

class DeleteMemoryPayload(BaseModel):
    uuid: str = Field(..., description="The UUID of the memory to delete.")

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
    request.state.timing_marks.append(('data-write', time.time()))
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
        request.state.timing_marks.append(('data-fetch', time.time()))
        return JSONResponse(content=response_content, status_code=status_code, headers=headers)
    except ValueError as e:
        # Senden einer 400-Antwort, wenn sowohl Such- als auch Filterparameter gesetzt sind
        return JSONResponse(content={"detail": str(e)}, status_code=400)
    
@app.delete(
    "/delete_memory", 
    summary="Delete a Short Term Memory defined by a UUID", 
    description="Deletes a Short Term Memory by a UUID.",
    operation_id="deleteShortTermMemorybyUUID",
    response_model=MemoryResponse,
    tags=["ShortTermMemory"]
)
async def delete_short_term_memory_by_uuid(request: Request, payload: DeleteMemoryPayload):
    response_content, status_code, headers = await memory_client.delete_action(request, "messages/delete_memory_by_uuid.json")
    request.state.timing_marks.append(('data-delete', time.time()))
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
