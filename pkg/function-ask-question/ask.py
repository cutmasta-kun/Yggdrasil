import logging
import requests
import json

def validate_messages(messages):
    if not messages:
        return False

    for message in messages:
        if 'role' not in message or 'content' not in message:
            return False

    return True

def send_request(messages, headers, AI_MODEL):
    data = {
        'model': AI_MODEL,
        'messages': messages
    }

    logging.debug(data)

    try:
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        logging.error(f"Http Error: {errh}")
        logging.error(f"Response Message: {response.text}")
        return None, 'Server Error', 500
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
        return None, 'Server Error', 500
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
        return None, 'Server Error', 500
    except requests.exceptions.RequestException as err:
        logging.error(f"Something went wrong: {err}")
        return None, 'Server Error', 500

    logging.debug(response)

    return response.json(), None, 200
