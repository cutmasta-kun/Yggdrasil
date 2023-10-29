import requests
import json
import re
import logging
import os

# Globale Konstanten
QUESTION_SOLVER_ASK_QUESTION = os.getenv('QUESTION_SOLVER_ASK_QUESTION', 'http://function-ask-question:5022/ask')

def ask_deepthought(messages):
    response = requests.post(QUESTION_SOLVER_ASK_QUESTION, json={"messages": messages})
    response.raise_for_status()
    return response.json()

from pydantic.json import pydantic_encoder

def generate_task_status_from_system_message(system_message: str):
    valid_statuses = {'in-progress', 'failed', 'done'}

    messages = [{"role": "user", "content": system_message}]

    with open('evaluate_task_status.json', 'r') as f:
        system_messages = json.load(f)
    
    messages = system_messages + messages

    logging.info('messages for task status assembled...')
    logging.debug(messages)

    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought")
        return None

    messages = deepthought_response.get('messages', [])
    if messages:
        result = messages[-1].get('content', '').strip().lower()
    else:
        result = ''
        logging.warning("No messages in DeepThought's response.")

    logging.debug(f"result task status: {result}")

    if result in valid_statuses:
        return result
    else:
        logging.error(f"Invalid task status received: '{result}'. Expected one of {valid_statuses}")
        return None

def generate_system_message(task, system_messages_path='evaluate_system_message.json'):
    with open(system_messages_path, 'r') as f:
        system_messages = json.load(f)

    task_dict = task.dict()
    task_json = json.dumps(task_dict, default=pydantic_encoder)

    user_message = '\n```json\n' + task_json + '\n```\n'
    messages = system_messages + [{"role": "user", "content": user_message}]

    logging.info('messages for system_message assembled...')
    logging.debug(messages)

    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought for task {task.queueID}: {e}")
        return None

    messages = deepthought_response.get('messages', [])
    if messages:
        result = messages[-1].get('content', '')
    else:
        result = ''
        logging.warning("No messages in DeepThought's response.")

    logging.debug(f"result system_message: {result}")

    return result

def find_task(tasks, criteria):
    for task in tasks:
        if all(hasattr(task, key) and getattr(task, key) == value for key, value in criteria.items() if not key.startswith('metadata.')):
            if task.metadata:
                if all(task.metadata.get(key.split('.', 1)[1]) == value for key, value in criteria.items() if key.startswith('metadata.')):
                    return task
            else:
                return task
    return None

def uuid_regex_match(uuid):
    uuid_regex = re.compile(r'\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b')
    return uuid_regex.match(uuid)

