import logging
import requests
import json
from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict
from enum import Enum

# Configurate loggin
logging.basicConfig(level=logging.INFO)

RETRIEVAL_API_URL_BASE = 'http://retrieval-app:8080'

### FUNKTIONS

def search_knowledge(search_term):
    api_url = f"{RETRIEVAL_API_URL_BASE}/query"
    headers = {"Content-Type": "application/json"}

    # Erstellen Sie die Daten für den POST-Request
    data = {
        "queries": [
            {
                "query": search_term
            }
        ]
    }

    try:
        # Senden Sie den POST-Request an die API
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Dies wirft eine Ausnahme, wenn der Request fehlschlägt
    except requests.RequestException as e:
        # Behandeln Sie hier jegliche Request-Fehler
        return f"Ein Fehler ist aufgetreten: {e}"
    
    # Die Antwort der API
    api_response = response.json()

    # Formatieren Sie die Antwort für eine bessere Lesbarkeit
    formatted_response = format_api_response(api_response)

    return formatted_response
    
def add_memory(text):
    api_url = "http://retrieval-app:8080/upsert"
    headers = {"Content-Type": "application/json"}

    # Erstellen Sie die Daten für den POST-Request
    data = {
        "documents": [
            {
                "text": text,
                # Fügen Sie hier weitere Felder hinzu oder setzen Sie Standardwerte, falls erforderlich
            }
        ]
    }

    try:
        # Senden Sie den POST-Request an die API
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()  # Dies wirft eine Ausnahme, wenn der Request fehlschlägt
    except requests.RequestException as e:
        # Behandeln Sie hier jegliche Request-Fehler
        return f"Ein Fehler ist aufgetreten: {e}"
    
    # Die Antwort der API
    api_response = response.json()

    # Extrahieren Sie die IDs aus der Antwort
    document_ids = api_response.get("ids", [])

    # Formatieren Sie die Antwort für eine bessere Lesbarkeit
    if document_ids:
        formatted_response = f"Erinnerung erfolgreich hinzugefügt. Dokument-ID(s): {', '.join(document_ids)}"
    else:
        formatted_response = "Es wurde keine neue Erinnerung hinzugefügt."

    return formatted_response

def format_api_response(api_response):
    formatted_response = ""
    if 'results' in api_response:
        for result in api_response['results']:
            query = result.get('query')
            formatted_response += f"Anfrage: {query}\n"
            if 'results' in result:
                for item in result['results']:
                    text = item.get('text')
                    score = item.get('score')
                    document_id = item.get('metadata', {}).get('document_id')
                    source = item.get('metadata', {}).get('source')
                    
                    formatted_response += f"Dokument-ID: {document_id}\n"
                    formatted_response += f"Text: {text}\n"
                    formatted_response += f"Score: {score}\n"
                    formatted_response += f"Quelle: {source}\n"
                    formatted_response += "\n"  # Fügt eine Leerzeile für die Lesbarkeit hinzu
    else:
        formatted_response = "Keine Ergebnisse gefunden."
    
    return formatted_response


functions = [
    {
        "name": "search_knowledge",
        "description": "Führt eine Suchanfrage in der Wissensdatenbank aus",
        "parameters": {
            "type": "object",
            "properties": {
                "search_term": {
                    "type": "string",
                    "description": "Der Begriff oder die Phrase, nach der in der Wissensdatenbank gesucht werden soll",
                }
                # Sie können hier zusätzliche erwartete Parameter hinzufügen, basierend auf Ihrer API-Spezifikation
            },
            "required": ["search_term"],
        },
    },
    {
        "name": "add_memory",
        "description": "Fügt einen neuen Text zur Wissensdatenbank hinzu, der als Erinnerung gespeichert wird",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Der Text, der als Erinnerung in der Wissensdatenbank gespeichert werden soll"
                }
                # Sie können hier zusätzliche Parameter hinzufügen, wenn Ihre API sie benötigt
            },
            "required": ["text"],
        },
    }
]

### OPENAPI API LLM

