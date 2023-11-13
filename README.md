# Yggdrasil - Short Term Memory Plugin

Yggdrasil's Short Term Memory Plugin is a flexible and robust system designed to store and retrieve short-term memory items. It provides a RESTful API for interaction with the short-term memory service, allowing for operations such as adding and retrieving memories based on UUIDs.

## Overview

The Short Term Memory Plugin is part of the Yggdrasil ecosystem and is responsible for managing temporary data storage. It is ideal for scenarios where data needs to be retained for a short period and accessed via unique identifiers.

## Getting Started

To get started with the Short Term Memory Plugin, clone the repository and navigate to the plugin directory:

```bash
git clone https://github.com/cutmasta-kun/Yggdrasil.git
cd Yggdrasil/pkg/plugin-short-term-memory
```

Ensure that you have Python 3.8 or higher installed, and install the required dependencies:

```bash
pip install -r requirements.txt
```

Start the service by running:

```bash
python main.py
```

## API Endpoints

The service provides the following endpoints:

- `POST /add_memory`: Adds a message to the short term memory.
- `GET /get_memory`: Retrieves a specific memory by its UUID or all memories if no UUID is provided.
- `GET /healthcheck`: Returns the health status of the service and its dependencies.

For detailed information on request parameters and response formats, refer to the API documentation provided in the `openapi.yaml` file.

## Health Checks

The `/healthcheck` endpoint provides a quick way to assess the health of the service and its dependencies. A successful check returns a status code of 200 and a JSON response indicating the status of each dependency.

## Configuration

The service can be configured using environment variables. The following are key variables:

- `MEMORY_HOST`: The hostname of the memory service.
- `PORT`: The port on which the service will run.

Set these variables before starting the service to ensure proper connectivity and operation.

## Error Handling

The service uses standard HTTP status codes to indicate the success or failure of an API request. In case of an error, the response will include a JSON object with an `error` field describing the issue.

## Dependencies

This plugin requires the following services to be running:

- Memory Service: A separate service that handles the actual storage of memory items.

Ensure that the Memory Service is accessible via the `MEMORY_HOST` environment variable.

## Development and Contribution

Contributions to the Short Term Memory Plugin are welcome. Please follow the standard GitHub flow by forking the repository, making changes, and submitting a pull request.

## Testing

To run the automated tests, use the following command:

```bash
pytest
```

Ensure that all tests pass before submitting any changes to the codebase.

## Deployment

The service can be deployed as a standalone application or as part of a Docker container. For containerized deployment, use the provided `Dockerfile`.

## Versioning

The service follows semantic versioning. Check the `CHANGELOG.md` file for information on changes between versions.

## Security Considerations

It is recommended to run the service behind a reverse proxy that handles SSL termination. Do not expose the service directly to the internet without proper security measures in place.

## FAQs

For frequently asked questions, please refer to the `FAQ.md` file in the repository.

## Contact and Support

For support or to contact the maintainers, please open an issue on the GitHub repository.

1. **Informationsbeschaffung**: Yggdrasil kann an neue und unabhängige Informationen kommen. Zum Beispiel ermöglicht das Arxiv Search Plugin die Suche nach wissenschaftlichen Arbeiten auf ArXiv.

2. **Informationsspeicherung**: Yggdrasil kann Informationen speichern und abrufen. Dies wird durch den Memory Service und das Memory Interface Plugin ermöglicht, die sowohl für kurzfristige als auch für langfristige Speicheranforderungen verwendet werden können.

3. **Kommunikation**: Yggdrasil kann Benachrichtigungen an externe Systeme senden und auf spezifische NTFY-Themen hören. Dies wird durch das NTFY Plugin und den Communication Service ermöglicht.

4. **Funktionsauslösung**: Yggdrasil kann verschiedene Funktionen auslösen, basierend auf den empfangenen Nachrichten. Dies wird durch den Communication Service und den Function Service ermöglicht.

## Installation

Um Yggdrasil zu installieren, führen Sie die folgenden Befehle aus:

```bash
git clone https://github.com/cutmasta-kun/Yggdrasil.git
cd /Yggdrasil/deploy
docker compose build
docker compose up
```

## Weiterentwicklung

Yggdrasil ist ein offenes Projekt und wir freuen uns über Beiträge von der Community. Wenn Sie eine Idee für eine Verbesserung haben oder einen Fehler gefunden haben, zögern Sie bitte nicht, ein Issue zu eröffnen oder einen Pull Request zu erstellen.
