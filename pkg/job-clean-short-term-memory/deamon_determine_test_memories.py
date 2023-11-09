# deamon_determine_test_memories.py

import time
import os
import logging
import json
from tasks_repository import Task, update_task, add_task
from common_utils import search_test_entries, setup_task, ask_deepthought, generate_system_message, uuid_regex_match, generate_task_status_from_system_message
from deamon_delete_memories import check_delete_tasks

logging.basicConfig(level=logging.INFO)

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

def parse_task_data(task: Task):
    messages = [{"role": "user", "content": task.taskData}]

    with open('./messages/generate_list.json', 'r') as f:
        system_messages = json.load(f)

    messages = system_messages + messages

    logging.info('messages assembled...')
    logging.debug(f"messages: {messages}")
    return messages

def solve_task(task: Task):
    try:
        messages = parse_task_data(task)

        logging.info('searching for test entries...')
        uuid_list = search_test_entries(messages)

        # Parsen der UUIDs als Liste von Strings
        uuid_dict = [str(uuid) for uuid in uuid_list.uuids]

        logging.debug(f"Test Entries: {uuid_list}")

        task.result = json.dumps(uuid_dict)
        system_message = generate_system_message(task)

        return system_message

    except Exception as e:
        logging.error(f"Failed to ask deepthought for task {task.queueID}: {e}")
        return None

def initialize_task(task: Task):
    task.status = "in-progress"
    task.systemMessage = "Ich schau mir das mal an..."
    return update_task(MEMORY_HOST, task)

def finalize_task(task: Task, success: bool, system_message: str):
    task.status = "done" if success else "failed"
    task.systemMessage = system_message if system_message else 'Systemnachricht gerade nicht verfügbar...'
    return update_task(MEMORY_HOST, task)

def create_delete_task(task: Task):
    try:
        parsed_result = json.loads(task.result)
    except json.JSONDecodeError:
        parsed_result = task.result

    uuids_to_delete = []

    if isinstance(parsed_result, list):
        uuids_to_delete = [uuid for uuid in parsed_result if uuid_regex_match(uuid)]
    elif uuid_regex_match(parsed_result):
        uuids_to_delete.append(parsed_result)

    if not uuids_to_delete:
        return None

    delete_task_data = {
        "taskData": json.dumps({"uuids": uuids_to_delete}),
        "status": "queued",
        "metadata": {"task-type": "delete-memories"},
        "parent": task.queueID
    }

    new_task = Task(**delete_task_data)
    queueID = add_task(MEMORY_HOST, new_task)

    return queueID

def post_process(task: Task):
    new_task_queueID = create_delete_task(task)
    if not new_task_queueID:
        logging.error("Failed to create delete task.")
        return

    logging.info("Delete task created successfully.")
    
    # Füge die QueueID des neuen Tasks zur Liste der children des ursprünglichen Tasks hinzu
    task.children.append(new_task_queueID)
    
    # Aktualisiere den ursprünglichen Task, um die neuen children zu speichern
    if update_task(MEMORY_HOST, task):
        logging.info("Task updated successfully with new children.")
    else:
        logging.error("Failed to update task with new children.")
    
    check_delete_tasks()

def check_tasks():
    try:
        task = setup_task(MEMORY_HOST, {'status': 'queued', 'metadata.task-type': 'clean-short-memory'})
        if not task:
            return

        success = initialize_task(task)
        
        if not success:
            logging.error(f"Failed to update task {task.queueID}")
            return

        system_message = solve_task(task)
        task_status = generate_task_status_from_system_message(system_message)

        if task_status == "done":
            finalize_task(task, True, system_message)
            logging.info('Task updated successfully after being solved')
            post_process(task)
        else:
            finalize_task(task, False, system_message)
            logging.error('Failed to solve the task')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'task' in locals():
            finalize_task(task, False, "Es gab ein Problem beim Lösen des Tasks.")
        time.sleep(5)

if __name__ == "__main__":
    while True:
        time.sleep(20)
        check_tasks()