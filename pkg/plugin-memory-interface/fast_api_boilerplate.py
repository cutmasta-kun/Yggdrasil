# fast_api_boilerplate.py
#
# version 1.1

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import yaml

def setup_app(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.options("/openapi.yaml", include_in_schema=False)
    def options_openapi():
        return Response(status_code=200)

    # Überprüfen, ob die Datei 'logo.png' existiert, bevor der Endpunkt registriert wird
    if os.path.isfile('logo.png'):
        @app.get("/logo.png", include_in_schema=False)
        def plugin_logo():
            return FileResponse('logo.png', media_type='image/png')

    # Überprüfen, ob die Datei 'ai-plugin.json' existiert, bevor der Endpunkt registriert wird
    if os.path.isfile('./ai-plugin.json'):
        @app.options("/.well-known/ai-plugin.json", include_in_schema=False)
        def options_plugin_manifest():
            return Response(status_code=200)

        @app.get("/.well-known/ai-plugin.json", include_in_schema=False)
        async def plugin_manifest(request: Request):
            return FileResponse('./ai-plugin.json', media_type="application/json")

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

from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json

class RegistryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extrahieren des X-Request-ID-Headers, falls vorhanden
        request_id = request.headers.get('X-Request-ID')
        origin_service = request.headers.get('X-Origin-Service')

        if request_id:
            # Hier wird die Tracking-Logik ausgeführt, wenn die X-Request-ID vorhanden ist
            logging.info(f"Request ID: {request_id}")
            logging.info(f"Request path: {request.url.path}")
            logging.info(f"Request method: {request.method}")
            logging.info(f"Request origin_service: {origin_service}")

            # Hier könnten Sie auch Informationen über Query-Parameter und Body extrahieren
            # Achten Sie dabei auf die Sensibilität der Daten
            query_params = dict(request.query_params)
            logging.info(f"Query parameters: {query_params}")

            # Der Body kann nur in bestimmten Fällen gelesen werden, da er ein Stream ist
            # Eine Möglichkeit ist, ihn zu lesen und dann in ein Ersatz-Request-Objekt zu setzen
            # Dies kann jedoch zu Problemen bei großen Datenmengen führen und sollte mit Vorsicht verwendet werden

            # Hier könnte ein Update auf die ServiceCommunicationTable erfolgen

        # Weiterleitung des Requests an den nächsten Middleware-Handler oder die eigentliche Anwendungslogik
        response = await call_next(request)

        return response
