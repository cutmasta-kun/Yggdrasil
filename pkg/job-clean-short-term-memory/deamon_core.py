import time
import os
import logging
import json
from tasks_repository import Task, get_tasks_with_metadata, update_task, find_task
from common_utils import generate_task_status_from_system_message, generate_system_message, uuid_regex_match

logging.basicConfig(level=logging.INFO)

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

def parse_task_data(task: Task):
    try:
        return json.loads(task.taskData), None
    except json.JSONDecodeError as e:
        logging.error(f"Invalid task data format for task {task.queueID}: {e}")
        return None, f"Invalid task data format: {e}"

def update_task_status(task: Task, success, message=None):
    task.systemMessage = generate_system_message(task) if not message else message
    task_status = generate_task_status_from_system_message(task.systemMessage)
    task.status = task_status if task_status else "failed"
    return update_task(MEMORY_HOST, task)

def check_tasks(task_type, solve_task_function):
    try:
        tasks = get_tasks_with_metadata(MEMORY_HOST)
        if not tasks:
            logging.info('No tasks retrieved or list is empty.')
            return

        task = find_task(tasks, {'status': 'queued', 'metadata.task-type': task_type})
        if not task:
            logging.info(f'No {task_type} task found with the given criteria.')
            return

        task.status = "in-progress"
        task.systemMessage = "Ich bearbeite den Task..."
        update_task(MEMORY_HOST, task)

        success, message = solve_task_function(task)
        update_task_status(task, success, message)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'task' in locals():
            task.status="failed"
            task.result="Es gab ein Problem beim Bearbeiten des Tasks."
            update_task(MEMORY_HOST, task)
        time.sleep(5)
