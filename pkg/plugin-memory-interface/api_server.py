# api_server.py
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
from memory_client import MemoryClient
from fast_api_boilerplate import setup_app
from pydantic import BaseModel

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:5006')
PORT = os.getenv('PORT', 5005)
memory_client = MemoryClient(MEMORY_HOST)

app = FastAPI(
    title="Plugin Memory Interface",
    description="A generic interface to interact with the memory service which performs CRUD operations on JSON data.",
    version="1.0.0",
    openapi_tags=[{
        "name": "MemoryOperations",
        "description": "CRUD operations for memory data handling.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

setup_app(app)

IGNORED_PATHS = ["favicon.ico"]

@app.get("/{path:path}", 
         summary="Retrieve Memory Data", 
         description="Retrieves data from the memory service based on the given path.", 
         operation_id="getMemoryData",
         tags=["MemoryOperations"])
async def catch_all_get(path: str, request: Request):
    if path in IGNORED_PATHS:
        return Response(status_code=204)  # No Content
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.get_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.post("/{path:path}", 
          summary="Add or Update Memory Data", 
          description="Adds or updates data in the memory service based on the given path.", 
          operation_id="addOrUpdateMemoryData",
          tags=["MemoryOperations"])
async def catch_all_post(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.post_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.delete("/{path:path}", 
            summary="Delete Memory Data", 
            description="Deletes data from the memory service based on the given path.", 
            operation_id="deleteMemoryData",
            tags=["MemoryOperations"])
async def catch_all_delete(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.delete_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
