# flask_server.py
from flask import Flask, send_file, request, Response
from flask_cors import CORS
import requests
import json
import logging
import uuid

# Configurate application
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS

@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def plugin_manifest():
    host = request.headers['Host']
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def catch_all(path):
    # Überprüfen Sie, ob der Pfad mit '.json' endet und fügen Sie es hinzu, wenn nicht
    if not path.endswith('.json'):
        path += '.json'

    generated_uuid = None
    if request.method == 'POST':
        generated_uuid = uuid.uuid4()
        data = request.get_json()
        if data is not None:  # überprüfen, ob der Request Body leer ist
            data['uuid'] = str(generated_uuid)
        else:
            data = {'uuid': str(generated_uuid)}
        data = json.dumps(data)
    else:
        data = request.get_data()

    params = request.args.to_dict() if request.method == 'GET' else {}

    response = requests.request(
        method=request.method,
        url=f"http://memory:8001/{path}",
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
                logging.info(body.get('redirect'))
                body['redirect'] = f"{redirect_base}{generated_uuid}"
                logging.info(body.get('redirect'))
                response_content = json.dumps(body)
        except ValueError:
            logging.error(ValueError)
            pass  # Not a JSON response; do nothing

    response = app.response_class(
        response_content,
        status=response.status_code,
        headers=headers,
        mimetype='application/json')

    return response

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5005)
