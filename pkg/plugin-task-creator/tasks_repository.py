# tasks_repository.py
import uuid
import logging
import requests
import json

# Configurate application
logging.basicConfig(level=logging.INFO)

def add_task(host, task):
    """
    Create a new task into the tasks table
    :param host: The host URL of the Datasette instance
    :param task: A list representing the task
    :return: queueID
    """
    # Generate a unique queueID
    queueID = str(uuid.uuid4())
    # Update the queueID in the task
    task[0] = queueID
    # Define the URL for the add_task query
    url = f"{host}/tasks/add_task.json"
    # Define the headers for the POST request
    headers = {
        'Content-Type': 'application/json'
    }
    logging.debug(task)
    # Define the data for the POST request
    data = {
        "queueID": queueID,
        "taskData": task[1],
        "status": task[2],
        "result": task[3],
        "systemMessage": task[4]
    }
    logging.debug(data)
    try:
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Check if the request was successful
        response.raise_for_status()
        # Return the queueID
        return queueID
    except requests.exceptions.HTTPError as errh:
        # Log the error and return None
        print(f"Http Error: {errh}")
        print(f"Response Message: {response.text}")  # Add this line
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    return None

def get_task_by_queueID(host, queueID):
    """
    Query task by queueID
    :param host: The host of the Datasette server
    :param queueID: queueID of the task
    :return: task data
    """
    # Define the URL
    url = f"{host}/tasks/get_tasks_by_queueID.json"
    # Define the parameters
    params = {"queueID": queueID}
    try:
        # Send the GET request
        response = requests.get(url, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Check if any tasks were returned
            if data and "rows" in data and len(data["rows"]) > 0:
                # Return the first task
                return data["rows"][0]
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

def get_tasks(host):
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
                # Return all
                return data["rows"]
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

def update_task(host, task):
    """
    Update a task in the tasks table
    :param host: The host URL of the Datasette instance
    :param task: A dictionary representing the task
    :return: True if successful, False otherwise
    """
    # Check if the necessary fields are in the task
    valid_statuses = [
        'in-progress',
        'failed',
        'done',
        'queued',
        'need-review'
        ]

    logging.debug(task)

    if not all(key in task for key in ("queueID", "status", "systemMessage")) or task["status"] not in valid_statuses:
        logging.debug('task not valid')
        return False

    logging.debug('task is valid')

    # Define the URL for the update_task query
    url = f"{host}/tasks/update_task.json"
    logging.debug(url)
    # Define the headers for the POST request
    headers = {
        'Content-Type': 'application/json'
    }
    # Define the data for the POST request
    data = {
        "queueID": task["queueID"],
        "status": task["status"],
        "result": task.get("result", None),
        "systemMessage": task["systemMessage"]
    }

    logging.debug(data)

    try:
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Check if the request was successful
        response.raise_for_status()
        # Return True if the update was successful
        return True
    except requests.exceptions.HTTPError as errh:
        # Log the error and return False
        print(f"Http Error: {errh}")
        print(f"Response Message: {response.text}")  # Add this line
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")
    return False
