# post_flask_actions.py
import uuid
import json
import requests
import logging

def post_action(request, path, MEMORY_HOST):
    generated_uuid = uuid.uuid4()
    data = request.get_json()
    if data is not None:  # überprüfen, ob der Request Body leer ist
        data['uuid'] = str(generated_uuid)
    else:
        data = {'uuid': str(generated_uuid)}
    data = json.dumps(data)

    params = request.args.to_dict()

    response = requests.request(
        method=request.method,
        url=f"{MEMORY_HOST}/{path}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        params=params, 
        data=data,
        allow_redirects=False)

    headers = [('Transfer-Encoding', 'identity')]  # Disable chunked transfer encoding

    # Check if the 'Location' header is in the response, and if so, add it to your own headers
    if 'Location' in response.headers:
        headers.append(('Location', f"{response.headers['Location']}{generated_uuid}"))
    
    # Assume the response is not JSON and set response_content accordingly
    response_content = response.text

    logging.info(response.headers.get('Content-Type'))

    # Check if the response is JSON, and if so, change the 'redirect' field
    if response.headers.get('Content-Type').startswith('application/json'):
        try:
            body = response.json()  # Convert the response body to a Python dict
            logging.info(body)
            if body.get("ok", False) and body.get("message", "").endswith(" inserted") and 'redirect' in body:
                redirect_base = body['redirect']
                body['redirect'] = f"{redirect_base}{generated_uuid}"
                response_content = json.dumps(body)
        except ValueError:
            logging.error(ValueError)
            pass  # Not a JSON response; do nothing

    return response_content, response.status_code, headers
