# fast_api_boilerplate.py
#
# version 1.9
# 
# /healthcheck Endpoint
# /ask-api Endpoint
#   needs ./api_assistant.py >=1.5

from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml

import logging

# Konfigurieren Sie das Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PATHS_BLACKLIST = ["/healthcheck", "/ask-api"]

def setup_app(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if os.path.isfile('README.md'):
        @app.options("/README.md", include_in_schema=False)
        def options_logo():
            return Response(status_code=200)
        
        @app.get("/README.md", include_in_schema=False)
        def plugin_logo():
            return FileResponse('README.md', media_type='text/markdown')
        
    if os.path.isfile('api_description.md'):
        @app.options("/api_description.md", include_in_schema=False)
        def options_logo():
            return Response(status_code=200)
        
        @app.get("/api_description.md", include_in_schema=False)
        def plugin_logo():
            return FileResponse('api_description.md', media_type='text/markdown')

    if os.path.isfile('favicon.ico'):
        @app.options("/favicon.ico", include_in_schema=False)
        def options_logo():
            return Response(status_code=200)
        
        @app.get("/favicon.ico", include_in_schema=False)
        def plugin_logo():
            return FileResponse('favicon.ico', media_type='image/vnd.microsoft.icon')

    if os.path.isfile('logo.png'):
        @app.options("/logo.png", include_in_schema=False)
        def options_logo():
            return Response(status_code=200)
        
        @app.get("/logo.png", include_in_schema=False)
        def plugin_logo():
            return FileResponse('logo.png', media_type='image/png')

    if os.path.isfile('./ai-plugin.json'):
        @app.options("/.well-known/ai-plugin.json", include_in_schema=False)
        def options_plugin_manifest():
            return Response(status_code=200)

        @app.get("/.well-known/ai-plugin.json", include_in_schema=False)
        async def plugin_manifest(request: Request):
            return FileResponse('./ai-plugin.json', media_type="application/json")

    @app.options("/openapi.yaml", include_in_schema=False)
    def options_openapi():
        return Response(status_code=200)
    
    @app.get("/openapi.yaml", include_in_schema=False)
    def get_openapi_yaml():
        if os.path.isfile("openapi.yaml"):
            with open("openapi.yaml") as f:
                text = f.read()
                return Response(text, media_type="text/yaml")
        else:
            openapi_schema = app.openapi()

            if "servers" in openapi_schema:
                for server in openapi_schema["servers"]:
                    if hasattr(server["url"], "__str__"):
                        server["url"] = server["url"].__str__()

            order = ['openapi', 'info', 'servers', 'paths', 'components']

            yaml_output = ""
            for key in order:
                if key in openapi_schema:
                    section = {key: openapi_schema[key]}
                    yaml_output += yaml.dump(section, sort_keys=False)

            return Response(yaml_output, media_type="text/yaml")
        








from pydantic import BaseModel
import socket
from urllib.parse import urlparse

class DependencyStatus(BaseModel):
    up: bool
    details: dict = None

def ping_host(url: str) -> DependencyStatus:
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    port = parsed_url.port or 80

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((hostname, port))
        sock.close()
        return DependencyStatus(up=True)
    except socket.error as e:
        return DependencyStatus(up=False, details={"error": str(e)})

from datetime import datetime
    
def setup_healthcheck(app: FastAPI, dependencies: dict):
    @app.get("/healthcheck", include_in_schema=False)
    def healthcheck(request: Request,):
        status = 200
        health_status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "dependencies": []
        }
        for dep_name, check_func in dependencies.items():
            dep_status = check_func()
            if not dep_status.up:
                status = 503
                health_status["status"] = "error"
            health_status["dependencies"].append({
                "name": dep_name,
                "status": "up" if dep_status.up else "down",
                "detail": dep_status.details
            })

        request.state.timing_marks.append(('healthcheck-status', time.time()))

        return JSONResponse(content=health_status, status_code=200)











from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
import requests

class AskApiResponse(BaseModel):
    result: Any
    error: bool = Field(default=False)
    message: Optional[str]

