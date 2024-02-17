# Short Term Memory Plugin Documentation

## Overview

The Short Term Memory Plugin is a component of the Yggdrasil ecosystem designed to manage temporary data storage. It provides a RESTful API for adding and retrieving short-term memory items, which are identified by UUIDs.

## API Endpoints

The plugin provides several endpoints for interacting with the short-term memory:

- `POST /add_memory`: Adds a new memory item.
- `GET /get_memory`: Retrieves memory items by UUID or all memories if no UUID is provided.
- `GET /healthcheck`: Checks the health of the service and its dependencies.

## Configuration

The service can be configured using environment variables:

- `MEMORY_HOST`: The hostname of the memory service (default: `http://memory:5006`).
- `PORT`: The port on which the service will run (default: `5030`).

Set these variables before starting the service to customize its behavior.
