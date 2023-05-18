# main.py
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import multiprocessing
from logger import getLogger
import time
import requests

logger = getLogger()

def get_listen_topics_from_env():
    listen_topics = {}
    logger.debug(os.environ.items())
    for key, value in os.environ.items():
        if key.startswith('LISTEN_TOPIC_'):
            topic = key[len('LISTEN_TOPIC_'):]
            listen_topics[topic] = value
    
    return listen_topics

def head_request(session, endpoint):
    return session.head(endpoint)

def wait_for_function(endpoint, max_retries=5, delay=1, request_function=head_request):
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
            logger.debug(f"Connected to the function at {endpoint} on attempt {i+1}")
            return
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError,
                requests.exceptions.Timeout, requests.exceptions.RequestException) as err:
            logger.debug(f"Attempt {i+1}: {err}")
        time.sleep(delay)
    raise Exception(f"Could not connect to the function at {endpoint} after {max_retries} attempts")

def subscribe_to_topic_and_forward_messages(topic, endpoint, get_request_function=requests.get, post_request_function=requests.post):
    wait_for_function(endpoint)
    logger.debug(f"Subscribing to topic: {topic} and sending messages to endpoint: {endpoint}")
    
    response = get_request_function(f"https://ntfy.sh/{topic}/json", stream=True)

    for line in response.iter_lines():
        if line:
            message = json.loads(line)
            logger.debug(message)
            post_request_function(endpoint, json=message)

def main():
    logger.info('Start Communication System... ')

    listen_topics = {}
    for _ in range(10):  # Versuche 10 mal, die Umgebungsvariablen zu bekommen
        listen_topics = get_listen_topics_from_env()
        if listen_topics:
            break
        else:
            logger.info('... Communication System booting...')
            time.sleep(1)

    if not listen_topics:
        logger.error('... Communication System failed: No Topics to listen to')
        return

    processes = []
    for topic, endpoint in listen_topics.items():
        process = multiprocessing.Process(target=subscribe_to_topic_and_forward_messages, args=(topic, endpoint))
        processes.append(process)
        process.start()

    logger.info('... Communication System running')

    # Warte, bis alle run_ntfy-Aufrufe abgeschlossen sind
    while True:
        if all(not process.is_alive() for process in processes):
            break

if __name__ == "__main__":
    main()
