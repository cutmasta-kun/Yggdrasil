# flask_server.py
from flask import Flask, send_file, request, Response, jsonify
from flask_cors import CORS
import logging
import os
from tasks_repository import get_tasks, add_task, get_task_by_queueID, update_task

# Configurate application
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app)  # Enable CORS

# Extrahieren Sie den MEMORY_HOST aus den Umgebungsvariablen oder verwenden Sie den Standardwert
MEMORY_HOST = os.getenv('MEMORY_HOST', 'http://memory:8001')

@app.route("/logo.png", methods=['GET'])
def plugin_logo():
    filename = 'logo.png'
    return send_file(filename, mimetype='image/png')

@app.route("/openapi.yaml", methods=['GET'])
def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return Response(text, mimetype="text/yaml")

@app.route("/.well-known/ai-plugin.json", methods=['GET'])
def plugin_manifest():
    host = request.headers['Host']
    with open("./ai-plugin.json") as f:
        text = f.read()
        return Response(text, mimetype="application/json")

@app.route('/get_queues', methods=['GET'])
def get_queues():
    # Get the tasks
    tasks = get_tasks(MEMORY_HOST)
    if tasks:
        # Prepare a list to hold the task dictionaries
        tasks_list = []
        # Loop through the tasks
        for task in tasks:
            # Append each task as a dictionary to the list
            tasks_list.append({
                "queueID": task[1],
                "taskData": task[2],
                "status": task[3],
                "result": task[4],
                "systemMessage": task[5],
                "created_at": task[6]
            })
        # Return the list of tasks
        return jsonify(tasks_list)
    else:
        return jsonify({"error": "No tasks found"}), 404


@app.route('/get_queue_status', methods=['GET'])
def get_queue_status():
    queueID = request.args.get('queueID')
    # Get the task by queueID
    task = get_task_by_queueID(MEMORY_HOST, queueID)
    if task:
        # Return the task status
        return jsonify({
            "taskData": task[2],
            "status": task[3],
            "result": task[4],
            "systemMessage": task[5]
        })
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/queue_task', methods=['POST'])
def queue_task():
    taskData = request.get_json().get('taskData')
    # Create a new task
    task = [None, taskData, 'queued', None, None]

    # Add the task to the memory
    queueID = add_task(MEMORY_HOST, task)
    # Return the response
    return jsonify({
        "status": "queued",
        "queueID": queueID,
        "systemMessage": None
    })

@app.route('/update_task', methods=['PATCH'])
def update_task_action():
    # Get the task data from the request
    task = request.get_json()
    # Update the task in the memory
    result = update_task(MEMORY_HOST, task)
    # If the update was successful, return a success response
    if result:
        return jsonify({
            "status": "success",
            "message": "Task updated successfully"
        })
    # If the update was not successful, return an error response
    else:
        return jsonify({"error": "Task update failed"}), 400


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5010)