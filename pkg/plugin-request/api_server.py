# api_server.py
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os
import requests
import yaml
import logging
from starlette.types import Receive, Send, Scope

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Request API",
    description="An API to make GET and POST requests to other URLs.",
    version="1.0.0",
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logging.info(f"Incoming request: {body.decode()}")

    async def _mock_receive() -> dict:
        return {"type": "http.request", "body": body}

    request._receive = _mock_receive
    response = await call_next(request)
    return response

@app.get("/logo.png", include_in_schema=False)
def plugin_logo():
    filename = 'logo.png'
    return FileResponse(filename, media_type='image/png')

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
def plugin_manifest():
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(content=text, media_type="application/json")

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components']
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")

class Payload(BaseModel):
    url: str = Field(..., description="The URL to which the request will be sent.")
    data: dict = Field(default={}, description="The data to be sent in the request. Use an empty dict if no payload is required.")

class APIRequest(BaseModel):
    payload: Payload

class ResponseModel(BaseModel):
    status: int
    content: str
    headers: dict

@app.post(
    "/get", 
    summary="GET Requester", 
    description="Accepts a POST request with a URL and optional payload.",
    operation_id="makeGetRequest",
    response_model=ResponseModel
)
def make_get_request(request: APIRequest):
    try:
        response = requests.get(request.payload.url, params=request.payload.data)
        response.raise_for_status()
        return {
            'status': response.status_code,
            'content': response.text,
            'headers': dict(response.headers)
        }
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError):
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        else:
            raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/post", 
    summary="POST Requester", 
    description="Accepts a POST request with a URL and payload.",
    operation_id="makePostRequest",
    response_model=ResponseModel
)
def make_post_request(request: APIRequest):
    try:
        response = requests.post(request.payload.url, json=request.payload.data)
        response.raise_for_status()
        return {
            'status': response.status_code,
            'content': response.text,
            'headers': dict(response.headers)
        }
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError):
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        else:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5200)
