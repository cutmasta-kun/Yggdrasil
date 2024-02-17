### Task Queue Manager API Documentation

#### API Specification (`openapi.yaml`)
- **Base URL**: `http://localhost:5010`
- **Endpoints**:
  - **`GET /get_queues`**: Retrieve All Tasks in Queues
    - **OperationId**: `getAllQueuedTasks`
    - **Responses**:
      - **200**: Successful Response - List of all tasks in queues.
      - **422**: Validation Error

  - **`GET /get_queue_status`**: Retrieve Specific Task Status
    - **OperationId**: `getSpecificTaskStatus`
    - **Required Parameters**:
      - `queueID`: UUID (required)
    - **Responses**:
      - **200**: Successful Response - Status of a specific task.
      - **422**: Validation Error

  - **`POST /queue_task`**: Queue a New Task
    - **OperationId**: `queueNewTask`
    - **RequestBody**:
      - `QueueTaskPayload`: Includes taskData and optional metadata.
    - **Responses**:
      - **200**: Successful Response - New task queued.
      - **422**: Validation Error

  - **`PATCH /update_task`**: Update an Existing Task
    - **OperationId**: `updateExistingTask`
    - **RequestBody**:
      - `Task`: Task details including queueID, taskData, status, result, systemMessage and metadata.
    - **Responses**:
      - **200**: Successful Response - Task updated.
      - **422**: Validation Error

#### Capabilities & Usage (`README.md`)
- **Main Feature**: Management and retrieval of tasks within a queue system.
- **Usage**:
  - **Retrieve Tasks**: GET request to `/get_queues` to retrieve all tasks.
  - **Get Task Status**: GET request to `/get_queue_status` with `queueID`.
  - **Queue New Task**: POST request to `/queue_task` with `TaskData`.
  - **Update Task**: PATCH request to `/update_task` with task details.