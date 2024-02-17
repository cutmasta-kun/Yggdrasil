# ask.py

import logging
import json
import os
from typing import List, Dict, Tuple
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

class Message(BaseModel):
    content: str
    role: str

def load_system_messages(json_file_path: str) -> List[Message]:
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return [Message(**message) for message in data['messages']]
    except FileNotFoundError:
        logging.error(f"Die Datei {json_file_path} wurde nicht gefunden.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Es gab einen Fehler beim Decodieren der Datei {json_file_path}.")
        return []
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return []

from openai import OpenAI

client = OpenAI()

def send_request(messages: List[Message], model: str) -> Tuple[Dict, str, int]:
    has_system_message = any(msg.role == 'system' for msg in messages)
    system_messages = load_system_messages('system.json')

    all_messages = system_messages + messages if not has_system_message else messages

    completion_result = client.chat.completions.create(
        messages=[msg.dict() for msg in all_messages],
        model=model,
    )

    completion_message = completion_result.choices[0].message.content

    if not completion_message:
        error_message = "Entschuldigung, ich konnte keine Antwort generieren. Bitte versuchen Sie es später erneut."
        all_messages.append(Message(content=error_message, role="assistant"))
        return {'messages': [msg.dict() for msg in all_messages]}, None, 200

    if isinstance(completion_message, dict) and "content" in completion_message:
        completion_message = completion_message["content"]
    
    all_messages.append(Message(content=completion_message, role="assistant"))

    if not has_system_message:
        all_messages = all_messages[len(system_messages):]

    return {'messages': [msg.dict() for msg in all_messages]}, None, 200
