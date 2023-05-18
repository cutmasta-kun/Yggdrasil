import requests
import json

url = "http://localhost:8001/messages/add_message.json"
data = {"message": "Hello, world!"}

response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

print(response.status_code)
print(response.text)
