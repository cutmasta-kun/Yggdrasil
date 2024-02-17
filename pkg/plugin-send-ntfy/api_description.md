### NTFY Plugin Documentation

#### API Specification (`openapi.yaml`)
- **Version**: 1.0.0
- **Endpoint `/send` (POST)**
  - **OperationId**: `send`
  - **Required Parameters**:
    - `message`: String (required)
    - `tags`: String or null (optional)

#### Capabilities & Usage (`README.md`)
- **Main Feature**: Send notifications via API calls
- **Usage**: POST request to `/send` with `message` and optional `tags`
- **Request Example**:
  ```json
  {
    "message": "Hello World!",
    "tags": "urgent"
  }
  ```
- **Response Codes**:
  - **200**: Successful
  - **400**: Client Error
  - **422**: Validation Error