class AskApiPayload(BaseModel):
    message: Optional[str] = Field(..., description="The message to request against the api")

from api_assistant import ApiAssistant, MaybeApiPayload
import time

def fetch(url: str) -> (str, bool):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text, True
    except requests.RequestException as e:
        logger.error(f"Fehler beim Abrufen von {url}: {e}")
        return str(e), False
    
def requestApi(payload: MaybeApiPayload, operation_info):
    try:
        response = requests.request(method=operation_info['method'], url=operation_info['url'], 
                                    json=payload.result.parameters if operation_info['method'] in ['POST', 'DELETE', 'PATCH'] else None, 
                                    params=payload.result.parameters if operation_info['method'] == 'GET' else None)
        return response.json(), response.status_code
    except Exception as e:
        logging.error(f"Error making request to operation URL: {e}")
        return {"error": True, "message": str(e)}, 500

def setup_ask(app: FastAPI, config: Dict[str, Any], withState: bool = False):
    @app.post(
        "/ask-api",
        summary="Ask the api",
        operation_id="askApi",
        response_model=AskApiResponse,
        tags=["AskApi"]
    )
    def askApi(request: Request, askPayload: AskApiPayload):
        ##### Dokumentation sammeln #####
        documentation = {
            doc_name: doc_text
            for doc_name, doc_url in config.get('documentation', {}).items()
            if (doc_text := fetch(doc_url)[0])
        }

        ##### Assistant initialisieren #####
        assistant = ApiAssistant(documentation=documentation, withState=withState)
        assistant.add_event(f"Request: {askPayload.message}")

        ##### Healthcheck und Kontext #####
        validationContext = None
        healthcheckUrl = config.get('meta', {}).get('healthcheck')
        if healthcheckUrl:
            healthcheck_result, healthcheck_success = fetch(healthcheckUrl)
            validationContext = {
                "context": f"# API HEALTHCHECK STATUS {healthcheck_result}"
            } if healthcheckUrl and healthcheck_success else None
            if validationContext:
                assistant.add_event(validationContext["context"])

        ##### Validierung der Benutzeranfrage #####
        request.state.timing_marks.append(('documentation-collect', time.time()))

        validation = assistant.validate_user_request_against_api(
            userRequest=askPayload.message, 
            context=validationContext
        )
        request.state.timing_marks.append(('validation-generate', time.time()))

        if hasattr(request.state, 'cost'):
            request.state.cost.append(validation._raw_response.usage.total_tokens)
            request.state.input.append(validation._raw_response.usage.prompt_tokens)
            request.state.output.append(validation._raw_response.usage.completion_tokens)

        ##### Antwort auf Validierung #####
        if validation.error:
            return JSONResponse(
                content={"result": None, "error": True, "message": validation.message},
                status_code=400
            )
        if not validation.result.is_valid:
            return JSONResponse(
                content={"result": None, "error": True, "message": validation.result.explanation},
                status_code=400
            )

        print(f"## VALID REQUEST: {validation.result.explanation}")



        
        operations = config.get("operations")
        context = config.get("context")
        
        payload: MaybeApiPayload = assistant.interpret_user_request(askPayload.message, context=context)
        request.state.timing_marks.append(('payload-generate', time.time()))

        if hasattr(request.state, 'cost'):
            request.state.cost.append(payload._raw_response.usage.total_tokens)
            request.state.input.append(payload._raw_response.usage.prompt_tokens)
            request.state.output.append(payload._raw_response.usage.completion_tokens)

        print(f"## PAYLOAD RECEIVED: {payload.model_dump()}")
        if payload.error:
            return JSONResponse(content={"error": True, "message": payload.message}, status_code=500)

        operation_info = operations.get(payload.result.action if payload.result else None)
        if not operation_info:
            return JSONResponse(content={"error": True, "message": f"Keine gültige Operation gefunden: {payload.result.action}"}, status_code=400)

        max_retries = 1
        current_try = 0
        cumulative_error_context = ""

        while current_try <= max_retries:
            result, status_code = requestApi(payload, operation_info)
            request.state.timing_marks.append(('api-request', time.time()))

            # Im Erfolgsfall
            if 200 <= status_code < 300:
                assistant.add_event(f"Successful Request: The request was successful with status code {status_code}. Response: {result}")
                break

            # Im Fehlerfall
            elif 400 <= status_code < 500:
                failed_response_json = result
                assistant.add_event(f"Failed Request: status code {status_code}, detailed response: {failed_response_json}.")
                error_message = f"Failed on try {current_try + 1} with status code {status_code}, response: {failed_response_json}"

                # Akkumuliere den Fehlerkontext
                cumulative_error_context += f"\n{error_message}"
                error_context = f"### Accumulated Errors: {cumulative_error_context}\nThis payload resulted in the failure: {payload.result.model_dump()}"

                if current_try < max_retries:
                    logging.warning(f"error_context: {error_context}")
                    assistant.add_event("Retry Payload Generation")
                    
                    retry_payload: MaybeApiPayload = assistant.interpret_user_request(askPayload.message, context=error_context)
                    
                    request.state.timing_marks.append(('retry-payload-generate', time.time()))

                    if hasattr(request.state, 'cost'):
                        request.state.cost.append(retry_payload._raw_response.usage.total_tokens)
                        request.state.input.append(retry_payload._raw_response.usage.prompt_tokens)
                        request.state.output.append(retry_payload._raw_response.usage.completion_tokens)
                    
                    payload = retry_payload  # Setze den Payload für den nächsten Versuch
                else:
                    end_time = time.time()
                    timing_string = generate_timing_string(request.state.timing_marks, request.state.start_time, end_time)
                    assistant.add_event(f"Request Timing: {timing_string}")
                    logging.error(error_message)
                    return JSONResponse(content={"error": True, "message": error_message}, status_code=status_code)

            current_try += 1

        # Erfolgreicher Request nach Schleifenende
        if status_code >= 200 and status_code < 300:
            end_time = time.time()
            timing_string = generate_timing_string(request.state.timing_marks, request.state.start_time, end_time)
            assistant.add_event(f"Request Timing: {timing_string}")
            logging.info(f"assistant.events: {assistant.events}")
            if withState:
                assistant.update_state_file()
                request.state.timing_marks.append(('state-generate', time.time()))

            return JSONResponse(content={"result": result, "error": False, "message": validation.result.explanation}, status_code=status_code)



























