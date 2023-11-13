# Short Term Memory Plugin Documentation

## Overview

The Short Term Memory Plugin is a component of the Yggdrasil ecosystem designed to manage temporary data storage. It provides a RESTful API for adding and retrieving short-term memory items, which are identified by UUIDs.

## Installation

To install the Short Term Memory Plugin, follow these steps:

1. Clone the Yggdrasil repository:
   ```bash
   git clone https://github.com/cutmasta-kun/Yggdrasil.git
   ```
2. Navigate to the plugin directory:
   ```bash
   cd Yggdrasil/pkg/plugin-short-term-memory
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To start the service, run the following command in the plugin directory:
```bash
python main.py
```

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

## Development

To contribute to the development of the Short Term Memory Plugin, you can fork the repository, make changes, and submit a pull request.

## Testing

Run the automated tests with the following command:
```bash
pytest
```

Ensure that all tests pass before submitting any changes to the codebase.

## Deployment

The service can be deployed as a standalone application or as part of a Docker container. Refer to the `Dockerfile` for containerized deployment instructions.

## Contact

For support or to contact the maintainers, please open an issue on the GitHub repository.
