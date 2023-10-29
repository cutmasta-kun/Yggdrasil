# api_server.py
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import logging
import os
import yaml
from tasks_repository import get_tasks_with_metadata, add_task, add_task_with_metadata, get_task_by_queueID, update_task, Task

# Configurate application
logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="Task Queue Manager",
    description="The Task Queue Manager API is responsible for managing and retrieving tasks in a queue system. It supports operations like adding new tasks, retrieving existing tasks, updating task statuses, and querying tasks by their queue ID. The system is designed to efficiently handle task queues for various purposes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class TaskData(BaseModel):
    taskData: str
    metadata: Optional[dict] = None

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

@app.get("/logo.png", include_in_schema=False)
async def plugin_logo():
    return Response(content=open("logo.png", "rb").read(), media_type="image/png")


@app.get("/openapi.yaml", include_in_schema=False)
def get_openapi_yaml():
    openapi_schema = app.openapi()

    order = ['openapi', 'info', 'paths', 'components']
    
    yaml_output = ""
    for key in order:
        section = {key: openapi_schema[key]}
        yaml_output += yaml.dump(section)
    
    return Response(yaml_output, media_type="text/yaml")

@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def plugin_manifest(request: Request):
    host = request.client.host
    return Response(content=open("./ai-plugin.json", "r").read(), media_type="application/json")


@app.get('/get_queues')
async def get_queues():
    tasks = get_tasks_with_metadata(MEMORY_HOST)

    if tasks:
        tasks_list = [task.dict() for task in tasks]
        return tasks_list
    else:
        raise HTTPException(status_code=404, detail="No tasks found")


@app.get('/get_queue_status')
async def get_queue_status(queueID: str):
    task = get_task_by_queueID(MEMORY_HOST, queueID)
    
    if task:
        return task.dict()
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.post('/queue_task')
async def queue_task(task: TaskData):
    new_task = Task(taskData=task.taskData, status='queued', result=None, systemMessage=None, metadata=task.metadata)
    
    if task.metadata:
        queueID = add_task_with_metadata(MEMORY_HOST, new_task)
    else:
        queueID = add_task(MEMORY_HOST, new_task)
    
    if queueID:
        return {
            "status": "queued",
            "queueID": queueID,
            "systemMessage": None
        }
    else:
        raise HTTPException(status_code=500, detail="Error queueing task")


@app.patch('/update_task')
async def update_task_action(task: Task):
    result = update_task(MEMORY_HOST, task)
    if result:
        return {
            "status": "success",
            "message": "Task updated successfully"
        }
    else:
        raise HTTPException(status_code=400, detail="Task update failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5010)
