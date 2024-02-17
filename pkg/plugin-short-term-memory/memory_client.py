# memory_client.py
import requests
import json
import re
import uuid
import logging
from fastapi import Request

logging.basicConfig(level=logging.INFO)

class MemoryClient:
    """
    A client for interacting with the Memory Service.
    It handles GET, POST, and DELETE actions, transforming them into appropriate requests.
    """

    SUPPORTED_FILTERS = ['limit']
    SUPPORTED_SEARCH = ['uuid', 'queueID', 'id']
    PATH_PATTERN = r'^.+/get_.+\.json$'
    PATH_EXTRACT_PATTERN = r'^(.+)/get_(.+)(\.json)$'

    def __init__(self, memory_host: str, service_name: str):
        """
        Initialize the MemoryClient with a specified memory host.
        :param memory_host: The base URL of the Memory Service.
        """
        self.memory_host = memory_host
        self.service_name = service_name

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

        request_id = str(uuid.uuid4())

        headers['X-Request-ID'] = request_id
        headers['X-Origin-Service'] = self.service_name

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

        try:
            response = await self.send_request(
                method='DELETE',
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
            headers['Location'] = f"{response.headers['Location']}"

        response_content = response.text

        try:
            response_json = json.loads(response_content)
            # Wenn die Deserialisierung erfolgreich ist, response_json verwenden
            response_content = response_json
        except json.JSONDecodeError:
            # Wenn die Deserialisierung fehlschlägt, wird response_content als String belassen
            pass

        return response_content, response.status_code, headers

    async def get_action(self, request, path):
        """
        Handles a GET action by sending a request to the Memory Service.
        It adjusts the path based on the parameters and formats the response.
        :param request: The incoming FastAPI request object.
        :param path: URL path for the GET action.
        :return: Response content, status code, and headers.
        """
        headers = {key: value for (key, value) in request.headers.items() if key != 'Host'}

        body_data = await request.body()

        response = await self.send_request(
            method='GET',
            path=path,
            headers=headers,
            params=request.query_params,
            data=body_data
        )

        return response.json(), response.status_code, {}