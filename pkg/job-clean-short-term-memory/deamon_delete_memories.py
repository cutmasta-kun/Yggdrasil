# deamon_delete_memories.py
import time
import os
import logging
import json
from tasks_repository import Task, get_tasks_with_metadata, update_task
from memory_repository import delete_memory_by_uuid
from common_utils import generate_task_status_from_system_message, generate_system_message, find_task

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

def update_task_status(task: Task, success):
    task.systemMessage = generate_system_message(task)
    task_status = generate_task_status_from_system_message(task.systemMessage)
    task.status = task_status if task_status else "failed"

    return update_task(MEMORY_HOST, task)

def solve_delete_task(task: Task):
    parsed_task_data, error_message = parse_task_data(task)
    if error_message:
        task.result = error_message
        return False

    uuids_to_delete = parsed_task_data.get("uuids", [])
    if not uuids_to_delete:
        logging.info(f"No UUIDs to delete for task {task.queueID}")
        return True

    result_messages, success = process_uuids(task, uuids_to_delete)
    task.result = "\n".join(result_messages)
    return success

def check_delete_tasks():
    try:
        tasks = get_tasks_with_metadata(MEMORY_HOST)
        if not tasks:
            logging.info('No tasks retrieved or list is empty.')
            return

        task = find_task(tasks, {'status': 'queued', 'metadata.task-type': 'delete-memories'})
        if not task:
            logging.info('No delete task found with the given criteria.')
            return

        task.status = "in-progress"
        task.systemMessage = "Ich lösche die Einträge mal eben..."
        update_task(MEMORY_HOST, task)

        success = solve_delete_task(task)
        update_task_status(task, success)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'task' in locals():
            task.status="failed"
            task.result="Es gab ein Problem beim Löschen der Erinnerungen."
            update_task(MEMORY_HOST, task)
        time.sleep(5)

if __name__ == "__main__":
    while True:
        time.sleep(20)
        check_delete_tasks()
