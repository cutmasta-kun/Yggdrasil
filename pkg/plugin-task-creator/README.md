Basierend auf Ihren Dokumentationen für die "Task Queue Manager" API und dem AI-Plugin, erstelle ich eine README-Datei, die sich am Beispiel der "Short Term Memory Plugin Documentation" orientiert.

---

# Task Queue Manager Documentation

## Overview

The Task Queue Manager is a sophisticated system designed to manage and control tasks within a queue system. This API facilitates the management, retrieval, and updating of tasks, offering a robust solution for task queueing and processing.

## API Endpoints

The Task Queue Manager provides the following endpoints:

- `GET /get_queues`: Retrieve all tasks in the queue.
- `GET /get_queue_status`: Get the status of a specific task using its queue ID.
- `POST /queue_task`: Add a new task to the queue.
- `PATCH /update_task`: Update an existing task in the queue.

## Configuration

Configuration can be done using environment variables:

- `PORT`: Port for running the service (default: `5010`).
- `MEMORY_HOST`: URL of the memory service (default: `http://plugin-memory-interface:5005`).

Ensure these variables are set before launching the service.
