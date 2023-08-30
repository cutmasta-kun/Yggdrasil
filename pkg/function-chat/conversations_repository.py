# conversations_repository.py
import uuid
import logging
import requests
import json

# Configurate application
logging.basicConfig(level=logging.INFO)

def create_conversation(host):
    """
    Create a new conversation in the conversations table
    :param host: The host URL of the Datasette instance
    :return: uuid of the new conversation
    """
    # Generate a unique UUID
    conversation_uuid = str(uuid.uuid4())
    # Define the URL for the create_conversation query
    url = f"{host}/conversations/create_conversation.json"
    # Define the headers for the POST request
    headers = {
        'Content-Type': 'application/json'
    }
    # Define the data for the POST request
    data = {
        "uuid": conversation_uuid
    }
    try:
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Check if the request was successful
        response.raise_for_status()
        # Return the UUID
        return conversation_uuid
    except requests.exceptions.RequestException as err:
        # Log the error and return None
        print(f"Something went wrong: {err}")
        return None

from typing import NamedTuple, Optional, List, Union
import re

class SpeechBubble(NamedTuple):
    content: str
    role: str
    name: Optional[str] = None
    function_call: Optional[str] = None
    metadata: Optional[str] = None

    def _format_function_call(self, function_call_str: Union[str, dict]) -> dict:
        """Konvertiert den function_call String in ein Dictionary, wobei 'arguments' ein String bleibt."""

        if isinstance(function_call_str, dict):
            return function_call_str
        
        if not function_call_str or function_call_str == 'None':
            return {}
        
        # Ersetzen von Mustern wie '{'name': 'value'}' in {"name": "value"}
        if re.match(r"^\{'.+': '.+'\}$", function_call_str):
            function_call_str = function_call_str.replace("'", "\"").replace('"{', '{').replace('}"', '}')
        
        try:
            return json.loads(function_call_str)
        except json.JSONDecodeError:
            logging.error(f"Failed to format function_call string: {function_call_str}")
            return {"error": "Invalid function_call format"}

    def to_user_bubble_json(self) -> dict:
        if self.role != 'user':
            raise ValueError("This method should only be called on 'user' SpeechBubble objects.")
        return {"role": self.role, "content": self.content}

    def speech_bubble_to_dict(self) -> dict:
        bubble_dict = {
            "content": self.content,
            "role": self.role,
            "name": self.name,
            "function_call": self._format_function_call(self.function_call)
        }

        # If function_call exists and is a dictionary, and contains 'arguments', then convert 'arguments' to a string
        function_call = bubble_dict.get("function_call")
        if isinstance(function_call, dict) and 'arguments' in function_call:
            bubble_dict["function_call"]["arguments"] = json.dumps(function_call["arguments"])

        # Remove None or 'None' values
        if self.function_call == 'None' or self.function_call is None:
            bubble_dict.pop("function_call", None)
        if self.name == 'None' or self.name is None:
            bubble_dict.pop("name", None)

        return bubble_dict

def add_speech_bubble(host: str, conversation_uuid: str, speech_bubble: SpeechBubble) -> bool:
    """
    Add a speech bubble to a conversation
    :param host: The host URL of the Datasette instance
    :param conversation_uuid: UUID of the conversation
    :param speech_bubble: SpeechBubble object representing the speech bubble to be added
    :return: True if successful, False otherwise
    """
    # Define the URL for the add_speech_bubble query
    url = f"{host}/conversations/add_speech_bubble.json"
    
    # Define the headers for the POST request
    headers = {
        'Content-Type': 'application/json'
    }

    # Get the speech bubble data in the desired format
    data = {}
    data["content"] = speech_bubble.content
    data["role"] = speech_bubble.role
    data["function_call"] = speech_bubble.function_call
    data["uuid"] = conversation_uuid  # Add the conversation UUID to the data
    data["name"] = speech_bubble.name
    data["metadata"] = speech_bubble.metadata
    if speech_bubble.function_call is None:
        data["function_call"] = None

    # Ensure metadata is serialized to JSON if it is not None
    if data.get('metadata') is not None:
        data['metadata'] = json.dumps(data['metadata'])

    try:
        # Send the POST request
        response = requests.post(url, headers=headers, data=json.dumps(data))
        # Check if the request was successful
        response.raise_for_status()
        # Return True if the addition was successful
        return True
    except requests.exceptions.RequestException as err:
        # Log the error and return False
        print(f"Something went wrong: {err}")
        return False

def get_conversation_from_repo(host: str, conversation_uuid: str) -> Optional[List[SpeechBubble]]:
    """
    Get a conversation by UUID
    :param host: The host URL of the Datasette instance
    :param conversation_uuid: UUID of the conversation
    :return: List of the last 5 speech bubbles in the conversation
    """
    # Define the URL for the get_conversation query
    url = f"{host}/conversations/get_conversation_by_uuid.json"

    # Define the parameters for the GET request
    params = {
        "uuid": conversation_uuid
    }
    return fetch_data_from_repo(url, params)

def search_in_conversation_from_repo(host, conversation_uuid, query_tags):
    """
    Search for a specific tag in a conversation
    :param host: The host URL of the Datasette instance
    :param conversation_uuid: UUID of the conversation
    :param query_tags: Tag to search for in the conversation
    :return: List of speech bubbles containing the tag in the conversation
    """
    # Define the URL for the search_in_conversation query
    url = f"{host}/conversations/search_in_conversation.json"
    # Define the parameters for the GET request
    params = {
        "uuid": conversation_uuid,
        "queryTags": query_tags
    }
    return fetch_data_from_repo(url, params)

def fetch_data_from_repo(url: str, params: dict) -> Optional[List[SpeechBubble]]:
    """
    Fetch data from Datasette instance
    :param url: The URL for the query
    :param params: The parameters for the GET request
    :return: List of speech bubbles 
    """
    try:
        # Send the GET request
        response = requests.get(url, params=params)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Check if any speech bubbles were returned
            if data and "rows" in data and "columns" in data and len(data["rows"]) > 0:
                # Convert rows to list of dictionaries
                rows_as_dicts = [dict(zip(data["columns"], row)) for row in data["rows"]]

                return [SpeechBubble(**row_dict) for row_dict in rows_as_dicts]

    except requests.exceptions.RequestException as err:
        # Log the error and return None
        print(f"Something went wrong: {err}")
        return None

def get_all_conversations(host):
    """
    Get all conversations that have at least one speech bubble
    :param host: The host URL of the Datasette instance
    :return: List of UUIDs of the conversations
    """
    # Define the URL for the get_all_conversations query
    url = f"{host}/conversations/get_all_conversations.json"
    try:
        # Send the GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            # Check if any UUIDs were returned
            if data and "rows" in data and len(data["rows"]) > 0:
                # Return the UUIDs
                return [row[0] for row in data["rows"]]
    except requests.exceptions.RequestException as err:
        # Log the error and return None
        print(f"Something went wrong: {err}")
        return None
