# tasks_repository.py
#
# version=1.2
#
###
import uuid
import logging
import requests
import json
from pydantic import BaseModel
from pydantic import parse_obj_as
from typing import List, Optional

# Configurate application
logging.basicConfig(level=logging.INFO)

import uuid

class Task(BaseModel):
    queueID: str = None
    taskData: str
    status: str
    result: str = None
    systemMessage: str = None
    metadata: Optional[dict] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.queueID is None:
            self.queueID = str(uuid.uuid4())

def add_task(host: str, task: Task) -> Optional[str]:
    """
    Create a new task into the tasks table
    :param host: The host URL of the Datasette instance
    :param task: An instance of Task class
    :return: queueID or None
    """
    url = f"{host}/tasks/add_task.json"
    headers = {'Content-Type': 'application/json'}

    # Convert the task to a dictionary and remove the 'metadata' field
    data = task.dict(exclude={'metadata'})

    logging.debug(f"Task data being sent: {data}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        logging.info(f"Task added successfully with queueID: {task.queueID}")
        return task.queueID
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}. Response text: {response.text}")
    except requests.exceptions.ConnectionError as err:
        logging.error(f"Error connecting to the server: {err}")
    except requests.exceptions.Timeout as err:
        logging.error(f"Timeout error: {err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}")

    return None

def add_task_with_metadata(host, task: Task):
    """
    Create a new task with metadata into the tasks table
    :param host: The host URL of the Datasette instance
    :param task: An instance of Task class
    :return: queueID or None
    """
    if task.metadata is None:
        print("Metadata is required for add_task_with_metadata")
        return None

    url = f"{host}/tasks/add_task_with_metadata.json"
    headers = {
        'Content-Type': 'application/json'
    }

    # Convert the Task instance to a dictionary
    data = task.dict()

    # Ensure metadata is serialized to JSON if it is not None
    if data.get('metadata') is not None:
        data['metadata'] = json.dumps(data['metadata'])

    logging.debug(f"data in add_task_with_metadata: {data}")

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        logging.debug(f"response from task creation: {response.json()}")
        
        return task.queueID
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if response:
            print(f"Response Message: {response.text}")
        return None

def get_task_by_queueID(host: str, queueID: str) -> Optional[Task]:
    """
    Query task by queueID
    :param host: The host of the Datasette server
    :param queueID: queueID of the task
    :return: Task object or None
    """
    url = f"{host}/tasks/get_tasks_by_queueID.json"
    params = {"queueID": queueID}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # This will check if the request was successful

        data = response.json()
        rows = data.get("rows")
        if rows and len(rows) > 0:
            row = rows[0]  # Get the first row (task details)

            # Attempt to deserialize the metadata field into a dictionary
            metadata_str = row[5] if len(row) > 5 else "{}"
            try:
                metadata_dict = json.loads(metadata_str)
            except json.JSONDecodeError:
                logging.error(f"Error decoding metadata: {metadata_str}")
                metadata_dict = {}  # Use an empty dictionary if decoding fails

            # Create a dictionary representing the task
            task_data = {
                "queueID": row[0],
                "taskData": row[1],
                "status": row[2],
                "result": row[3],
                "systemMessage": row[4],
                "metadata": metadata_dict
            }

            # Create and return a Task object
            return Task(**task_data)

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")  # Log the error
    except requests.exceptions.ConnectionError as err:
        logging.error(f"Error connecting to the server: {err}")
    except requests.exceptions.Timeout as err:
        logging.error(f"Timeout error: {err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}")

    return None  # Return None if any exception occurs or no task is found

def get_tasks(host) -> Optional[List[Task]]:
    """
    Get all tasks
    :param host: The host of the Datasette server
    :return: taskList
    """
    # Define the URL
    url = f"{host}/tasks/get_tasks.json"

    try:
        # Send the GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Check if any tasks were returned
            if data and "rows" in data and len(data["rows"]) > 0:
                # Prepare a list to hold Task objects
                tasks = []
                # Map the column names to their respective values in each row
                for task_data in data:

                    task_dict = {
                        "queueID": task_data.get('queueID'),
                        "taskData": task_data.get('taskData'),
                        "status": task_data.get('status'),
                        "result": task_data.get('result'),
                        "systemMessage": task_data.get('systemMessage')
                    }

                    # Create a Task object from the dictionary and append it to the list
                    tasks.append(Task(**task_dict))
                
                return tasks
    except requests.exceptions.HTTPError as errh:
        # Log the error and return None
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    # If the request was not successful or no tasks were returned, return None
    return None

def get_tasks_with_metadata(host) -> Optional[List[Task]]:
    """
    Get all tasks
    :param host: The host of the Datasette server
    :return: taskList
    """
    # Define the URL
    url = f"{host}/tasks/get_tasks_with_metadata.json"

    try:
        # Send the GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Check if any tasks were returned
            if data:
                # Prepare a list to hold Task objects
                tasks = []

                for task_data in data:
                    # Deserialize the metadata field into a dictionary
                    metadata_str = task_data.get('metadata', "{}")

                    try:
                        metadata_dict = json.loads(metadata_str)
                    except json.JSONDecodeError:
                        logging.error(f"Error decoding metadata: {metadata_str}")
                        metadata_dict = {}  # Use an empty dictionary if decoding fails

                    task_dict = {
                        "queueID": task_data.get('queueID'),
                        "taskData": task_data.get('taskData'),
                        "status": task_data.get('status'),
                        "result": task_data.get('result'),
                        "systemMessage": task_data.get('systemMessage'),
                        "metadata": metadata_dict
                    }

                    # Create a Task object from the dictionary and append it to the list
                    tasks.append(Task(**task_dict))
                
                return tasks
    except requests.exceptions.HTTPError as errh:
        # Log the error and return None
        logging.error(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Something went wrong: {err}")
    # If the request was not successful or no tasks were returned, return None
    return None

def update_task(host: str, task: Task) -> bool:
    """
    Update a task in the tasks table
    :param host: The host URL of the Datasette instance
    :param task: An instance of Task class
    :return: True if successful, False otherwise
    """
    # Define valid statuses
    valid_statuses = ['in-progress', 'failed', 'done', 'queued', 'need-review']

    # Validate the task's status
    if task.status not in valid_statuses:
        logging.error('Invalid task status')
        return False

    logging.debug(f"Updating task: {task}")

    url = f"{host}/tasks/update_task.json"
    headers = {'Content-Type': 'application/json'}

    # Convert the task to a dictionary
    data = task.dict()

    # Ensure metadata is serialized to a JSON string if it is not None
    if data.get('metadata') is not None:
        data['metadata'] = json.dumps(data['metadata'])

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        logging.info("Task updated successfully.")
        return True
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}. Response text: {response.text}")
    except requests.exceptions.ConnectionError as err:
        logging.error(f"Error connecting to the server: {err}")
    except requests.exceptions.Timeout as err:
        logging.error(f"Timeout error: {err}")
    except requests.exceptions.RequestException as err:
        logging.error(f"A request error occurred: {err}")

    return False
