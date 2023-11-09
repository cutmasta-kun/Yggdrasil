# memory_repository.py

import requests
import logging
import json

logging.basicConfig(level=logging.INFO)

def delete_memory_by_uuid(host, uuid): 
    url = f"{host}/messages/delete_memory_by_uuid.json"
    headers = {'Content-Type': 'application/json'}

    data = {
        "uuid": uuid 
    }

    try:
        response = requests.delete(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        response_json = response.json()

        message = response_json.get("message", "Unknown response")
        return True, f"{message}. UUID: {uuid}"
    except requests.exceptions.HTTPError:
        message = "Resource not found"
        logging.error(f"{message}. UUID: {uuid}")
        return False, f"{message}. UUID: {uuid}"
    except requests.exceptions.ConnectionError as err:
        logging.error(f"Error connecting to the server: {err}")
    except requests.exceptions.Timeout as err:
        logging.error(f"Timeout error: {err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}")

    return False, f"Error occurred. UUID: {uuid}"
