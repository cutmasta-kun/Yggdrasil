# deamon_delete_memories.py

import time
import os
import logging
import json
from tasks_repository import Task, update_task
from memory_repository import delete_memory_by_uuid
from common_utils import setup_task, generate_task_status_from_system_message, generate_system_message

logging.basicConfig(level=logging.INFO)

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

def parse_task_data(task: Task):
    try:
        return json.loads(task.taskData), None
    except json.JSONDecodeError as e:
        logging.error(f"Invalid task data format for task {task.queueID}: {e}")
        return None, f"Invalid task data format: {e}"

def process_uuids(task: Task, uuids_to_delete):
    result_messages = []
    success_statuses = []

    for uuid in uuids_to_delete:
        success, message = delete_memory_by_uuid(MEMORY_HOST, uuid)
        result_messages.append(message)
        success_statuses.append(success)
        if not success:
            logging.error(f"Failed to delete memory with UUID {uuid} for task {task.queueID}")

    return result_messages, all(success_statuses)

def initialize_task(task: Task):
    task.status = "in-progress"
    task.systemMessage = "Ich lösche die Einträge mal eben..."
    return update_task(MEMORY_HOST, task)

def finalize_task(task: Task, success: bool, result_message: str):
    task.result = result_message
    task.systemMessage = generate_system_message(task)
    task.status = generate_task_status_from_system_message(task.systemMessage) if success else "failed"
    update_task(MEMORY_HOST, task)

def handle_error(task: Task):
    task.status = "failed"
    task.result = "Es gab ein Problem beim Löschen der Erinnerungen."
    update_task(MEMORY_HOST, task)

def check_delete_tasks():
    try:
        task = setup_task(MEMORY_HOST, {'status': 'queued', 'metadata.task-type': 'delete-memories'})
        if not task:
            return

        success = initialize_task(task)

        if not success:
            logging.error(f"Failed to update task {task.queueID}")
            return

        parsed_task_data, error_message = parse_task_data(task)

        if error_message:
            finalize_task(task, False, error_message)
            return

        uuids_to_delete = parsed_task_data.get("uuids", [])
        if not uuids_to_delete:
            logging.info(f"No UUIDs to delete for task {task.queueID}")
            finalize_task(task, True, "No UUIDs to delete.")
            return

        result_messages, success = process_uuids(task, uuids_to_delete)
        finalize_task(task, success, "\n".join(result_messages))

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'task' in locals():
            handle_error(task)
        time.sleep(5)

if __name__ == "__main__":
    while True:
        time.sleep(20)
        check_delete_tasks()
