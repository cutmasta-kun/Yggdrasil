# api_server.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, UUID4
from typing import List, Optional
import logging
import os
from tasks_repository import get_tasks, add_task, get_task_by_queueID, update_task, Task
from fast_api_boilerplate import setup_app
import uuid

PORT = int(os.environ.get('PORT', 5010))

# Configurate application
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Task Queue Manager",
    description="The Task Queue Manager API is responsible for managing and retrieving tasks in a queue system.",
    version="1.0.0",
    openapi_tags=[{
        "name": "Tasks",
        "description": "Operations to manage tasks in the queue.",
    }],
    servers=[{"url": f"http://localhost:{PORT}", "description": "Local server"}],
)

setup_app(app)

class TaskResponse(BaseModel):
    queueID: UUID4
    taskData: str
    status: str
    result: Optional[str]
    systemMessage: Optional[str]
    metadata: Optional[dict]
    parent: Optional[str]
    children: List[str]

class QueueTaskResponse(BaseModel):
    status: str
    queueID: UUID4
    systemMessage: Optional[str]

class UpdateTaskResponse(BaseModel):
    status: str
    message: str

class TaskData(BaseModel):
    taskData: str
    metadata: Optional[dict] = None

MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

@app.get(
    '/get_queues', 
    summary="Get All Queues",
    description="Retrieves a list of all tasks in the queue.",
    response_model=List[TaskResponse],
    tags=["Tasks"]
)
async def get_queues():
    tasks = get_tasks(MEMORY_HOST)

    if tasks:
        tasks_list = [task.model_dump() for task in tasks]
        return tasks_list
    else:
        raise HTTPException(status_code=404, detail="No tasks found")


@app.get(
    '/get_queue_status',
    summary="Get Queue Status",
    description="Retrieves the status of a specific task in the queue by its queue ID.",
    response_model=TaskResponse,
    tags=["Tasks"]
)
async def get_queue_status(queueID: UUID4 = Query(..., description="The ID of the queue to retrieve")):
    task = get_task_by_queueID(MEMORY_HOST, queueID)
    
    if task:
        return task.model_dump()
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.post('/queue_task')
async def queue_task(task: TaskData):
    new_task = Task(taskData=task.taskData, status='queued', result=None, systemMessage=None, metadata=task.metadata)
    
    queueID = add_task(MEMORY_HOST, new_task)
    
    if queueID:
        return {
            "status": "queued",
            "queueID": queueID,
            "systemMessage": None
        }
    else:
        raise HTTPException(status_code=500, detail="Error queueing task")


@app.patch(
    '/update_task', 
    summary="Update a Task",
    description="Updates an existing task in the queue.",
    response_model=UpdateTaskResponse,
    tags=["Tasks"]
)
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
    uvicorn.run(app, host="0.0.0.0", port=PORT)
