# api_server.py
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel, UUID4, Field
from typing import List, Optional, Any
import logging
import time
import os
from tasks_repository import get_tasks, add_task, get_task_by_queueID, update_task, Task
from fast_api_boilerplate import setup_app, ServerTimingMiddleware
import uuid

PORT = int(os.environ.get('PORT', 5010))
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://plugin-memory-interface:5005')

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

app.add_middleware(ServerTimingMiddleware)

class QueueTaskPayload(BaseModel):
    taskData: str
    metadata: Optional[dict] = None

class Response(BaseModel):
    result: Any = None
    error: bool = Field(default=False)
    message: Optional[str] = None

@app.get(
    '/get_queues', 
    summary="Get All Tasks in Queues",
    description="Retrieves a comprehensive list of all tasks currently present in the queue system. This is useful for getting an overview of all tasks and their statuses.",
    operation_id="getAllQueuedTasks",
    response_model=Response,
    tags=["Tasks"])
async def get_queues(request: Request):
    try:
        tasks = get_tasks(MEMORY_HOST)
        tasks_list = [task.model_dump() for task in tasks] if tasks else []
        request.state.timing_marks.append(('tasks-load', time.time()))
        return Response(result=tasks_list)
    except Exception as e:
        return Response(error=True, message=str(e))

@app.get(
    '/get_queue_status',
    summary="Retrieve Specific Task Status",
    description="Provides detailed status information for a specific task identified by its queue ID. This endpoint is key for tracking the progress or issues of individual tasks.",
    operation_id="getSpecificTaskStatus",
    response_model=Response,
    tags=["Tasks"])
async def get_queue_status(request: Request, queueID: UUID4 = Query(..., description="The ID of the queue to retrieve")):
    try:
        task = get_task_by_queueID(MEMORY_HOST, queueID)
        request.state.timing_marks.append(('task-load', time.time()))
        return Response(result=task.model_dump())
    except Exception as e:
        return Response(error=True, message=str(e))

@app.post(
    '/queue_task',
    summary="Queue a New Task",
    description="Allows the submission of a new task to the queue system. This endpoint is used to add tasks that will be processed according to the queue logic.",
    operation_id="queueNewTask",
    response_model=Response,
    tags=["Tasks"])
async def queue_task(request: Request, payload: QueueTaskPayload):
    try:
        new_task = Task(taskData=payload.taskData, status='queued', metadata=payload.metadata)
        task = add_task(MEMORY_HOST, new_task)
        if task:
            request.state.timing_marks.append(('task-write', time.time()))
            return Response(result=task.model_dump(), message="Task created successfully")
        else:
            return Response(error=True, message="Task creation failed")
    except Exception as e:
        return Response(error=True, message=str(e))

@app.patch(
    '/update_task', 
    summary="Update an Existing Task",
    description="Updates the properties of an existing task in the queue. This can be used to modify the status, systemmessage, result or other metadata after the task has been queued.",
    operation_id="updateExistingTask",
    response_model=Response,
    tags=["Tasks"])
async def update_task_action(request: Request, task: Task):
    try:
        updated_task = update_task(MEMORY_HOST, task)
        if updated_task:
            request.state.timing_marks.append(('task-write', time.time()))
            return Response(result=updated_task.model_dump(), message="Task updated successfully")
        else:
            return Response(error=True, message="Task update failed")
    except Exception as e:
        return Response(error=True, message=str(e))

# Exception-Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return Response(result=None, error=True, message=exc.detail)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
