# deamon_determine_test_memories.py
import time
import os
import logging
import json
from tasks_repository import Task, get_tasks_with_metadata, update_task, add_task_with_metadata
from common_utils import ask_deepthought, generate_system_message, find_task, uuid_regex_match, generate_task_status_from_system_message
from deamon_delete_memories import check_delete_tasks


logging.basicConfig(level=logging.INFO)

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

def solve_task(task: Task):
    messages = [{"role": "user", "content": task.taskData}]

    with open('system.json', 'r') as f:
        system_messages = json.load(f)

    messages = system_messages + messages

    logging.info('messages assembled...')
    logging.debug(f"messages: {messages}")
    
    try:
        logging.info('asking deepthought...')
        deepthought_response = ask_deepthought(messages)
        logging.debug(f"Response from DeepThought: {deepthought_response}")

        result = deepthought_response.get('messages', [])[-1].get('content', '') if deepthought_response.get('messages') else ''

        task.result = result
        system_message = generate_system_message(task)

        return system_message

    except Exception as e:
        logging.error(f"Failed to ask deepthought for task {task.queueID}: {e}")
        return None

def create_delete_task(task):
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
        return False

    delete_task_data = {
        "taskData": json.dumps({"uuids": uuids_to_delete}),
        "status": "queued",
        "result": None,
        "systemMessage": None,
        "metadata": {"task-type": "delete-memories"}
    }

    new_task = Task(**delete_task_data)
    queueID = add_task_with_metadata(MEMORY_HOST, new_task)

    return queueID is not None

def check_tasks():
    try:
        logging.info('getting tasks...')
        tasks = get_tasks_with_metadata(MEMORY_HOST)

        logging.debug(f"tasks: {tasks}")

        if not tasks:
            logging.info('No tasks retrieved or list is empty.')
            return

        task = find_task(tasks, {'status': 'queued', 'metadata.task-type': 'clean-short-memory'})

        if not task:
            logging.info('No task found with the given criteria.')
            return

        task.status = "in-progress"
        task.systemMessage = "Ich schau mir das mal an..."
        success = update_task(MEMORY_HOST, task)

        if not success:
            logging.error(f"Failed to update task {task.queueID}")
            return

        system_message = solve_task(task)
        task_status = generate_task_status_from_system_message(system_message)

        if task_status == "done":
            task.status = "done"
            task.systemMessage = system_message if system_message else 'Systemnachricht gerade nicht verfügbar...'
            update_success = update_task(MEMORY_HOST, task)

            if not update_success:
                logging.error(f"Failed to update task {task.queueID} after solving")
                return

            logging.info('Task updated successfully after being solved')

            if task.metadata.get("task-type") == "clean-short-memory":
                delete_task_created = create_delete_task(task)
                if delete_task_created:
                    logging.info("Delete task created successfully.")
                    check_delete_tasks()
                else:
                    logging.error("Failed to create delete task.")
        else:
            task.status = "failed"
            task.systemMessage = system_message if system_message else 'Systemnachricht gerade nicht verfügbar...'
            update_task(MEMORY_HOST, task)
            logging.error('Failed to solve the task')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        time.sleep(5)
        update_task(task, "failed", "Es gab ein Problem beim Lösen des Tasks.")

if __name__ == "__main__":
    while True:
        time.sleep(20)
        check_tasks()