# fastapi_server.py
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from deamon_determine_test_memories import check_tasks
import requests
import json
import logging
import os
import yaml

# Konfigurieren der Anwendung
logging.basicConfig(level=logging.WARNING)
app = FastAPI()

def run_check_tasks():
    check_tasks()

# CORS aktivieren
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')
GET_MEMORY_PATH = 'messages/get_memory.json'

TASK_CREATOR_HOST = os.getenv('TASK_CREATOR_HOST', 'http://plugin-task-creator:5010')
TASK_CREATOR_PATH = 'queue_task'

@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components']
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")

from tasks_repository import Task, add_task

@app.post('/create_task_clean')
async def create_task_clean(background_tasks: BackgroundTasks):
    try:
        url = f"{MEMORY_HOST}/{GET_MEMORY_PATH}"
        data = requests.get(url).json()

        logging.debug(url)
        logging.debug(data)
    except Exception as e:
        logging.error(f"Failed to get data from Memory Service: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data from Memory Service")

    with open('./messages/determine_messages_to_delete.txt', 'r') as file:
        task_text = file.read()

    tasks_str = json.dumps(data)

    task_data = task_text.replace('<<TASKS>>', tasks_str)
    
    new_task = Task(
        taskData=task_data,
        status='queued',
        metadata={
            "task-type": "clean-short-memory"
        }
    )

    logging.debug(f"new_task: {new_task}")

    # Versuche, den Task zur Warteschlange hinzuzufügen
    queueID = add_task(MEMORY_HOST, new_task)

    if queueID is None:
        raise HTTPException(status_code=500, detail="Failed to queue task")

    # Füge run_check_tasks als Hintergrund-Task hinzu
    background_tasks.add_task(run_check_tasks)

    # Rückgabe einer Erfolgsmeldung
    return {"detail": "Task successfully queued. Starting job.", "queueID": queueID}

@app.get('/get_task_text')
async def get_task_text():
    try:
        url = f"{MEMORY_HOST}/{GET_MEMORY_PATH}"
        data = requests.get(url).json()

        logging.debug(url)
        logging.debug(data)
    except Exception as e:
        logging.error(f"Failed to get data from Memory Service: {e}")
        raise HTTPException(status_code=500, detail="Failed to get data from Memory Service")

    # Lese den Task-Text aus der Datei
    with open('task_text.txt', 'r') as file:
        task_text = file.read()

    # Konvertiere die Daten in einen formatierten String
    tasks_str = json.dumps(data, indent=4)  # Macht den JSON lesbarer

    # Ersetze den Platzhalter durch die tatsächlichen Daten
    task_data = task_text.replace('<<TASKS>>', tasks_str)

    return task_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5021, log_level="info")
