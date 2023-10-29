# memory_client.py
import requests
import json
import re
import uuid
from response_formatter import sqlite_to_dict
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO)

class MemoryClient:
    """
    A client for interacting with the Memory Service.
    It handles GET, POST, and DELETE actions, transforming them into appropriate requests.
    """

    SUPPORTED_FILTERS = ['limit']
    SUPPORTED_SEARCH = ['uuid']
    PATH_PATTERN = r'^.+/get_.+\.json$'
    PATH_EXTRACT_PATTERN = r'^(.+)/get_(.+)(\.json)$'

    def __init__(self, memory_host):
        """
        Initialize the MemoryClient with a specified memory host.
        :param memory_host: The base URL of the Memory Service.
        """
        self.memory_host = memory_host

    async def send_request(self, method, path, headers=None, params=None, data=None):
        """
        Sends an HTTP request to the Memory Service.
        :param method: HTTP method (GET, POST, etc.)
        :param path: URL path for the request.
        :param headers: Optional headers for the request.
        :param params: Optional query parameters for the request.
        :param data: Optional data to be sent in the request body.
        :return: Response from the Memory Service.
        """

        if isinstance(data, dict):
            data = json.dumps(data)
        elif isinstance(data, str):
            try:
                # Überprüfen, ob der String ein valides JSON-Objekt darstellt
                json.loads(data)
            except json.JSONDecodeError:
                # Wenn der String kein valides JSON-Objekt ist, Fehler werfen oder entsprechend handeln
                raise ValueError(f"Übergebener String ist kein valides JSON-Objekt: {data}")

        try:
            response = requests.request(
                method=method,
                url=f"{self.memory_host}/{path}",
                headers=headers,
                params=params,
                data=data,
                allow_redirects=False
            )
            return response
        except requests.RequestException as e:
            raise e

    async def delete_action(self, request: Request, path: str):
        """
        Handles a DELETE action by sending a request to the Memory Service.
        It first checks if the resource exists before proceeding with the deletion.
        :param request: The incoming FastAPI request object.
        :param path: URL path for the DELETE action.
        :return: Response content, status code, and headers.
        """
        # headers = {key: value for key, value in request.headers.items() if key != 'host'}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            data = await request.json()
        except Exception as e:
            return {"message": "Invalid request. Could not parse JSON."}, 400, {}

        uuid = data.get("uuid")

        if not uuid:
            return {"message": "UUID not provided"}, 400, {}

        get_path = path.replace("delete", "get") + f"?uuid={uuid}"

        get_response_content, get_status_code, _ = await self.get_action(request, get_path)

        if get_status_code == 404 or not get_response_content:
            return {"ok": True, "message": "Resource not found or already deleted", "redirect": None}, 200, {}

        try:
            response = await self.send_request(
                method='POST',
                path=path,
                headers=headers,
                data=data
            )

            if response.text:  # Überprüfen, ob die Antwort nicht leer ist
                response_content = response.json()
                return response_content, response.status_code, response.headers
            else:
                logging.error("Empty response received from the Memory Service.")
                return {"message": "Internal Server Error"}, 500, {}

        except Exception as e:
            logging.error(f"Error occurred during POST request: {e}")
            return {"message": "Internal Server Error"}, 500, {}


    async def post_action(self, request, path):
        """
        Handles a POST action by sending a request to the Memory Service.
        It uses the provided UUID or queueID if available, otherwise it generates a new UUID for the new resource.
        :param request: The incoming FastAPI request object.
        :param path: URL path for the POST action.
        :return: Response content, status code, and headers.
        """
        data = await request.json()

        # Use the provided UUID or queueID if available, otherwise generate a new UUID
        identifier = data.get('uuid') or data.get('queueID') or uuid.uuid4()

        if data is not None:
            data['uuid'] = str(identifier)
        else:
            data = {'uuid': str(identifier)}

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = await self.send_request(
            method='POST',
            path=path,
            headers=headers,
            params=request.query_params,
            data=json.dumps(data)
        )

        headers = {}

        if 'Location' in response.headers:
            headers['Location'] = f"{response.headers['Location']}{identifier}"

        response_content = response.text

        try:
            response_json = json.loads(response_content)
            # Wenn die Deserialisierung erfolgreich ist, response_json verwenden
            response_content = response_json
        except json.JSONDecodeError:
            # Wenn die Deserialisierung fehlschlägt, wird response_content als String belassen
            pass

        if response.headers.get('Content-Type', '').startswith('application/json'):
            try:
                body = response.json()
                if body.get("ok", False) and body.get("message", "").endswith(" inserted") and 'redirect' in body:
                    redirect_base = body['redirect']
                    body['redirect'] = f"{redirect_base}{identifier}"
                    response_content = body
            except ValueError:
                pass  # Not a JSON response; do nothing

        return response_content, response.status_code, headers


    def construct_path(self, db_name, resource, param, json_ext, is_search):
        """
        Constructs a new path based on the given parameters.
        :param db_name: Database name.
        :param resource: Resource name.
        :param param: Parameter for the query.
        :param json_ext: JSON extension for the path.
        :param is_search: Indicates if the path is for a search action.
        :return: Constructed path.
        """
        action = 'by' if is_search else 'with'
        return f'{db_name}/get_{resource}_{action}_{param}{json_ext}'

    def determine_path(self, path, params):
        """
        Determines the path based on the provided parameters and existing patterns.
        :param path: Original path.
        :param params: Query parameters.
        :return: Modified path based on parameters.
        """
        for search_param in self.SUPPORTED_SEARCH:
            if path.endswith(f'by_{search_param}.json'):
                return path

        filter_found = False

        for param in params:
            if param in self.SUPPORTED_FILTERS and re.match(self.PATH_PATTERN, path):
                filter_found = True
                db_name, resource, json_ext = re.match(self.PATH_EXTRACT_PATTERN, path).groups()
                path = self.construct_path(db_name, resource, param, json_ext, False)
            elif param in self.SUPPORTED_SEARCH and re.match(self.PATH_PATTERN, path):
                if filter_found:
                    raise ValueError("Both search and filter parameters set. Only one can be provided at a time.")
                db_name, resource, json_ext = re.match(self.PATH_EXTRACT_PATTERN, path).groups()
                path = self.construct_path(db_name, resource, param, json_ext, True)
        
        return path

    def format_response_content(self, response_text):
        """
        Formats the response content from the Memory Service into a more readable structure.
        :param response_text: Response text from the Memory Service.
        :return: Formatted response content and status code.
        """
        response_dict = json.loads(response_text)

        if 'rows' in response_dict and 'columns' in response_dict:
            columns = response_dict['columns']
            rows = response_dict['rows']

            if not rows:
                return {"message": "Resource not found"}, 404

            formatted_rows = [dict(zip(columns, row)) for row in rows]
            return formatted_rows, 200
        else:
            return response_dict, 200

    async def get_action(self, request, path):
        """
        Handles a GET action by sending a request to the Memory Service.
        It adjusts the path based on the parameters and formats the response.
        :param request: The incoming FastAPI request object.
        :param path: URL path for the GET action.
        :return: Response content, status code, and headers.
        """
        params_dict = dict(request.query_params)
        path = self.determine_path(path, params_dict)

        headers = {key: value for (key, value) in request.headers.items() if key != 'Host'}

        body_data = await request.body()

        response = await self.send_request(
            method='GET',
            path=path,
            headers=headers,
            params=request.query_params,
            data=body_data
        )

        response_content = response.text

        response_content, status_code = self.format_response_content(response_content)

        return response_content, status_code, {}