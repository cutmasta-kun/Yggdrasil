# tasks_repository.py
#
# version=1.6
#
###
import uuid
import logging
import requests
import json
from pydantic import BaseModel, validator, root_validator
from typing import List, Optional, Dict

logging.basicConfig(level=logging.INFO)

class Task(BaseModel):
    queueID: Optional[str] = None
    taskData: Optional[str] = None
    status: str
    result: Optional[str] = None
    systemMessage: Optional[str] = None
    metadata: Optional[Dict] = '{}'
    parent: Optional[str] = None
    children: List[str] = []

    @root_validator(pre=True)
    def ensure_queueID(cls, values):
        if 'queueID' not in values or values['queueID'] is None:
            values['queueID'] = str(uuid.uuid4())
        return values

    @validator('children', pre=True)
    def ensure_children_is_list(cls, v):
        if not isinstance(v, list):
            return json.loads(v)
        return v

import json

def json_serialize_if_needed(data, key):
    """
    Serializes the specified key in the data dictionary to JSON if it is not already a JSON string.
    :param data: Dictionary containing the data.
    :param key: Key to be serialized.
    """
    if key in data and data[key] is not None:
        try:
            # Versucht, den Wert zu deserialisieren, um zu überprüfen, ob er bereits ein JSON-String ist
            json.loads(data[key])
        except (json.JSONDecodeError, TypeError):
            # Wenn ein Fehler auftritt, bedeutet dies, dass der Wert noch kein JSON-String ist
            data[key] = json.dumps(data[key])


def add_task(host, task):
    """
    Create a new task with metadata into the tasks table
    :param host: The host URL of the Datasette instance
    :param task: An instance of Task class
    :return: queueID or None
    """

    url = f"{host}/tasks/add_task.json"
    headers = {
        'Content-Type': 'application/json'
    }

    data = task.model_dump()

    json_serialize_if_needed(data, 'metadata')
    json_serialize_if_needed(data, 'children')

    logging.debug(data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        logging.info(f"response: {response.json()}")
        logging.info("Task updated successfully. Refetching the task")
        refetch_task = get_task_by_queueID(host, task.queueID)
        logging.info(f"refetched task: {refetch_task}")
        return refetch_task
    except requests.exceptions.RequestException as e:
        logging.error(f"An error occurred: {e}")
        if response:
            logging.error(f"Response Message: {response.text}")
        return None

def parse_task_data(task_data):
    """
    Parse task data and convert metadata to a dictionary.
    :param task_data: A dictionary containing task data.
    :return: Task object.
    """
    metadata = task_data.get("metadata", {})

    # Überprüfen, ob metadata ein gültiger String für json.loads() ist
    if isinstance(metadata, str):
        try:
            metadata_dict = json.loads(metadata)
        except json.JSONDecodeError:
            metadata_dict = {}
    else:
        metadata_dict = metadata if isinstance(metadata, dict) else {}

    task_data["metadata"] = metadata_dict

    # Convert children to a list if it's a string
    children_str = task_data.get("children", "[]")
    if isinstance(children_str, str):
        try:
            children_list = json.loads(children_str)
        except json.JSONDecodeError:
            logging.error(f"Error decoding children: {children_str}")
            children_list = []
    else:
        children_list = children_str if isinstance(children_str, list) else []

    task_data["children"] = children_list

    return Task(**task_data)

def get_task_by_queueID(host: str, queueID: str) -> Optional[Task]:
    """
    Query task by queueID
    :param host: The host of the Datasette server
    :param queueID: queueID of the task
    :return: Task object or None
    """
    url = f"{host}/tasks/get_task_by_queueID.json"
    params = {"queueID": queueID}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        response_queue_id = str(data[0]['queueID'])
        input_queue_id = str(queueID)

        if response_queue_id == input_queue_id:
            return parse_task_data(data[0])
    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred: {err}")

    return None

def get_tasks(host) -> Optional[List[Task]]:
    """
    Get all tasks
    :param host: The host of the Datasette server
    :return: taskList
    """
    url = f"{host}/tasks/get_task.json"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if data:
                tasks = [parse_task_data(task_data) for task_data in data]
                return tasks
    except requests.exceptions.RequestException as err:
        logging.error(f"Something went wrong: {err}")

    return None

def update_task(host: str, task: Task) -> bool:
    """
    Update a task in the tasks table
    :param host: The host URL of the Datasette instance
    :param task: An instance of Task class
    :return: True if successful, False otherwise
    """
    valid_statuses = ['in-progress', 'failed', 'done', 'queued', 'need-review']

    if task.status not in valid_statuses:
        logging.error('Invalid task status')
        return False

    logging.debug(f"Updating task: {task}")

    url = f"{host}/tasks/update_task.json"
    headers = {'Content-Type': 'application/json'}

    data = task.model_dump()
    json_serialize_if_needed(data, 'metadata')
    json_serialize_if_needed(data, 'children')

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        logging.info(f"response: {response.json()}")
        logging.info("Task updated successfully. Refetching the task")
        refetch_task = get_task_by_queueID(host, task.queueID)
        logging.info(f"refetched task: {refetch_task}")
        return refetch_task
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}. Response text: {response.text if response else 'No response'}")
        return None