def call_openai_api(headers, model, messages, functions=None):
    openai_api_url = 'https://api.openai.com/v1/chat/completions'

    data = {
        'model': model,
        'messages': messages
    }
    if functions:
        data['functions'] = functions

    logging.debug(data)

    try:
        response = requests.post(openai_api_url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        logging.error(f"An error occurred: {err}")
        return None
    
def load_system_messages(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data['messages']
    except FileNotFoundError:
        print(f"Die Datei {json_file_path} wurde nicht gefunden.")
        return []
    except json.JSONDecodeError:
        print(f"Es gab einen Fehler beim Decodieren der Datei {json_file_path}.")
        return []
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return []

def send_request(messages, headers, AI_MODEL, functions=functions):
    all_messages = messages  # Setzen Sie all_messages standardmäßig auf die übergebenen Nachrichten

    # Überprüfen, ob eine system-Nachricht in den übergebenen Nachrichten vorhanden ist
    has_system_message = any(msg.get('role') == 'system' for msg in messages)

    system_messages = load_system_messages('system.json')

    # Wenn keine system-Nachricht vorhanden ist, laden Sie die system-Nachrichten und fügen Sie sie hinzu
    if not has_system_message:
        all_messages = system_messages + messages

    logging.info(f"all_messages: {all_messages}")
    
    response_data = call_openai_api(headers, AI_MODEL, all_messages, functions)

    if not response_data:
        return None, 'Server Error', 500

    # Überprüfen, ob ein Funktionsaufruf erforderlich ist
    if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
        choice = response_data['choices'][0]
        message = choice.get('message', {})  # Extrahieren des 'message'-Objekts aus 'choice'

        if 'function_call' in message:  # Prüfen, ob 'function_call' in 'message' vorhanden ist
            function_call_data = message['function_call']
            function_name = function_call_data['name']
            # Die "arguments" sind als String im JSON-Format, wir müssen sie in ein Dictionary umwandeln
            arguments = json.loads(function_call_data['arguments'])

            # Hinzufügen des Funktionsaufrufs als separate Nachricht
            function_call_message = {
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": function_call_data['arguments']  # Behalten Sie die Argumente als JSON-String
                }
            }

            all_messages.append(function_call_message)

            # Aufrufen der entsprechenden Funktion basierend auf dem Funktionsnamen
            if function_name in [
                'search_knowledge',
                'add_memory'
                ]:  # Fügen Sie hier weitere Funktionsnamen hinzu, wenn notwendig

                function_result = globals()[function_name](**arguments)  # globals() ermöglicht den dynamischen Aufruf der Funktion nach Namen
                
                # Füge die Funktionsantwort als separate Nachricht hinzu
                function_response_message = {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)  # Die Antwort muss als String vorliegen
                }

                all_messages.append(function_response_message)

                # Nachdem die Funktion aufgerufen wurde und ihre Antwort erhalten hat, führen Sie den zweiten Aufruf durch
                second_response_data = call_openai_api(headers, AI_MODEL, all_messages)

                if not second_response_data:
                    return None, 'Server Error', 500

                if 'choices' in second_response_data and len(second_response_data['choices']) > 0:
                    # Extrahiere die Antwort des Assistenten aus den "choices"
                    assistant_reply = second_response_data['choices'][0].get('message', {}).get('content', '')
                    
                    # Füge die Antwort des Assistenten als neue Nachricht hinzu
                    assistant_reply_message = {
                        "role": "assistant",
                        "content": assistant_reply
                    }
                    all_messages.append(assistant_reply_message)
        else:
            # Wenn kein Funktionsaufruf vorliegt, fügen Sie die Antwort des Assistenten direkt hinzu
            assistant_reply = message.get('content', '')
            assistant_reply_message = {
                "role": "assistant",
                "content": assistant_reply
            }
            all_messages.append(assistant_reply_message)

    # Entfernen von Systemnachrichten aus der Antwort
    # Da system_messages am Anfang hinzugefügt wurden, können wir einfach die ersten N Elemente entfernen,
    # wobei N die Anzahl der Nachrichten in system_messages ist.
    
    response_messages = all_messages

    if not has_system_message:
        response_messages = all_messages[len(system_messages):]

    return {'messages': response_messages}, None, 200

def validate_messages(messages):
    logging.info(f"validate_messages messages: {messages}")
    if not messages:
        return False

    for message in messages:
        if 'role' not in message or 'content' not in message:
            return False

    return True