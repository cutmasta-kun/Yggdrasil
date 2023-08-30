# api_server.py
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import os
from post_flask_actions import post_action
from get_flask_actions import get_action

app = FastAPI()

# Enable CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:8001')

@app.get("/logo.png")
def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json")
def plugin_manifest():
    with open("./ai-plugin.json") as f:
        text = f.read()
        return JSONResponse(content=text)

@app.get("/openapi.yaml")
def openapi_spec():
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(content=text, media_type="text/yaml")

@app.get("/{path:path}")
async def catch_all_get(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = await get_action(request, path, MEMORY_HOST)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

@app.post("/{path:path}")
def catch_all_post(path: str, request: Request):
    if not path.endswith('.json'):
        path += '.json'

    response_content, status_code, headers = post_action(request, path, MEMORY_HOST)
    return JSONResponse(content=response_content, status_code=status_code, headers=headers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005)
