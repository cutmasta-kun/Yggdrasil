### Short Term Memory Interface Plugin Documentation

#### API Specification (`openapi.yaml`)
- **Version**: 1.0.0
- **Endpoints**:
  - **`POST /add_memory`**: Add to Short Term Memory
    - **OperationId**: `addToShortTermMemory`
    - **Required Parameters**:
      - `message`: String (required)
    - **Responses**:
      - **200**: Successful Response
      - **422**: Validation Error

  - **`GET /get_memory`**: Retrieve Short Term Memory
    - **OperationId**: `getShortTermMemory`
    - **Parameters**:
      - `uuid`: String or null (optional)
      - `limit`: Integer (optional, default 10)
    - **Responses**:
      - **200**: Successful Response
      - **422**: Validation Error

  - **`DELETE /delete_memory`**: Delete a Short Term Memory
    - **OperationId**: `deleteShortTermMemorybyUUID`
    - **Required Parameters**:
      - `uuid`: String (required)
    - **Responses**:
      - **200**: Successful Response
      - **422**: Validation Error

#### Capabilities & Usage (`README.md`)
- **Main Feature**: Manage temporary data storage identified by UUIDs
- **Usage**:
  - **Add Memory**: POST request to `/add_memory` with `message`
  - **Get Memory**: GET request to `/get_memory` with optional `uuid` and `limit`
  - **Delete Memory**: DELETE request to `/delete_memory` with `uuid`

#### Request & Response Examples
- **Add Memory Request**:
  ```json
  {
    "message": "Sample memory message"
  }
  ```
- **Get Memory Response**:
  ```json
  {
    "ok": true,
    "message": "Memory retrieved",
    "redirect": "optional_redirect_url"
  }
  ```