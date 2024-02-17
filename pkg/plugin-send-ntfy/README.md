# NTFY Plugin

## Overview
The NTFY Plugin allows users to send notifications via NTFY directly from the chat interface. It's designed to be simple and effective, enabling you to send a quick message or notification to yourself or your team.

## Version
1.0.0

## Features
- **Send Notifications**: Send a notification with a simple API call.

## How to Use
To send a notification, make a POST request to the `/send` endpoint with the required parameters.

### Request Example:
```json
POST /send
Content-Type: application/json

{
  "message": "Hello World!",
  "tags": "urgent"
}
```

### Response:
- **200**: Notification sent successfully.
- **422**: Validation Error.

## Error Handling
Errors are returned as HTTPValidationError objects. Each error will detail the location, message, and type of error that occurred.

## Contact and Support
For any queries or support, please contact: cutmastakun@gmail.com

## Legal Information
For legal inquiries, please visit: [Legal Info](https://example.com/legal)

## Additional Information
This plugin is developed to be used as a part of a larger system. It relies on the OpenAPI specification for defining and documenting its API interactions. For further customization or integration, refer to the `openapi.yaml` and `ai-plugin.json` files located at the server root.

### Request Examples
- Send a basic message: `{'action': 'send', 'parameters': {'message': '# EXAMPLE MESSAGE'}}`

### Logo
![NTFY Plugin Logo](http://localhost:5003/logo.png)

Thank you for using the NTFY Plugin!
```