from starlette.middleware.base import BaseHTTPMiddleware
import time

def generate_timing_string(timing_marks: list, start_time: float, end_time: float) -> str:
    timing_header = []
    prev_time = start_time
    for name, current_time in timing_marks:
        duration = (current_time - prev_time) * 1000
        timing_header.append(f"{name};dur={duration:.2f}")
        prev_time = current_time

    total_duration = (end_time - start_time) * 1000
    timing_header.append(f"total;dur={total_duration:.2f}")

    return ', '.join(timing_header)

class ServerTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request.state.timing_marks = []
        request.state.start_time = start_time

        response = await call_next(request)

        end_time = time.time()

        server_timing_header = generate_timing_string(request.state.timing_marks, start_time, end_time)

        response.headers["Server-Timing"] = server_timing_header

        return response
    
class ServerCostMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.cost = []
        request.state.input = []
        request.state.output = []

        response = await call_next(request)

        price_input = 0.01
        price_output = 0.03

        total_cost = sum(request.state.cost)
        total_input_token = sum(request.state.input)
        total_output_token = sum(request.state.output)

        price_input_total = (total_input_token / 1000) * price_input
        price_output_total = (total_output_token / 1000) * price_output

        price_total = price_input_total + price_output_total

        response.headers["Server-Cost"] = f"{round(price_total, 5)} $"

        del response.headers["Access-Control-Allow-Credentials"]

        return response
    
class RegistryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.info(f"request.headers: {request.headers}")

        response = await call_next(request)

        

        return response