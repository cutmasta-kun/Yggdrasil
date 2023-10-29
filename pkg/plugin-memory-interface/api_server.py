# api_server.py
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml
import os
from memory_client import MemoryClient

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:5006')
PORT = os.getenv('PORT', 5005)
memory_client = MemoryClient(MEMORY_HOST)

app = FastAPI(
    title="Plugin Memory Interface",
    version="1.0.0",
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

@app.options("/openapi.yaml")
def options_openapi():
    return Response(status_code=200)

@app.options("/.well-known/ai-plugin.json")
def options_plugin_manifest():
    return Response(status_code=200)

@app.get("/logo.png")
def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def plugin_manifest(request: Request):
    host = request.client.host
    return Response(content=open("./ai-plugin.json", "r").read(), media_type="application/json")

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, media_type="text/yaml")

IGNORED_PATHS = ["favicon.ico"]

@app.get("/{path:path}")
async def catch_all_get(path: str, request: Request):
    if path in IGNORED_PATHS:
        return Response(status_code=204)  # No Content
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.get_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.post("/{path:path}")
async def catch_all_post(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.post_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.delete('/{path:path}')
async def catch_all_delete(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await memory_client.delete_action(request, path)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
