# communicate.py
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import multiprocessing
import time
import logging

# Configurate daemon
logging.basicConfig(level=logging.INFO)

NTFY_HOST = os.environ.get('NTFY_HOST', "https://ntfy.sh")

def create_session(max_retries=5):
    s = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    return s

SESSION = create_session()

def get_listen_topics_from_env():
    listen_topics_json = os.getenv('LISTEN_TOPICS', '[]')  # Set default to an empty JSON array
    logging.info(f"listen_topics_json: {listen_topics_json}")
    try:
        topics_list = json.loads(listen_topics_json)
        listen_topics = {item['topic']: item['endpoint'] for item in topics_list}
        return listen_topics
    except json.JSONDecodeError:
        logging.error("Error decoding the LISTEN_TOPICS JSON string.")
        return {}

def load_listen_topics(retries=10, delay=2):
    for _ in range(retries):
        listen_topics = get_listen_topics_from_env()
        if listen_topics:
            return listen_topics
        logging.info('... Communication System booting...')
        time.sleep(delay)
    return {}

def head_request(session, endpoint):
    return session.head(endpoint)

def wait_for_function(endpoint, max_retries=5, delay=2, request_function=head_request):
    if not endpoint:
        logging.error("No endpoint provided!")
        return False  # Guard condition
    
    s = requests.Session()
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    s.mount("http://", adapter)
    s.mount("https://", adapter)

    for i in range(max_retries):
        try:
            response = request_function(s, endpoint)
            response.raise_for_status()
            logging.info(f"Connected to the function at {endpoint} on attempt {i+1}")
            return
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.RequestException) as err:
            logging.debug(f"Attempt {i+1}: {err}")
        time.sleep(delay)
    raise Exception(f"Could not connect to the function at {endpoint} after {max_retries} attempts")

def subscribe_to_topic_and_forward_messages(topic, endpoint, get_request_function=SESSION.get, post_request_function=SESSION.post):
    if not topic or not endpoint:
        logging.error("Either topic or endpoint is missing!")
        return  # Guard condition
    
    wait_for_function(endpoint)
    logging.debug(f"Subscribing to topic: {topic} and sending messages to endpoint: {endpoint}")
    
    try:
        response = get_request_function(f"{NTFY_HOST}/{topic}/json", stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            if line:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    logging.error(f"Failed to decode message: {line}")
                    continue
                logging.debug(message)
                try:
                    post_request_function(endpoint, json=message)
                except requests.RequestException as err:
                    logging.error(f"Failed to post message to {endpoint}: {err}")
                    time.sleep(2)  # Add a delay in case of errors

    except requests.RequestException as err:
        logging.error(f"Failed to subscribe to topic {topic}: {err}")
        time.sleep(2)

def main():
    logging.info('Start Communication System... ')

    listen_topics = load_listen_topics()

    if not listen_topics:
        logging.error('... Communication System failed: No Topics to listen to')
        return

    processes = []
    for topic, endpoint in listen_topics.items():
        process = multiprocessing.Process(target=subscribe_to_topic_and_forward_messages, args=(topic, endpoint))
        processes.append(process)
        process.start()

    logging.info('... Communication System running')

    # Warte, bis alle run_ntfy-Aufrufe abgeschlossen sind
    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
