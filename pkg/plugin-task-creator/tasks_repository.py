# tasks_repository.py
#
# version=1.5
#
###
import uuid
import logging
import requests
import json
from pydantic import BaseModel
from typing import List, Optional

logging.basicConfig(level=logging.INFO)

class Task(BaseModel):
    queueID: str = None
    taskData: str
    status: str
    result: str = None
    systemMessage: str = None
    metadata: Optional[dict] = None
    parent: Optional[str] = None
    children: List[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        if self.queueID is None:
            self.queueID = str(uuid.uuid4())

        # Stelle sicher, dass die children-Liste immer eine Liste ist
        if not isinstance(self.children, list):
            self.children = json.loads(self.children)

def json_serialize_if_needed(data, key):
    """
    Serializes the specified key in the data dictionary to JSON if it exists.
    :param data: Dictionary containing the data.
    :param key: Key to be serialized.
    """
    if data.get(key) is not None:
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

    data = task.dict()

    json_serialize_if_needed(data, 'metadata')
    json_serialize_if_needed(data, 'children')

    logging.debug(data)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return task.queueID
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
    try:
        metadata_dict = json.loads(task_data.get("metadata", "{}"))
    except json.JSONDecodeError:
        logging.error(f"Error decoding metadata: {task_data.get('metadata')}")
        metadata_dict = {}

    task_data["metadata"] = metadata_dict

    # Convert children to a list if it's a string
    children_str = task_data.get("children", "[]")
    try:
        children_list = json.loads(children_str)
    except json.JSONDecodeError:
        logging.error(f"Error decoding children: {children_str}")
        children_list = []

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

    data = task.dict()
    json_serialize_if_needed(data, 'metadata')
    json_serialize_if_needed(data, 'children')

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        logging.info("Task updated successfully.")
        return True
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}. Response text: {response.text if response else 'No response'}")
        return False

    return False
