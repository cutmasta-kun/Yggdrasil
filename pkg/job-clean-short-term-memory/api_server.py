# fastapi_server.py
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import json
import logging
import os
import yaml

# Konfigurieren der Anwendung
logging.basicConfig(level=logging.WARNING)
app = FastAPI()

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
GET_MEMORY_PATH = 'messages/get_memories.json'

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

@app.post('/create_task_clean')
async def create_task_clean():
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

    # Erstelle die URL und die Anforderungsdaten für den Task Creator
    task_creator_url = f"{TASK_CREATOR_HOST}/{TASK_CREATOR_PATH}"
    task_creator_data = {
        "taskData": task_data,
        "metadata": {
            "task-type": "clean-short-memory"
            }
        }

    try:
        # Füge den Task zur Warteschlange hinzu
        response = requests.post(task_creator_url, json=task_creator_data)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to queue task: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue task")

    return {"detail": "Task successfully queued"}

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
