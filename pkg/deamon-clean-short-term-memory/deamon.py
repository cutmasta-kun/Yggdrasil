# daemon.py
import time
import requests
import os
import logging
import json

# Configurate deamon
logging.basicConfig(level=logging.INFO)

TASK_CREATOR_GET_TASKS = os.getenv('TASK_CREATOR_GET_TASKS', 'http://plugin-memory-interface:5005/tasks/get_tasks_with_metadata.json')
TASK_CREATOR_UPDATE_TASK = os.getenv('TASK_CREATOR_UPDATE_TASK', 'http://plugin-task-creator:5010/update_task')
QUESTION_SOLVER_ASK_QUESTION = os.getenv('QUESTION_SOLVER_ASK_QUESTION', 'http://function-ask-question:5022/ask')

def get_tasks():
    # Step 1: Send a GET request to the memory to retrieve the tasks
    response = requests.get(TASK_CREATOR_GET_TASKS)

    response.raise_for_status()  # Raise an exception if the request was not successful
    return response.json()

def update_task(task, status, system_message):
    # Update the task status and add a system message
    update_response = requests.patch(TASK_CREATOR_UPDATE_TASK, json={
        "queueID": task["queueID"],
        "status": status,
        "result": task.get("result", ""),
        "systemMessage": system_message
    })
    update_response.raise_for_status()  # Raise an exception if the request was not successful

def ask_deepthought(messages):
    response = requests.post(QUESTION_SOLVER_ASK_QUESTION, json={"messages": messages})
    response.raise_for_status()  # Raise an exception if the request was not successful
    return response.json()

def solve_task(task):
    # Call the DeepThought service
    messages = [{"role": "user", "content": task["taskData"]}]

    # Load system messages from system.json
    with open('system.json', 'r') as f:
        system_messages = json.load(f)

    # Prepend system messages to the list of messages
    messages = system_messages + messages

    logging.info('messages assembled...')
    logging.debug(messages)
    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought for task {task['queueID']}: {e}")
        return None
    
    logging.info(f"Response from DeepThought: {deepthought_response}")

    # Extract the result from the DeepThought response
    result = deepthought_response.get('choices', [{}])[0].get('message', {}).get('content', '')

    # Return the task with the result
    task["result"] = result
    return task

def generate_system_message(task):
    # Load system messages from evaluate.json
    with open('evaluate.json', 'r') as f:
        system_messages = json.load(f)

    # Create the user message with the task object in JSON format
    user_message = '\n```json\n' + json.dumps(task) + '\n```\n'
    messages = system_messages + [{"role": "user", "content": user_message}]

    logging.info('messages for system_message assembled...')
    logging.debug(messages)

    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought for task {task['queueID']}: {e}")
        return None
    
    logging.info(f"Response from DeepThought: {deepthought_response}")

    # Extract the result from the DeepThought response
    result = deepthought_response.get('choices', [{}])[0].get('message', {}).get('content', '')

    return result

def find_task(tasks, criteria):
    """
    Find the first task in the list of tasks that satisfies all the criteria.

    :param tasks: List of tasks.
    :param criteria: Dictionary of criteria. Each key-value pair in the dictionary is a criterion that the task must satisfy.
    :return: The first task that satisfies all the criteria, or None if no such task is found.
    """
    for task in tasks:
        if all(task.get(key) == value for key, value in criteria.items()):
            # If the task has metadata, check if it satisfies the criteria
            if 'metadata' in task:
                metadata = json.loads(task['metadata'])
                if all(metadata.get(key) == value for key, value in criteria.items() if key.startswith('metadata.')):
                    return task
            else:
                return task
    return None

def check_tasks():
    try:
        logging.info('getting tasks...')
        tasks = get_tasks()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve tasks: {e}")
        return
    
    # happy_path: found list of tasks
    time.sleep(5)

    logging.info('tasks found...')
    logging.debug(tasks)

    # task = find_task(tasks, {'status': 'queued', 'metadata.type': 'myType'})
    task = find_task(tasks, {'status': 'queued'})

    # happy_path: found task which satisfied criteria

    logging.info('first task with status "queued"...')
    logging.debug(task)

    if task is not None:
        try:
            logging.info('update task status to "in-progress"...')
            update_task(task, "in-progress", "Ich schau mir das mal an...")
        except requests.RequestException as e:
            logging.error(f"Failed to update task {task['queueID']}: {e}")
            return
        time.sleep(5)

        # happy_path: update task to show progress in solving the task 

        try:
            logging.info('try to solve the task...')

            solved_task = solve_task(task)

            # happy_path: taskData got succesfully solved by deepthought service

            if solved_task is not None:
                logging.info('task is solved, analyze result and generate systemMessage...')

                systemMessage = generate_system_message(solved_task)

                if systemMessage is None:
                    logging.info('update task status to "done" without systemMessage...')
                    update_task(solved_task, "done", 'systemMessage grad nicht verfügbar...')
                    return
                
                logging.info('update task status to "done" with systemMessage...')
                update_task(solved_task, "done", systemMessage)

                # happy_path: update task with solved result and analyzed systemmessage

        except requests.RequestException as e:
            logging.error(f"Failed to solve task {task['queueID']}: {e}")
            # Update the task status to 'failed'
            time.sleep(5)
            logging.info('update task status to "failed"...')
            update_task(task, "failed", "Es gab ein Problem beim Lösen des Tasks.")

while True:
    check_tasks()
    time.sleep(60)  # Wait for 1 minute
