import logging
import json
import autogen
from autogen import config_list_from_json, AssistantAgent, UserProxyAgent, Completion
import os
from typing import List, Dict, Tuple

logging.basicConfig(level=logging.INFO)

test_config = config_list_from_json(env_or_file="OAI_CONFIG_LIST")
logging.info(f"test_config: {test_config}")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

def load_system_messages(json_file_path: str) -> List[Dict]:
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data['messages']
    except FileNotFoundError:
        logging.error(f"Die Datei {json_file_path} wurde nicht gefunden.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Es gab einen Fehler beim Decodieren der Datei {json_file_path}.")
        return []
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return []

def send_request(messages: List[Dict]) -> Tuple[Dict, str, int]:
    has_system_message = any(msg.get('role') == 'system' for msg in messages)
    system_messages = load_system_messages('system.json')

    all_messages = system_messages + messages if not has_system_message else messages

    completion_result = Completion.create(
        messages=all_messages,
        model="gpt-4",
    )

    completion_message = completion_result.get("choices", [{}])[0].get("message", None)

    if not completion_message:
        error_message = "Entschuldigung, ich konnte keine Antwort generieren. Bitte versuchen Sie es später erneut."
        all_messages.append({"content": error_message, "role": "assistant"})
        return {'messages': all_messages}, None, 200

    if isinstance(completion_message, dict) and "content" in completion_message:
        completion_message = completion_message["content"]
    
    all_messages.append({"content": completion_message, "role": "assistant"})

    if not has_system_message:
        all_messages = all_messages[len(system_messages):]

    return {'messages': all_messages}, None, 200

def validate_messages(messages: List[Dict]) -> bool:
    if not messages:
        return False

    for message in messages:
        if 'role' not in message or 'content' not in message:
            return False

    return True