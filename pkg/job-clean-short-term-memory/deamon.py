# daemon.py
import time
import requests
import os
import logging
import json
from tasks_repository import Task, get_tasks_with_metadata, update_task

# Configurate deamon
logging.basicConfig(level=logging.INFO)

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')
QUESTION_SOLVER_ASK_QUESTION = os.getenv('QUESTION_SOLVER_ASK_QUESTION', 'http://function-ask-question:5022/ask')

def ask_deepthought(messages):
    response = requests.post(QUESTION_SOLVER_ASK_QUESTION, json={"messages": messages})
    response.raise_for_status()  # Raise an exception if the request was not successful
    
    return response.json()

def solve_task(task: Task):
    # Call the DeepThought service
    messages = [{"role": "user", "content": task.taskData}]

    # Load system messages from system.json
    with open('system.json', 'r') as f:
        system_messages = json.load(f)

    # Prepend system messages to the list of messages
    messages = system_messages + messages

    logging.info('messages assembled...')
    logging.debug(f"messages: {messages}")
    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
        logging.debug(f"Response from DeepThought: {deepthought_response}")

        result = ''

        # Extract the result from the DeepThought response
        messages = deepthought_response.get('messages', [])
        if messages:
            result = messages[-1].get('content', '')
        else:  
            logging.warning("No messages in DeepThought's response.")

        # Aktualisieren des Task-Objekts mit dem Ergebnis
        task.result = result

        # Generieren eines Systemnachrichten basierend auf dem gelösten Task
        system_message = generate_system_message(task)  # Diese Funktion sollte auch ein Task-Objekt akzeptieren und verarbeiten

        return True, system_message  # Rückgabe des Erfolgsstatus und der Systemnachricht

    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought for task {task.queueID}: {e}")
        return False, None  # Rückgabe von False und None im Fehlerfall

from pydantic.json import pydantic_encoder

def generate_system_message(task):
    # Load system messages from evaluate.json
    with open('evaluate.json', 'r') as f:
        system_messages = json.load(f)

    # Convert the task object to a JSON-compatible dict using Pydantic's encoder
    task_dict = task.dict()
    task_json = json.dumps(task_dict, default=pydantic_encoder)  # Encode the Pydantic model properly

    # Create the user message with the task object in JSON format
    user_message = '\n```json\n' + task_json + '\n```\n'
    messages = system_messages + [{"role": "user", "content": user_message}]

    logging.info('messages for system_message assembled...')
    logging.debug(messages)

    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
    except requests.RequestException as e:
        logging.error(f"Failed to ask deepthought for task {task.queueID}: {e}")  # Access queueID as an attribute
        return None

    # Extract the result from the DeepThought response
    messages = deepthought_response.get('messages', [])
    if messages:
        result = messages[-1].get('content', '')
    else:
        result = ''
        logging.warning("No messages in DeepThought's response.")

    return result

def find_task(tasks, criteria):
    """
    Findet die erste Aufgabe in der Liste der Aufgaben, die allen Kriterien entspricht.

    :param tasks: Liste von Aufgaben.
    :param criteria: Wörterbuch der Kriterien. Jedes Schlüssel-Wert-Paar im Wörterbuch ist ein Kriterium, das die Aufgabe erfüllen muss.
    :return: Die erste Aufgabe, die allen Kriterien entspricht, oder None, wenn keine solche Aufgabe gefunden wird.
    """

    logging.debug(f"tasks in find_task: {tasks}")

    for task in tasks:
        # Wir verwenden hier die hasattr und getattr Funktionen, um mit Objektattributen zu arbeiten
        if all(hasattr(task, key) and getattr(task, key) == value for key, value in criteria.items() if not key.startswith('metadata.')):
            # Wenn die Aufgabe Metadaten hat, prüfen Sie, ob sie den Kriterien entspricht
            if task.metadata:  # da 'metadata' ein Attribut des Task-Objekts ist
                if all(task.metadata.get(key.split('.', 1)[1]) == value for key, value in criteria.items() if key.startswith('metadata.')):
                    return task
            else:
                return task
    return None

def check_tasks():
    try:
        logging.info('getting tasks...')
        tasks = get_tasks_with_metadata(MEMORY_HOST)
        logging.debug(f"tasks found: {tasks}")
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve tasks: {e}")
        return  # Beenden, wenn ein Fehler bei der Abfrage der Aufgaben auftritt

    if not tasks:  # Überprüfen, ob tasks eine leere Liste oder None ist
        logging.info('No tasks retrieved or list is empty.')
        return  # Beenden, wenn keine Aufgaben abgerufen wurden oder die Liste leer ist

    logging.debug(f"tasks found: {tasks}")

    task = find_task(tasks, {'status': 'queued', 'metadata.task-type': 'clean-short-memory'})

    if not task:
        logging.info('No task found with the given criteria.')
        return

    logging.debug(f"task found: {task}")

    # Attributwerte des Task-Objekts aktualisieren
    task.status = "in-progress"
    task.systemMessage = "Ich schau mir das mal an..."

    try:
        logging.info('update task status to "in-progress"...')
        success = update_task(MEMORY_HOST, task)
        if not success:
            logging.error(f"Failed to update task {task.queueID}")
            return
    except Exception as e:  # Hier fangen wir allgemeine Ausnahmen ab, da update_task bereits spezifische HTTP-Fehler behandelt
        logging.error(f"An error occurred: {e}")
        return

    try:
        logging.info('try to solve the task...')

        success, system_message = solve_task(task)  # Ändern der Funktion, um Erfolg und systemMessage zurückzugeben

        if success:
            task.status = "done"
            task.systemMessage = system_message if system_message is not None else 'systemMessage gerade nicht verfügbar...'

            update_success = update_task(MEMORY_HOST, task)
            if not update_success:
                logging.error(f"Failed to update task {task.queueID} after solving")
                return

            logging.info('Task updated successfully after being solved')
        else:
            logging.error('Failed to solve the task')

    except requests.RequestException as e:
        logging.error(f"Failed to solve task {task['queueID']}: {e}")
        # Update the task status to 'failed'
        time.sleep(5)
        logging.info('update task status to "failed"...')
        update_task(task, "failed", "Es gab ein Problem beim Lösen des Tasks.")

while True:
    time.sleep(20)
    check_tasks()
    
